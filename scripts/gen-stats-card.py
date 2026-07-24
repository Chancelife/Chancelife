#!/usr/bin/env python3
"""Generate a static lapis-themed GitHub "Stats" card SVG for the profile README.

Self-hosted replacement for the github-profile-summary-cards Action's
`3-stats.svg` / `0-profile-details.svg`, which stopped generating once GitHub
tightened the Action's default GITHUB_TOKEN access to user-level GraphQL data
("Resource not accessible by integration") — AUTO_PUSH then deleted the cards.

This pulls the same numbers via the authenticated `gh` CLI (your token, which
*can* see user-level + private-contribution data) and renders them in the exact
lapis palette, so it can never 503 or lose access. Same static-by-design pattern
as gen-weekly-contrib.py / gen-agent-stack.py.

    python scripts/gen-stats-card.py

Requires: `gh auth login`.
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _backup import add_backup_args, maybe_snapshot  # noqa: E402

# --- lapis theme (shared with gen-weekly-contrib.py) -----------------------
BG = "#0A1633"        # surface
BORDER = "#1E2A54"    # border
TRACK = "#1E2A54"     # rank ring track
INK = "#C7D0E8"       # primary text
INK_MUTED = "#7A88B8" # labels / secondary
BLUE = "#3B6BB0"
GOLD = "#B7995B"      # icons, values accent, rank ring/letter
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"

# octicons (16x16 viewBox) — icon for each stat row
ICONS = {
    "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z",
    "commit": "M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "pr": "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.573.677A.25.25 0 0 1 10 .854V2.5h1A2.5 2.5 0 0 1 13.5 5v5.628a2.251 2.251 0 1 1-1.5 0V5a1 1 0 0 0-1-1h-1v1.646a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354ZM3.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm0 9.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm8.25.75a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0Z",
    "issue": "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z",
    "repo": "M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z",
}


def fetch(login):
    query = (
        "query($login:String!){user(login:$login){"
        "contributionsCollection{totalCommitContributions restrictedContributionsCount "
        "totalPullRequestReviewContributions}"
        "repositoriesContributedTo(first:1,contributionTypes:[COMMIT,PULL_REQUEST,ISSUE,REPOSITORY,PULL_REQUEST_REVIEW]){totalCount}"
        "repositories(first:100,ownerAffiliations:OWNER,isFork:false){nodes{stargazerCount}}"
        "pullRequests{totalCount} openIssues:issues(states:OPEN){totalCount} "
        "closedIssues:issues(states:CLOSED){totalCount} followers{totalCount}}}"
    )
    cmd = ["gh", "api", "graphql", "-f", "query=" + query, "-f", "login=" + login]
    u = json.loads(subprocess.check_output(cmd, text=True))["data"]["user"]
    cc = u["contributionsCollection"]
    return {
        "stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "prs": u["pullRequests"]["totalCount"],
        "issues": u["openIssues"]["totalCount"] + u["closedIssues"]["totalCount"],
        "contributed": u["repositoriesContributedTo"]["totalCount"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "followers": u["followers"]["totalCount"],
    }


def calc_rank(s):
    """github-readme-stats v2 rank algorithm -> (letter, percentile)."""
    def exp_cdf(x):
        return 1 - 2 ** -x

    def log_normal_cdf(x):
        return x / (1 + x)

    MED = {"commits": 1000, "prs": 50, "issues": 25, "reviews": 2,
           "stars": 50, "followers": 10}
    W = {"commits": 2, "prs": 3, "issues": 1, "reviews": 1, "stars": 4, "followers": 1}
    total_w = sum(W.values())
    rank = 1 - (
        W["commits"] * exp_cdf(s["commits"] / MED["commits"])
        + W["prs"] * exp_cdf(s["prs"] / MED["prs"])
        + W["issues"] * exp_cdf(s["issues"] / MED["issues"])
        + W["reviews"] * exp_cdf(s["reviews"] / MED["reviews"])
        + W["stars"] * log_normal_cdf(s["stars"] / MED["stars"])
        + W["followers"] * log_normal_cdf(s["followers"] / MED["followers"])
    ) / total_w
    thresholds = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
    levels = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]
    pct = rank * 100
    letter = next(lv for t, lv in zip(thresholds, levels) if pct <= t)
    return letter, pct


def human(n):
    if n >= 1000:
        return f"{n/1000:.1f}".rstrip("0").rstrip(".") + "k"
    return str(n)


def icon(name, x, y):
    return (f'<g transform="translate({x},{y})" fill="{GOLD}">'
            f'<path fill-rule="evenodd" d="{ICONS[name]}"/></g>')


def render(s, year):
    W, H = 470, 200
    L = 28
    letter, pct = calc_rank(s)

    rows = [
        ("star", "Total Stars Earned", s["stars"]),
        ("commit", f"Total Commits ({year})", s["commits"]),
        ("pr", "Total PRs", s["prs"]),
        ("issue", "Total Issues", s["issues"]),
        ("repo", "Contributed to (last year)", s["contributed"]),
    ]
    val_right = 320  # right edge of the value column

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="{L}" y="36" fill="{INK}" font-size="18" '
        f'font-weight="600">GitHub Stats</text>',
    ]

    row_y0, step = 66, 27
    for i, (ic, label, val) in enumerate(rows):
        cy = row_y0 + i * step
        out.append(icon(ic, L, cy - 13))  # 16px glyph, vertically centred on text
        out.append(
            f'<text x="{L+26}" y="{cy}" fill="{INK_MUTED}" font-size="13">{label}</text>'
        )
        out.append(
            f'<text x="{val_right}" y="{cy}" fill="{INK}" font-size="13" '
            f'font-weight="600" text-anchor="end">{val:,}</text>'
        )

    # --- rank ring (right) --------------------------------------------------
    import math
    cx, cyc, r = 400, 104, 44
    frac = max(0.02, 1 - pct / 100)  # better rank (lower pct) => fuller ring
    circ = 2 * math.pi * r
    # track
    out.append(
        f'<circle cx="{cx}" cy="{cyc}" r="{r}" fill="none" stroke="{TRACK}" '
        f'stroke-width="6"/>'
    )
    # progress arc, starting at 12 o'clock, clockwise
    out.append(
        f'<circle cx="{cx}" cy="{cyc}" r="{r}" fill="none" stroke="{GOLD}" '
        f'stroke-width="6" stroke-linecap="round" '
        f'stroke-dasharray="{circ:.2f}" '
        f'stroke-dashoffset="{circ*(1-frac):.2f}" '
        f'transform="rotate(-90 {cx} {cyc})"/>'
    )
    out.append(
        f'<text x="{cx}" y="{cyc+2}" fill="{GOLD}" font-size="26" '
        f'font-weight="700" text-anchor="middle">{letter}</text>'
    )
    out.append(
        f'<text x="{cx}" y="{cyc+20}" fill="{INK_MUTED}" font-size="10" '
        f'text-anchor="middle">top {pct:.0f}%</text>'
    )

    out.append("</svg>")
    return "\n".join(out)


def main():
    import datetime as dt
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", default="Chancelife")
    ap.add_argument("--year", default=str(dt.date.today().year))
    ap.add_argument("--out", default="assets/stats-card.svg")
    add_backup_args(ap)
    args = ap.parse_args()

    s = fetch(args.login)
    svg = render(s, args.year)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg + "\n")
    letter, pct = calc_rank(s)
    print(f"wrote {args.out}: stars={s['stars']} commits={s['commits']} "
          f"prs={s['prs']} issues={s['issues']} contributed={s['contributed']} "
          f"rank={letter} (top {pct:.0f}%)")
    maybe_snapshot(args)


if __name__ == "__main__":
    main()
