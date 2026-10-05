#!/usr/bin/env python3
"""Generate a static lapis-themed GitHub "Streak" card SVG for the profile README.

Self-hosted replacement for github-readme-streak-stats.herokuapp.com, which
started timing out / returning 503 — GitHub's camo proxy then renders a broken
image. Same three numbers (total contributions, current streak, longest streak),
pulled via the authenticated `gh` CLI and rendered in the lapis palette. Same
static-by-design pattern as gen-stats-card.py / gen-weekly-contrib.py.

    python scripts/gen-streak-card.py

Requires: `gh auth login`.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _backup import add_backup_args, maybe_snapshot  # noqa: E402

# --- lapis theme (shared with gen-stats-card.py) ----------------------------
BG = "#0A1633"        # surface
BORDER = "#1E2A54"    # border / dividers / ring track
INK = "#C7D0E8"       # primary numbers
INK_MUTED = "#7A88B8" # labels / date ranges
GOLD = "#B7995B"      # ring, flame, current-streak label
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"

# octicon flame (16x16 viewBox)
FLAME = ("M9.533.753V.752c.217 2.385 1.463 3.626 2.653 4.81C13.37 6.74 14.498 "
         "7.863 14.498 10c0 3.5-3 6-6.5 6S1.5 13.512 1.5 10c0-1.298.536-2.56 "
         "1.425-3.286.376-.308.862 0 1.035.454C4.46 8.487 5.581 8.419 6 8c.282-"
         ".282.341-.811-.003-1.5C4.34 3.187 7.035.75 8.77.146c.39-.137.726.204."
         "763.607ZM8.5 14.5c1.5 0 2.5-1 2.5-2.5 0-.5-.08-1.064-.5-1.5-.448 1.17-"
         "1.5 1.5-1.5 1.5s.52-1.37-.5-2.5c-1 1-2.5 1.5-2.5 2.5 0 1.5 1 2.5 2.5 2.5Z")


def gh_graphql(query, **vars_):
    cmd = ["gh", "api", "graphql", "-f", "query=" + query]
    for k, v in vars_.items():
        cmd += ["-f", f"{k}={v}"]
    return json.loads(subprocess.check_output(cmd, text=True))["data"]


def fetch_days(login, today):
    """All contribution days since account creation, oldest first.

    contributionsCollection spans at most one year per call, so walk year by
    year from createdAt to today.
    """
    created = gh_graphql(
        "query($login:String!){user(login:$login){createdAt}}", login=login
    )["user"]["createdAt"][:10]
    start = dt.date.fromisoformat(created)
    query = (
        "query($login:String!,$from:DateTime!,$to:DateTime!){"
        "user(login:$login){contributionsCollection(from:$from,to:$to){"
        "contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"
    )
    days = {}
    for year in range(start.year, today.year + 1):
        lo = max(start, dt.date(year, 1, 1))
        hi = min(today, dt.date(year, 12, 31))
        cal = gh_graphql(
            query, login=login,
            **{"from": f"{lo}T00:00:00Z", "to": f"{hi}T23:59:59Z"},
        )["user"]["contributionsCollection"]["contributionCalendar"]
        for w in cal["weeks"]:
            for d in w["contributionDays"]:
                day = dt.date.fromisoformat(d["date"])
                if lo <= day <= hi:
                    days[day] = d["contributionCount"]
    return start, sorted(days.items())


def streaks(days, today):
    """-> (current, cur_start, cur_end, longest, long_start, long_end).

    Like streak-stats, a zero day *today* doesn't break the current streak
    (the day isn't over yet).
    """
    longest = (0, None, None)
    run, run_start = 0, None
    for day, n in days:
        if n > 0:
            if run == 0:
                run_start = day
            run += 1
            if run > longest[0]:
                longest = (run, run_start, day)
        else:
            run = 0
    # current streak: walk back from today, tolerating an empty today
    counts = dict(days)
    d = today
    if counts.get(d, 0) == 0:
        d -= dt.timedelta(days=1)
    end = d
    cur = 0
    while counts.get(d, 0) > 0:
        cur += 1
        d -= dt.timedelta(days=1)
    cur_start = d + dt.timedelta(days=1)
    return (cur, cur_start if cur else None, end if cur else None,
            longest[0], longest[1], longest[2])


def fmt_day(d, today):
    return d.strftime("%b %-d" if os.name != "nt" else "%b %#d") + (
        "" if d.year == today.year else d.strftime(", %Y"))


def fmt_range(a, b, today):
    if a is None:
        return "—"
    if a == b:
        return fmt_day(a, today)
    return f"{fmt_day(a, today)} – {fmt_day(b, today)}"


def render(total, since, cur, cur_rng, longest, long_rng):
    W, H = 495, 195
    col = W / 3
    c1, c2, c3 = col / 2, W / 2, W - col / 2
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # column dividers
        f'<line x1="{col:.1f}" y1="28" x2="{col:.1f}" y2="{H-28}" stroke="{BORDER}"/>',
        f'<line x1="{2*col:.1f}" y1="28" x2="{2*col:.1f}" y2="{H-28}" stroke="{BORDER}"/>',
    ]

    def stat(cx, value, label, sub, value_y, label_y, label_fill):
        out.append(
            f'<text x="{cx:.1f}" y="{value_y}" fill="{INK}" font-size="28" '
            f'font-weight="700" text-anchor="middle">{value}</text>')
        out.append(
            f'<text x="{cx:.1f}" y="{label_y}" fill="{label_fill}" font-size="14" '
            f'font-weight="600" text-anchor="middle">{label}</text>')
        out.append(
            f'<text x="{cx:.1f}" y="{label_y + 22}" fill="{INK_MUTED}" '
            f'font-size="12" text-anchor="middle">{sub}</text>')

    stat(c1, f"{total:,}", "Total Contributions", since, 92, 128, INK_MUTED)
    stat(c3, f"{longest:,}", "Longest Streak", long_rng, 92, 128, INK_MUTED)

    # current streak: gold ring with a flame notch on top
    ry = 80
    r = 40
    out.append(
        f'<circle cx="{c2:.1f}" cy="{ry}" r="{r}" fill="none" stroke="{GOLD}" '
        f'stroke-width="5"/>')
    out.append(  # mask the ring behind the flame
        f'<rect x="{c2-13:.1f}" y="{ry-r-14}" width="26" height="26" fill="{BG}"/>')
    out.append(
        f'<g transform="translate({c2-10:.1f},{ry-r-12}) scale(1.25)" '
        f'fill="{GOLD}"><path d="{FLAME}"/></g>')
    out.append(
        f'<text x="{c2:.1f}" y="{ry+10}" fill="{INK}" font-size="28" '
        f'font-weight="700" text-anchor="middle">{cur:,}</text>')
    out.append(
        f'<text x="{c2:.1f}" y="{ry+r+28}" fill="{GOLD}" font-size="14" '
        f'font-weight="700" text-anchor="middle">Current Streak</text>')
    out.append(
        f'<text x="{c2:.1f}" y="{ry+r+50}" fill="{INK_MUTED}" font-size="12" '
        f'text-anchor="middle">{cur_rng}</text>')
    out.append("</svg>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", default="Chancelife")
    ap.add_argument("--out", default="assets/streak-card.svg")
    add_backup_args(ap)
    args = ap.parse_args()

    today = dt.date.today()
    start, days = fetch_days(args.login, today)
    total = sum(n for _, n in days)
    cur, cs, ce, longest, ls, le = streaks(days, today)
    svg = render(
        total, f"{fmt_day(start, dt.date.min)} – Present",
        cur, fmt_range(cs, ce, today), longest, fmt_range(ls, le, today),
    )
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg + "\n")
    print(f"wrote {args.out}: total={total} current={cur} longest={longest}")
    maybe_snapshot(args)


if __name__ == "__main__":
    main()
