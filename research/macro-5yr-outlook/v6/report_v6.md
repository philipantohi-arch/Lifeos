# report_v6.md — historical replay of the BDCR-26 put structures

Generated 2026-09-17 01:56 from raw data with cached downloads. **N = 10 crash episodes, 4 non-event windows, 404 unconditional month-end entries.** Ten replayed crash episodes (eleven defined) is not a distribution: every number below is a range-carrying estimate from a small sample, and no point estimate should be read without its neighbours in the episode table. Episodes excluded: 2025 (no daily SPX after 2024-03-28). Pre-2000 surfaces are parametric guesses; results are reported with and without pre-2000 episodes in §2.

**Source tags.** spx: futures-derived (Panama-adjusted continuous, re-anchored monthly to Shiller spot average; 3 Oct-1987 sessions overridden with published spot returns); ndx: futures-derived (Panama-adjusted, re-anchored to 10 remembered spot closes; VERIFY anchors); r3m: proxy (100 - Eurodollar/SOFR 3m futures, continuous); vix: real 1990+, realized proxy before; vix_term: VIX futures slope 2006+, default mean-reversion before; skew: NOT AVAILABLE -> parametric default 0.35*T^-0.25 (flat 0.10 before 1987-10 per regime flag); hy_oas: NOT AVAILABLE -> entry filter run without the HY leg; cape_ep_dy: Shiller monthly to 2023-09; NaN after (2025 episode excluded). Every surface is *parametric* (no licensed surface is reachable here). VIX term structure: 'vix-futures' where the VIX-futures slope exists (2006+), 'default-MR' before. Put wing: spec default 0.35·T^-0.25 everywhere (SKEW unavailable to fit), flat 0.10 before 1987-10-19.

## 0. Timing reconciliation (v4 engine vs report §2)

| Window | Report §2 | v4 engine | v6 engine |
|---|---:|---:|---:|
| pre-Nov-26 | 7% | 0.0% | 6.8% |
| Nov-26–Jun-27 | 13% | 32.2% | 12.2% |
| Jul-27–Jun-28 | 38% | 29.3% | 38.7% |
| Jul–Sep-28 | 4% | 1.4% | 5.2% |
| No crash within 24m | ~38% | 37.1% | 37.1% |

The v6 replay does not use scenario timing (it replays real dates), but the scenario-weighted EV in §1 uses the current BDCR-26 weights (28/19/17/17/14/5). For the synthetic model, the v6 windows above are the reconciled timing and are what `put_scenario_model_sept2026.py` should adopt (`SecondWave` 40% in months 0–1.5 and 60% in 1.5–20; `AI Bust` 6–22; `Repression` 8–24; `Fracture` 16–24). The report's §2 table is the timing used.

## 1. Main table (v4 format), historical conditionals

Entries within 12 months of each episode peak, exit rule = v4 (−22% index trigger), 7% haircuts. Conditionals are pooled means by BDCR analog: Muddle = 0.65 × correction episodes (2011/2015/2018) + 0.35 × non-event windows; Escape = non-event windows; Fracture = 1998 only (N=1). EV hist-weighted = Σ weight × conditional. Not replayable: SOXX (no index history here); NVDA, ORCL, PLTR, CRWV, VRT, DLR (single names: no price/vol history); HYG (no credit-ETF history).

| structure | cost % (median) | EV hist-weighted | P0 (crash entries) | >=3x | >=10x | Mu/Rp/AB/SW/Es/Fr | v4 synthetic EV (Sep-16) | v4 reconciled-timing EV | steep-skew cost % | steep-skew EV |
|---|---|---|---|---|---|---|---|---|---|---|
| SPX Jun-28 10% OTM | 4.51 | 1.72 | 0.71 | 0.21 | 0.05 | 0.1/2.1/0.6/7.0/0.1/0.0 | 2.20 | 1.92 | 4.24 | 1.91 |
| SPX Dec-27 10% OTM | 3.65 | 1.57 | 0.74 | 0.17 | 0.05 | 0.0/0.9/0.4/7.7/0.0/0.0 | 2.37 | 1.75 | 3.54 | 1.63 |
| SPX Mar-27 10% OTM | 2.10 | 1.29 | 0.85 | 0.10 | 0.05 | 0.0/0.0/0.2/7.3/0.0/0.0 | 1.28 | 1.63 | 2.26 | 1.20 |
| SPX Dec-27 90/70 spread | 2.00 | 1.12 | 0.73 | 0.19 | 0.03 | 0.0/1.5/0.7/4.2/0.1/0.0 | 2.07 | 1.46 | 2.02 | 1.11 |
| QQQ Jun-28 90/65 spread | 3.65 | 1.08 | 0.64 | 0.13 | 0.00 | 0.1/4.0/1.5/0.2/0.1/0.1 | 1.77 | 1.58 | 3.85 | 1.02 |
| SPX Mar-27 90/75 spread | 1.32 | 0.74 | 0.85 | 0.10 | 0.02 | 0.1/0.0/0.3/4.0/0.0/0.0 | 1.11 | 1.22 | 1.29 | 0.71 |
| QQQ Dec-27 90/65 spread | 3.38 | 0.68 | 0.76 | 0.08 | 0.00 | 0.1/1.8/1.5/0.2/0.1/0.1 | 1.92 | 1.44 | 3.45 | 0.65 |
| QQQ Dec-27 10% OTM | 5.70 | 0.51 | 0.76 | 0.05 | 0.00 | 0.1/1.2/1.2/0.3/0.1/0.1 | 2.19 | 1.65 | 5.53 | 0.52 |
| [B] QQQ Jun-27 p 11% OTM | 4.08 | 0.28 | 0.83 | 0.03 | 0.00 | 0.1/0.1/1.1/0.3/0.0/0.0 | 1.82 | 1.62 | 4.15 | 0.27 |

