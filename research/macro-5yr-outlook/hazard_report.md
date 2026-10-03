# BDCR-27 Crash-Timing Engine — first run, 2026-09-28

Response to the red-team memo. The 32-indicator composite is retained as the *structural* layer; everything below is new. Tags: T1 direct, T2 near-direct, T3 leading, T4 structural, T5 narrative (memo §25). Dollar figures: V verified in the record, E estimate, P placeholder.

## 0. Dashboard (memo §28)

| Metric | Value |
|---|---:|
| Systemic vulnerability (structural, de-duplicated) | 76.2 |
| BDCR-26 additive composite (for reference) | 70.3 |
| Transmission stress | 61.8 |
| Policy capacity remaining | 28.6 |
| Reflexivity | 23.7 |
| Liquidity stress | 62.4 |
| Credit deterioration | 55.0 |
| Market internals | 61.1 |
| Catalyst proximity | 91.0 |

**Crash hazard (systemic, ≥25% with financial transmission), posterior = prior blended with engine at λ=0.69, × policy-suppression modifier:**

| Window | Probability |
|---|---:|
| next 3m | 2.9% |
| 3-6m | 4.0% |
| 6-12m | 14.9% |
| 12-18m | 13.5% |
| 18-24m | 7.6% |
| 24-36m | 8.1% |
| 36-month cumulative | 51% |

- **Current modal month: Sep 2027**  (prior: Oct 2027; engine alone: Apr 2027)
- **80% timing interval: Feb 2027 – Mar 2029**
- **Confidence: HIGH** (cross-market confirmation 2 of 5 domains fully confirmed, 3.0 weighted; independent clocks converging on H2-2027/H1-2028: 5 of 5)
- First-crack candidate node: **Oracle** (distance-to-default proxy 0.62); most central node: **Nvidia**; highest centrality × fragility: **OpenAI**
- Primary transmission: engine A (Sovereign / bond-market), furthest along its chain on Tier-1 evidence (stage 4: *funding contraction (gates, failed syndication)*)
- Confidence decomposition: specification stability 100% of 162 specs keep the modal month within ±2 months (modal distribution {'Sep 2027': 138, 'Jul 2027': 18, 'Oct 2027': 6}); cross-market confirmation 2/3 required; combined score 0.83 → **HIGH**
- Key clock: the Treasury rollover (~$11.8T over the next 12 months repricing from 3.41% toward 5.1%) and the Q1–Q2 2027 AI funding need (Oracle FY27 + OpenAI round); see §3.

### Three-date output (memo §27)

| Clock | Modal month | 80% interval | 36-month cumulative |
|---|---|---|---:|
| A — First crack (Tier-1 credit/liquidity event) | **Oct–Nov 2026** (Oct 1 gates / Car-Mart; Oct 8 30Y; Micron guide) | Oct 2026 – Mar 2027 | n/a (event, not index) |
| Correction (≥10%) | **Feb 2027** | Nov 2026 – Feb 2028 | 88% |
| B — Bear market (≥20%) | **Sep 2027** | Feb 2027 – Feb 2029 | 53% |
| C — Systemic crash (≥25% + transmission) | **Sep 2027** | Feb 2027 – Mar 2029 | 51% |

Moves earlier if: a Tier-1 event in engine A (a 30Y auction tail ≥4bp with cover <2.2 on Oct 8; a fails/repo spike at quarter-end), or a second Tier-1 event in engine B (an AI-chain default, an SPV impairment, a capex guide cut), or the confirmation count reaching 3 of 5 for two consecutive observations. Moves later if: the 30Y closes <5.30% for five sessions; the Nov 4 QRA cuts long-coupon sizes and the long end accepts it; Oct 1 gate requests fall; the AI funding-gap coverage ratio rises above 1.2 on new equity.

## 1. Causal-factor model (memo #2)

Nine latent factors; within-factor aggregation is 0.6·max + 0.4·mean, so several symptoms of one shock count roughly once. De-duplicated systemic vulnerability **76.2** vs the additive composite 70.3.

