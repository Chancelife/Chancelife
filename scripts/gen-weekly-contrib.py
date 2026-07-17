#!/usr/bin/env python3
"""Generate a static weekly-contributions bar chart SVG for the profile README.

Pulls GitHub contribution data via the authenticated `gh` CLI (GraphQL
contributionCalendar, which is already grouped by week), aggregates each week
into a single total, and renders a lapis-themed bar chart.

Static by design: run it whenever you want to refresh the card.

    python scripts/gen-weekly-contrib.py                 # this year -> today
    python scripts/gen-weekly-contrib.py --to 2026-07-16 # pin the end date

Requires: `gh auth login` (uses your token for the GraphQL call).
"""
import argparse
import datetime as dt
import json
import subprocess

# --- lapis theme -----------------------------------------------------------
BG = "#0A1633"        # surface
BORDER = "#1E2A54"    # border + recessive gridlines
GRID = "#1B294F"      # gridlines (slightly under border)
INK = "#C7D0E8"       # primary text
INK_MUTED = "#7A88B8" # secondary text / labels
BLUE = "#3B6BB0"      # gradient bottom
GOLD = "#B7995B"      # gradient top / max highlight
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"


def fetch_weeks(login, dfrom, dto):
    query = (
        "query($login:String!,$from:DateTime!,$to:DateTime!){"
        "user(login:$login){contributionsCollection(from:$from,to:$to){"
        "contributionCalendar{totalContributions "
        "weeks{firstDay contributionDays{date contributionCount}}}}}}"
    )
    cmd = [
        "gh", "api", "graphql",
        "-f", "query=" + query,
        "-f", "login=" + login,
        "-f", "from=" + dfrom + "T00:00:00Z",
        "-f", "to=" + dto + "T23:59:59Z",
    ]
    data = json.loads(subprocess.check_output(cmd, text=True))
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [
        (w["firstDay"], sum(d["contributionCount"] for d in w["contributionDays"]))
        for w in cal["weeks"]
    ]
    return weeks, cal["totalContributions"]


def nice_ceiling(v):
    if v <= 0:
        return 100
    step = 100 if v > 200 else 50 if v > 100 else 20
    import math
    return int(math.ceil(v / step) * step)


def top_rounded_bar(x, y, w, h, r):
    """Path for a bar with only its top corners rounded, baseline at y+h."""
    r = max(0, min(r, w / 2, h))
    return (
        f"M{x:.1f},{y + h:.1f} "
        f"V{y + r:.1f} "
        f"A{r:.1f},{r:.1f} 0 0 1 {x + r:.1f},{y:.1f} "
        f"H{x + w - r:.1f} "
        f"A{r:.1f},{r:.1f} 0 0 1 {x + w:.1f},{y + r:.1f} "
        f"V{y + h:.1f} Z"
    )


def render(weeks, total, year, dto):
    W, H = 850, 232
    L, R, T, B = 46, 18, 56, 34
    plot_w = W - L - R
    plot_h = H - T - B
    n = len(weeks)
    vals = [v for _, v in weeks]
    vmax = max(vals) if vals else 0
    ymax = nice_ceiling(vmax)

    slot = plot_w / n
    bar_w = slot * 0.60
    base_y = T + plot_h

    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">'
    )
    # defs: vertical gradient (blue bottom -> gold top), shared across the plot
    out.append(
        f'<defs><linearGradient id="bar" gradientUnits="userSpaceOnUse" '
        f'x1="0" y1="{base_y}" x2="0" y2="{T}">'
        f'<stop offset="0" stop-color="{BLUE}"/>'
        f'<stop offset="1" stop-color="{GOLD}"/>'
        f'</linearGradient></defs>'
    )
    # background card
    out.append(
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6" '
        f'fill="{BG}" stroke="{BORDER}"/>'
    )
    # title + subtitle
    out.append(
        f'<text x="{L}" y="26" fill="{INK}" font-size="17" '
        f'font-weight="600">Weekly Contributions</text>'
    )
    out.append(
        f'<text x="{L}" y="44" fill="{INK_MUTED}" font-size="12">'
        f'{year} · {total:,} contributions</text>'
    )
    # gridlines + y labels
    steps = 4
    for i in range(steps + 1):
        val = ymax * i // steps
        gy = base_y - (val / ymax) * plot_h
        out.append(
            f'<line x1="{L}" y1="{gy:.1f}" x2="{W-R}" y2="{gy:.1f}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{L-8}" y="{gy+3.5:.1f}" fill="{INK_MUTED}" '
            f'font-size="10" text-anchor="end">{val}</text>'
        )
    # bars
    for i, (first_day, v) in enumerate(weeks):
        x = L + i * slot + (slot - bar_w) / 2
        h = (v / ymax) * plot_h if ymax else 0
        y = base_y - h
        is_max = v == vmax and v > 0
        fill = GOLD if is_max else "url(#bar)"
        if h > 0:
            out.append(
                f'<path d="{top_rounded_bar(x, y, bar_w, h, 3)}" fill="{fill}"/>'
            )
        if is_max:
            out.append(
                f'<text x="{x + bar_w/2:.1f}" y="{y-5:.1f}" fill="{GOLD}" '
                f'font-size="10" font-weight="600" text-anchor="middle">{v}</text>'
            )
    # month labels (place at first week of each month)
    prev_month = None
    for i, (first_day, _) in enumerate(weeks):
        month = first_day[:7]
        if month != prev_month:
            prev_month = month
            cx = L + i * slot + slot / 2
            label = dt.date.fromisoformat(first_day).strftime("%b")
            out.append(
                f'<text x="{cx:.1f}" y="{base_y+18:.1f}" fill="{INK_MUTED}" '
                f'font-size="10" text-anchor="middle">{label}</text>'
            )
    out.append("</svg>")
    return "\n".join(out)


def main():
    today = dt.date.today()
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", default="Chancelife")
    ap.add_argument("--from", dest="dfrom", default=f"{today.year}-01-01")
    ap.add_argument("--to", dest="dto", default=today.isoformat())
    ap.add_argument("--out", default="assets/weekly-contributions.svg")
    args = ap.parse_args()

    weeks, total = fetch_weeks(args.login, args.dfrom, args.dto)
    year = args.dfrom[:4]
    svg = render(weeks, total, year, args.dto)

    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg + "\n")
    print(f"wrote {args.out}: {len(weeks)} weeks, {total} total, peak {max(v for _,v in weeks)}")


if __name__ == "__main__":
    main()
