# BDCR-27 Crash-Timing Engine — first run, 2026-09-28

Response to the red-team memo. The 32-indicator composite is retained as the *structural* layer; everything below is new. Tags: T1 direct, T2 near-direct, T3 leading, T4 structural, T5 narrative (memo §25). Dollar figures: V verified in the record, E estimate, P placeholder.

## 0. Dashboard (memo §28)

| Metric | Value |
|---|---:|
| Systemic vulnerability (structural, de-duplicated) | 77.0 |
| BDCR-26 additive composite (for reference) | 71.7 |
| Transmission stress | 49.5 |
| Policy capacity remaining | 28.6 |
| Reflexivity | 54.4 |
| Liquidity stress | 64.3 |
| Credit deterioration | 58.3 |
| Market internals | 56.0 |
| Catalyst proximity | 64.8 |

**Crash hazard (systemic, ≥25% with financial transmission), posterior = prior blended with engine at λ=0.61, × policy-suppression modifier:**

| Window | Probability |
|---|---:|
| next 3m | 4.3% |
| 3-6m | 5.9% |
| 6-12m | 16.5% |
| 12-18m | 17.4% |
| 18-24m | 6.8% |
| 24-36m | 9.2% |
| 36-month cumulative | 60% |

- **Current modal month: Oct 2027**  (prior: Oct 2027; engine alone: Nov 2026)
- **80% timing interval: Feb 2027 – Feb 2029**
- **Confidence: LOW** (cross-market confirmation 1 of 5 domains fully confirmed, 2.0 weighted; independent clocks converging on H2-2027/H1-2028: 4 of 4)
- First-crack candidate node: **Oracle** (distance-to-default proxy 0.62); most central node: **Nvidia**; highest centrality × fragility: **OpenAI**
- Primary transmission: engine A (Sovereign / bond-market), furthest along the first-crack chain (stage 4: *funding contraction (gates, failed syndication)*)
- Key clock: the Treasury rollover (~$11.8T over the next 12 months repricing from 3.41% toward 5.1%) and the Q1–Q2 2027 AI funding need (Oracle FY27 + OpenAI round); see §3.

### Three-date output (memo §27)

| Clock | Modal month | 80% interval | 36-month cumulative |
|---|---|---|---:|
| A — First crack (Tier-1 credit/liquidity event) | **Oct–Nov 2026** (Oct 1 gates / Car-Mart; Oct 8 30Y; Micron guide) | Oct 2026 – Mar 2027 | n/a (event, not index) |
| Correction (≥10%) | **Nov 2026** | Nov 2026 – Feb 2028 | 91% |
| B — Bear market (≥20%) | **Oct 2027** | Jan 2027 – Jan 2029 | 66% |
| C — Systemic crash (≥25% + transmission) | **Oct 2027** | Feb 2027 – Feb 2029 | 60% |

Moves earlier if: a Tier-1 event in engine A (a 30Y auction tail ≥4bp with cover <2.2 on Oct 8; a fails/repo spike at quarter-end), or a second Tier-1 event in engine B (an AI-chain default, an SPV impairment, a capex guide cut), or the confirmation count reaching 3 of 5 for two consecutive observations. Moves later if: the 30Y closes <5.30% for five sessions; the Nov 4 QRA cuts long-coupon sizes and the long end accepts it; Oct 1 gate requests fall; the AI funding-gap coverage ratio rises above 1.2 on new equity.

## 1. Causal-factor model (memo #2)

Nine latent factors; within-factor aggregation is 0.6·max + 0.4·mean, so several symptoms of one shock count roughly once. De-duplicated systemic vulnerability **77.0** vs the additive composite 71.7.

