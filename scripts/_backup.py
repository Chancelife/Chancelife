"""Shared helper: archive a just-generated asset into backup/ with a timestamp.

Every generator calls snapshot(out_path) right after writing its SVG, so backup/
accumulates a dated copy of *every* version — a stacked history you can browse
chronologically and diff to see how each number moved over time. The README
never references backup/, so these copies stay off the profile page.

Filenames are `<stem>_<YYYY-MM-DD_HHMM>.svg`, e.g. `stats-card_2026-07-24_1450.svg`.
Pass a shared `stamp` (see scripts/refresh-all.py) so a single refresh of all
cards lands under one coherent timestamp.
"""
import datetime as dt
import os
import shutil

BACKUP_DIR = "backup"


def default_stamp():
    return dt.datetime.now().strftime("%Y-%m-%d_%H%M")


def snapshot(out_path, stamp=None):
    """Copy out_path into backup/ with a timestamped name; return the dest path."""
    stamp = stamp or default_stamp()
    stem, ext = os.path.splitext(os.path.basename(out_path))
    os.makedirs(BACKUP_DIR, exist_ok=True)
    dest = os.path.join(BACKUP_DIR, f"{stem}_{stamp}{ext}")
    shutil.copyfile(out_path, dest)
    return dest


def add_backup_args(ap):
    """Register the shared --stamp / --no-backup flags on an ArgumentParser."""
    ap.add_argument("--stamp", default=None,
                    help="timestamp label for the backup copy (default: now)")
    ap.add_argument("--no-backup", action="store_true",
                    help="skip writing a timestamped copy into backup/")


def maybe_snapshot(args):
    """Snapshot args.out unless --no-backup; print the backup path."""
    if getattr(args, "no_backup", False):
        return None
    dest = snapshot(args.out, args.stamp)
    print(f"  backup -> {dest}")
    return dest
