#!/usr/bin/env python3
"""
BDCR-26 — US Big Debt Cycle Regime Algorithm
=============================================

A 31-indicator, 7-pillar mechanical implementation of Ray Dalio's
"How Countries Go Broke" (2025) 9-stage big-debt-cycle framework and
"The Changing World Order" (2021) cycle markers, hardened with:

  * Jorda-Schularick-Taylor credit-damage weighting (levered bubbles kill,
    equity bubbles bruise)
  * Kindleberger/Minsky bubble-stage markers scored against the 2026 AI boom
    (capex-to-revenue gap, circular/vendor financing, debt/SPV share,
    forensic first-credit-event tripwires)
  * Consumer-stress thresholds calibrated to 2007-2010 GFC levels
    (delinquency transitions, utilization, subprime lender failures)
  * China/global contagion and JGB carry-trade legs

Composite = sum(weight_i * score_i) / 3  ->  0-100 scale
  (weights sum to 100, scores are 0-3, so the max raw sum is 300)

Regime assignment is score-band SUBJECT TO TWO GATES:
  * MONETIZATION GATE (Regime 4): a score in the R4 band does NOT mean
    fiscal dominance until the Fed is actually buying duration / capping
    yields / holding real rates negative under fiscal pressure — Dalio
    Stage 5. Without the gate: "R3-upper, repression-lite onset".
  * CRISIS GATE (Regime 5): composite >= 85 AND at least one hard
    crisis marker, OR any two markers at any score (failed auction,
    Dalio triple, foreign buyers' strike, 30Y > 6% sustained,
    funding-plumbing run). A score alone never triggers R5 — the
    market-failure event is the definition.

TIEBREAK CONVENTION: where a current reading is an estimate range that
straddles a threshold boundary, score the MIDPOINT of the range. Bands
are half-open: R3 = [45, 70), R4 = [70, 85), R5 = [85, 100].

Design note: an own-currency reserve issuer "goes broke" via inflation,
financial repression and devaluation (chronic), not coupon default (acute).
Regime 4 is therefore the central attractor of the system, not a waypoint
to Armageddon. The algorithm scores POSITION IN THE CYCLE, explicitly not
market timing.

Baseline readings as of 2026-07-28; RE-SCORED 2026-09-10 (see SEPT 2026 RE-SCORE LOG at end) (sources in each
indicator's `series` field; refresh cadence: monthly, quarterly deep
refresh for TIC / COFER / NY Fed HHDC series). Where a reading could not
be verified against a primary source it is marked UNVERIFIED in the note.

This is an analytical framework, not investment advice.
"""

from dataclasses import dataclass, field


@dataclass
class Indicator:
    name: str
    pillar: str
    series: str          # exact data source / FRED ID where available
    thresholds: str      # numeric mapping to danger scores 0-3
    weight: int          # fixed weight, all weights sum to 100
    value: str           # current reading as of 2026-07-28
    score: int           # 0 (benign) .. 3 (crisis-consistent)
    note: str = ""

    @property
    def contribution(self) -> int:
        return self.weight * self.score