| Factor | Weight | Score /3 | Members (score) |
|---|---:|---:|---|
| Sovereign funding | 18 | 2.65 | Net interest / federal revenue (3), Deficit % of GDP (2), Debt held by public % GDP (2), r-minus-g on federal debt (1), 10Y term premium (2), Auction stress composite (2), Foreign official demand (2), 30Y yield stress level (3) |
| Monetary constraint | 12 | 1.90 | Core PCE y/y (2), Inflation expectations (survey vs market) (2), Fed independence stress (2), Monetization & real-rate stance (Stage-5 GATE) (1) |
| Equity valuation/speculation | 12 | 3.00 | Shiller CAPE (3), Equity risk premium (3), Top-10 S&P concentration (3), Retail froth (margin debt + 0DTE) (3) |
| AI capital cycle | 14 | 2.80 | AI capex-to-revenue gap (2), Circular / vendor-financed revenue share (3), Net investment / GDP (capital-cycle position) (3), Forensic first-credit-event tripwires (2) |
| Private/corporate credit | 10 | 2.00 | Credit complacency/stress (two-sided) (2), Debt/SPV-financed share of AI capex (2) |
| Household leverage | 12 | 1.80 | Card + auto 90+ delinquency transitions (2), Utilization / maxed-out / min-pay share (2), Subprime auto 60+ (Fitch ABS index) (2), Student loan 90+ share (2), Household debt service ratio (0), Subprime lender defaults / funding stress (1) |
| External/global funding | 10 | 2.00 | External conflict index (2), Reserve erosion & gold signal (2), China / global contagion index (2) |
| Political/institutional | 6 | 2.00 | Internal disorder index (2) |
| Liquidity/plumbing | 6 | 1.93 | engine inputs (MOVE, stock-bond corr, plumbing) — no BDCR-26 indicator exists; gap accepted |

## 2. Four crash engines (memo #4, #8–#10, #19)

