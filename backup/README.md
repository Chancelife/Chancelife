# backup/

A stacked, timestamped archive of every generated profile card.

Each time a generator runs it writes its live SVG into `assets/` **and** drops a
dated copy here, named `<card>_<YYYY-MM-DD_HHMM>.svg`. Nothing here is deleted or
overwritten across runs, so this folder grows into a full history you can:

- browse chronologically to see *when* each card was refreshed, and
- diff between two dates to see exactly how each number moved
  (`git diff --no-index backup/stats-card_A.svg backup/stats-card_B.svg`).

The README never references `backup/`, so these copies stay off the profile page.

## Refresh (writes assets/ + a new dated set here)

```
python scripts/refresh-all.py          # all cards, one shared timestamp
python scripts/gen-stats-card.py       # a single card (its own timestamp)
```

Add `--no-backup` to any of them to refresh without archiving.