'steep-skew' = put slope 0.35·T^-0.5 instead of the spec default T^-0.25. The spec default prices short-dated deep wings far below observed levels (a 2-month 25%-OTM SPX put on 2020-02-14 costs 0.03% of spot under the default vs ~0.19% under the steep variant; the spec's own 2020 sanity band of 20-50x is met only by the steep variant). Long-dated 10%-OTM structures are much less sensitive to the choice.


With pre-2000 episodes excluded (2000, 2007, 2011, 2015, 2018, 2020, 2022 only):

(Fracture conditional = Second Wave here, since the only Fracture analog, 1998, is pre-2000.)

| structure | EV hist-weighted (post-2000) | Mu/Rp/AB/SW/Es/Fr |
|---|---|---|
| SPX Jun-28 10% OTM | 1.61 | 0.1/4.0/0.6/3.3/0.1/3.3 |
| SPX Dec-27 90/70 spread | 1.45 | 0.0/2.8/0.7/3.5/0.1/3.5 |
| SPX Dec-27 10% OTM | 1.29 | 0.0/1.8/0.4/4.0/0.0/4.0 |
| QQQ Jun-28 90/65 spread | 1.09 | 0.1/4.0/1.5/0.2/0.1/0.2 |
| SPX Mar-27 10% OTM | 0.93 | 0.0/0.0/0.2/4.0/0.0/4.0 |
| SPX Mar-27 90/75 spread | 0.78 | 0.1/0.0/0.3/3.2/0.0/3.2 |
| QQQ Dec-27 90/65 spread | 0.68 | 0.1/1.8/1.5/0.2/0.1/0.2 |
| QQQ Dec-27 10% OTM | 0.52 | 0.1/1.2/1.2/0.3/0.1/0.3 |
| [B] QQQ Jun-27 p 11% OTM | 0.30 | 0.1/0.1/1.1/0.3/0.0/0.3 |

### 1b. Seagulls (put spread part-financed by a far-OTM short call)

v5 is not present here; the definitions are reconstructed (SPX 16m +90p/−70p/−125c, QQQ 16m +90p/−65p/−135c, SPX 7m +90p/−75p/−115c). Multiples are of *max risk* = short-call loss on a +35% rally by expiry net of credit received, so they are not comparable to the put multiples above; the P&L columns in % of notional are the honest comparison. The lesson from the first pass (calls 8–12% OTM) survives: a seagull's payoff distribution is dominated by the short call in melt-ups, which is exactly the Muddle/Escape leg of the map.

| structure | set | N | mean P&L %notional | median P&L | worst P&L | best P&L | mean multiple of max-risk |
|---|---|---|---|---|---|---|---|
| QQQ Dec-27 seagull 90/65 -135c | crash entries (<=12m) | 78 | -1.79 | -0.99 | -34.47 | 14.75 | 1.33 |
| SPX Dec-27 seagull 90/70 -125c | crash entries (<=12m) | 123 | 2.80 | 2.75 | -8.31 | 16.15 | 2.48 |
| SPX Mar-27 seagull 90/75 -115c | crash entries (<=12m) | 123 | 0.69 | 0.19 | -14.81 | 11.39 | 1.04 |
| QQQ Dec-27 seagull 90/65 -135c | non-event windows | 25 | -3.30 | -2.68 | -9.42 | 14.75 | -0.07 |
| SPX Dec-27 seagull 90/70 -125c | non-event windows | 84 | -3.00 | -1.87 | -21.93 | 16.15 | 0.84 |
| SPX Mar-27 seagull 90/75 -115c | non-event windows | 91 | -0.53 | -0.54 | -15.11 | 2.95 | 0.97 |
| QQQ Dec-27 seagull 90/65 -135c | baseline 1990+ | 275 | -1.29 | -0.05 | -51.43 | 15.03 | 0.92 |
| SPX Dec-27 seagull 90/70 -125c | baseline 1990+ | 394 | 0.78 | 1.03 | -41.83 | 19.06 | 1.89 |
| SPX Mar-27 seagull 90/75 -115c | baseline 1990+ | 403 | 0.53 | 0.38 | -23.20 | 13.56 | 1.03 |

## 2. Episode table (v4 exit rule): best / median / worst entry offset

| episode | structure | best | median | worst | miss |
|---|---|---|---|---|---|
| 1987 | SPX Dec-27 10% OTM | 35.7x @-1m | 0.00x | 0.00x @-8m | 50% |
| 1987 | SPX Dec-27 90/70 spread | 14.3x @-1m | 0.00x | 0.00x @-8m | 50% |
| 1987 | SPX Dec-27 seagull 90/70 -125c | 8.7x @-11m | 3.10x | -16.27x @-23m | 50% |
| 1987 | SPX Jun-28 10% OTM | 31.2x @-1m | 0.00x | 0.00x @-24m | 25% |
| 1987 | SPX Mar-27 10% OTM | 55.7x @-1m | 0.00x | 0.00x @-24m | 88% |
| 1987 | SPX Mar-27 90/75 spread | 20.6x @-1m | 0.00x | 0.00x @-24m | 88% |
| 1987 | SPX Mar-27 seagull 90/75 -115c | 1.7x @-5m | 1.06x | 0.13x @-8m | 88% |
| 1990 | SPX Dec-27 10% OTM | 0.0x @-14m | 0.00x | 0.00x @-24m | 46% |
| 1990 | SPX Dec-27 90/70 spread | 0.0x @-14m | 0.00x | 0.00x @-24m | 46% |
| 1990 | SPX Dec-27 seagull 90/70 -125c | 9.6x @-8m | 5.17x | -1.21x @-22m | 46% |
| 1990 | SPX Jun-28 10% OTM | 0.0x @-19m | 0.00x | 0.00x @-24m | 21% |
| 1990 | SPX Mar-27 10% OTM | 0.0x @-10m | 0.00x | 0.00x @-21m | 83% |
| 1990 | SPX Mar-27 90/75 spread | 0.0x @-10m | 0.00x | 0.00x @-21m | 83% |
| 1990 | SPX Mar-27 seagull 90/75 -115c | 1.4x @-8m | 1.14x | 0.64x @-18m | 83% |
| 1998 | SPX Dec-27 10% OTM | 0.0x @-15m | 0.00x | 0.00x @-24m | 42% |
| 1998 | SPX Dec-27 90/70 spread | 0.0x @-15m | 0.00x | 0.00x @-24m | 42% |
| 1998 | SPX Dec-27 seagull 90/70 -125c | 2.5x @-4m | -0.71x | -3.77x @-16m | 42% |
| 1998 | SPX Jun-28 10% OTM | 0.0x @-12m | 0.00x | 0.00x @-24m | 12% |
| 1998 | SPX Mar-27 10% OTM | 0.0x @-5m | 0.00x | 0.00x @-17m | 79% |
| 1998 | SPX Mar-27 90/75 spread | 0.0x @-5m | 0.00x | 0.00x @-17m | 79% |
| 1998 | SPX Mar-27 seagull 90/75 -115c | 1.1x @-4m | 0.99x | 0.28x @-18m | 79% |
| 2000 | QQQ Dec-27 10% OTM | 1.8x @-1m | 1.75x | 1.54x @-2m | 100% |
| 2000 | QQQ Dec-27 90/65 spread | 2.7x @-3m | 2.28x | 2.02x @-1m | 100% |
| 2000 | QQQ Dec-27 seagull 90/65 -135c | 15.8x @-3m | 14.53x | 12.06x @-1m | 100% |
| 2000 | QQQ Jun-28 90/65 spread | 2.1x @-3m | 1.82x | 1.70x @-1m | 100% |
| 2000 | SPX Dec-27 10% OTM | 2.3x @-3m | 0.00x | 0.00x @-24m | 100% |
| 2000 | SPX Dec-27 90/70 spread | 4.7x @-3m | 0.00x | 0.00x @-24m | 100% |
| 2000 | SPX Dec-27 seagull 90/70 -125c | 17.2x @-3m | 3.38x | -20.85x @-19m | 100% |
| 2000 | SPX Jun-28 10% OTM | 2.8x @-4m | 0.00x | 0.00x @-24m | 100% |
| 2000 | SPX Mar-27 10% OTM | 0.0x @-5m | 0.00x | 0.00x @-23m | 100% |
| 2000 | SPX Mar-27 90/75 spread | 0.0x @-5m | 0.00x | 0.00x @-23m | 100% |
| 2000 | SPX Mar-27 seagull 90/75 -115c | 1.2x @-2m | 1.15x | -0.18x @-19m | 100% |
| 2000 | [B] QQQ Jun-27 p 11% OTM | 2.4x @-1m | 1.92x | 0.60x @-3m | 100% |
| 2007 | QQQ Dec-27 10% OTM | 4.3x @-4m | 0.00x | 0.00x @-23m | 100% |
| 2007 | QQQ Dec-27 90/65 spread | 7.4x @-4m | 0.00x | 0.00x @-23m | 100% |
| 2007 | QQQ Dec-27 seagull 90/65 -135c | 14.2x @-1m | 1.24x | 0.86x @-10m | 100% |
| 2007 | QQQ Jun-28 90/65 spread | 6.9x @-8m | 0.00x | 0.00x @-23m | 79% |
| 2007 | SPX Dec-27 10% OTM | 5.8x @-4m | 0.00x | 0.00x @-23m | 100% |
| 2007 | SPX Dec-27 90/70 spread | 10.4x @-4m | 0.00x | 0.00x @-23m | 100% |
| 2007 | SPX Dec-27 seagull 90/70 -125c | 3.4x @-2m | 1.13x | 1.07x @-10m | 100% |
| 2007 | SPX Jun-28 10% OTM | 6.5x @-6m | 0.00x | 0.00x @-23m | 79% |
| 2007 | SPX Mar-27 10% OTM | 0.1x @-1m | 0.00x | 0.00x @-23m | 100% |
| 2007 | SPX Mar-27 90/75 spread | 0.1x @-1m | 0.00x | 0.00x @-23m | 100% |
| 2007 | SPX Mar-27 seagull 90/75 -115c | 1.1x @-2m | 1.01x | 1.00x @-10m | 100% |
| 2007 | [B] QQQ Jun-27 p 11% OTM | 1.0x @-0m | 0.00x | 0.00x @-23m | 100% |
| 2011 | QQQ Dec-27 10% OTM | 0.0x @-13m | 0.00x | 0.00x @-10m | 56% |
| 2011 | QQQ Dec-27 90/65 spread | 0.0x @-13m | 0.00x | 0.00x @-10m | 56% |
| 2011 | QQQ Dec-27 seagull 90/65 -135c | 6.2x @-24m | 1.80x | -6.57x @-22m | 56% |
| 2011 | QQQ Jun-28 90/65 spread | 0.0x @-14m | 0.00x | 0.00x @-24m | 32% |
| 2011 | SPX Dec-27 10% OTM | 0.0x @-13m | 0.00x | 0.00x @-19m | 56% |
| 2011 | SPX Dec-27 90/70 spread | 0.0x @-13m | 0.00x | 0.00x @-19m | 56% |
| 2011 | SPX Dec-27 seagull 90/70 -125c | 2.7x @-10m | 1.22x | 0.72x @-22m | 56% |
| 2011 | SPX Jun-28 10% OTM | 0.0x @-14m | 0.00x | 0.00x @-24m | 32% |
| 2011 | SPX Mar-27 10% OTM | 1.0x @-2m | 0.00x | 0.00x @-6m | 92% |
| 2011 | SPX Mar-27 90/75 spread | 1.6x @-2m | 0.00x | 0.00x @-6m | 92% |
| 2011 | SPX Mar-27 seagull 90/75 -115c | 1.2x @-2m | 1.03x | 0.38x @-8m | 92% |
| 2011 | [B] QQQ Jun-27 p 11% OTM | 0.0x @-16m | 0.00x | 0.00x @-24m | 80% |
| 2015 | QQQ Dec-27 10% OTM | 0.0x @-13m | 0.00x | 0.00x @-24m | 71% |
| 2015 | QQQ Dec-27 90/65 spread | 0.0x @-13m | 0.00x | 0.00x @-24m | 71% |
| 2015 | QQQ Dec-27 seagull 90/65 -135c | 0.0x @-8m | 0.00x | -3.18x @-23m | 71% |
| 2015 | QQQ Jun-28 90/65 spread | 0.0x @-14m | 0.00x | 0.00x @-24m | 46% |
| 2015 | SPX Dec-27 10% OTM | 0.0x @-13m | 0.00x | 0.00x @-2m | 71% |
| 2015 | SPX Dec-27 90/70 spread | 0.0x @-13m | 0.00x | 0.00x @-2m | 71% |
| 2015 | SPX Dec-27 seagull 90/70 -125c | 0.9x @-23m | 0.83x | 0.59x @-21m | 71% |
| 2015 | SPX Jun-28 10% OTM | 0.0x @-14m | 0.00x | 0.00x @-24m | 46% |
| 2015 | SPX Mar-27 10% OTM | 0.1x @-3m | 0.00x | 0.00x @-13m | 100% |
| 2015 | SPX Mar-27 90/75 spread | 0.2x @-3m | 0.00x | 0.00x @-13m | 100% |
| 2015 | SPX Mar-27 seagull 90/75 -115c | 1.0x @-23m | 0.96x | 0.95x @-2m | 100% |
| 2015 | [B] QQQ Jun-27 p 11% OTM | 0.0x @-2m | 0.00x | 0.00x @-24m | 96% |
| 2018 | QQQ Dec-27 10% OTM | 3.3x @-1m | 0.00x | 0.00x @-24m | 46% |
| 2018 | QQQ Dec-27 90/65 spread | 3.5x @-1m | 0.00x | 0.00x @-24m | 46% |
| 2018 | QQQ Dec-27 seagull 90/65 -135c | 3.9x @-1m | 0.00x | -1.93x @-23m | 46% |
| 2018 | QQQ Jun-28 90/65 spread | 3.0x @-1m | 0.00x | 0.00x @-24m | 21% |
| 2018 | SPX Dec-27 10% OTM | 0.0x @-24m | 0.00x | 0.00x @-24m | 46% |
| 2018 | SPX Dec-27 90/70 spread | 0.0x @-24m | 0.00x | 0.00x @-24m | 46% |
| 2018 | SPX Dec-27 seagull 90/70 -125c | 0.8x @-2m | 0.81x | 0.13x @-24m | 46% |
| 2018 | SPX Jun-28 10% OTM | 4.2x @-1m | 0.00x | 0.00x @-24m | 21% |
| 2018 | SPX Mar-27 10% OTM | 0.0x @-13m | 0.00x | 0.00x @-24m | 83% |
| 2018 | SPX Mar-27 90/75 spread | 0.0x @-13m | 0.00x | 0.00x @-24m | 83% |
| 2018 | SPX Mar-27 seagull 90/75 -115c | 1.0x @-6m | 0.96x | 0.83x @-15m | 83% |
| 2018 | [B] QQQ Jun-27 p 11% OTM | 4.7x @-1m | 0.00x | 0.00x @-24m | 71% |
| 2020 | QQQ Dec-27 10% OTM | 3.5x @-17m | 0.00x | 0.00x @-24m | 38% |
| 2020 | QQQ Dec-27 90/65 spread | 3.7x @-17m | 0.00x | 0.00x @-24m | 38% |
| 2020 | QQQ Dec-27 seagull 90/65 -135c | 4.0x @-17m | -1.68x | -9.70x @-5m | 38% |
| 2020 | QQQ Jun-28 90/65 spread | 3.1x @-17m | 0.00x | 0.00x @-24m | 12% |
| 2020 | SPX Dec-27 10% OTM | 5.6x @-2m | 0.00x | 0.00x @-24m | 38% |
| 2020 | SPX Dec-27 90/70 spread | 5.2x @-10m | 0.00x | 0.00x @-24m | 38% |
| 2020 | SPX Dec-27 seagull 90/70 -125c | 1.9x @-10m | 0.83x | 0.77x @-9m | 38% |
| 2020 | SPX Jun-28 10% OTM | 4.7x @-17m | 1.31x | 0.00x @-24m | 12% |
| 2020 | SPX Mar-27 10% OTM | 10.7x @-2m | 0.00x | 0.00x @-24m | 75% |
| 2020 | SPX Mar-27 90/75 spread | 7.2x @-3m | 0.00x | 0.00x @-24m | 75% |
| 2020 | SPX Mar-27 seagull 90/75 -115c | 1.5x @-6m | 0.96x | 0.76x @-14m | 75% |
| 2020 | [B] QQQ Jun-27 p 11% OTM | 5.1x @-17m | 0.00x | 0.00x @-2m | 62% |
| 2022 | QQQ Dec-27 10% OTM | 3.0x @-23m | 0.00x | 0.00x @-22m | 71% |
| 2022 | QQQ Dec-27 90/65 spread | 2.7x @-23m | 0.00x | 0.00x @-22m | 71% |
| 2022 | QQQ Dec-27 seagull 90/65 -135c | 5.9x @-1m | 0.00x | -45.41x @-21m | 71% |
| 2022 | QQQ Jun-28 90/65 spread | 2.5x @-23m | 0.32x | 0.00x @-22m | 46% |
| 2022 | SPX Dec-27 10% OTM | 3.2x @-23m | 0.00x | 0.00x @-15m | 71% |
| 2022 | SPX Dec-27 90/70 spread | 3.0x @-23m | 0.00x | 0.00x @-15m | 71% |
| 2022 | SPX Dec-27 seagull 90/70 -125c | 2.4x @-22m | 0.74x | -5.91x @-21m | 71% |
| 2022 | SPX Jun-28 10% OTM | 2.6x @-23m | 0.00x | 0.00x @-21m | 46% |
| 2022 | SPX Mar-27 10% OTM | 5.4x @-23m | 0.00x | 0.00x @-10m | 100% |
| 2022 | SPX Mar-27 90/75 spread | 5.3x @-0m | 0.00x | 0.00x @-10m | 100% |
| 2022 | SPX Mar-27 seagull 90/75 -115c | 1.5x @-22m | 0.91x | 0.11x @-14m | 100% |
| 2022 | [B] QQQ Jun-27 p 11% OTM | 4.1x @-23m | 0.00x | 0.00x @-21m | 96% |

## 3. Entry-offset heatmap (median multiple, crash episodes pooled, v4 exit rule; columns = months before peak)

| structure | -0m | -3m | -6m | -9m | -12m | -15m | -18m | -21m | -24m |
|---|---|---|---|---|---|---|---|---|---|
| QQQ Dec-27 10% OTM | 2.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| QQQ Dec-27 90/65 spread | 2.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| QQQ Dec-27 seagull 90/65 -135c | 2.93 | 1.77 | 0.53 | 0.00 | 0.00 | 0.00 | -0.00 | 0.00 | -0.35 |
| QQQ Jun-28 90/65 spread | 1.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| SPX Dec-27 10% OTM | 2.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| SPX Dec-27 90/70 spread | 2.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| SPX Dec-27 seagull 90/70 -125c | 1.75 | 1.96 | 1.10 | 0.83 | 1.09 | 1.07 | 0.82 | 0.81 | 1.55 |
| SPX Jun-28 10% OTM | 2.19 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| SPX Mar-27 10% OTM | 0.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| SPX Mar-27 90/75 spread | 1.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| SPX Mar-27 seagull 90/75 -115c | 1.11 | 1.07 | 1.02 | 0.96 | 1.00 | 0.99 | 0.96 | 0.97 | 0.95 |
| [B] QQQ Jun-27 p 11% OTM | 1.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

## 4. Bleed table

Per non-event window: mean multiple of a structure bought at every month-end, and the premium burned per year (% of notional) by one unit held continuously and rolled at expiry = median cost ÷ tenor × (1 − mean multiple). Seagulls are in §1b.

| window | structure | entries | mean_mult | burn_pct_notional_per_yr |
|---|---|---|---|---|
| 1995-99 | SPX Dec-27 10% OTM | 60 | 0.06 | 1.91 |
| 1995-99 | SPX Dec-27 90/70 spread | 60 | 0.13 | 0.87 |
| 1995-99 | SPX Jun-28 10% OTM | 60 | 0.10 | 1.47 |
| 1995-99 | SPX Mar-27 10% OTM | 60 | 0.00 | 3.29 |
| 1995-99 | SPX Mar-27 90/75 spread | 60 | 0.00 | 1.92 |
| 2013 | QQQ Dec-27 10% OTM | 12 | 0.00 | 4.63 |
| 2013 | QQQ Dec-27 90/65 spread | 12 | 0.00 | 2.78 |
| 2013 | QQQ Jun-28 90/65 spread | 12 | 0.00 | 2.18 |
| 2013 | SPX Dec-27 10% OTM | 12 | 0.00 | 3.37 |
| 2013 | SPX Dec-27 90/70 spread | 12 | 0.00 | 1.92 |
| 2013 | SPX Jun-28 10% OTM | 12 | 0.00 | 3.02 |
| 2013 | SPX Mar-27 10% OTM | 12 | 0.00 | 3.84 |
| 2013 | SPX Mar-27 90/75 spread | 12 | 0.00 | 2.51 |
| 2013 | [B] QQQ Jun-27 p 11% OTM | 12 | 0.00 | 5.01 |
| 2017 | QQQ Dec-27 10% OTM | 12 | 0.00 | 3.39 |
| 2017 | QQQ Dec-27 90/65 spread | 12 | 0.00 | 2.20 |
| 2017 | QQQ Jun-28 90/65 spread | 12 | 0.00 | 1.82 |
| 2017 | SPX Dec-27 10% OTM | 12 | 0.00 | 2.46 |
| 2017 | SPX Dec-27 90/70 spread | 12 | 0.00 | 1.54 |
| 2017 | SPX Jun-28 10% OTM | 12 | 0.00 | 2.32 |
| 2017 | SPX Mar-27 10% OTM | 12 | 0.00 | 2.42 |
| 2017 | SPX Mar-27 90/75 spread | 12 | 0.00 | 1.72 |
| 2017 | [B] QQQ Jun-27 p 11% OTM | 12 | 0.00 | 3.42 |
| 2023-24 | SPX Mar-27 10% OTM | 7 | 0.00 | 5.51 |
| 2023-24 | SPX Mar-27 90/75 spread | 7 | 0.00 | 3.37 |

Unconditional baseline (every month-end 1990-01 → last date the structure can expire inside the data):

| structure | entries | mean_mult | P0 | ge3 | cost | burn_pct_notional_per_yr |
|---|---|---|---|---|---|---|
| QQQ Dec-27 10% OTM | 275 | 0.46 | 0.77 | 0.03 | 6.52 | 2.62 |
| QQQ Dec-27 90/65 spread | 275 | 0.54 | 0.77 | 0.04 | 3.62 | 1.25 |
| QQQ Jun-28 90/65 spread | 269 | 0.61 | 0.73 | 0.05 | 3.72 | 0.79 |
| SPX Dec-27 10% OTM | 394 | 0.49 | 0.83 | 0.06 | 3.94 | 1.52 |
| SPX Dec-27 90/70 spread | 394 | 0.60 | 0.82 | 0.11 | 2.09 | 0.63 |
| SPX Jun-28 10% OTM | 388 | 0.54 | 0.81 | 0.07 | 4.72 | 1.20 |
| SPX Mar-27 10% OTM | 403 | 0.41 | 0.88 | 0.06 | 2.21 | 2.25 |
| SPX Mar-27 90/75 spread | 403 | 0.46 | 0.88 | 0.07 | 1.39 | 1.29 |
| [B] QQQ Jun-27 p 11% OTM | 281 | 0.47 | 0.80 | 0.04 | 4.88 | 3.11 |

Sizing overlay: with a 1.25%/yr premium budget, the median-cost SPX Dec-27 10% OTM put (cost ≈ 3.7% of notional) buys ≈ 34% of portfolio notional per year of coverage; cumulative bleed over a 5-year non-event stretch (1995–99) = ≈ 6.2% of portfolio; budget-adjusted payoff in a crash episode = multiple × 1.25% of portfolio per year held (e.g. a 6x = +7.5%).

## 5. Exit-rule comparison (crash entries within 12 months of the peak; last column = non-event windows)

`peak_-22` is a v6 addition: exit at −22% from the running peak since entry rather than from the entry spot. It is the rule the synthetic model implicitly assumes (crashes start from the entry level).

| rule | EV | hit | ge3 | P0 | EV_nonevent |
|---|---|---|---|---|---|
| IPS | 1.49 | 0.59 | 0.08 | 0.13 | 0.38 |
| hold | 1.04 | 0.22 | 0.10 | 0.66 | 0.28 |
| peak_-22 | 1.69 | 0.43 | 0.11 | 0.45 | 0.26 |
| tiered | 1.51 | 0.43 | 0.12 | 0.42 | 0.28 |
| v4_-22 | 1.31 | 0.30 | 0.13 | 0.60 | 0.25 |

## 6. Entry-filter test (tranche rule) on the unconditional baseline

Rule: (ERP ≤ 0 or CAPE > 32) AND VIX < 18. **HY OAS leg not applied (series unavailable here).** ERP = trailing E/P − 10y (not forward). Sensitivity ±25% on each threshold.

| filter | entries | EV | P0 | ge3 | EV_unfiltered | P0_unfiltered |
|---|---|---|---|---|---|---|
| base (ERP<=0 | CAPE>32) & VIX<18 | 566 | 0.63 | 0.65 | 0.05 | 0.71 | 0.65 |
| ERP -25% (<=-0.5pp) | 486 | 0.68 | 0.63 | 0.05 | 0.71 | 0.65 |
| ERP +25% (<=+0.5pp) | 648 | 0.60 | 0.66 | 0.04 | 0.71 | 0.65 |
| CAPE 24 | 1731 | 0.53 | 0.71 | 0.05 | 0.71 | 0.65 |
| CAPE 40 | 482 | 0.49 | 0.71 | 0.04 | 0.71 | 0.65 |
| VIX 13.5 | 229 | 0.38 | 0.71 | 0.03 | 0.71 | 0.65 |
| VIX 22.5 | 1040 | 0.94 | 0.59 | 0.09 | 0.71 | 0.65 |

## 7. Diagnostics

Surface ATM vol at each trough by tenor vs v4's crash_iv (34 SPX / 42 NDX); put slope is the default (no realized skew is observable here):

| episode | und | vix_at_trough | iv_3m | iv_1y | v4_crash_iv | term | put_slope | iv_10otm_1y |
|---|---|---|---|---|---|---|---|---|
| 1987 | spx | 53.00 | 45.50 | 33.10 | 34 | default-MR | 0.35 | 42.90 |
| 1990 | spx | 34.00 | 31.10 | 26.10 | 34 | default-MR | 0.35 | 35.70 |
| 1998 | spx | 44.30 | 38.90 | 30.00 | 34 | default-MR | 0.35 | 38.20 |
| 2000 | spx | 42.10 | 38.50 | 32.10 | 34 | default-MR | 0.35 | 39.30 |
| 2000 | ndx | 54.80 | 50.00 | 41.80 | 42 | default-MR | 0.35 | 49.40 |
| 2007 | spx | 49.70 | 45.30 | 36.50 | 34 | vix-futures | 0.35 | 42.10 |
| 2007 | ndx | 64.60 | 60.20 | 50.40 | 42 | vix-futures | 0.35 | 57.00 |
| 2011 | spx | 45.50 | 44.90 | 43.20 | 34 | vix-futures | 0.35 | 47.90 |
| 2011 | ndx | 59.10 | 58.30 | 56.10 | 42 | vix-futures | 0.35 | 61.40 |
| 2015 | spx | 28.10 | 24.80 | 19.70 | 34 | vix-futures | 0.35 | 23.40 |
| 2015 | ndx | 36.60 | 32.60 | 26.00 | 42 | vix-futures | 0.35 | 30.30 |
| 2018 | spx | 36.10 | 31.10 | 23.00 | 34 | default-MR | 0.35 | 27.20 |
| 2018 | ndx | 46.90 | 40.40 | 29.90 | 42 | default-MR | 0.35 | 34.60 |
| 2020 | spx | 61.60 | 52.20 | 36.50 | 34 | vix-futures | 0.35 | 39.90 |
| 2020 | ndx | 80.10 | 67.90 | 47.40 | 42 | vix-futures | 0.35 | 51.30 |
| 2022 | spx | 33.60 | 32.50 | 30.00 | 34 | vix-futures | 0.35 | 34.50 |
| 2022 | ndx | 43.60 | 42.60 | 40.00 | 42 | vix-futures | 0.35 | 44.90 |

How often the −22% exit fired, and fired before the trough (v4 rule, all entries):

| episode | exit22_fired | before_trough |
|---|---|---|
| 1987 | 0.23 | 0.23 |
| 1990 | 0.00 | 0.00 |
| 1998 | 0.00 | 0.00 |
| 2000 | 0.11 | 0.11 |
| 2007 | 0.17 | 0.17 |
| 2011 | 0.00 | 0.00 |
| 2015 | 0.00 | 0.00 |
| 2018 | 0.02 | 0.00 |
| 2020 | 0.26 | 0.26 |
| 2022 | 0.23 | 0.22 |

Sensitivity of the 1-year ATM mark at the trough to the term rule (MR model vs the spec's literal VIX×0.95):

| episode | iv_1y_MR | iv_1y_spec095 |
|---|---|---|
| 2007 | 36.50 | 47.20 |
| 2020 | 36.50 | 58.60 |

Surface validation on 300 random dates: parity violations 0, calendar 0, butterfly 0. Term tags: {'default-MR': 174, 'vix-futures': 126}.

## 8. Delta vs v5 / v4

v5 is not present in this environment; the comparison is against the v4 synthetic model re-run on the reconciled §0 timing (exit rule on, 6,000 paths). Structures in the top 8 with a gap above 30%:

**QQQ Jun-28 90/65 spread**: historical-weighted 1.08x vs v4 synthetic 1.58x (-32%); 7 episodes, 78 entries. Historical conditionals Mu 0.1 / Rp 4.0 / AB 1.5 / SW 0.2 / Es 0.1 / Fr 0.1. In 14% of these entries the option expired before the episode trough, and in 69% the −22%-from-entry trigger never fired at all (the index rallied after entry, so the eventual drawdown from the peak was not a 22% drawdown from the entry spot). The synthetic model starts every crash from the entry level and never lets a position expire before the crash, which is where the gap comes from; the peak-anchored exit rule in §5 recovers part of it. QQQ conditionals rest on NDX data that begin 1999-12, so the 2000 episode contributes only entries at 0–3 months before the peak.
**SPX Mar-27 90/75 spread**: historical-weighted 0.74x vs v4 synthetic 1.22x (-39%); 10 episodes, 123 entries. Historical conditionals Mu 0.1 / Rp 0.0 / AB 0.3 / SW 4.0 / Es 0.0 / Fr 0.0. In 80% of these entries the option expired before the episode trough, and in 90% the −22%-from-entry trigger never fired at all (the index rallied after entry, so the eventual drawdown from the peak was not a 22% drawdown from the entry spot). The synthetic model starts every crash from the entry level and never lets a position expire before the crash, which is where the gap comes from; the peak-anchored exit rule in §5 recovers part of it. 
**QQQ Dec-27 90/65 spread**: historical-weighted 0.68x vs v4 synthetic 1.44x (-53%); 7 episodes, 78 entries. Historical conditionals Mu 0.1 / Rp 1.8 / AB 1.5 / SW 0.2 / Es 0.1 / Fr 0.1. In 37% of these entries the option expired before the episode trough, and in 78% the −22%-from-entry trigger never fired at all (the index rallied after entry, so the eventual drawdown from the peak was not a 22% drawdown from the entry spot). The synthetic model starts every crash from the entry level and never lets a position expire before the crash, which is where the gap comes from; the peak-anchored exit rule in §5 recovers part of it. QQQ conditionals rest on NDX data that begin 1999-12, so the 2000 episode contributes only entries at 0–3 months before the peak.
**QQQ Dec-27 10% OTM**: historical-weighted 0.51x vs v4 synthetic 1.65x (-69%); 7 episodes, 78 entries. Historical conditionals Mu 0.1 / Rp 1.2 / AB 1.2 / SW 0.3 / Es 0.1 / Fr 0.1. In 37% of these entries the option expired before the episode trough, and in 78% the −22%-from-entry trigger never fired at all (the index rallied after entry, so the eventual drawdown from the peak was not a 22% drawdown from the entry spot). The synthetic model starts every crash from the entry level and never lets a position expire before the crash, which is where the gap comes from; the peak-anchored exit rule in §5 recovers part of it. QQQ conditionals rest on NDX data that begin 1999-12, so the 2000 episode contributes only entries at 0–3 months before the peak.

## 9. Red-team checklist status

- Survivorship: non-event rows and the unconditional baseline are in §4 (headline, not appendix).
- Regime shift: §1 reports with and without pre-2000 episodes.
- Liquidity: 7% haircut applied on entry and exit; far-OTM open-interest caps NOT modelled (no OI data).
- Filter overfitting: ±25% sensitivity in §6; HY leg untested.
- Small N: stated in the header; ranges in §2.
- Data integrity: SPX daily is futures-derived (crash-day moves can be exaggerated when the basis dislocates; Oct-1987 overridden with published returns); NDX anchors are from memory and must be verified.