| Engine | Chain stage reached (T1/T2 evidence) | Reflexivity | Refi coverage | T1 / T2 items | Clock |
|---|---|---:|---:|---|---|
| A — Sovereign / bond-market | 4: funding contraction (gates, failed syndication) — 5Y auction tail 3.1bp at 5.03% (T1); 30Y 5.56 through the buyback (T1); MOVE 105 (T2); buyback under-filled (T1); no failed auction, no fails spike (T1 absent) | 0.82 (loop gain 0.03 pp/pp per year (damped, cumulative); rescue half-life 6 -> 2 sessions) | 0.73 | 3 / 3 | Nov 4 QRA (coupon sizes) -> Q1-27 refunding + $9.7T rollover at 5%+ -> post-election coupon step-up and the Oct-8 30Y auction as the near test |
| B — AI capital cycle | 2: lender concern (CDS, marks) — Oracle force majeure on Jupiter (T1: contractual); Jupiter loans 89-91 + CDS record (T2); CoreWeave-tenant paper 9.25% vs 8.25% (T2); no default, no capex cut, no impairment (T1 absent) | 0.55 (capex -> revenue coverage 46% (gap $490B); prepayment financing in revenue (ASC 606) = A->B->A loop forming; write-offs 2028-29) | 0.90 | 1 / 3 | Micron/DRAM contract rollover Q4-26 -> OpenAI 2027 round + Oracle FY27 debt need (Q1-Q2 27) -> OpenAI cash-out / write-off window (2028) |
| C — Private credit | 3: credit-spread widening — Fitch PC default 6.3% record (T2); all perpetual BDCs gated 5% (T2); OBDC mark at 5c (T2); no insurer/pension writedown, no BDC bond >600, no covenant breach (T1 absent); Oct 1 windows pending | 0.50 (gates -> NAV doubt -> redemptions -> gates: loop live but capped by the 5% structure; discount to NAV ~25% = the market's own mark) | 0.85 | 0 / 4 | Oct 1 Q3 windows -> Jan 1 Q4 windows (second gate wave) -> 2027 BDC unsecured maturities (placeholder) |
| D — Consumer / recession | 1: missed payment / covenant breach / force majeure — hires 3.2% and saving 3.0% at trigger (T3); subprime auto 6.13% re-accelerating (T2); prime 0.49% contained (T2); claims 197K, mortgage DQ stable (T2 benign); Car-Mart alive to Oct 1 (T1 pending) | 0.30 (delinquency -> tighter credit -> spending -> jobs: not self-reinforcing while claims <230K) | 1.10 | 0 / 2 | second hike Oct 27 + $105 oil + 7% mortgages transmit on a 6-9 month lag -> Q2-Q3 2027 |

Reading: engine A (sovereign) is furthest along the chain and is the only one with three Tier-1 items; engine B has the single most important Tier-1 event (force majeure) but no default; engine C is structurally gated, which slows its loop; engine D is a lagging engine that the second hike arms for mid-2027. The AI engine is **not** a prerequisite: the hazard curve is a union of the four.

## 3. Liability maturity clock (memo #3, #22, #24) — $B per quarter

| Cohort | 2026Q4 | 2027Q1 | 2027Q2 | 2027Q3 | 2027Q4 | 2028Q1 | 2028Q2 | 2028Q3 | 2028Q4 | Tag | Source |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Hyperscaler bond issuance need | 70 | 100 | 105 | 105 | 110 | 110 | 110 | 110 | 110 | E | GS: ~$250B 2026 / ~$400-420B 2027 hyperscaler bonds (Sep-16/22 notes); 2028 held flat |
| Oracle external funding (capex - OCF) | 16 | 16 | 16 | 17 | 17 | 17 | 17 | 17 | 17 | E | FY27 capex $90-95B debt/lease-only, FCF guide -$42B (Sep-10 note); ATM exhausted; $3.3B guarantee matured Sep-26 |
| OpenAI funding need | 10 | 15 | 15 | 20 | 20 | 30 | 30 | 35 | 35 | E | deck: FCF -$278B 2026-30, cash out by 2028, seeking >$1.2T; SoftBank $10B lands Oct 1 (V); profile back-loaded |
| Neocloud / GPU-collateral debt (CRWV, NBIS, xAI SPV) | 4.0 | 5.0 | 6.0 | 8.0 | 8.0 | 10 | 10 | 10 | 10 | E | CRWV $4.2B convert (V), DDTL amortization schedules, xAI $12.5B SPV debt (V); maturities NF -> profile assumed |
| Project-level DC debt (Jupiter, Hyperion, Meta ladder) | 5.0 | 8.0 | 10 | 10 | 12 | 12 | 12 | 12 | 12 | E | Jupiter $18B (V, in distress), Digital Drive 9.25% (V), CleanSpark 8.25% (V); construction-draw profile assumed |
| Private-credit BDC redemptions (gated 5%/qtr) | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | E | all perpetual BDCs capped 5%/qtr (V); ~$500B non-traded BDC/interval AUM x 5% (E) |
| BDC / private-credit fund unsecured maturities | 5.0 | 8.0 | 10 | 8.0 | 10 | 12 | 12 | 12 | 12 | P | PLACEHOLDER: fill from BDC 10-Ks; OBDC/BCRED/ARCC ladders |
| Leveraged loans maturing | 25 | 35 | 40 | 45 | 50 | 70 | 75 | 80 | 80 | E | US LL maturity wall ~$150B 2027 / ~$300B 2028 (E, general market data; fill from PitchBook/LCD) |
| CRE / CMBS maturities | 220 | 225 | 225 | 225 | 225 | 210 | 210 | 210 | 210 | E | MBA ~$900B/yr 2026-27 (E); office share the stressed slice |
| Subprime auto / BHPH facilities | 1.5 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | V/E | Car-Mart $300M (V, waivers to Oct 1); CACC; Tricolor/First Brands aftermath; ABS BB spreads |
| Treasury coupon + bill rollover (repricing) | 2,400 | 2,450 | 2,450 | 2,500 | 2,500 | 2,550 | 2,550 | 2,600 | 2,600 | E | ~33% of ~$29.5T reprices within 12m (V) + $2.1T deficit (V) -> ~$11.8T/yr, spread evenly |
| **Private/AI/credit total (ex-Treasury, ex-CRE)** | **162** | **213** | **228** | **239** | **253** | **287** | **292** | **302** | **302** | | |

The wall is back-loaded: the private/AI/credit funding need rises from ~$162B in 2026Q4 to ~$302B a quarter by 2028 while the cheapest source (hyperscaler IG at ~115bp over) is the one whose spread is widening deal by deal. PLACEHOLDER rows must be filled from 10-Ks before the clock is used for dates finer than a quarter.

## 4. AI funding-gap test (memo #3) — next 12 months, $B

| Case | Required external funding | Equity available | Debt capacity | Gap | Coverage |
|---|---:|---:|---:|---:|---:|
| base | 710 | 120 | 520 | 70 | 0.90 |
| rates +100bp | 710 | 120 | 442 | 148 | 0.79 |
| AI revenue -30% | 780 | 120 | 520 | 140 | 0.82 |
| spreads +150bp | 710 | 120 | 403 | 187 | 0.74 |
| utilization -20% | 724 | 120 | 520 | 84 | 0.88 |
| all four | 795 | 120 | 325 | 350 | 0.56 |

Base case: the complex can fund itself only because the IG market is assumed to absorb ~$520B; coverage falls below 1.0 under any single stress and to ~0.6 under all four. The measurable clock is therefore the IG/private spread on AI paper, not the capex number.

## 5. Sovereign engine (memo #11–#15)

- Repricing in the next 12 months: **$11.8T** (33% of marketable debt + deficit) at a marginal rate ~5.1% vs average coupon 3.41% → extra interest **$200B/yr** from one year of rollover; net interest / revenue 19.4%; marginal r−g **+0.9pp** (the average-coupon r−g is still negative: the memo's point exactly).
- Treasury-demand clearing (FY27, $T): required absorption 2.10 − identified demand 1.35 = residual **0.75T** for price-sensitive domestic private buyers → required yield premium ≈ **+19bp** at 25bp/$T (E). All demand inputs are estimates; the structure is the deliverable.
- Reflexivity loop (yield → interest → deficit → issuance → yield): gain **0.03 pp per pp per year** — damped within a year, but it compounds and is the loop the 2028–29 interest step-up feeds.
- Buyers'-strike detector: score 0.55, verdict **emerging** (2 of 5 scored auctions with ≥2 stress flags; the 7Y result is missing). One weak auction is noise; the 5Y is the second consecutive flagged sale.
- Failed-rescue counter: half-lives [4, 6, 2] sessions, fill ratios [1.0, 0.87, 0.68]; **decaying = True**. Each rescue is buying less time and Treasury is filling less of its own cap.
- Policy-exhaustion clock: **29 / 100 capacity remaining** (tier-weighted): Fed rate room 55; Fed balance sheet/QE 35; Treasury buybacks 25; Fiscal impulse 15; Foreign demand 25; Political capacity 30.

## 6. Cross-market confirmation (memo #16)

| Domain | Confirmed | Evidence |
|---|:---:|---|
| Treasury stress | YES | 5Y tail; 30Y 5.56 through buyback; MOVE 105; two consecutive weeks |
| Credit stress | PARTIAL | HY 268->280 (first widening since hike); ORCL CDS record; but HY <300 = still complacency band |
| Equity breadth | PARTIAL | no new records since Sep 22; R2K -4% 1M; NDX led down Sep 23/28; one observation |
| Funding/plumbing stress | no | no repo/SRF/fails signal; Sep 30 quarter-end test pending |
| Real-economy deterioration | no | claims 197K; mortgage DQ 3.53%; hires/saving AT trigger, not through it |

**1 of 5 fully confirmed** (2.0 weighted). The 3-of-5 rule is NOT met: the systemic-clock hazard is gated to 61% of its unconfirmed value. This is why the near-term systemic hazard stays low while the correction hazard is high.

## 7. Market internals (memo #7)

| Signal | Reading | Stress 0–1 | Tier |
|---|---|---:|:---:|
| Breadth: R2K vs SPX 1M | R2K -4% 1M vs SPX ~0 | 0.6 | T3 |
| Breadth: NYSE Composite / new records | flat on the week of Sep 16-22; NDX ATH Sep 22 not extended | 0.5 | T3 |
| Leadership: equal-weight vs cap-weight | RSP lagged 2-4 pts (Sep 22); NF since | 0.5 | T3 |
| Leadership: semis vs software / MU | MU +17% in 7 sessions into print; Burry short in size | 0.4 | T4 |
| Volatility: VIX / VVIX | 14.87 / 90.6 | 0.2 | T2 |
| Volatility: MOVE | 104.6 (from ~80; +30% wk) | 0.8 | T2 |
| Stock-bond correlation | positive every session Sep 23-28 | 0.7 | T2 |
| Liquidity: Treasury depth / repo / SRF | no stress print; SRF quarter-end test Sep 30 pending | 0.3 | T3 |
| Positioning: CTAs | sellers in every 1-wk scenario (GS); down-tape branch engaged Sep 23/28 | 0.7 | T3 |
| Positioning: margin debt | $1.45T record (Aug), +37% y/y | 0.7 | T2 |
| Positioning: buyback blackout / pension | blackout to mid-Oct; Sep 30 rebalance = sell equities | 0.6 | T3 |

Internals score **56 / 100**: bond volatility and positioning are stressed, equity volatility is not — the transition signal is half-formed.

## 8. Historical analogue engine (memo #18)

State vector ['capez', 'cape_lvl', 'ret12', 'dy10', 'rvol', 'erp_pp'] at t, t−3, t−6, t−12 (CAPE z-score vs 20-yr mean, 12-month return, 12-month change in the 10-year, realized 12-month vol, ERP) over the Shiller monthly record 1881–2023 (1651 months); distance = ½ point distance + ½ DTW over the trajectory; 20 nearest, de-clustered at 18 months. Current-state inputs are ESTIMATES (12m return +17%, 10Y +1.0pp, CAPE 40.9, ERP −0.6). VIX is not used (unavailable before 1990); pre-1982 episodes are therefore included.

| Match date | Distance | CAPE | Months to −10% | to −20% | to −25% |
|---|---:|---:|---:|---:|---:|
| 2000-02-01 | 1.25 | 42.2 | 10 | 13 | 19 |
| 1997-11-01 | 2.09 | 32.3 | 10 | >36 | >36 |
| 2018-09-01 | 2.45 | 32.6 | 3 | >36 | >36 |
| 1929-10-01 | 2.47 | 29.0 | 1 | 1 | 1 |
| 1966-04-01 | 2.73 | 23.1 | 4 | >36 | >36 |
| 1902-04-01 | 2.87 | 22.8 | 12 | 15 | 16 |
| 1964-09-01 | 2.96 | 22.9 | 23 | >36 | >36 |
| 1968-12-01 | 2.99 | 22.3 | 7 | 17 | 17 |
| 1962-03-01 | 3.01 | 21.4 | 2 | 3 | >36 |
| 2004-07-01 | 3.03 | 25.7 | >36 | >36 | >36 |
| 1899-08-01 | 3.04 | 21.7 | 13 | >36 | >36 |
| 2002-06-01 | 3.09 | 26.4 | 1 | >36 | >36 |
| 2006-02-01 | 3.13 | 26.2 | 23 | 31 | 32 |
| 2007-10-01 | 3.16 | 27.3 | 3 | 11 | 12 |
| 1995-08-01 | 3.33 | 23.3 | >36 | >36 | >36 |
| 2017-02-01 | 3.39 | 28.7 | 22 | >36 | >36 |
| 1892-10-01 | 3.4 | 19.0 | 7 | 9 | 9 |
| 1960-01-01 | 3.42 | 18.3 | 28 | 29 | >36 |
| 1937-08-01 | 3.53 | 19.8 | 1 | 2 | 2 |
| 1956-10-01 | 3.54 | 17.4 | 12 | >36 | >36 |

Empirical hazard from the matches (events / at-risk per bucket):

| Bucket | −10% | −20% | −25% |
|---|---|---|---|
| 0-6m | 7/20 = 35% | 3/20 = 15% | 2/20 = 10% |
| 6-12m | 6/13 = 46% | 2/17 = 12% | 2/18 = 11% |
| 12-18m | 1/7 = 14% | 3/15 = 20% | 2/16 = 12% |
| 18-24m | 3/6 = 50% | 0/12 = 0% | 1/14 = 7% |
| 24-36m | 1/3 = 33% | 2/12 = 17% | 1/13 = 8% |

Small-sample caveat: twenty matched months, many from the same few regimes. The analogue hazard enters the engine curve at 30% weight.

## 9. Network centrality (memo #20)

| Node | Centrality | Distance-to-default proxy | Centrality × fragility |
|---|---:|---:|---:|
| OpenAI | 0.66 | 0.55 (T2) | 0.36 |
| Oracle | 0.54 | 0.62 (T2) | 0.33 |
| Blue Owl | 0.58 | 0.45 (T2) | 0.26 |
| CoreWeave/neoclouds | 0.36 | 0.60 (T2) | 0.22 |
| Equities | 0.61 | 0.35 (T3) | 0.21 |
| Treasury | 0.58 | 0.35 (T1) | 0.20 |
| Nvidia | 1.00 | 0.18 (T2) | 0.18 |
| Hyperscalers | 0.90 | 0.20 (T2) | 0.18 |
| Private credit/BDCs | 0.37 | 0.45 (T2) | 0.16 |
| Memory/semis | 0.32 | 0.30 (T3) | 0.10 |
| Corporate debt/IG | 0.37 | 0.25 (T2) | 0.09 |
| Japan (JGB/yen) | 0.24 | 0.35 (T2) | 0.08 |
| Foreign reserve mgrs | 0.27 | 0.25 (T2) | 0.07 |
| Consumers | 0.21 | 0.30 (T3) | 0.06 |
| Banks | 0.32 | 0.12 (T2) | 0.04 |
| Fed | 0.16 | 0.10 (T3) | 0.02 |
| Housing | 0.08 | 0.20 (T3) | 0.02 |
| MMFs | 0.31 | 0.05 (T2) | 0.02 |

## 10. Hazard curves (memo #17) — monthly P(crash in t | none before t)

| Month | Correction prior | Correction post | Bear prior | Bear post | Systemic prior | Systemic engine | Systemic post | Suppression |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Oct 2026 | 26.5 | 8.6 | 3.0 | 1.6 | 3.1 | 2.1 | 1.4 | 0.55 |
| Nov 2026 | 36.0 | 10.4 | 3.0 | 1.8 | 3.3 | 2.5 | 1.5 | 0.55 |
| Dec 2026 | 10.4 | 6.2 | 2.4 | 2.1 | 1.7 | 2.3 | 1.5 | 0.75 |
| Jan 2027 | 11.6 | 6.2 | 2.5 | 2.1 | 1.7 | 2.3 | 1.5 | 0.75 |
| Feb 2027 | 13.2 | 12.6 | 2.8 | 3.4 | 1.7 | 2.5 | 2.3 | 1.00 |
| Mar 2027 | 15.2 | 13.9 | 3.1 | 3.6 | 2.0 | 2.6 | 2.5 | 1.00 |
| Apr 2027 | 6.4 | 11.0 | 3.4 | 3.7 | 2.2 | 2.7 | 2.7 | 1.00 |
| May 2027 | 6.9 | 11.2 | 3.8 | 3.8 | 2.5 | 2.6 | 2.8 | 1.00 |
| Jun 2027 | 7.4 | 11.5 | 4.2 | 3.9 | 2.7 | 2.6 | 2.8 | 1.00 |
| Jul 2027 | 8.0 | 11.7 | 5.4 | 4.4 | 4.8 | 2.5 | 3.7 | 1.00 |
| Aug 2027 | 8.7 | 12.1 | 6.1 | 4.6 | 5.4 | 2.5 | 3.9 | 1.00 |
| Sep 2027 | 9.5 | 12.6 | 6.8 | 4.9 | 6.1 | 2.4 | 4.2 | 1.00 |
| Oct 2027 | 2.2 | 7.5 | 6.9 | 5.2 | 6.9 | 2.4 | 4.5 | 1.00 |
| Nov 2027 | 2.2 | 7.3 | 7.1 | 5.2 | 7.0 | 2.3 | 4.5 | 1.00 |
| Dec 2027 | 2.3 | 7.1 | 7.2 | 5.2 | 7.1 | 2.2 | 4.5 | 1.00 |
| Jan 2028 | 2.3 | 6.7 | 7.2 | 5.1 | 7.1 | 2.1 | 4.4 | 1.00 |
| Feb 2028 | 2.4 | 6.3 | 7.3 | 5.0 | 7.1 | 1.9 | 4.3 | 1.00 |
| Mar 2028 | 2.5 | 5.8 | 7.3 | 4.9 | 7.0 | 1.7 | 4.2 | 1.00 |
| Apr 2028 | 2.5 | 7.4 | 7.3 | 4.0 | 6.9 | 1.3 | 3.9 | 1.00 |
| May 2028 | 2.6 | 3.9 | 7.3 | 2.8 | 6.7 | 1.1 | 2.7 | 0.80 |
| Jun 2028 | 2.6 | 3.5 | 7.8 | 2.8 | 6.5 | 1.0 | 2.5 | 0.80 |
| Jul 2028 | 2.7 | 3.3 | 2.9 | 1.2 | 2.8 | 0.8 | 1.3 | 0.80 |
| Aug 2028 | 2.8 | 3.0 | 2.9 | 1.1 | 2.9 | 0.7 | 1.3 | 0.80 |
| Sep 2028 | 2.9 | 2.9 | 3.0 | 1.1 | 3.0 | 0.6 | 1.2 | 0.80 |
| Oct 2028 | 3.0 | 1.7 | 3.1 | 1.3 | 3.1 | 0.4 | 1.1 | 0.80 |
| Nov 2028 | 3.1 | 1.6 | 3.2 | 1.3 | 3.2 | 0.3 | 1.1 | 0.80 |
| Dec 2028 | 3.1 | 2.8 | 3.3 | 1.8 | 3.3 | 0.3 | 1.6 | 1.00 |
| Jan 2029 | 3.3 | 2.8 | 3.4 | 1.8 | 3.4 | 0.3 | 1.6 | 1.00 |
| Feb 2029 | 3.4 | 2.8 | 3.6 | 1.9 | 3.5 | 0.2 | 1.7 | 1.00 |
| Mar 2029 | 3.5 | 2.8 | 3.7 | 1.9 | 3.7 | 0.2 | 1.7 | 1.00 |
| Apr 2029 | 3.6 | 2.9 | 3.8 | 2.0 | 3.8 | 0.2 | 1.8 | 1.00 |
| May 2029 | 3.7 | 2.9 | 4.0 | 2.0 | 4.0 | 0.2 | 1.8 | 1.00 |
| Jun 2029 | 3.9 | 3.0 | 4.2 | 2.1 | 4.1 | 0.2 | 1.9 | 1.00 |
| Jul 2029 | 4.0 | 3.1 | 4.3 | 2.2 | 4.3 | 0.2 | 2.0 | 1.00 |
| Aug 2029 | 4.2 | 3.2 | 4.5 | 2.3 | 4.5 | 0.2 | 2.1 | 1.00 |
| Sep 2029 | 4.4 | 3.4 | 4.8 | 2.4 | 4.7 | 0.2 | 2.2 | 1.00 |

## 11. What was adopted, changed, or rejected from the memo

- **Adopted in full:** causal factors (§1); four engines with a first-crack chain, reflexivity gain and coverage ratio (§2); the liability clock (§3, first fill); the hard cash-flow test (§4); marginal-rate sovereign engine, clearing model, buyers'-strike detector, failed-rescue counter, policy-exhaustion clock (§5); 3-of-5 confirmation (§6); internals as a timing layer (§7); analogue engine with trajectory matching (§8); network centrality (§9); a monthly hazard model with three separate clocks (§10); evidence tiers; election calendar demoted to a suppression modifier; forecast separated from trade timing; October 2027 demoted to a prior.
- **Changed:** the 32-indicator composite is *kept*, renamed the structural layer, and reported alongside the de-duplicated vulnerability score rather than replaced — the pre-registered thresholds and amendment log are the audit trail the new engine does not yet have. The hazard model is a Bayesian blend (prior × engine, λ set by confirmation and convergence) rather than a purely statistical survival fit: ten crash episodes cannot support a fitted survival model without a prior, and the memo itself says to treat the current forecast as one.
- **Rejected / deferred:** a fitted survival regression on episode data (N too small; the analogue engine's empirical hazard is used instead); Dynamic Time Warping over 24-month windows (implemented over four trajectory points — longer windows overfit the 1929/2000 shapes); a full maturity database (the environment cannot reach EDGAR/LCD/Bloomberg, so the clock ships with tagged placeholders).
- **What the first run says:** the engine curve and the prior agree on the centre of mass (H2-2027) but the engine puts more mass in Q1–Q2 2027 than the judgment did, because the sovereign engine is further along the chain than the AI engine and its clocks (QRA, rollover, Oct 8) come first. The posterior modal month is unchanged at October 2027 only because the confirmation gate (2 of 5) and the election modifier suppress the near-term systemic hazard; if confirmation reaches 3 of 5 before year-end, the modal month moves into the first half of 2027.