INDICATORS = [
    # ------------------------------------------------------------------
    # PILLAR 1 — FISCAL SUSTAINABILITY (weight 17)
    # ------------------------------------------------------------------
    Indicator(
        "Net interest / federal revenue", "1. Fiscal",
        "MTS net interest / receipts (FRED FYOINT/FYFR; fiscaldata.treasury.gov)",
        "0:<10% | 1:10-14 | 2:14-18 | 3:>=18  (1991 record ~18; UK-1976 >20)",
        6, "~18.6% FY26 ($857B net interest in 9mo, +13% y/y)", 3,
        "Interest now exceeds defense AND Medicare; the debt compounds on itself"),
    Indicator(
        "Deficit % of GDP", "1. Fiscal",
        "FRED FYFSGDA188S; CBO Monthly Budget Review",
        "0:<3 (Dalio's 3% solution) | 1:3-5 | 2:5-7 | 3:>=7",
        6, "5.8-6.1% (FY26 tracking $1.9-2.0T; tariff offset gutted by SCOTUS IEEPA ruling)", 2,
        "OBBBA locked in ~6% structural deficits; a recession from here = 9-10%"),
    Indicator(
        "Debt held by public % GDP", "1. Fiscal",
        "FRED FYGFGDQ188S; Debt to the Penny / BEA GDP",
        "0:<75 | 1:75-90 | 2:90-105 | 3:>=105 (1946 peak 106; CBO crosses ~106 by 2029-30)",
        3, "100.2% — crossed 100% April 2026; CBO path 118% by 2035", 2,
        "Every prior crisis response started from a far lower base (2008: 35%, 2020: 79%)"),
    Indicator(
        "r-minus-g on federal debt", "1. Fiscal",
        "Avg rate on marketable debt (fiscaldata) minus nominal GDP y/y (FRED GDP)",
        "0:<=-1.5pp | 1:-1.5-0 | 2:0-+1 | 3:>+1pp",
        2, "-0.6 to -0.9pp (avg coupon 3.41% vs ~4-4.3% NGDP) but marginal 10Y = 4.63%", 1,
        "Blanchard's free lunch fading: ~33% of debt reprices within a year"),

    # ------------------------------------------------------------------
    # PILLAR 2 — DEBT SUPPLY / DEMAND (weight 16)
    # ------------------------------------------------------------------
    Indicator(
        "10Y term premium", "2. Supply/Demand",
        "FRED THREEFYTP10 (Kim-Wright); NY Fed ACM cross-check",
        "0:<0 | 1:0-0.5 | 2:0.5-1.0 | 3:>=1.0%",
        4, "0.73% (Jul 2026) — highest since 2014 after a decade near zero", 2,
        "The restored price of supply outrunning price-insensitive demand"),
    Indicator(
        "Auction stress composite", "2. Supply/Demand",
        "TreasuryDirect results: tails vs when-issued, bid-to-cover, dealer takedown",
        "0:none | 1:occasional | 2:>=6 serial tails OR dealer 2x norm | 3:tail>=4bp & BTC<2.2 at 10/30Y",
        5, "[Sep-10] Score rests on the '>=6 consecutive tails in any tenor' clause: 5Y tail streak continued (Aug 26 +0.2bp). NOT on the 10Y: Sep 9 10Y BTC 2.71 (best since 2019), dealers 4.3%, stop-through — demand clears at a higher price. No failed-adjacent auction", 2,
        "Bifurcated demand: belly buyers' strike vs record indirects at the long end"),
    Indicator(
        "Foreign official demand", "2. Supply/Demand",
        "Treasury TIC major-holders + official/private split",
        "0:official buying >$100B/y | 1:flat | 2:official selling, private offset | 3:broad selling >$300B/y",
        3, "Official SOLD $39.9B May-26; China $652B (-$113B y/y); private +$172B offset", 2,
        "Dalio Stage-4 marker: owned demand replaced by rented (levered basis-trade) demand"),
    Indicator(
        "30Y yield stress level", "2. Supply/Demand",
        "FRED DGS30",
        "0:<4.5 | 1:4.5-5.0 | 2:5.0-5.5 | 3:>=5.5% (forced-intervention zone)",
        4, "[Sep-10] 5.31% (2007 high; 5.33% Aug-18 peak) after TWO Treasury buyback escalations (Aug 19 $4B/op, Sep 9 $6B/op) each retraced within sessions. WATCH: score held at 2 under the unamended >=5.5% rule; see prospective amendment in log", 2,
        "The long end is where repression regimes break (US-1951, UK-1976, Japan-2025)"),

    # ------------------------------------------------------------------
    # PILLAR 3 — MONETARY / INFLATION (weight 13)
    # ------------------------------------------------------------------
    Indicator(
        "Core PCE y/y", "3. Monetary",
        "FRED PCEPILFE",
        "0:<2.5 | 1:2.5-3.0 | 2:3.0-4.0 | 3:>=4.0%",
        4, "3.4% (May-26, m/m highest since Oct-23); headline PCE 4.1%", 2,
        "Tariff pass-through (+0.8pp per Dallas Fed) + Hormuz oil = classic wave one"),
    Indicator(
        "Inflation expectations (survey vs market)", "3. Monetary",
        "UMich 5-10yr; FRED T10YIE; +1 notch if survey-market gap >1pp",
        "0:<2.9 | 1:2.9-3.2 | 2:3.2-3.5 or gap>1pp | 3:>=3.5 or breakeven>2.8",
        3, "UMich 5-10y 3.3%, 1y 4.2%; 10Y breakeven anchored 2.28% — ~1pp gap", 2,
        "Households de-anchored, market not: the breakeven following is THE tell"),
    Indicator(
        "Fed independence stress", "3. Monetary",
        "Event index: removals/litigation (Trump v. Cook), probes, confirmation margins",
        "0:none | 1:rhetoric | 2:attempted removals/probes/accord machinery | 3:commanded easing",
        4, "Cook firing blocked 5-4; criminal probe of a Fed chair; Warsh confirmed 54-45 — but FOMC is HIKE-biased", 2,
        "The firewall held by one vote; board tilts through 2028"),
    Indicator(
        "Monetization & real-rate stance (Stage-5 GATE)", "3. Monetary",
        "Real EFFR (EFFR - PCEPILFE); H.4.1 composition (bills vs coupons vs YCC)",
        "0:real>=+1%, no buys | 1:0-1%, bills-only | 2:real<0 w/ PCE>3 OR coupon QE | 3:YCC / real<-1% + QE",
        2, "[Sep-10] Fed: real EFFR ~+0.3%, bills-only, ~59% priced to HIKE Sep 16 = affirmative evidence AGAINST the gate. Treasury buying duration ($6B/op, bill-funded 'Treasury Twist') counts toward 30Y stress (market forcing fiscal action) but NOT toward this gate, which requires the FED to accommodate: documented trigger = Fed duration purchases or a formal cap", 1,
        "THE gate indicator: Dalio Stage 5 has demonstrably NOT begun — the key 'not yet'"),

    # ------------------------------------------------------------------
    # PILLAR 4 — MARKET FRAGILITY (weight 12)
    # ------------------------------------------------------------------
    Indicator(
        "Shiller CAPE", "4. Fragility",
        "Shiller/Yale (multpl.com)",
        "0:<25 | 1:25-32 | 2:32-40 (>1929's 32.6) | 3:>=40 (only Dec-1999's 44.2 higher)",
        5, "~40.9 (live 40.6-40.9, Jul 2026); Buffett indicator 234% of GDP (record; dot-com peak 172%)", 3,
        "From CAPE 41 the base rate is ~0%/yr real 10-yr returns; 1966-82 is the template"),
    Indicator(
        "Equity risk premium", "4. Fragility",
        "S&P fwd E/P minus FRED DGS10",
        "0:>=+3pp | 1:+1-3 | 2:0-1 | 3:<=0",
        3, "Straddles zero: 21-22x forward (E/P 4.5-4.8%) vs 10Y 4.63% = -0.13 to +0.17pp; midpoint ~0 -> band 2 by tiebreak", 2,
        "Zero cushion: term-premium shocks transmit one-for-one into multiples"),
    Indicator(
        "Credit complacency/stress (two-sided)", "4. Fragility",
        "FRED BAMLH0A0HYM2 / BAMLC0A0CM; private-credit true-default indices",
        "0:HY 350-500 | 1:300-350/500-600 | 2:<300 (complacency) or 600-800 | 3:>800 or PC defaults>6%",
        4, "[Sep-10] HY OAS 265bp / IG ~78bp richest decile; Fitch private-credit default rate RECORD 6.1% (headline incl. extensions); BCRED capped 3rd qtr, Cliffwater capped; BDC median discount ~26%, non-accruals highest since 2017; LL defaults 0.87%. 'High 2' — the 3-clause's transmission-to-insurers/pensions leg is NOT evidenced", 2,
        "Tightest-decile spreads offer zero cushion against the AI-credit or consumer channels"),

    # ------------------------------------------------------------------
    # PILLAR 5 — BUBBLE DYNAMICS: Kindleberger/Minsky (weight 14)
    # ------------------------------------------------------------------
    Indicator(
        "Top-10 S&P concentration", "5. Bubble",
        "S&P DJ factsheets; GS/JPM concentration work",
        "0:<22 | 1:22-27 (2000 peak) | 2:27-35 | 3:>=35%",
        2, "~38% top-10 (top-5 ~30%, most in 50+ yrs); AI names = 75% of returns since Nov-22", 3,
        "Index outcomes hinge on ~$545B/yr of AI capex earning its cost of capital"),
    Indicator(
        "AI capex-to-revenue gap", "5. Bubble",
        "Big-4 hyperscaler TOTAL capex guidance minus annualized genAI end-market revenue (disclosed cloud-AI run-rates + lab ARR; Sequoia/Bain aggregation)",
        "0:<$100B | 1:100-300 | 2:300-500 | 3:>=$500B",
        3, "~$455-525B: big-4 2026 capex $725B (+77% y/y, confirmed) vs genAI revenue ~$200-270B; midpoint ~$490B -> band 2 by tiebreak; divergence 46% vs 32% at telecom-2001 peak", 2,
        "AI revenue does not yet cover the ~$110B/yr depreciation on the installed base"),
    Indicator(
        "Circular / vendor-financed revenue share", "5. Bubble",
        "NVDA 10-Q concentration + deal map (OpenAI/Oracle/CoreWeave/SPVs); Lucent = 21% benchmark",
        "0:<5 | 1:5-15 | 2:15-30 (Lucent zone) | 3:>=30% or vendor debt guarantees at scale",
        2, "[Sep-10] SIGNED: NVDA $105B residual-value guarantee on OpenAI's 20-yr Ohio lease (8-K Aug 17; cut from $250B) = vendor credit support >= 1 quarter of revenue and > NVDA's $99B equity book (stakes in its own customers). Watch, not counted: $500B platform (no deal), $36B rev-share (paused), Broadcom ~$100B (assembling)", 3,
        "Lucent/Nortel at 10x scale — mitigated by funders' ~$475B/yr real operating cash flow"),
    Indicator(
        "Debt/SPV-financed share of AI capex", "5. Bubble",
        "AI IG issuance + private-credit DC loans + DC ABS/CMBS over total AI capex",
        "0:<10 (2024 cash phase) | 1:10-20 | 2:20-35 | 3:>=35% (JST regime-flip)",
        2, "~25-35% 2026E vs ~10% 2024: $175B bonds, >$200B private credit, >$120B SPV in 18mo", 2,
        "THE damage variable: decides whether an AI bust is 2001-shaped or 1873/2008-shaped"),
    Indicator(
        "Forensic first-credit-event tripwires", "5. Bubble",
        "NVDA DSO>60d / 2-cust>40% / inv>$25B; ORCL CDS>150; capex guide CUT; B200 spot<$4/hr; SPV impairment; depreciation-life cut",
        "0:none | 1:warning proximity >=2 | 2:1-2 confirmed | 3:>=3 confirmed or any AI credit default",
        3, "[Sep-10] 1 CONFIRMED on list: ORCL 5Y CDS >150bp (record ~215bp Aug; BBB-, FY27 FCF -$42B guided). Adjacent/not listed: NVDA Q3 GM guide -100bp, top-3 customers 44% of rev, CRWV CDS ~855bp. NOT: no capex cut (3 raises/0 cuts), MSFT LENGTHENED DC lives 15->25y, no AI credit default", 2,
        "Minsky Stage 4 starts with funding failures; first-distress-to-peak ran 6-18 months historically"),
    Indicator(
        "Retail froth (margin debt + 0DTE)", "5. Bubble",
        "FINRA margin debt / GDP; Cboe 0DTE share",
        "0:<2.5 | 1:2.5-3.0 (2000 ~2.8) | 2:3.0-3.5 | 3:>3.5% GDP or 0DTE>55%",
        2, "Record $1.53T margin debt (+51.5% y/y, ~4.0% GDP > 2021 peak ratio); 0DTE 59-65% of SPX volume", 3,
        "Every prior margin-debt record (1929, 2000, 2007, 2021) preceded major drawdowns by 6-18mo"),

    # ------------------------------------------------------------------
    # PILLAR 6 — HOUSEHOLD / CONSUMER CREDIT (weight 13)
    # ------------------------------------------------------------------
    Indicator(
        "Card + auto 90+ delinquency transitions", "6. Consumer",
        "NY Fed HHDC transition rates (quarterly)",
        "Card 0:<5.5 | 1:5.5-6.5 | 2:6.5-9.0 | 3:>=9.0 (GFC 13.7). Auto 0:<2.4 | 1:2.4-2.7 | 2:2.7-3.3 | 3:>=3.3",
        4, "Card ~7.0% (peak 7.2% mid-24, plateaued - highest since 2011, ~half the GFC's 13.7%); auto ~2.9-3.0% - NY Fed Q1-26: auto delinquency highest ever recorded", 2,
        "In the 2008-entry zone but PLATEAUED; the flip signal is re-acceleration + claims >2.3M"),
    Indicator(
        "Utilization / maxed-out / min-pay share", "6. Consumer",
        "Philly Fed min-pay share; NY Fed >90% utilization share; aggregate utilization",
        "0:minpay<9.5 & maxed<8 | 1:9.5-10.3 | 2:>=10.3 (record zone) or maxed>=10% | 3:minpay>11 & util>26%",
        2, "Min-pay ~10.5-10.9% (series record); ~10% of borrowers maxed out (1-in-6 GenZ); avg utilization ~29% (Experian); APR ~22-23%", 2,
        "The buffer-less cohort converts any labor shock into delinquency with unusual speed"),
    Indicator(
        "Subprime auto 60+ (Fitch ABS index)", "6. Consumer",
        "Fitch subprime auto ABS 60+ dpd; prime 60+ (<0.6% trigger) as contagion check",
        "0:<4.0 | 1:4.0-5.0 | 2:5.0-6.0, or >=6.0 with prime contained | 3:>=6.0 AND prime 60+ >0.6% (stress escaping the bottom quartile)",
        2, "[Sep-10] RE-ACCELERATING: 6.13% Jul (from 5.80% Jun; record 6.90% Jan); Fitch guides 'weaken further in H2'; PRIME 60+ 0.49% vs 0.6% escape trigger (closest yet); America's Car-Mart at going-concern (non-fraud failure candidate #1, covenant runway to Nov 6)", 2,
        "Above GFC-era levels but confined to the bottom quartile; PRIME contamination is the systemic signal"),
    Indicator(
        "Student loan 90+ share", "6. Consumer",
        "NY Fed HHDC; Dept. of Education default/garnishment counts",
        "0:<6 | 1:6-9 | 2:9-12 | 3:>=12% or >15% of portfolio garnished",
        1, "[Sep-10 CORRECTION] involuntary collections PAUSED since Jan 16 2026 (not scaling); ~5.3-5.5M in default = latent drag; 90+ share ~10%", 2,
        "A policy-manufactured drain on bottom-half cash flow that leaks into other products"),
    Indicator(
        "Household debt service ratio", "6. Consumer",
        "FRED TDSP",
        "0:<10.5 (2019 ~9.8) | 1:10.5-11.5 | 2:11.5-13 | 3:>=13% (2007 peak 13.2)",
        2, "~9.9-10.1% — AT 2019 levels; ~95% of mortgages fixed sub-4%", 0,
        "The great stabilizer vs 2007: the biggest household liability is cheap and locked"),
    Indicator(
        "Subprime lender defaults / funding stress", "6. Consumer",
        "Failure count (BHPH/fintech/specialty) T12M; ABS BB spread persistence",
        "0:none | 1:1 idiosyncratic, spreads re-tighten | 2:2-3 in 12mo or +200bp sustained | 3:funding freeze",
        2, "Tricolor Ch.7 (Sep-25, $1.4B ABS, fraud, >$1B bank hit) + First Brands; spreads re-tightened; no verified 2026 failures", 1,
        "Dimon's cockroach rule: fraud DISCOVERY, not credit deterioration, is the likely surprise vector"),

    # ------------------------------------------------------------------
    # PILLAR 7 — BIG CYCLE / CONFLICT / GLOBAL (weight 15)
    # ------------------------------------------------------------------
    Indicator(
        "Internal disorder index", "7. Big Cycle",
        "Political-violence counts; election-machinery events; DFA top-1% share; Dalio Stage-5/6 checklist",
        "0:normal | 1:polarized | 2:Stage-5 markers | 3:Stage-6 onset (contested election, organized violence)",
        5, "Stage 5: political attacks at 30-yr high; two assassinations + one attempt; top-1% wealth 31.7% (record); Nov-26 midterms ahead", 2,
        "Markets priced this twice (Apr-25 'Sell America', Jan-26 Fed-probe spike) — episodically, not persistently"),
    Indicator(
        "External conflict index", "7. Big Cycle",
        "Hormuz/Iran status (Brent); US-China truce (expiry Nov-10-26); Taiwan posture; capital-war provisions",
        "0:none | 1:trade war | 2:regional war + commodity disruption OR truce fraying | 3:great-power confrontation",
        3, "Iran war since Feb-26, Brent $86.6 (>$90 in July); new 12.5% S.301 tariff Jul-23-26; truce expires Nov-10-26", 2,
        "The oil channel is the live stagflation transmitter; reserve transitions tip on wars (Suez 1956)"),
    Indicator(
        "Reserve erosion & gold signal", "7. Big Cycle",
        "IMF COFER USD share; gold vs USTs in CB reserves (WGC/ECB); Dalio triple check",
        "0:COFER>60 | 1:57.5-60 drifting | 2:55-57.5 + gold>USTs + CB>700t/y + gold+20%y/y | 3:<55 falling fast or triple confirmed 3mo",
        4, "[Sep-10 CORRECTION] gold ATH was $5,596 (Jan 28 2026); ~$4,400 now = -20% from record, ~+20% y/y. Score rests on LEVEL clauses that survive: COFER 57.13% (in 55-57.5 band, though UP q/q), gold > USTs in CB reserves, gold +~20% y/y; CB buying slower YTD. Dalio triple 2 of 3 (yields up, DXY 98.8 down; gold NOT up since Jun 1). Low end of 2", 2,
        "Hedging the dollar system without leaving it: no successor exists (euro 20%, RMB 2%)"),
    Indicator(
        "China / global contagion index", "7. Big Cycle",
        "NBS China FAI cumulative y/y; 30Y JGB + BOJ; global mfg PMI; CNY/JPY tail checks",
        "0:FAI>+4, JGB30<2, PMI>52 | 1:FAI 0-4 or JGB 2-3 | 2:FAI contracting + JGB30>3 + PMI<=50.5 | 3:China credit event / CNY>7.5 / carry unwind 2.0 / JP repatriation>$200B/y",
        3, "China FAI -5.7% y/y H1-26 (property -14%, PPI negative ~39mo); 30Y JGB ~3.5% record, yen ~164; global PMI ~49.7-50.8", 2,
        "Two-edged: China's deflation export is worth 30-50bp OFF US yields; Japan is the real Treasury-flow risk"),
]


