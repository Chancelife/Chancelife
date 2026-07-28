#!/usr/bin/env python3
"""Refresh all self-hosted profile cards in one go, under a single timestamp.

Runs each generator (stats / weekly-contributions / agent-stack), which writes
its SVG into assets/ AND drops a timestamped copy into backup/. Passing one
shared --stamp means a single refresh lands as one coherent dated set in backup/,
so you can browse `backup/*_2026-07-24_1450.svg` as "everything as of that run".

    python scripts/refresh-all.py                # refresh all, archive to backup/
    python scripts/refresh-all.py --no-backup    # refresh without archiving

Requires: `gh auth login` (stats + weekly hit the GitHub GraphQL API).
"""
import argparse
import datetime as dt
import subprocess
import sys

GENERATORS = [
    "scripts/gen-stats-card.py",
    "scripts/gen-weekly-contrib.py",
    "scripts/gen-agent-stack.py",
    "scripts/gen-model-fleet.py",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-backup", action="store_true",
                    help="refresh the cards but skip the backup/ snapshots")
    args = ap.parse_args()

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    print(f"refresh-all @ {stamp}")

    failures = []
    for gen in GENERATORS:
        cmd = [sys.executable, gen, "--stamp", stamp]
        if args.no_backup:
            cmd.append("--no-backup")
        print(f"\n$ {' '.join(cmd)}")
        if subprocess.run(cmd).returncode != 0:
            failures.append(gen)

    if failures:
        print(f"\nDONE with errors: {', '.join(failures)} failed", file=sys.stderr)
        sys.exit(1)
    print(f"\nDONE — all cards refreshed{'' if args.no_backup else f', backups tagged {stamp}'}")


if __name__ == "__main__":
    main()