| Factor | Weight | Score /3 | Members (score) |
|---|---:|---:|---|
| Sovereign funding | 18 | 2.65 | Net interest / federal revenue (3), Deficit % of GDP (2), Debt held by public % GDP (2), r-minus-g on federal debt (1), 10Y term premium (2), Auction stress composite (2), Foreign official demand (2), 30Y yield stress level (3) |
| Monetary constraint | 12 | 1.90 | Core PCE y/y (2), Inflation expectations (survey vs market) (2), Fed independence stress (2), Monetization & real-rate stance (Stage-5 GATE) (1) |
| Equity valuation/speculation | 12 | 3.00 | Shiller CAPE (3), Equity risk premium (3), Top-10 S&P concentration (3), Retail froth (margin debt + 0DTE) (3) |
| AI capital cycle | 14 | 2.80 | AI capex-to-revenue gap (2), Circular / vendor-financed revenue share (3), Net investment / GDP (capital-cycle position) (3), Forensic first-credit-event tripwires (2) |
| Private/corporate credit | 10 | 1.80 | Credit complacency/stress (two-sided) (1), Debt/SPV-financed share of AI capex (2) |
| Household leverage | 12 | 1.80 | Card + auto 90+ delinquency transitions (2), Utilization / maxed-out / min-pay share (2), Subprime auto 60+ (Fitch ABS index) (2), Student loan 90+ share (2), Household debt service ratio (0), Subprime lender defaults / funding stress (1) |
| External/global funding | 10 | 2.00 | External conflict index (2), Reserve erosion & gold signal (2), China / global contagion index (2) |
| Political/institutional | 6 | 2.00 | Internal disorder index (2) |
| Liquidity/plumbing | 6 | 1.87 | engine inputs (MOVE, stock-bond corr, plumbing) — no BDCR-26 indicator exists; gap accepted |

## 2. Four crash engines (memo #4, #8–#10, #19)