# ----------------------------------------------------------------------
# Regime bands and gates
# ----------------------------------------------------------------------

REGIMES = [
    (0, 25,  "R1 — Stable Expansion",
     "Full risk: cap-weight equities, normal 60/40 duration, minimal gold."),
    (25, 45, "R2 — Late-Cycle Buildup",
     "Stay but migrate: equal-weight/quality tilt, shorten credit, build gold/TIPS 5-10%."),
    (45, 70, "R3 — Stagflationary Fragility / Pre-Crisis Squeeze",
     "Defense with carry: underweight long nominals (bills/TIPS instead); gold 10-15%; "
     "equal-weight/value/ex-US tilt; avoid the AI-circularity credit chain and tightest-decile HY; "
     "own convex hedges; 6-12mo liquidity — drawdowns arrive as air pockets."),
    (70, 85, "R4 — Financial Repression / Fiscal Dominance  [requires Monetization Gate]",
     "Repression playbook: gold/hard assets, real assets with pricing power, equities only as "
     "inflation pass-throughs, foreign non-repressing currencies, floating/short duration, "
     "SHUN long nominals; borrow long+fixed — the state subsidizes debtors."),
    (85, 101, "R5 — Debt Crisis / Disorderly Deleveraging  [requires Crisis Gate]",
     "Survive then harvest: max gold, non-US bills, vol; do NOT catch long bonds until the policy "
     "response is announced — then buy duration the day caps/QE arrive (1951, UK 2022)."),
]

