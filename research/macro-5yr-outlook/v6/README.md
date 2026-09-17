# v6 — historical-replay module for the BDCR-26 put-strategy model

One command (from `research/macro-5yr-outlook`):

    python3 -m v6.run          # downloads (cached in v6/data/cache), replays, writes v6/report_v6.md
    python3 -m pytest v6/tests -q

Files: `data/loaders.py` (loaders + source tags), `surfaces.py` (parametric surface per date + arbitrage checks),
`episodes.yaml`, `replay.py` (structures, daily walk, exit rules, filter), `timing.py` (§0 reconciliation),
`run.py` (driver + report), `tests/`, `report_v6.md`, `results_*.csv`, `v4_reconciled.json`.

Acceptance-criteria status (spec §10):
- §7 tests: 6/6 pass. The 2020 sanity band (20–50x) is met by the steep-skew surface (T^-0.5); the spec-default
  slope gives ~300x and is asserted as such so the discrepancy stays visible.
- Regenerates from raw data in one command with cached downloads: yes (GitHub-hosted mirrors; FRED/CBOE/Yahoo/Stooq are
  blocked in this environment).
- Every number carries a source tag: report header + `meta` in loaders. No real surface is available; everything is
  parametric, spliced or proxy and says so.
- Header states N episodes, exclusions and that ranges, not points, are the deliverable.
- §0 timing reconciliation documented; the report's §2 timing is the one used; `v4_reconciled.json` holds the
  synthetic EVs re-run on that timing.

Known gaps: SKEW, VXO, VIX3M/6M/1Y, HY OAS, daily SPX after 2024-03-28 and any licensed surface are not reachable here.
NDX anchors in `loaders.ANCHORS_NDX` are from memory and must be verified. The v5 file is not present; seagull
definitions are reconstructed.
