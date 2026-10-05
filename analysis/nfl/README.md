# NFL Scorer Tracker

Builds the Google Sheet **NFL Scorer Tracker 2026**
(https://docs.google.com/spreadsheets/d/1VPYeOtn3BGq4JYPiwkI_XfvVXCGyvg7nMhGGOzl2VTM/edit,
spreadsheet ID `1VPYeOtn3BGq4JYPiwkI_XfvVXCGyvg7nMhGGOzl2VTM`) from ESPN box scores,
play-by-play and the ESPN injuries feed. Small stakes, for fun.

## Weekly refresh (Tuesday, after Monday night)

1. Rebuild every tab. `--week` is the last 2026 week to include:

   ```
   python3 analysis/nfl/build_tracker.py --week 5
   ```

   It downloads only the new 2026 games (parsed games are cached in `data/`), then writes:
   - `out/sheet_values.json`: every tab as a 2D array, ready for the Sheets connector
     (text like `3/4` is prefixed with `'` so Sheets does not turn it into a date)
   - `out/*.csv`: the same tabs as CSV
   - `out/rank_2026.md`: the 2026-only top 15 TD and receptions tables for the report

   A game inside `--week` that is not final yet is skipped and named on the Notes tab;
   rerun the same command after it ends.

2. Push to the sheet with the Google Sheets connector, one tab at a time:
   `batch_clear_values` on `'<Tab>'!A2:AD500`, then `update_values` with range `'<Tab>'!A1`
   and the tab's array from `out/sheet_values.json`. Tabs: Scorers, Red Zone, Injuries,
   Defense, Week Shortlist, Notes. To print one tab:

   ```
   python3 -c "import json;print(json.dumps(json.load(open('analysis/nfl/out/sheet_values.json'))['Scorers']))"
   ```

3. Commit `data/` and `out/` so the next run starts from the cache.

## Saturday injury recheck

```
python3 analysis/nfl/build_tracker.py --week 5 --injuries-only
```

Refreshes only Injuries, Week Shortlist and Notes from the live injuries feed (no game downloads).
Push those three tabs.

## How numbers are computed

- TD = rushing + receiving TD (no return or passing TDs). Hit % = games with a TD / games played.
- RZ opp = target or carry on a play that started inside the opponent 20 (i10 = inside the 10),
  counted from play-by-play text, penalties excluded. Estimates, not official counts.
- Defense rank #1 = allows the most to that position (softest). RZ TD% allowed = opponent drives
  with a play inside the 20 that ended in a TD.
- Week Shortlist verdicts follow a fixed rule written on the Notes tab.
- Sources that block scripts (Pro-Football-Reference, FootballDB) are not used; routes run and
  snap counts are not available.