# Gate conditions (booleans set from current data, 2026-07-28)
MONETIZATION_GATE = False   # Fed duration purchases / YCC / sustained negative real rates: NOT met
                            # (Warsh Fed hike-biased, bills-only RMP, real EFFR ~ +0.2%)
CRISIS_GATE = False         # No failed 10-30Y auction; Dalio triple not confirmed; no buyers' strike
                            # R5 requires: composite >=85 AND >=1 crisis event, or any two events


def composite_score(indicators=INDICATORS) -> float:
    assert sum(i.weight for i in indicators) == 100, "weights must sum to 100"
    return sum(i.contribution for i in indicators) / 3.0


def classify(score: float) -> tuple[str, str]:
    for lo, hi, name, playbook in REGIMES:
        if lo <= score < hi:
            if name.startswith("R4") and not MONETIZATION_GATE:
                return ("R3-upper — repression-lite onset (R4 band, Monetization Gate NOT met)",
                        REGIMES[2][3])
            if name.startswith("R5") and not CRISIS_GATE:
                return ("R4-adjacent (R5 band, Crisis Gate NOT met)", REGIMES[3][3])
            return name, playbook
    return "unclassified", ""


def dashboard():
    print(__doc__.split("\n")[1])
    print("BDCR-26 dashboard — readings as of 2026-07-28")
    print("=" * 100)
    pillar_totals: dict[str, list[int]] = {}
    for ind in INDICATORS:
        pillar_totals.setdefault(ind.pillar, [0, 0])
        pillar_totals[ind.pillar][0] += ind.contribution
        pillar_totals[ind.pillar][1] += ind.weight * 3
        flag = ["  ", "· ", "! ", "!!"][ind.score]
        print(f"{flag} [{ind.score}/3 w{ind.weight:>2}] {ind.name:<46} {ind.value[:88]}")
    print("-" * 100)
    for pillar, (got, mx) in pillar_totals.items():
        bar = "#" * round(20 * got / mx)
        print(f"  {pillar:<18} {got:>3}/{mx:<3} {bar}")
    score = composite_score()
    regime, playbook = classify(score)
    print("=" * 100)
    print(f"COMPOSITE: {score:.1f} / 100   (raw {sum(i.contribution for i in INDICATORS)} of 300)")
    print(f"REGIME:    {regime}")
    print(f"GATES:     monetization={MONETIZATION_GATE}  crisis={CRISIS_GATE}")
    print(f"\nPLAYBOOK:  {playbook}")
    n2 = sum(1 for i in INDICATORS if i.score == 2)
    print(f"\nNote: {n2} of {len(INDICATORS)} indicators score exactly 2 — 'amber everywhere, red almost "
          "nowhere' is itself the signature of a late-cycle system with no slack. Honest recalibrations "
          "span roughly 62-76 (thresholds anchored to the ZIRP decade read mean-reversion as danger; "
          "re-anchoring to 1960-2025 distributions gives ~63-65). The REGIME call (upper R3, monetization "
          "gate unmet) is robust across that whole range; the point estimate is not.")