| Engine | Chain stage reached (T1/T2 evidence) | Reflexivity | Refi coverage | T1 / T2 items | Clock |
|---|---|---:|---:|---|---|
| E — Market plumbing | 3: volatility regime shift — MOVE 80 -> 105 (T2); stock-bond correlation positive every session (T2); margin debt $1.45T record (T2); CTA down-tape branch engaged (T3); repo/SRF/fails QUIET (T2 benign); Treasury depth not retrieved; Sep 30 quarter-end SRF test pending. Absent: margin calls, forced liquidation. | 0.51 (collateral loop: prices -> collateral -> margin -> forced selling; strongest loop today because the buyback bid is in blackout and CTAs are sellers) | 1.00 | 0 / 3 | Sep 30 quarter-end funding test -> Oct 8 30Y auction -> Nov 4 QRA; thereafter whenever a 10% index move meets the collateral loop |
| A — Sovereign / bond-market | 4: funding contraction (gates, failed syndication) — 5Y and 7Y auctions weak (T1); 30Y five closes >=5.50, 5.632 high since 2002 (T1); Oct 1 buyback: $46.4B offered for a $6B cap, pre-op level regained in 2 sessions = fourth rescue with the shortest half-life (T1); 10Y +6bp on a +29K payroll (T2); MOVE 108 (T2); short end and plumbing CLEAN (T1 benign); no failed auction, no fails spike (T1 absent) | 0.82 (loop gain 0.03 pp/pp per year (damped, cumulative); rescue half-life 6 -> 2 sessions) | 0.73 | 3 / 3 | Nov 4 QRA (coupon sizes) -> Q1-27 refunding + $9.7T rollover at 5%+ -> post-election coupon step-up and the Oct-8 30Y auction as the near test |
| B — AI capital cycle | 2: lender concern (CDS, marks) — Oracle force majeure on Jupiter (T1: contractual); Jupiter loans 89-91, CDS record 227, long bonds >8% (T2); CoreWeave-tenant paper 9.25% vs 8.25% (T2); Micron FY27 capex RAISED >$40B = supply response funded (T3); SoftBank $10B funded Oct 1 with 9%+ junk, SB CDS >400 (T2); no default, no capex cut, no impairment, no DRAM rollover (T1 absent) | 0.55 (capex -> revenue coverage 46% (gap $490B); prepayment financing in revenue (ASC 606) = A->B->A loop forming; write-offs 2028-29) | 0.90 | 1 / 3 | Micron/DRAM contract rollover Q4-26 -> OpenAI 2027 round + Oracle FY27 debt need (Q1-Q2 27) -> OpenAI cash-out / write-off window (2028) |
| C — Private credit | 5: gates — PC sequence at 'gates' (stage 5 of 7): Oct 1 windows -- OTIC 39% requested, OCIC 16.8%, BCRED ~10%, ADS 14.7%, HLEND ~11.5%, ASIF 11.6%, all capped 5% again, requests EASING except AI/tech lending (T2); Fitch PC default 6.3% record (T2); OWL -46% YTD (T3); NOT reached: forced sales, insurer/pension writedown (T1 absent), BDC bond >600, covenant breach | 0.50 (gates -> NAV doubt -> redemptions -> gates: loop live but capped by the 5% structure; discount to NAV ~25% = the market's own mark) | 0.85 | 0 / 4 | Oct 1 Q3 windows -> Jan 1 Q4 windows (second gate wave) -> 2027 BDC unsecured maturities (placeholder) |
| D — Consumer / recession | 1: missed payment / covenant breach / force majeure — LABOR TURNED Oct 2: payrolls +29K, revisions -60K, July -10K, UR 4.2, real AHE ~-0.4% (T2); Conf Board 81.9, expectations 63.6 (T3); hires 3.3% (T3, above trigger); saving 4.1% on the REVISED series (T2; old-series trigger moot); subprime auto 6.13% (T2); prime 0.49% contained (T2); claims 197K / continuing 1.70M benign (T2); mortgage 7.28% (T2); Car-Mart alive to Oct 8 (T1 pending) | 0.35 (delinquency -> tighter credit -> spending -> jobs: not self-reinforcing while claims <230K, but the income side (payrolls, real wages) flipped this week) | 1.05 | 0 / 4 | payroll stall + 7.3% mortgages + $100 oil transmit on a 4-8 month lag -> Q1-Q2 2027 (pulled forward from Q2-Q3 on the Oct 2 print) |

Reading: engine A (sovereign) is furthest along its chain with Tier-1 evidence and is the only one with three Tier-1 items; engine B has the single most important Tier-1 event (force majeure) but no default; engine C has reached 'gates' on the private-credit sequence but not 'forced sales'; engine D is a lagging engine that the second hike arms for mid-2027; engine E (plumbing) shows a volatility-regime shift in rates only. The AI engine is **not** a prerequisite: the hazard curve is a union of the five.

### 2b. Dalio decision tree (BDCR 2.0 memo §5) — encoded conditions, current pass/fail

| # | Node | Condition (specified before looking) | Reading | Tier | Passes |
|---|---|---|---|:---:|:---:|
| 1 | Debt rising faster than income | federal debt growth vs nominal GDP growth (y/y) | debt +~7-8% vs NGDP +4.2% (E) | T4 | YES |
| 2 | Debt service becoming restrictive | net interest / revenue >= 18% OR marginal r - g > 0 | 19.4% (V); marginal r-g +0.9pp (V) | T2 | YES |
| 3 | Monetary policy unable to fully offset | Fed constrained by inflation: core PCE >= 3% with headline >3% while policy is restrictive; real EFFR > 0 | core 3.0% (revised, methodology), headline 3.4%, ISM prices 77.9; Oct hike ~17% after payrolls but no easing path with 6% consumer expectations (V) | T2 | YES |
| 4 | Credit contraction | HY OAS > 400 OR bank C&I standards tightening > +20 net OR private-credit gates AND defaults > 6% | HY 280 (no); gates + 6.3% defaults (yes, private only) | T2 | no |
| 5 | Spending deterioration | real retail sales < 0 y/y OR claims > 260K OR saving rate < 3.0% (old series; ~4.0% on the Sep-30 revised series) | real PCE +0.6% Aug, claims 197K, saving 4.1% (revised series); payrolls +29K and real wages negative are the leading edge but not the written condition | T2 | no |
| 6 | Deleveraging regime | household or corporate debt/GDP falling with defaults rising | no | T2 | no |

Tree stage **3 of 6**: the system is past 'monetary policy unable to offset' and stops at **Credit contraction** — the bank/HY channel has not contracted (HY 280) and spending has not deteriorated (claims 197K). That is the precise statement of 'amber, not red' in causal form, and it is the node the Sep 30 / Oct 2 / Oct 6 prints test.

### 2c. Reflexivity loops (BDCR 2.0 memo §13) — one-year gain of each loop

| Loop | Gain | Note |
|---|---:|---|
| Sovereign: yield -> interest -> deficit -> issuance -> yield | 0.03 | damped within a year; compounds into the 2028-29 interest step-up (V inputs) |
| Credit: losses -> lending -> activity -> defaults | 0.17 | live in private credit only; the bank channel has not engaged (HY <300) (E) |
| Collateral: prices -> collateral -> margin -> forced selling -> prices | 0.51 | margin debt record, CTA down-tape branch engaged, buyback bid in blackout: the strongest loop today (E) |

Gain scale: >1 explosive, 0.3–1 self-reinforcing, <0.3 damped. The collateral loop is the only one in the self-reinforcing band today; the sovereign loop is damped on a one-year horizon but compounds.

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
| rates +200bp | 710 | 120 | 364 | 226 | 0.68 |
| AI revenue -30% | 780 | 120 | 520 | 140 | 0.82 |
| spreads +150bp | 710 | 120 | 403 | 187 | 0.74 |
| utilization -20% | 724 | 120 | 520 | 84 | 0.88 |
| asset values -25% (GPU/DC collateral) | 710 | 120 | 474 | 116 | 0.84 |
| financing window half-closed (-30%) | 710 | 120 | 364 | 226 | 0.68 |
| all: +100bp, rev -30%, spreads +150, util -20% | 795 | 120 | 325 | 350 | 0.56 |
| severe: +200bp, rev -30%, assets -25%, financing -30% | 780 | 120 | 233 | 428 | 0.45 |

Base case: the complex can fund itself only because the IG market is assumed to absorb ~$520B; coverage falls below 1.0 under any single stress and to ~0.6 under all four. The measurable clock is therefore the IG/private spread on AI paper, not the capex number.

## 5. Sovereign engine (memo #11–#15)

- Repricing in the next 12 months: **$11.8T** (33% of marketable debt + deficit) at a marginal rate ~5.1% vs average coupon 3.41% → extra interest **$200B/yr** from one year of rollover; net interest / revenue 19.4%; marginal r−g **+0.9pp** (the average-coupon r−g is still negative: the memo's point exactly).
- Treasury-demand clearing (FY27, $T): required absorption 2.10 − identified demand 1.35 = residual **0.75T** for price-sensitive domestic private buyers → required yield premium ≈ **+19bp** at 25bp/$T (E). All demand inputs are estimates; the structure is the deliverable.
- Reflexivity loop (yield → interest → deficit → issuance → yield): gain **0.03 pp per pp per year** — damped within a year, but it compounds and is the loop the 2028–29 interest step-up feeds.
- Buyers'-strike detector: score 0.77, verdict **persistent** (3 of 7 scored auctions with ≥2 stress flags; the 7Y result is missing). One weak auction is noise; the 5Y is the second consecutive flagged sale.
- Failed-rescue counter: half-lives [4, 6, 2, 2] sessions, fill ratios [1.0, 0.87, 0.68, 1.0]; **decaying = False**. Each rescue is buying less time and Treasury is filling less of its own cap.
- Policy-exhaustion clock: **29 / 100 capacity remaining** (tier-weighted): Fed rate room 55; Fed balance sheet/QE 35; Treasury buybacks 25; Fiscal impulse 15; Foreign demand 25; Political capacity 30.

## 6. Cross-market confirmation (memo #16)

| Domain | Confirmed | Evidence |
|---|:---:|---|
| Treasury stress | YES | THIRD consecutive week: 30Y five closes >=5.50 (5.632 high, since 2002), 10Y 5.342 intraday (since 2002), 7Y weak, Oct 1 buyback drew $46.4B of offers for $6B, MOVE 108, long end sold off into a +29K payroll |
| Credit stress | PARTIAL | FRED HY OAS 308->312 (Sep 29-30), CCC 1,179; ORCL CDS record 227, long bonds >8%; SB CDS >400; still no default/writedown; HY <350 |
| Equity breadth | YES | CONFIRMED: NYSE lows > highs 23 consecutive sessions, 43-49% above 200dma, 75% of S&P down in September, RSP -1.9% vs SPX +2.0% in Q3 -- while NDX made a record Oct 2 (the divergence IS the signal) |
| Funding/plumbing stress | no | quarter-end PASSED CLEAN: SOFR 3.90% on Sep 30 inside the band through a $202B coupon settlement; bills 2.7-2.8x covered; MMF assets record $7.98T; Fed RMP paused to Oct 14 without incident |
| Real-economy deterioration | PARTIAL | PARTIAL: payrolls +29K with -60K revisions and July -10K, UR 4.2, AHE 3.0 (real negative), Conf Board 81.9 lowest since 2014, Challenger hiring plans 15-yr low; against: claims 197K / continuing 1.70M (3-yr low), real PCE +0.6% |

**2 of 5 fully confirmed** (3.0 weighted). The 3-of-5 rule is NOT met: the systemic-clock hazard is gated to 74% of its unconfirmed value. This is why the near-term systemic hazard stays low while the correction hazard is high.

## 7. Market internals (memo #7)

| Signal | Reading | Stress 0–1 | Tier |
|---|---|---:|:---:|
| Breadth: new lows vs new highs | NYSE lows > highs 23 straight sessions (longest since Oct-23); Oct 1 lows 393 vs highs 15 | 0.9 | T2 |
| Breadth: % above 200dma / 50dma | 43-49% above 200dma, ~31% above 50dma, with NDX at a record (lowest 7% of days historically for a near-record index) | 0.8 | T2 |
| Leadership: equal-weight vs cap-weight | RSP -1.9% in Q3 vs SPX +2.0%; 75% of S&P members fell in September | 0.7 | T2 |
| Leadership: semis / memory | NVDA record $234, MU ~$1,097, SOXX +2% Oct 2 after its worst quarter since 2025 | 0.4 | T3 |
| Volatility: VIX / VVIX | 15.5 (range 15.5-16.4 this week); VVIX contained | 0.2 | T2 |
| Volatility: MOVE | 108 (Oct 1) from ~80 on Sep 22 | 0.8 | T2 |
| Stock-bond correlation | 10Y +6bp on a +29K payroll; stocks up on the same print | 0.6 | T2 |
| Liquidity: Treasury depth / repo / SRF | $202B settlement Sep 30 passed without a reported SOFR/SRF spike (pending rates sweep) | 0.3 | T3 |
| Positioning: CTAs / dealer gamma | GS: CTA now asymmetric to the UPSIDE (+$9B US up-tape vs -$0.5B down); dealers 'extremely short gamma into a breakout' (GS); Nomura: clustering risk | 0.5 | T3 |
| Positioning: margin debt | $1.45T record (Aug), +37% y/y; Sept due ~Oct 15 | 0.7 | T2 |
| Positioning: pension / blackout | $30-33B quarter-end pension sell EXECUTED (late-day Sep 30 dump); blackout ~61% of cap, reopens ~Oct 13 | 0.4 | T3 |

Internals score **61 / 100**: bond volatility and positioning are stressed, equity volatility is not — the transition signal is half-formed.

## 8. Historical analogue engine (memo #18)

State vector ['capez', 'cape_lvl', 'ret12', 'dy10', 'rvol', 'erp_pp'] at t, t−3, t−6, t−12 (CAPE z-score vs 20-yr mean, 12-month return, 12-month change in the 10-year, realized 12-month vol, ERP) over the Shiller monthly record 1881–2023 (1651 months); distance = ½ point distance + ½ DTW over the trajectory; 20 nearest, de-clustered at 18 months. Current-state inputs are ESTIMATES (12m return +17%, 10Y +1.0pp, CAPE 40.9, ERP −0.6). VIX is not used (unavailable before 1990); pre-1982 episodes are therefore included.

| Match date | Distance | CAPE | Months to −10% | to −20% | to −25% |
|---|---:|---:|---:|---:|---:|
| 2000-02-01 | 1.25 | 42.2 | 10 | 13 | 19 |
| 1997-11-01 | 2.09 | 32.3 | 10 | >36 | >36 |
| 2018-09-01 | 2.45 | 32.6 | 3 | >36 | >36 |
| 2002-06-01 | 3.09 | 26.4 | 1 | >36 | >36 |
| 2007-10-01 | 3.16 | 27.3 | 3 | 11 | 12 |
| 2004-06-01 | 3.28 | 26.4 | >36 | >36 | >36 |
| 1996-03-01 | 3.66 | 25.6 | 30 | >36 | >36 |

Empirical hazard from the matches (events / at-risk per bucket):

| Bucket | −10% | −20% | −25% |
|---|---|---|---|
| 0-6m | 3/7 = 43% | 0/7 = 0% | 0/7 = 0% |
| 6-12m | 2/4 = 50% | 1/7 = 14% | 1/7 = 14% |
| 12-18m | 0/2 = 0% | 1/6 = 17% | 0/6 = 0% |
| 18-24m | 0/2 = 0% | 0/5 = 0% | 1/6 = 17% |
| 24-36m | 1/2 = 50% | 0/5 = 0% | 0/5 = 0% |

Mechanism filter ON: candidates restricted to the 111 months (of 1651) that satisfy rule R1 or R2 at the match date, so matches share the transmission mechanism, not just the chart (BDCR 2.0 memo §6, §15). Small-sample caveat: twenty matched months, many from the same few regimes. The analogue hazard enters the engine curve at 30% weight.

Chart-only matching (no mechanism filter), for comparison — the memo warns against exactly this: 2000-02, 1997-11, 2018-09, 1929-10, 1966-04, 1902-04, 1964-09, 1968-12, 1962-03, 2004-07.

### 8b. Backtest of pre-specified mechanism rules (BDCR 2.0 memo §4–§6)

Rules written before looking at outcomes: **R1 no-cushion valuation** = CAPE >= 25 AND (E/P - 10Y) <= +0.5pp; **R2 rate shock into richness** = CAPE >= 25 AND 12-month change in 10Y >= +0.75pp; **R3 top formation** = R1 AND 12-month return >= +10% AND realized vol rising vs 6 months earlier. Today satisfies R1, R2 and R3. Outcome = a drawdown of the stated size from the running high within the stated horizon, measured on Shiller monthly prices 1881–2023. In-sample / out-of-sample split at 1960.

| State | n | P(−10% in 12m) | P(−20% in 24m) | P(−25% in 36m) | pre-1960: n, −25%/36m | post-1960: n, −25%/36m |
|---|---:|---:|---:|---:|---|---|
| R1 no-cushion valuation | 89 | 51% | 47% | 52% | 0, 0% | 89, 52% |
| R2 rate shock into richness | 17 | 41% | 53% | 59% | 0, 0% | 17, 59% |
| R3 top formation | 29 | 28% | 17% | 31% | 0, 0% | 29, 31% |
| R1 AND R2 (today) | 12 | 50% | 75% | 75% | 0, 0% | 12, 75% |
| ALL months (base rate) | 1674 | 38% | 29% | 32% | 948, 37% | 726, 24% |

Episodes in today's state (R1 AND R2): [('1997-01-01', '1997-01-01'), ('1999-09-01', '2000-05-01'), ('2004-05-01', '2004-06-01')]. Read the lift, not the level: the rules were specified from the mechanism (no cushion + rate shock into richness), not tuned, and the question is whether the conditional rates beat the base rate in BOTH halves of the sample. Where they do, the mechanism has historical support; where the post-1960 sample is a handful of months, the test is inconclusive and says so.

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
| Oct 2026 | 26.5 | 7.9 | 3.0 | 0.9 | 3.1 | 1.1 | 1.0 | 0.55 |
| Nov 2026 | 36.0 | 9.2 | 3.0 | 1.0 | 3.3 | 1.3 | 1.0 | 0.55 |
| Dec 2026 | 10.4 | 6.0 | 2.4 | 1.2 | 1.7 | 1.2 | 1.0 | 0.75 |
| Jan 2027 | 11.6 | 6.0 | 2.5 | 1.2 | 1.7 | 1.2 | 1.0 | 0.75 |
| Feb 2027 | 13.2 | 11.8 | 2.8 | 1.8 | 1.7 | 1.3 | 1.5 | 1.00 |
| Mar 2027 | 15.2 | 12.9 | 3.1 | 2.0 | 2.0 | 1.3 | 1.7 | 1.00 |
| Apr 2027 | 6.4 | 10.6 | 3.4 | 2.7 | 2.2 | 2.1 | 2.3 | 1.00 |
| May 2027 | 6.9 | 10.8 | 3.8 | 2.8 | 2.5 | 2.1 | 2.4 | 1.00 |
| Jun 2027 | 7.4 | 11.0 | 4.2 | 2.9 | 2.7 | 2.1 | 2.5 | 1.00 |
| Jul 2027 | 8.0 | 11.2 | 5.4 | 3.3 | 4.8 | 2.0 | 3.1 | 1.00 |
| Aug 2027 | 8.7 | 11.5 | 6.1 | 3.5 | 5.4 | 2.0 | 3.3 | 1.00 |
| Sep 2027 | 9.5 | 11.8 | 6.8 | 3.7 | 6.1 | 2.0 | 3.5 | 1.00 |
| Oct 2027 | 2.2 | 6.3 | 6.9 | 3.8 | 6.9 | 1.2 | 3.2 | 1.00 |
| Nov 2027 | 2.2 | 6.1 | 7.1 | 3.8 | 7.0 | 1.1 | 3.2 | 1.00 |
| Dec 2027 | 2.3 | 5.8 | 7.2 | 3.8 | 7.1 | 1.0 | 3.2 | 1.00 |
| Jan 2028 | 2.3 | 5.5 | 7.2 | 3.8 | 7.1 | 0.9 | 3.1 | 1.00 |
| Feb 2028 | 2.4 | 5.0 | 7.3 | 3.7 | 7.1 | 0.8 | 3.0 | 1.00 |
| Mar 2028 | 2.5 | 4.5 | 7.3 | 3.7 | 7.0 | 0.7 | 3.0 | 1.00 |
| Apr 2028 | 2.5 | 4.0 | 7.3 | 2.9 | 6.9 | 1.5 | 3.5 | 1.00 |
| May 2028 | 2.6 | 2.0 | 7.3 | 2.1 | 6.7 | 1.4 | 2.5 | 0.80 |
| Jun 2028 | 2.6 | 1.7 | 7.8 | 2.2 | 6.5 | 1.3 | 2.3 | 0.80 |
| Jul 2028 | 2.7 | 1.5 | 2.9 | 0.9 | 2.8 | 1.2 | 1.4 | 0.80 |
| Aug 2028 | 2.8 | 1.3 | 2.9 | 0.9 | 2.9 | 1.1 | 1.3 | 0.80 |
| Sep 2028 | 2.9 | 1.2 | 3.0 | 0.8 | 3.0 | 1.1 | 1.3 | 0.80 |
| Oct 2028 | 3.0 | 1.9 | 3.1 | 0.8 | 3.1 | 0.1 | 0.8 | 0.80 |
| Nov 2028 | 3.1 | 1.8 | 3.2 | 0.8 | 3.2 | 0.1 | 0.8 | 0.80 |
| Dec 2028 | 3.1 | 3.1 | 3.3 | 1.2 | 3.3 | 0.1 | 1.2 | 1.00 |
| Jan 2029 | 3.3 | 3.0 | 3.4 | 1.2 | 3.4 | 0.0 | 1.2 | 1.00 |
| Feb 2029 | 3.4 | 3.0 | 3.6 | 1.2 | 3.5 | 0.0 | 1.2 | 1.00 |
| Mar 2029 | 3.5 | 3.1 | 3.7 | 1.3 | 3.7 | 0.0 | 1.3 | 1.00 |
| Apr 2029 | 3.6 | 3.1 | 3.8 | 1.3 | 3.8 | 0.0 | 1.3 | 1.00 |
| May 2029 | 3.7 | 3.2 | 4.0 | 1.3 | 4.0 | 0.0 | 1.4 | 1.00 |
| Jun 2029 | 3.9 | 3.2 | 4.2 | 1.4 | 4.1 | 0.0 | 1.4 | 1.00 |
| Jul 2029 | 4.0 | 3.3 | 4.3 | 1.5 | 4.3 | 0.0 | 1.5 | 1.00 |
| Aug 2029 | 4.2 | 3.4 | 4.5 | 1.5 | 4.5 | 0.0 | 1.5 | 1.00 |
| Sep 2029 | 4.4 | 3.5 | 4.8 | 1.6 | 4.7 | 0.0 | 1.6 | 1.00 |

### 10b. Specification stability (BDCR 2.0 memo §16: confidence = stability across specifications)

162 specifications: engine weight λ ±0.15, analogue blend 0.15/0.30/0.45, engine level ×0.7/1.0/1.3, analogue neighbours k = 12/20/30, election deferral on/off. **100%** keep the systemic modal month within ±2 months of the base result. Modal-month distribution: {'Sep 2027': 138, 'Jul 2027': 18, 'Oct 2027': 6}. 10th-percentile start month ranges Dec 2026 – Mar 2027. Confidence score = ½ stability + ½ min(1, confirmed domains / 3) = 0.83 → **HIGH**.


## 11. What was adopted, changed, or rejected from the memo

- **Adopted in full:** causal factors (§1); four engines with a first-crack chain, reflexivity gain and coverage ratio (§2); the liability clock (§3, first fill); the hard cash-flow test (§4); marginal-rate sovereign engine, clearing model, buyers'-strike detector, failed-rescue counter, policy-exhaustion clock (§5); 3-of-5 confirmation (§6); internals as a timing layer (§7); analogue engine with trajectory matching (§8); network centrality (§9); a monthly hazard model with three separate clocks (§10); evidence tiers; election calendar demoted to a suppression modifier; forecast separated from trade timing; October 2027 demoted to a prior.
- **Changed:** the 32-indicator composite is *kept*, renamed the structural layer, and reported alongside the de-duplicated vulnerability score rather than replaced — the pre-registered thresholds and amendment log are the audit trail the new engine does not yet have. The hazard model is a Bayesian blend (prior × engine, λ set by confirmation and convergence) rather than a purely statistical survival fit: ten crash episodes cannot support a fitted survival model without a prior, and the memo itself says to treat the current forecast as one.
- **Rejected / deferred:** a fitted survival regression on episode data (N too small; the analogue engine's empirical hazard is used instead); Dynamic Time Warping over 24-month windows (implemented over four trajectory points — longer windows overfit the 1929/2000 shapes); a full maturity database (the environment cannot reach EDGAR/LCD/Bloomberg, so the clock ships with tagged placeholders).
- **What the first run says:** the engine curve and the prior agree on the centre of mass (H2-2027) but the engine puts more mass in Q1–Q2 2027 than the judgment did, because the sovereign engine is further along the chain than the AI engine and its clocks (QRA, rollover, Oct 8) come first. The posterior modal month is unchanged at October 2027 only because the confirmation gate (2 of 5) and the election modifier suppress the near-term systemic hazard; if confirmation reaches 3 of 5 before year-end, the modal month moves into the first half of 2027.