if __name__ == "__main__":
    dashboard()


# ======================================================================
# SEPT 2026 RE-SCORE LOG (2026-09-10)
# ======================================================================
# Composite 67.3 -> 69.0 (raw 202 -> 207). Regime: R3 upper bound. The 70 line
# was NOT crossed on unchanged rules. Two upgrades survived adversarial audit
# (circularity 2->3, forensic tripwires 1->2); two proposed upgrades (30Y 2->3,
# credit 2->3) were REVERTED because they required re-anchoring a pre-registered
# threshold in the same update that benefited from it / waiving a conjunctive clause.
#
# PROSPECTIVE RULE AMENDMENTS (effective next scoring; never retroactive):
#   30Y stress -> 3 if: 30Y closes >5.40 for 5 sessions, OR buybacks >$10B/op,
#     OR Fed enters duration, OR an official long-end intervention fails to hold
#     (yields at/above pre-intervention level within 5 sessions).
#   Credit stress -> 3 if: a named insurer/pension writedown on private-credit
#     marks, OR a BDC unsecured bond >600bp OAS, OR a BDC covenant breach / forced
#     deleveraging, OR HY OAS >500bp. (Gate/request ratios are leading, not scoring.)
#   Circularity 'at scale' = signed vendor credit support >= 25% of trailing-4Q
#     revenue or >= vendor equity book.
#   Consumer transitions 'weak-3 / watch' flag: escalate if hires rate <3.2% for
#     2 months, OR saving rate <3.0%, OR prime auto 60+ >0.6%.
#   Reserve-erosion/Fracture: add Section 899 legislative progress as a tripwire.
#
# PROBABILITIES (reconciled between consistency + calibration reviewers):
#   Muddle 31 | Repression 20 | AI Bust 16 | Second Wave/Long-End Accident 13 |
#   Productivity Escape 16 | Fracture 4   (Aug 19: 33/21/15/10/18/3)
#
# HONESTY NOTES: (1) Every indicator that rose is a financial-market indicator;
# every real-economy indicator was held despite deterioration in hires (3.2%),
# saving (3.0%), real wages (-0.1% y/y), subprime auto (6.13% re-accelerating)
# and Walmart's bottom-half warning — the composite measures narrative heat more
# than household stress. (2) A Fed ~59% priced to hike is evidence AGAINST fiscal
# dominance; the risk that rose is a hike-into-weakness slowdown plus an inflation
# leg, not a monetization event. (3) Japan's -$93B of UST sales (May-Jun) is mostly
# mechanical funding of a $98B yen intervention that SUCCEEDED (164 -> 153); do not
# score the pending TIC print of those sales as new stress.
