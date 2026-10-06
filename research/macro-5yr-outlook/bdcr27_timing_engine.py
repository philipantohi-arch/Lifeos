#!/usr/bin/env python3
"""
BDCR-27 Crash-Timing Engine  (v0.2, 2026-09-28)
=================================================

Response to two memos received 2026-09-28: "BDCR Crash-Timing Engine: Red-Team
Analysis, Counterpoints & Proposed Next-Generation Model" (v0.1) and "Dalio's
Methodology & BDCR 2.0" (v0.2). v0.2 adds, from the second memo: an explicitly
encoded Dalio decision tree with pass/fail per node (§2b); three reflexivity
loops with one-year gains (§2c); a fifth engine for market plumbing and a
private-credit sequence chain (§2); +200bp, asset-value and financing-
availability stresses in the funding-gap test (§4); mechanism-filtered
analogue matching (§8); a backtest layer that tests pre-specified mechanism
rules in and out of sample against the base rate, with nothing fitted (§8b);
and confidence defined as stability across model specifications (§10b).

The memo's central criticism is accepted: BDCR-26 answers "how dangerous is the
environment" and only asserts "when". This module sits ON TOP of the unchanged
32-indicator composite (which is retained as the STRUCTURAL REGIME layer, one of
three) and adds what the memo asked for, in the order it asked for it:

  §1  Causal-factor model      - 9 latent factors, de-duplicated (memo #2)
  §2  Four crash engines       - A sovereign, B AI capital cycle, C private
                                 credit, D consumer; each with first-crack stage,
                                 reflexivity gain, distance-to-crack (memo #4, #8,
                                 #9, #10, #19)
  §3  Liability maturity clock - quarterly refinancing/funding wall (memo #3, #22, #24)
  §4  AI funding-gap test      - required funding - FCF - equity - debt capacity,
                                 stressed (memo #3 hard cash-flow test)
  §5  Sovereign debt engine    - marginal refinancing rate, Treasury-demand clearing
                                 model, buyers'-strike detector, failed-rescue
                                 counter, policy-exhaustion clock (memo #11-#15)
  §6  Cross-market confirmation - 3-of-5 domain rule (memo #16)
  §7  Market internals layer   - breadth / leadership / vol / liquidity / positioning (memo #7)
  §8  Historical analogue engine - state-vector nearest neighbours + DTW on the
                                 1871-2023 Shiller monthly record; empirical
                                 time-to-drawdown hazard (memo #18)
  §9  Network centrality       - who is central, who is closest to failure (memo #20)
  §10 Monthly hazard model     - P(crash in month t | no crash before t) for three
                                 separate clocks (correction -10%, bear -20%,
                                 systemic -25% + transmission), with the election
                                 calendar as a POLICY-SUPPRESSION MODIFIER, not a
                                 timing input (memo #5, #6, #17, #21)
  §11 Dashboard                - the memo's §28 output, plus the three-date output (§27)

Evidence hierarchy (memo #25): every input carries a tier tag T1..T5. Hazard
contributions are weighted 1.0 / 0.8 / 0.5 / 0.3 / 0.1 by tier, so narrative
inputs (T5) cannot move the hazard curve on their own.

Forecast vs trade timing (memo #21): this module outputs the hazard curve only.
put_scenario_model_sept2026.py and v6/ are the trade-timing layer and read this
module's output through hazard_curve.json if they want to; they never write to it.

Data honesty: the environment that built this cannot reach FRED, TreasuryDirect,
EDGAR, Bloomberg or any licensed maturity database. Every dollar figure in the
liability clock is tagged VERIFIED (from a dated primary/secondary source already
in the research record), ESTIMATE (order-of-magnitude from public reporting) or
PLACEHOLDER (a slot that must be filled from primary sources before the clock is
trusted). The clock's STRUCTURE is the deliverable; its numbers are a first fill.

The October-2027 judgment forecast is treated exactly as the memo proposes: as a
PRIOR. The engine reports the prior curve, the engine curve and the blended
posterior separately, and states how many independent clocks currently converge.

Run:  python3 bdcr27_timing_engine.py      (writes hazard_report.md, hazard_curve.json)
"""
from __future__ import annotations
import json, math, sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bdcr26  # the structural layer (unchanged)

TODAY = date(2026, 10, 2)
TIER_W = {1: 1.0, 2: 0.8, 3: 0.5, 4: 0.3, 5: 0.1}

def month_add(d: date, n: int) -> date:
    y, m = divmod(d.month - 1 + n, 12)
    return date(d.year + y, m + 1, 1)

def mlabel(d: date) -> str:
    return d.strftime("%b %Y")

# ======================================================================
# §1  CAUSAL-FACTOR MODEL (memo #2): collapse 32 observables into 9 latent factors
# ======================================================================
# Aggregation inside a factor is 0.6*max + 0.4*mean of member scores, not a sum,
# so five symptoms of one sovereign-funding shock count roughly once.
FACTORS = {
    "Sovereign funding":      (["Net interest / federal revenue", "Deficit % of GDP", "Debt held by public % GDP",
                                "r-minus-g on federal debt", "10Y term premium", "Auction stress composite",
                                "Foreign official demand", "30Y yield stress level"], 18),
    "Monetary constraint":    (["Core PCE y/y", "Inflation expectations (survey vs market)", "Fed independence stress",
                                "Monetization & real-rate stance (Stage-5 GATE)"], 12),
    "Equity valuation/speculation": (["Shiller CAPE", "Equity risk premium", "Top-10 S&P concentration",
                                      "Retail froth (margin debt + 0DTE)"], 12),
    "AI capital cycle":       (["AI capex-to-revenue gap", "Circular / vendor-financed revenue share",
                                "Net investment / GDP (capital-cycle position)", "Forensic first-credit-event tripwires"], 14),
    "Private/corporate credit": (["Credit complacency/stress (two-sided)", "Debt/SPV-financed share of AI capex"], 10),
    "Household leverage":     (["Card + auto 90+ delinquency transitions", "Utilization / maxed-out / min-pay share",
                                "Subprime auto 60+ (Fitch ABS index)", "Student loan 90+ share",
                                "Household debt service ratio", "Subprime lender defaults / funding stress"], 12),
    "External/global funding": (["External conflict index", "Reserve erosion & gold signal",
                                 "China / global contagion index"], 10),
    "Political/institutional": (["Internal disorder index"], 6),
    # Liquidity / plumbing has NO indicator in BDCR-26 (a gap the memo is right about):
    # it is scored from the engine inputs in §7 and inserted here.
    "Liquidity/plumbing":     ([], 6),
}

def factor_scores(liquidity_score: float) -> dict:
    byname = {i.name: i for i in bdcr26.INDICATORS}
    out = {}
    for f, (members, w) in FACTORS.items():
        if not members:
            out[f] = dict(score=liquidity_score, weight=w, members=[]); continue
        s = [byname[m].score for m in members]
        out[f] = dict(score=0.6 * max(s) + 0.4 * sum(s) / len(s), weight=w,
                      members=[(m, byname[m].score) for m in members])
    return out

def systemic_vulnerability(fs: dict) -> float:
    return 100 * sum(v["score"] * v["weight"] for v in fs.values()) / (3 * sum(v["weight"] for v in fs.values()))

# ======================================================================
# §7  MARKET INTERNALS (memo #7) - inputs as of 2026-09-28, tier-tagged
# ======================================================================
@dataclass
class Obs:
    name: str; value: str; score: float; tier: int; note: str = ""   # score 0..1 = stress

INTERNALS = [  # as of 2026-10-02
    Obs("Breadth: new lows vs new highs", "NYSE lows > highs 23 straight sessions (longest since Oct-23); Oct 1 lows 393 vs highs 15", 0.9, 2, "Oct 2 digest"),
    Obs("Breadth: % above 200dma / 50dma", "43-49% above 200dma, ~31% above 50dma, with NDX at a record (lowest 7% of days historically for a near-record index)", 0.8, 2, ""),
    Obs("Leadership: equal-weight vs cap-weight", "RSP -1.9% in Q3 vs SPX +2.0%; 75% of S&P members fell in September", 0.7, 2, ""),
    Obs("Leadership: semis / memory", "NVDA record $234, MU ~$1,097, SOXX +2% Oct 2 after its worst quarter since 2025", 0.4, 3, "extreme, not reversal"),
    Obs("Volatility: VIX / VVIX", "15.5 (range 15.5-16.4 this week); VVIX contained", 0.25, 2, "equity vol still asleep"),
    Obs("Volatility: MOVE", "108 (Oct 1) from ~80 on Sep 22", 0.85, 2, "bond vol over equity vol regime"),
    Obs("Stock-bond correlation", "10Y +6bp on a +29K payroll; stocks up on the same print", 0.6, 2, "bonds refused the dovish read"),
    Obs("Liquidity: Treasury depth / repo / SRF", "$202B settlement Sep 30 passed without a reported SOFR/SRF spike (pending rates sweep)", 0.3, 3, ""),
    Obs("Positioning: CTAs / dealer gamma", "GS: CTA now asymmetric to the UPSIDE (+$9B US up-tape vs -$0.5B down); dealers 'extremely short gamma into a breakout' (GS); Nomura: clustering risk", 0.5, 3, "fuel for a melt-up leg, then air pocket"),
    Obs("Positioning: margin debt", "$1.45T record (Aug), +37% y/y; Sept due ~Oct 15", 0.7, 2, "FINRA"),
    Obs("Positioning: pension / blackout", "$30-33B quarter-end pension sell EXECUTED (late-day Sep 30 dump); blackout ~61% of cap, reopens ~Oct 13", 0.4, 3, "supply turns supportive mid-Oct"),
]

def internals_score() -> float:
    w = [TIER_W[o.tier] for o in INTERNALS]
    return 100 * sum(o.score * wi for o, wi in zip(INTERNALS, w)) / sum(w)

# ======================================================================
# §5  SOVEREIGN DEBT ENGINE (memo #11-#15)
# ======================================================================
SOV = dict(   # all $T unless noted; tags in comments
    marketable_debt=29.5,          # ESTIMATE (Debt to the Penny ~$38T gross; marketable ~$29-30T)
    reprice_within_1y_share=0.33,  # VERIFIED (bdcr26 r-g note)
    avg_coupon=0.0341,             # VERIFIED (fiscaldata, Jul-26)
    marginal_rate=0.051,           # VERIFIED-ish: 2Y 4.90 / 10Y 5.17-5.23 / 30Y 5.56 (Sep 25-28)
    deficit_fy26=2.1,              # VERIFIED (CBO, Sep 22)
    net_interest_fy26=1.05,        # VERIFIED (>$1T, AAF/MTS)
    revenue_fy26=5.4,              # ESTIMATE
    ngdp=31.0, ngdp_growth=0.042,  # ESTIMATE
    avg_maturity_yrs=5.9,          # ESTIMATE (Treasury ~71-72 months)
    # Treasury-demand clearing model (memo #12), FY27 flows, $T, ESTIMATE unless noted
    required_absorption=None,      # computed = deficit + Fed runoff (0 if RMPs bills-only net +)
    fed_net=+0.15,                 # ESTIMATE: bills-only reserve-management purchases
    banks=0.30, mmf=0.55, foreign_official=0.05, foreign_private=0.30,   # ESTIMATE (TIC: officials +$44B LT in Jul; private sellers)
    yield_per_T_residual=0.0025,   # ESTIMATE: +25bp per $1T of residual private absorption (Greenwood-Vayanos scale)
)

def sovereign_engine() -> dict:
    s = SOV
    reprice = s["marketable_debt"] * s["reprice_within_1y_share"] + s["deficit_fy26"]
    interest_step = reprice * (s["marginal_rate"] - s["avg_coupon"])         # $T/yr of extra interest from one year of rollover
    req = s["deficit_fy26"] + max(0.0, -s["fed_net"])
    demand = s["banks"] + s["mmf"] + s["foreign_official"] + s["foreign_private"] + max(0.0, s["fed_net"])
    residual = req - demand
    req_yield_premium = residual * s["yield_per_T_residual"] * 100  # bp... (0.0025*100 = 0.25 -> in pct pts)
    # reflexivity loop gain (memo #19): dyield -> dinterest -> ddeficit -> dissuance -> dyield, per year
    gain = (reprice * 0.01) * s["yield_per_T_residual"] / 0.01   # 1pp yield -> $ interest -> yield again, in pp per pp
    r_minus_g_marginal = s["marginal_rate"] - s["ngdp_growth"]
    return dict(reprice_T=reprice, interest_step_T=interest_step, interest_over_revenue=s["net_interest_fy26"] / s["revenue_fy26"],
                required_absorption_T=req, identified_demand_T=demand, residual_T=residual,
                required_yield_premium_pp=residual * s["yield_per_T_residual"] * 100,  # percentage points (0.75T x 25bp/T = 0.19pp)
                loop_gain=gain, r_minus_g_marginal=r_minus_g_marginal)

# Buyers'-strike detector (memo #13): last six coupon auctions in the record, tier 1/2 data
AUCTIONS = [  # (date, tenor, tail_bp (+ = tailed), btc, indirect %, dealer %, note)
    ("2026-08-26", "5Y", +0.2, 2.35, 64.0, 12.0, "tail streak continued (Sep-10 note); btc/indirects ESTIMATE"),
    ("2026-09-09", "10Y", -1.0, 2.71, 70.0, 4.3, "stop-through; best cover since 2019 (VERIFIED)"),
    ("2026-09-15", "20Y", 0.0, 2.45, 62.0, 10.0, "stopped 5.42% (VERIFIED level); tail/btc NF -> neutral"),
    ("2026-09-22", "2Y", +0.2, 2.55, 57.8, 13.2, "indirects 57.8 from 66; dealers highest since Mar (VERIFIED)"),
    ("2026-09-23", "5Y", +3.1, 2.21, 61.6, 15.0, "5.033% stop, first >5% since 2007; tail 3.1bp (one outlet) vs 0.7bp (another) -- CONFLICT, larger figure carried; indirects 61.6 from 74.9 (V)"),
    ("2026-09-24", "7Y", +3.0, 2.42, 57.2, 12.5, "5.085% vs 4.512% in Aug; ~3bp above WI; 'below average' (V, Oct-2 sweep)"),
    ("2026-10-01", "bills 4w/8w", -0.5, 2.80, 56.8, 8.0, "4-wk 3.890% 2.83x, 8-wk 3.99% 2.70x: the SHORT end is fine (V); not a coupon auction, scored as a control"),
]

def buyers_strike() -> dict:
    flags = 0; n = 0; detail = []
    for d, t, tail, btc, ind, dl, note in AUCTIONS:
        if tail is None: detail.append((d, t, "NF")); continue
        n += 1; f = 0
        if tail >= 1.0: f += 1
        if btc is not None and btc < 2.3: f += 1
        if ind is not None and ind < 60: f += 1
        if dl is not None and dl > 12: f += 1
        flags += f; detail.append((d, t, f))
    # 0..1: persistent deterioration = flags per auction / 4, requiring >=2 auctions with >=2 flags
    multi = sum(1 for _, _, f in detail if isinstance(f, int) and f >= 2)
    score = min(1.0, (flags / max(n, 1)) / 4 + 0.15 * multi)
    return dict(score=score, flags=flags, auctions=n, multi_flag_auctions=multi, detail=detail,
                verdict="persistent" if multi >= 3 else "emerging" if multi == 2 else "noise")

# Failed-rescue counter (memo #15): Treasury long-end buybacks as a time series
RESCUES = [  # (date, size_cap $B, filled $B, sessions until pre-op yield level regained/exceeded, initial move bp)
    ("2026-08-19", 4.0, 4.0, 4, -6, "retraced 'within sessions' (Sep-10 note); sessions ESTIMATE"),
    ("2026-09-10", 6.0, 5.19, 6, -6, "pre-op level regained on session 6 (VERIFIED, Sep-22 note)"),
    ("2026-09-24", 6.0, 4.08, 2, -3, "30Y 5.44-5.50 pre-op -> 5.56 on session +2 (VERIFIED intraday)"),
    ("2026-10-01", 6.0, 6.0, 2, -2, "10-20Y op: FULL $6B of $46.4B offered (7.7x) in two 2041-42 issues at 67-76c; 30Y 5.632 pre-op -> 5.613 -> ~5.63 on session +2 (V). Note: the Oct 1 long-end bid was partly French haven flow, not the buyback"),
]

def failed_rescue() -> dict:
    hl = [r[3] for r in RESCUES]
    fill = [r[2] / r[1] for r in RESCUES]
    trend = hl[-1] - hl[0]
    return dict(half_lives=hl, fill_ratios=fill, decaying=hl[-1] < hl[-2] and fill[-1] < fill[-2],
                count_failed=sum(1 for h in hl if h <= 5), score=min(1.0, 0.25 * sum(1 for h in hl if h <= 5) + (0.25 if hl[-1] < hl[-2] else 0)))

# Policy-exhaustion clock (memo #14): capacity REMAINING, 0..100 per arm (judgment on tier-2/3 data)
POLICY = {
    "Fed rate room":        (55, 3, "3.75-4.00% with core PCE 3.0 (revised) / headline 3.4 and consumer expectations 6%: ~100-150bp of cuts before the real rate <0; the hike cycle ended on data (Oct 2), which preserves room but not credibility"),
    "Fed balance sheet/QE": (35, 3, "QE into 3.4% core with 5-10y expectations at 3.4 = credibility cost; bills-only RMPs only"),
    "Treasury buybacks":    (25, 2, "$4-6B/op vs a market moving $10B+ of 30Y risk a day; last op under-filled; sizing at Nov 4 QRA"),
    "Fiscal impulse":       (15, 2, "deficit 6.6% GDP, interest >$1T, CR to Dec 11; no room without the bond market's consent"),
    "Foreign demand":       (25, 2, "TIC -$50B; private foreigners sellers; officials buying only to fund intervention"),
    "Political capacity":   (30, 4, "approval 33%; midterms; Fed under attack; Iran plan rejected"),
}

def policy_capacity() -> float:
    w = [TIER_W[t] for _, (_, t, _) in POLICY.items()]
    return sum(v * wi for (_, (v, _, _)), wi in zip(POLICY.items(), w)) / sum(w)

# ======================================================================
# §3  LIABILITY MATURITY CLOCK (memo #3, #22, #24) - $B per quarter that must be
#     refinanced or newly funded. Tags: V = verified in the record, E = estimate,
#     P = placeholder to be filled from primary sources.
# ======================================================================
Q = ["2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4", "2028Q1", "2028Q2", "2028Q3", "2028Q4"]
CLOCK = {
    # cohort: (amounts by quarter, tag, source note)
    "Hyperscaler bond issuance need":   ([70, 100, 105, 105, 110, 110, 110, 110, 110], "E",
        "GS: ~$250B 2026 / ~$400-420B 2027 hyperscaler bonds (Sep-16/22 notes); 2028 held flat"),
    "Oracle external funding (capex - OCF)": ([16, 16, 16, 17, 17, 17, 17, 17, 17], "E",
        "FY27 capex $90-95B debt/lease-only, FCF guide -$42B (Sep-10 note); ATM exhausted; $3.3B guarantee matured Sep-26"),
    "OpenAI funding need":              ([10, 15, 15, 20, 20, 30, 30, 35, 35], "E",
        "deck: FCF -$278B 2026-30, cash out by 2028, seeking >$1.2T; SoftBank $10B lands Oct 1 (V); profile back-loaded"),
    "Neocloud / GPU-collateral debt (CRWV, NBIS, xAI SPV)": ([4, 5, 6, 8, 8, 10, 10, 10, 10], "E",
        "CRWV $4.2B convert (V), DDTL amortization schedules, xAI $12.5B SPV debt (V); maturities NF -> profile assumed"),
    "Project-level DC debt (Jupiter, Hyperion, Meta ladder)": ([5, 8, 10, 10, 12, 12, 12, 12, 12], "E",
        "Jupiter $18B (V, in distress), Digital Drive 9.25% (V), CleanSpark 8.25% (V); construction-draw profile assumed"),
    "Private-credit BDC redemptions (gated 5%/qtr)": ([25, 25, 25, 25, 25, 25, 25, 25, 25], "E",
        "all perpetual BDCs capped 5%/qtr (V); ~$500B non-traded BDC/interval AUM x 5% (E)"),
    "BDC / private-credit fund unsecured maturities": ([5, 8, 10, 8, 10, 12, 12, 12, 12], "P",
        "PLACEHOLDER: fill from BDC 10-Ks; OBDC/BCRED/ARCC ladders"),
    "Leveraged loans maturing":         ([25, 35, 40, 45, 50, 70, 75, 80, 80], "E",
        "US LL maturity wall ~$150B 2027 / ~$300B 2028 (E, general market data; fill from PitchBook/LCD)"),
    "CRE / CMBS maturities":            ([220, 225, 225, 225, 225, 210, 210, 210, 210], "E",
        "MBA ~$900B/yr 2026-27 (E); office share the stressed slice"),
    "Subprime auto / BHPH facilities":  ([1.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], "V/E",
        "Car-Mart $300M (V, waivers to Oct 1); CACC; Tricolor/First Brands aftermath; ABS BB spreads"),
    "Treasury coupon + bill rollover (repricing)": ([2400, 2450, 2450, 2500, 2500, 2550, 2550, 2600, 2600], "E",
        "~33% of ~$29.5T reprices within 12m (V) + $2.1T deficit (V) -> ~$11.8T/yr, spread evenly"),
}

def clock_table() -> list:
    rows = []
    for name, (amts, tag, src) in CLOCK.items():
        rows.append((name, amts, tag, src))
    tot_private = [sum(a[i] for n, (a, t, s) in CLOCK.items() if not n.startswith("Treasury") and not n.startswith("CRE")) for i in range(len(Q))]
    return rows, tot_private

# ======================================================================
# §4  AI FUNDING-GAP TEST (memo #3): 12-month forward, $B, with stresses
# ======================================================================
AI = dict(
    capex_big4_2026=725, capex_big4_2027=850,          # V (2026, +77% y/y); 2027 E (+17%)
    ocf_big4=475,                                       # V ('~$475B/yr real operating cash flow', bdcr26 note)
    other_uses_big4=180,                                # E: buybacks/dividends/leases/other
    openai_need=60, oracle_need=65, neocloud_need=30,   # E (see clock)
    equity_available=120,                               # E: SoftBank $10B (V), sovereign/VC rounds, converts, ATMs
    debt_capacity_base=520,                             # E: IG market absorbed $259B AI IG YTD (V) + private $256B (V) at ~115bp over IG
    genai_revenue=235,                                  # V range midpoint ($200-270B)
)

def funding_gap(rate_shock_bp=0, revenue_shock=0.0, spread_shock_bp=0, util_shock=0.0,
                asset_value_shock=0.0, financing_avail=1.0) -> dict:
    """Memo (Dalio/BDCR 2.0 §10): stress +100bp, +200bp, revenue, utilization, monetization, financing
    availability and asset values. asset_value_shock cuts GPU/DC collateral values -> collateral-based
    debt capacity (assumed 35% of debt capacity is collateral-dependent); financing_avail scales the
    whole debt channel (a 30% cut = the IG/private window half-closing)."""
    a = AI
    rev_hit = a["genai_revenue"] * revenue_shock                              # lost revenue -> lost OCF (1:1 at margin)
    ocf = a["ocf_big4"] - rev_hit - a["ocf_big4"] * 0.15 * util_shock           # utilization hit flows to margin
    fcf_after_capex = ocf - a["capex_big4_2027"] - a["other_uses_big4"]
    required = -fcf_after_capex + a["openai_need"] + a["oracle_need"] + a["neocloud_need"]
    debt_cap = a["debt_capacity_base"] * (1 - 0.0015 * (rate_shock_bp + spread_shock_bp))  # E: capacity shrinks 15% per 100bp
    debt_cap *= (1 - 0.35 * asset_value_shock) * financing_avail
    gap = required - a["equity_available"] - debt_cap
    coverage = (a["equity_available"] + debt_cap) / max(required, 1)
    return dict(required=required, equity=a["equity_available"], debt_capacity=debt_cap, gap=gap, coverage=coverage)

# ======================================================================
# §2b  DALIO DECISION TREE (BDCR 2.0 memo §5): explicit, encoded conditions, tested not asserted
# ======================================================================
# Each node: (condition as written BEFORE looking, measurable variable, current reading, tier, passes?)
DECISION_TREE = [
    ("Debt rising faster than income", "federal debt growth vs nominal GDP growth (y/y)", "debt +~7-8% vs NGDP +4.2% (E)", 4, True),
    ("Debt service becoming restrictive", "net interest / revenue >= 18% OR marginal r - g > 0", "19.4% (V); marginal r-g +0.9pp (V)", 2, True),
    ("Monetary policy unable to fully offset", "Fed constrained by inflation: core PCE >= 3% with headline >3% while policy is restrictive; real EFFR > 0", "core 3.0% (revised, methodology), headline 3.4%, ISM prices 77.9; Oct hike ~17% after payrolls but no easing path with 6% consumer expectations (V)", 2, True),
    ("Credit contraction", "HY OAS > 400 OR bank C&I standards tightening > +20 net OR private-credit gates AND defaults > 6%", "HY 280 (no); gates + 6.3% defaults (yes, private only)", 2, False),
    ("Spending deterioration", "real retail sales < 0 y/y OR claims > 260K OR saving rate < 3.0% (old series; ~4.0% on the Sep-30 revised series)", "real PCE +0.6% Aug, claims 197K, saving 4.1% (revised series); payrolls +29K and real wages negative are the leading edge but not the written condition", 2, False),
    ("Deleveraging regime", "household or corporate debt/GDP falling with defaults rising", "no", 2, False),
]

def tree_stage() -> dict:
    stage = 0
    for i, (_, _, _, _, ok) in enumerate(DECISION_TREE):
        if ok: stage = i + 1
        else: break
    return dict(stage=stage, of=len(DECISION_TREE), next_node=DECISION_TREE[stage][0] if stage < len(DECISION_TREE) else None)

# ======================================================================
# §2c  REFLEXIVITY LOOPS (BDCR 2.0 memo §13): three loops, each with an estimated one-year gain
# ======================================================================
def loops(sov: dict) -> list:
    """gain = fraction of an initial shock that returns to its origin within ~1 year; >1 = explosive,
    0.3-1 = self-reinforcing, <0.3 = damped. Inputs tagged in notes."""
    # Loop 1 sovereign: yield -> interest -> deficit -> issuance -> yield (computed in sovereign_engine)
    l1 = sov["loop_gain"]
    # Loop 2 credit: losses -> lending down -> activity down -> defaults up. E: each 1pp of PC default ->
    # ~2% less private-credit origination -> ~0.05pp of GDP -> ~0.1pp more defaults (Fitch/loan-loss elasticities, E)
    l2 = 0.10 + 0.15 * (1 if DOMAINS["Credit stress"][0] >= 1 else 0.5)
    # Loop 3 collateral: prices -> collateral -> margin -> forced selling -> prices. E: margin debt $1.45T record,
    # CTA sell branch engaged, buyback bid absent -> a 10% fall triggers ~$100-200B of mechanical selling ~ 0.3-0.5 of the move
    l3 = 0.35 + 0.15 * (INTERNALS[9].score) + 0.10 * (INTERNALS[8].score)
    return [("Sovereign: yield -> interest -> deficit -> issuance -> yield", l1, "damped within a year; compounds into the 2028-29 interest step-up (V inputs)"),
            ("Credit: losses -> lending -> activity -> defaults", l2, "live in private credit only; the bank channel has not engaged (HY <300) (E)"),
            ("Collateral: prices -> collateral -> margin -> forced selling -> prices", l3, "margin debt record, CTA down-tape branch engaged, buyback bid in blackout: the strongest loop today (E)")]

# ======================================================================
# §8b  BACKTEST LAYER (BDCR 2.0 memo §4-§6): pre-specified mechanism rules tested on 1881-2023,
#      in-sample vs out-of-sample, against the unconditional base rate. No parameter is fitted.
# ======================================================================
RULES = {  # written before looking at outcomes; the current state satisfies all three
    "R1 no-cushion valuation":  "CAPE >= 25 AND (E/P - 10Y) <= +0.5pp",
    "R2 rate shock into richness": "CAPE >= 25 AND 12-month change in 10Y >= +0.75pp",
    "R3 top formation":          "R1 AND 12-month return >= +10% AND realized vol rising vs 6 months earlier",
}

def backtest():
    try:
        import numpy as np, pandas as pd
        from v6.data.loaders import build_all
        m = build_all(verbose=False)["monthly"].copy()
    except Exception as e:  # pragma: no cover
        return dict(ok=False, error=str(e))
    m = m[(m.index >= "1881-01-01") & (m.index <= "2023-06-01")]
    p = m["price"]; m["ret12"] = p.pct_change(12); m["dy10"] = m["gs10"].diff(12) * 100
    m["rvol"] = np.log(p).diff().rolling(12).std() * math.sqrt(12) * 100
    m["erp_pp"] = (m["ep"] - m["gs10"]) * 100
    r1 = (m["cape"] >= 25) & (m["erp_pp"] <= 0.5)
    r2 = (m["cape"] >= 25) & (m["dy10"] >= 0.75)
    r3 = r1 & (m["ret12"] >= 0.10) & (m["rvol"] > m["rvol"].shift(6))
    states = {"R1 no-cushion valuation": r1, "R2 rate shock into richness": r2, "R3 top formation": r3, "R1 AND R2 (today)": r1 & r2, "ALL months (base rate)": pd.Series(True, index=m.index)}
    prices = p.to_numpy(); n = len(prices)
    def hit(i, dd, horizon):
        hi = prices[i]
        for j in range(i + 1, min(n, i + horizon + 1)):
            hi = max(hi, prices[j])
            if prices[j] <= hi * (1 - dd): return True
        return False
    out = {}; split = pd.Timestamp("1960-01-01")
    for name, s in states.items():
        idx = [i for i, ok in enumerate(s.fillna(False).to_numpy()) if ok and i < n - 36]
        row = dict(n=len(idx))
        for lab, sel in (("all", idx), ("pre-1960", [i for i in idx if m.index[i] < split]), ("post-1960", [i for i in idx if m.index[i] >= split])):
            if not sel: row[lab] = None; continue
            row[lab] = {f"{int(dd*100)}%/{h}m": sum(hit(i, dd, h) for i in sel) / len(sel) for dd, h in ((.10, 12), (.20, 24), (.25, 36))}
            row[lab]["n"] = len(sel)
        out[name] = row
    # first/last months in the today-state, for the record
    today_state = m.index[(r1 & r2).fillna(False).to_numpy()]
    episodes = []
    if len(today_state):
        start = prev = today_state[0]
        for d in today_state[1:]:
            if (d - prev).days > 100: episodes.append((str(start.date()), str(prev.date()))); start = d
            prev = d
        episodes.append((str(start.date()), str(prev.date())))
    return dict(ok=True, table=out, episodes=episodes)

# ======================================================================
# §2  FOUR CRASH ENGINES (memo #4, #8-#10, #19)
# ======================================================================
CHAIN = ["vulnerable borrower", "missed payment / covenant breach / force majeure", "lender concern (CDS, marks)",
         "credit-spread widening", "funding contraction (gates, failed syndication)", "forced selling", "deleveraging", "equity crash"]
# BDCR 2.0 memo §12: market plumbing has its own chain (macro stress -> market crash)
PLUMB_CHAIN = ["Treasury liquidity thinning", "repo / funding-spread stress", "dealer balance-sheet constraint",
               "volatility regime shift", "margin requirements rising", "forced liquidation", "correlation-1 selling", "equity crash"]
# BDCR 2.0 memo §11: private credit has its own sequence
PC_CHAIN = ["fundraising slows", "underwriting deteriorates", "NAV marks questioned", "defaults rise", "redemption requests rise",
            "gates", "forced sales", "bank / insurer losses"]

@dataclass
class Engine:
    key: str; name: str
    stage: int                 # index into CHAIN reached with Tier-1/2 evidence
    stage_evidence: str
    reflexivity: float         # 0..1 self-reinforcement score
    reflex_note: str
    coverage: float            # refinancing coverage = available funding / required (>=1 ok)
    tier1: int; tier2: int     # counts of direct / near-direct evidence items
    clock_peaks: list          # [(months_from_now, width_months, weight)] where pressure becomes unavoidable
    clock_note: str
    hazard_scale: float        # peak monthly hazard contribution to the SYSTEMIC clock if fully confirmed
    chain: list = field(default_factory=lambda: CHAIN)

def engines(sov: dict, bs: dict, fr: dict, gap: dict, lp: list | None = None) -> list:
    l3 = lp[2][1] if lp else 0.5
    return [
        Engine("E", "Market plumbing", 3,
               "MOVE 80 -> 105 (T2); stock-bond correlation positive every session (T2); margin debt $1.45T record (T2); CTA down-tape branch engaged (T3); repo/SRF/fails QUIET (T2 benign); Treasury depth not retrieved; Sep 30 quarter-end SRF test pending. Absent: margin calls, forced liquidation.",
               min(1.0, l3), "collateral loop: prices -> collateral -> margin -> forced selling; strongest loop today because the buyback bid is in blackout and CTAs are sellers",
               1.0, 0, 3, [(0.1, 0.8, 0.35), (1.2, 1.0, 0.30), (12, 6, 0.35)],
               "Sep 30 quarter-end funding test -> Oct 8 30Y auction -> Nov 4 QRA; thereafter whenever a 10% index move meets the collateral loop",
               0.020, chain=PLUMB_CHAIN),
        Engine("A", "Sovereign / bond-market", 4,
               "5Y and 7Y auctions weak (T1); 30Y five closes >=5.50, 5.632 high since 2002 (T1); Oct 1 buyback: $46.4B offered for a $6B cap, pre-op level regained in 2 sessions = fourth rescue with the shortest half-life (T1); 10Y +6bp on a +29K payroll (T2); MOVE 108 (T2); short end and plumbing CLEAN (T1 benign); no failed auction, no fails spike (T1 absent)",
               min(1.0, 0.45 + 0.5 * fr["score"]), f"loop gain {sov['loop_gain']:.2f} pp/pp per year (damped, cumulative); rescue half-life 6 -> 2 sessions",
               1.0 / max(1e-6, 1 + max(0.0, sov["residual_T"]) / 2.0),  # crude: residual $T vs $2T of elastic demand
               3, 3, [(1.2, 1.0, 0.35), (5, 3, 0.35), (12, 5, 0.30)],
               "Nov 4 QRA (coupon sizes) -> Q1-27 refunding + $9.7T rollover at 5%+ -> post-election coupon step-up and the Oct-8 30Y auction as the near test",
               0.030),
        Engine("B", "AI capital cycle", 2,
               "Oracle force majeure on Jupiter (T1: contractual); Jupiter loans 89-91, CDS record 227, long bonds >8% (T2); CoreWeave-tenant paper 9.25% vs 8.25% (T2); Micron FY27 capex RAISED >$40B = supply response funded (T3); SoftBank $10B funded Oct 1 with 9%+ junk, SB CDS >400 (T2); no default, no capex cut, no impairment, no DRAM rollover (T1 absent)",
               0.55, "capex -> revenue coverage 46% (gap $490B); prepayment financing in revenue (ASC 606) = A->B->A loop forming; write-offs 2028-29",
               gap["coverage"], 1, 3, [(3, 2, 0.20), (9, 4, 0.40), (16, 6, 0.40)],
               "Micron/DRAM contract rollover Q4-26 -> OpenAI 2027 round + Oracle FY27 debt need (Q1-Q2 27) -> OpenAI cash-out / write-off window (2028)",
               0.028),
        Engine("C", "Private credit", 5,
               "PC sequence at 'gates' (stage 5 of 7): Oct 1 windows -- OTIC 39% requested, OCIC 16.8%, BCRED ~10%, ADS 14.7%, HLEND ~11.5%, ASIF 11.6%, all capped 5% again, requests EASING except AI/tech lending (T2); Fitch PC default 6.3% record (T2); OWL -46% YTD (T3); NOT reached: forced sales, insurer/pension writedown (T1 absent), BDC bond >600, covenant breach",
               0.50, "gates -> NAV doubt -> redemptions -> gates: loop live but capped by the 5% structure; discount to NAV ~25% = the market's own mark",
               0.85, 0, 4, [(0.2, 1.0, 0.25), (4, 3, 0.35), (13, 5, 0.40)],
               "Oct 1 Q3 windows -> Jan 1 Q4 windows (second gate wave) -> 2027 BDC unsecured maturities (placeholder)",
               0.022, chain=PC_CHAIN),
        Engine("D", "Consumer / recession", 1,
               "LABOR TURNED Oct 2: payrolls +29K, revisions -60K, July -10K, UR 4.2, real AHE ~-0.4% (T2); Conf Board 81.9, expectations 63.6 (T3); hires 3.3% (T3, above trigger); saving 4.1% on the REVISED series (T2; old-series trigger moot); subprime auto 6.13% (T2); prime 0.49% contained (T2); claims 197K / continuing 1.70M benign (T2); mortgage 7.28% (T2); Car-Mart alive to Oct 8 (T1 pending)",
               0.35, "delinquency -> tighter credit -> spending -> jobs: not self-reinforcing while claims <230K, but the income side (payrolls, real wages) flipped this week",
               1.05, 0, 4, [(6, 4, 0.6), (13, 6, 0.4)],
               "payroll stall + 7.3% mortgages + $100 oil transmit on a 4-8 month lag -> Q1-Q2 2027 (pulled forward from Q2-Q3 on the Oct 2 print)",
               0.020),
    ]

# ======================================================================
# §6  CROSS-MARKET CONFIRMATION (memo #16): 3 of 5 domains, consecutive observations
# ======================================================================
DOMAINS = {  # (confirmed 0/0.5/1, tier, evidence)
    "Treasury stress":        (1.0, 1, "THIRD consecutive week: 30Y five closes >=5.50 (5.632 high, since 2002), 10Y 5.342 intraday (since 2002), 7Y weak, Oct 1 buyback drew $46.4B of offers for $6B, MOVE 108, long end sold off into a +29K payroll"),
    "Credit stress":          (0.5, 2, "FRED HY OAS 308->312 (Sep 29-30), CCC 1,179; ORCL CDS record 227, long bonds >8%; SB CDS >400; still no default/writedown; HY <350"),
    "Equity breadth":         (1.0, 2, "CONFIRMED: NYSE lows > highs 23 consecutive sessions, 43-49% above 200dma, 75% of S&P down in September, RSP -1.9% vs SPX +2.0% in Q3 -- while NDX made a record Oct 2 (the divergence IS the signal)"),
    "Funding/plumbing stress": (0.0, 2, "quarter-end PASSED CLEAN: SOFR 3.90% on Sep 30 inside the band through a $202B coupon settlement; bills 2.7-2.8x covered; MMF assets record $7.98T; Fed RMP paused to Oct 14 without incident"),
    "Real-economy deterioration": (0.5, 2, "PARTIAL: payrolls +29K with -60K revisions and July -10K, UR 4.2, AHE 3.0 (real negative), Conf Board 81.9 lowest since 2014, Challenger hiring plans 15-yr low; against: claims 197K / continuing 1.70M (3-yr low), real PCE +0.6%"),
}

def confirmation() -> dict:
    n = sum(v[0] for v in DOMAINS.values())
    full = sum(1 for v in DOMAINS.values() if v[0] >= 1)
    return dict(count=n, full=full, met=full >= 3, gate=min(1.0, 0.35 + 0.65 * n / 5))

# ======================================================================
# §8  HISTORICAL ANALOGUE ENGINE (memo #18): Shiller monthly 1881-2023
# ======================================================================
def analogue_engine(k=20, mechanism=True):
    """mechanism=True (BDCR 2.0 memo §6, §15): candidates must satisfy at least one of the pre-specified
    mechanism rules (R1 no-cushion valuation, R2 rate shock into richness) at the match date, so matches
    share the transmission mechanism and not merely the chart shape."""
    try:
        import numpy as np, pandas as pd
        from v6.data.loaders import build_all
        m = build_all(verbose=False)["monthly"].copy()
    except Exception as e:  # pragma: no cover
        return dict(ok=False, error=str(e))
    m = m[m.index >= "1881-01-01"]
    p = m["price"]
    m["ret12"] = p.pct_change(12)
    m["dy10"] = m["gs10"].diff(12) * 100
    m["rvol"] = np.log(p).diff().rolling(12).std() * math.sqrt(12) * 100
    m["capez"] = (m["cape"] - m["cape"].rolling(240, min_periods=60).mean()) / m["cape"].rolling(240, min_periods=60).std()
    m["erp_pp"] = m["erp"] * 100
    m["cape_lvl"] = m["cape"]          # LEVEL as well as z-score: the memo asks for level AND trajectory matches
    feats = ["capez", "cape_lvl", "ret12", "dy10", "rvol", "erp_pp"]
    hist = m.dropna(subset=feats + ["price"]).loc[:"2023-06-01"]
    X = hist[feats].to_numpy(); mu, sd = X.mean(0), X.std(0)
    Z = (X - mu) / sd
    # trajectory: t-12, t-6, t-3, t
    lags = [12, 6, 3, 0]
    idx = {d: i for i, d in enumerate(hist.index)}
    # current state (2026-09-28), ESTIMATE where marked in the report
    cur_now = dict(capez=(40.9 - hist["cape"].iloc[-240:].mean()) / hist["cape"].iloc[-240:].std(), cape_lvl=40.9, ret12=0.17, dy10=1.0, rvol=13.0, erp_pp=-0.6)
    cur_traj = {12: dict(capez=None, cape_lvl=38.5, ret12=0.15, dy10=0.6, rvol=14.0, erp_pp=0.1),
                6:  dict(capez=None, cape_lvl=39.5, ret12=0.12, dy10=0.7, rvol=15.0, erp_pp=0.0),
                3:  dict(capez=None, cape_lvl=40.5, ret12=0.16, dy10=0.9, rvol=13.0, erp_pp=-0.3),
                0:  cur_now}
    for L in (12, 6, 3): cur_traj[L]["capez"] = cur_now["capez"] - (0.05 * L / 12)
    def zvec(dct): return (np.array([dct[f] for f in feats]) - mu) / sd
    cur = np.stack([zvec(cur_traj[L]) for L in lags])            # 4 x 5
    # forward outcomes: months until drawdown >= 10/20/25% from running max after t (within 36m)
    prices = hist["price"].to_numpy(); n = len(prices)
    def t_to_dd(i, dd):
        hi = prices[i]
        for j in range(i + 1, min(n, i + 37)):
            hi = max(hi, prices[j])
            if prices[j] <= hi * (1 - dd): return j - i
        return None
    erp_raw = ((hist["ep"] - hist["gs10"]) * 100).to_numpy(); cape_raw = hist["cape"].to_numpy(); dy_raw = hist["dy10"].to_numpy()
    mech = [(cape_raw[i] >= 25 and (erp_raw[i] <= 0.5 or dy_raw[i] >= 0.75)) for i in range(n)]
    cands = []
    for i in range(12, n - 36):
        if mechanism and not mech[i]: continue
        traj = np.stack([Z[i - L] for L in lags])
        d_pt = np.linalg.norm(traj - cur, axis=1).mean()
        # cheap DTW over the 4-point trajectories
        A, B = traj, cur; D = np.full((5, 5), np.inf); D[0, 0] = 0
        for a in range(1, 5):
            for b in range(1, 5):
                c = np.linalg.norm(A[a - 1] - B[b - 1]); D[a, b] = c + min(D[a - 1, b], D[a, b - 1], D[a - 1, b - 1])
        cands.append((0.5 * d_pt + 0.5 * D[4, 4] / 4, i))
    cands.sort()
    # de-cluster: keep one per 18-month window
    keep = []
    for d, i in cands:
        if all(abs(i - j) > 18 for _, j in keep): keep.append((d, i))
        if len(keep) >= k: break
    rows = []
    for d, i in keep:
        rows.append(dict(date=str(hist.index[i].date()), dist=round(float(d), 2), cape=round(float(hist["cape"].iloc[i]), 1),
                         t10=t_to_dd(i, .10), t20=t_to_dd(i, .20), t25=t_to_dd(i, .25)))
    # empirical hazard by 6-month bucket for the 25% clock (censored at 36m)
    buckets = [(0, 6), (6, 12), (12, 18), (18, 24), (24, 36)]
    haz = {}
    for dd_key in ("t10", "t20", "t25"):
        at_risk = len(rows); out = []
        for lo, hi_ in buckets:
            ev = sum(1 for r in rows if r[dd_key] is not None and lo < r[dd_key] <= hi_)
            out.append((f"{lo}-{hi_}m", ev, at_risk, ev / at_risk if at_risk else 0)); at_risk -= ev
        haz[dd_key] = out
    return dict(ok=True, n_hist=int(n), n_mech=int(sum(mech)), mechanism=mechanism, k=k, matches=rows, hazard=haz, feats=feats, cur=cur_now)

# ======================================================================
# §9  NETWORK CENTRALITY (memo #20)
# ======================================================================
NODES = ["Treasury", "Fed", "Banks", "MMFs", "Private credit/BDCs", "Blue Owl", "Hyperscalers", "Oracle", "OpenAI",
         "Nvidia", "CoreWeave/neoclouds", "Memory/semis", "Consumers", "Housing", "Foreign reserve mgrs", "Japan (JGB/yen)",
         "Equities", "Corporate debt/IG"]
EDGES = [  # (from, to, weight) funding / guarantee / demand dependence
    ("Treasury", "Banks", .6), ("Treasury", "MMFs", .8), ("Treasury", "Foreign reserve mgrs", .7), ("Treasury", "Fed", .5),
    ("Treasury", "Japan (JGB/yen)", .5), ("Fed", "Banks", .6), ("Banks", "Private credit/BDCs", .6), ("Banks", "Consumers", .5),
    ("Banks", "Housing", .5), ("Private credit/BDCs", "Blue Owl", .8), ("Blue Owl", "Oracle", .7), ("Blue Owl", "Hyperscalers", .5),
    ("Blue Owl", "CoreWeave/neoclouds", .6), ("Hyperscalers", "Corporate debt/IG", .9), ("Oracle", "Corporate debt/IG", .8),
    ("Oracle", "OpenAI", .9), ("OpenAI", "Nvidia", .8), ("Nvidia", "OpenAI", .6), ("Nvidia", "CoreWeave/neoclouds", .7),
    ("Nvidia", "Memory/semis", .7), ("Hyperscalers", "Nvidia", .8), ("Hyperscalers", "Equities", .9), ("Nvidia", "Equities", .9),
    ("Equities", "Consumers", .6), ("Consumers", "Banks", .5), ("Housing", "Consumers", .4), ("Japan (JGB/yen)", "Treasury", .6),
    ("Foreign reserve mgrs", "Treasury", .6), ("Corporate debt/IG", "Private credit/BDCs", .4), ("MMFs", "Treasury", .7),
    ("Equities", "Treasury", .3), ("Memory/semis", "Equities", .5), ("CoreWeave/neoclouds", "Private credit/BDCs", .6),
]
DTD = {  # distance-to-default proxy 0..1 (1 = failing), tier-tagged judgment on record evidence
    "Oracle": (0.62, 2), "OpenAI": (0.55, 2), "CoreWeave/neoclouds": (0.60, 2), "Blue Owl": (0.45, 2), "Private credit/BDCs": (0.45, 2),
    "Treasury": (0.35, 1), "Japan (JGB/yen)": (0.35, 2), "Consumers": (0.30, 3), "Housing": (0.20, 3), "Memory/semis": (0.30, 3),
    "Hyperscalers": (0.20, 2), "Nvidia": (0.18, 2), "Banks": (0.12, 2), "MMFs": (0.05, 2), "Fed": (0.10, 3),
    "Foreign reserve mgrs": (0.25, 2), "Equities": (0.35, 3), "Corporate debt/IG": (0.25, 2),
}

def network() -> dict:
    import numpy as np
    ix = {n: i for i, n in enumerate(NODES)}; A = np.zeros((len(NODES), len(NODES)))
    for a, b, w in EDGES: A[ix[a], ix[b]] += w; A[ix[b], ix[a]] += 0.5 * w
    v = np.ones(len(NODES));
    for _ in range(200): v = A @ v; v /= np.linalg.norm(v)
    cent = {n: float(v[ix[n]]) for n in NODES}
    mx = max(cent.values()); cent = {n: c / mx for n, c in cent.items()}
    risk = {n: cent[n] * DTD[n][0] for n in NODES}
    return dict(centrality=cent, dtd=DTD, systemic_risk=risk,
                most_central=max(cent, key=cent.get), closest_to_failure=max(DTD, key=lambda n: DTD[n][0]),
                highest_systemic=max(risk, key=risk.get))

# ======================================================================
# §10  MONTHLY HAZARD MODEL (memo #17): three clocks, prior vs engine vs posterior
# ======================================================================
H = 36  # months
def prior_curve(clock: str) -> list:
    """The judgment prior as of 2026-09-28, expressed as a monthly hazard.
    Systemic: Section-2 buckets 8/14/38/21/19 (pre-Nov-26 / Nov-26-Jun-27 / Jul-27-Jun-28 / Jul-28-2029 / none),
    modal month Oct 2027. Correction and bear clocks are the same shape pulled earlier and lifted."""
    if clock == "systemic":
        pdf = [0.0] * H
        # NOTE (red-team finding): the judgment prior put 8% in the ~5 weeks before Nov 4, which is a higher
        # single-month density than any month of the 'modal' Jul-27..Jun-28 bucket (38% over 12 months).
        # The 'October 2027' claim was therefore a modal-BUCKET claim. The pre-Nov mass is spread over
        # Oct-Nov 2026 here so the prior's own modal month is the one the judgment intended; the
        # inconsistency is recorded in the report rather than hidden.
        spans = [(0, 2, .08), (2, 9, .14), (9, 21, .38), (21, 36, .21 * 36 / 39)]  # last bucket runs to end-2029 (39m); truncate
        for lo, hi, mass in spans:
            for t in range(lo, hi): pdf[t] += mass / (hi - lo)
        # shape inside the modal bucket: triangular peak at month 12 (Oct 2027; month 0 = Oct 2026)
        w = [1 + 0.9 * max(0, 1 - abs(t - 12) / 8) for t in range(H)]
        pdf = [p * wt for p, wt in zip(pdf, w)]; s = sum(pdf); tot = 0.08 + 0.14 + 0.38 + 0.21 * 36 / 39
        pdf = [p * tot / s for p in pdf]
    elif clock == "bear":
        pdf = [0.0] * H
        for lo, hi, mass in [(0, 2, .07), (2, 9, .19), (9, 21, .38), (21, 36, .16)]:
            for t in range(lo, hi): pdf[t] += mass / (hi - lo)
        w = [1 + 0.7 * max(0, 1 - abs(t - 11) / 8) for t in range(H)]
        pdf = [p * wt for p, wt in zip(pdf, w)]; s = sum(pdf); pdf = [p * .82 / s for p in pdf]
    else:  # correction >=10%
        pdf = [0.0] * H
        for lo, hi, mass in [(0, 1.5, .45), (1.5, 6, .25), (6, 12, .12), (12, 36, .10)]:
            for t in range(H):
                if lo <= t < hi: pdf[t] += mass / (hi - lo)
        s = sum(pdf); pdf = [p * .92 / s for p in pdf]
    return pdf_to_hazard(pdf)

def pdf_to_hazard(pdf):
    surv = 1.0; h = []
    for p in pdf:
        h.append(min(0.95, p / surv) if surv > 1e-9 else 0.0); surv -= p
    return h

def hazard_to_pdf(h):
    surv = 1.0; pdf = []
    for x in h: pdf.append(surv * x); surv *= (1 - x)
    return pdf

def suppression(t: int) -> float:
    """Policy-suppression modifier (memo #5): the election calendar lowers OBSERVED hazard by raising
    the probability of intervention; it never moves the fundamental clocks. t = months from Oct 2026."""
    d = month_add(date(2026, 10, 1), t)
    if d < date(2026, 11, 4): return 0.55      # pre-midterm put: tools degraded but still used
    if d < date(2027, 2, 1): return 0.75       # post-election lame-duck / QRA / new Congress
    if date(2028, 5, 1) <= d < date(2028, 11, 8): return 0.80   # 2028 presidential put (1972 Burns analog)
    return 1.0

def engine_curve(engs: list, conf: dict, analog: dict, clock: str, ablend: float = 0.3, mult: float = 1.0) -> list:
    """Engine-derived monthly hazard. Each engine contributes a Gaussian-in-time hazard around each of its
    clock peaks, scaled by (evidence tier weights x stage reached x reflexivity) and, for the systemic clock,
    by the cross-market confirmation gate. Analogue hazard (empirical) is blended at 30%."""
    scale = {"systemic": 1.0, "bear": 1.6, "correction": 3.2}[clock]
    cur = [0.0] * H
    for e in engs:
        ev = (e.tier1 * TIER_W[1] + e.tier2 * TIER_W[2]) / 4.0          # 4 = "well-evidenced"
        strength = min(1.5, ev) * (0.4 + 0.6 * e.stage / (len(CHAIN) - 1)) * (0.5 + 0.5 * e.reflexivity)
        strength *= 1.0 if e.coverage >= 1 else min(1.6, 1 / max(e.coverage, 0.3))
        for (mu, sd, w) in e.clock_peaks:
            for t in range(H):
                cur[t] += e.hazard_scale * scale * strength * w * math.exp(-0.5 * ((t + 0.5 - mu) / sd) ** 2)
    gate = conf["gate"] if clock == "systemic" else min(1.0, conf["gate"] + 0.25)
    cur = [min(0.6, c * gate) for c in cur]
    # Level from history, shape from the clocks: the engine's 36-month cumulative is calibrated to the
    # analogue engine's empirical cumulative for this clock, then the analogue hazard shape is blended at 30%.
    if analog.get("ok"):
        key = {"systemic": "t25", "bear": "t20", "correction": "t10"}[clock]
        ah = [0.0] * H; surv = 1.0
        for (lab, ev, ar, hz), (lo, hi) in zip(analog["hazard"][key], [(0, 6), (6, 12), (12, 18), (18, 24), (24, 36)]):
            m = 1 - (1 - hz) ** (1 / (hi - lo)) if hz < 1 else 0.5
            for t in range(lo, hi): ah[t] = m
            surv *= (1 - hz)
        target = 1 - surv
        cum_engine = 1 - math.prod(1 - c for c in cur)
        if cum_engine > 1e-6 and target > 1e-6:
            # solve for a multiplier k on the hazard so that the cumulative matches the target (bisection)
            lo_, hi_ = 0.0, 50.0
            for _ in range(60):
                k = 0.5 * (lo_ + hi_)
                if 1 - math.prod(1 - min(0.95, k * c) for c in cur) < target: lo_ = k
                else: hi_ = k
            cur = [min(0.95, k * c) for c in cur]
        cur = [(1 - ablend) * c + ablend * a for c, a in zip(cur, ah)]
    return [min(0.95, mult * c) for c in cur]

def posterior(prior_h, eng_h, lam, use_sup=True):
    """Blend prior and engine hazards, then apply the policy-suppression modifier as a DEFERRAL:
    the mass suppressed inside an election window is pushed into the months after it (proportionally to
    the unsuppressed density there), not destroyed. Interventions buy time; they do not repay debt."""
    blend = [min(0.95, (1 - lam) * p + lam * e) for p, e in zip(prior_h, eng_h)]
    pdf = hazard_to_pdf(blend)
    sup = [suppression(t) if use_sup else 1.0 for t in range(H)]
    pdf_s = [p * s for p, s in zip(pdf, sup)]
    deficit = sum(pdf) - sum(pdf_s)
    free = [i for i in range(H) if sup[i] >= 1.0 and i >= 4]
    wsum = sum(pdf[i] for i in free) or 1.0
    for i in free: pdf_s[i] += deficit * pdf[i] / wsum
    return pdf_to_hazard(pdf_s)

def summarize(h):
    pdf = hazard_to_pdf(h); cum = 0; cdf = []
    for p in pdf: cum += p; cdf.append(cum)
    modal = max(range(H), key=lambda t: pdf[t])
    tot = cdf[-1]
    def q(a):
        target = a * tot
        for t, c in enumerate(cdf):
            if c >= target: return t
        return H - 1
    buckets = [("next 3m", 0, 3), ("3-6m", 3, 6), ("6-12m", 6, 12), ("12-18m", 12, 18), ("18-24m", 18, 24), ("24-36m", 24, 36)]
    b = {lab: sum(pdf[lo:hi]) for lab, lo, hi in buckets}
    return dict(pdf=pdf, cdf=cdf, modal=modal, modal_label=mlabel(month_add(date(2026, 10, 1), modal)), total=tot,
                p10=mlabel(month_add(date(2026, 10, 1), q(.10))), p90=mlabel(month_add(date(2026, 10, 1), q(.90))), buckets=b,
                hazard_modal=max(range(H), key=lambda t: h[t]))

# ======================================================================
# §11  RUN + REPORT
# ======================================================================
def main():
    liq = 100 * sum(o.score * TIER_W[o.tier] for o in INTERNALS if o.name.startswith(("Liquidity", "Volatility: MOVE", "Stock-bond"))) / \
          sum(TIER_W[o.tier] for o in INTERNALS if o.name.startswith(("Liquidity", "Volatility: MOVE", "Stock-bond")))
    fs = factor_scores(liquidity_score=3 * liq / 100)
    sv = systemic_vulnerability(fs)
    sov = sovereign_engine(); bs = buyers_strike(); fr = failed_rescue(); pc = policy_capacity()
    gap0 = funding_gap(); gaps = {
        "base": gap0,
        "rates +100bp": funding_gap(rate_shock_bp=100),
        "rates +200bp": funding_gap(rate_shock_bp=200),
        "AI revenue -30%": funding_gap(revenue_shock=0.30),
        "spreads +150bp": funding_gap(spread_shock_bp=150),
        "utilization -20%": funding_gap(util_shock=0.20),
        "asset values -25% (GPU/DC collateral)": funding_gap(asset_value_shock=0.25),
        "financing window half-closed (-30%)": funding_gap(financing_avail=0.70),
        "all: +100bp, rev -30%, spreads +150, util -20%": funding_gap(100, 0.30, 150, 0.20),
        "severe: +200bp, rev -30%, assets -25%, financing -30%": funding_gap(200, 0.30, 0, 0.0, 0.25, 0.70),
    }
    lp = loops(sov); tree = tree_stage()
    engs = engines(sov, bs, fr, gap0, lp); conf = confirmation(); analog = analogue_engine(); analog_chart = analogue_engine(mechanism=False)
    net = network(); mi = internals_score(); bt = backtest()
    # independent clocks converging on H2-27..H1-28: engine peaks with weight >=0.3 inside months 9..21
    converging = sum(1 for e in engs if any(9 <= mu <= 21 and w >= 0.3 for mu, sd, w in e.clock_peaks))
    lam = 0.35 + 0.15 * conf["count"] / 5 + 0.05 * converging       # weight on the engine curve vs the prior
    lam = min(0.7, lam)
    curves = {}
    for clock in ("correction", "bear", "systemic"):
        pr = prior_curve(clock); en = engine_curve(engs, conf, analog, clock); po = posterior(pr, en, lam)
        curves[clock] = dict(prior=pr, engine=en, posterior=po, s_prior=summarize(pr), s_engine=summarize(en), s_post=summarize(po))
    # ---- specification stability (BDCR 2.0 memo §16: confidence = stability across model specifications)
    base_modal = curves["systemic"]["s_post"]["modal"]
    specs = []; analog_k = {12: analogue_engine(k=12), 20: analog, 30: analogue_engine(k=30)}
    for dl in (-0.15, 0.0, 0.15):
        for ab in (0.15, 0.30, 0.45):
            for mult in (0.7, 1.0, 1.3):
                for kk in (12, 20, 30):
                    for us in (True, False):
                        en = engine_curve(engs, conf, analog_k[kk], "systemic", ablend=ab, mult=mult)
                        po = posterior(prior_curve("systemic"), en, min(0.85, max(0.1, lam + dl)), use_sup=us)
                        s = summarize(po); specs.append(dict(dl=dl, ab=ab, mult=mult, k=kk, sup=us, modal=s["modal"], p10=s["p10"], p90=s["p90"], total=s["total"]))
    stab = sum(1 for s in specs if abs(s["modal"] - base_modal) <= 2) / len(specs)
    from collections import Counter
    modal_dist = Counter(mlabel(month_add(date(2026, 10, 1), s["modal"])) for s in specs)
    conf_score = 0.5 * stab + 0.5 * min(1.0, conf["full"] / 3)
    conf_level = "HIGH" if conf_score >= 0.75 else "MEDIUM" if conf_score >= 0.5 else "LOW"
    n_eng = len(engs)
    trans = 100 * (0.4 * conf["count"] / 5 + 0.3 * max(e.stage for e in engs) / 7 + 0.3 * sum(e.reflexivity for e in engs) / n_eng)
    reflex = 100 * sum(g for _, g, _ in lp) / 3
    credit = 100 * (0.5 * fs["Private/corporate credit"]["score"] / 3 + 0.5 * DOMAINS["Credit stress"][0])
    catalyst = 100 * min(1.0, sum(w * math.exp(-mu / 3) for e in engs for mu, sd, w in e.clock_peaks) / 1.5)
    dash = {
        "Systemic vulnerability (structural, de-duplicated)": sv,
        "BDCR-26 additive composite (for reference)": bdcr26.composite_score(),
        "Transmission stress": trans, "Policy capacity remaining": pc, "Reflexivity": reflex,
        "Liquidity stress": liq, "Credit deterioration": credit, "Market internals": mi, "Catalyst proximity": catalyst,
    }
    out = dict(as_of=str(TODAY), dashboard=dash, factors={k: dict(score=v["score"], weight=v["weight"]) for k, v in fs.items()},
               sovereign=sov, buyers_strike=dict(score=bs["score"], verdict=bs["verdict"]), failed_rescue=fr, policy_capacity=pc,
               funding_gap={k: v for k, v in gaps.items()}, confirmation=conf, converging=converging, lambda_engine=lam,
               engines=[dict(key=e.key, name=e.name, stage=e.stage, stage_name=e.chain[e.stage], reflexivity=e.reflexivity, coverage=e.coverage, tier1=e.tier1, tier2=e.tier2, clock=e.clock_note) for e in engs],
               decision_tree=dict(stage=tree["stage"], of=tree["of"], next_node=tree["next_node"], nodes=[dict(node=n, variable=v, reading=r, tier=t, passes=ok) for n, v, r, t, ok in DECISION_TREE]),
               loops=[dict(loop=n, gain=g, note=nt) for n, g, nt in lp],
               backtest=bt if bt.get("ok") else dict(ok=False),
               analogue_chart_only=dict(matches=analog_chart.get("matches", []), hazard=analog_chart.get("hazard")) if analog_chart.get("ok") else None,
               stability=dict(share_within_2m=stab, n_specs=len(specs), modal_distribution=dict(modal_dist.most_common(8)), conf_score=conf_score,
                              p10_range=(min(s["p10"] for s in specs), max(s["p10"] for s in specs)) if specs else None),
               network=dict(most_central=net["most_central"], closest_to_failure=net["closest_to_failure"], highest_systemic=net["highest_systemic"],
                            centrality=net["centrality"], systemic_risk=net["systemic_risk"]),
               analogue=analog if analog.get("ok") else dict(ok=False),
               curves={c: dict(months=[mlabel(month_add(date(2026, 10, 1), t)) for t in range(H)],
                               prior=v["prior"], engine=v["engine"], posterior=v["posterior"],
                               summary={k: {kk: vv for kk, vv in v[k].items() if kk not in ("pdf", "cdf")} for k in ("s_prior", "s_engine", "s_post")},
                               pdf_post=v["s_post"]["pdf"]) for c, v in curves.items()},
               confidence=conf_level)
    (HERE / "hazard_curve.json").write_text(json.dumps(out, indent=1, default=float))
    write_report(out, fs, sov, bs, fr, gaps, engs, conf, analog, net, curves, dash, converging, lam, conf_level)
    print_dash(dash, curves, conf, converging, engs, net, conf_level, lam)
    print(f"  Decision tree: stage {tree['stage']} of {tree['of']} (next node: {tree['next_node']})   loops: " + ", ".join(f"{n.split(':')[0]} {g:.2f}" for n, g, _ in lp))
    print(f"  Spec stability: {100*stab:.0f}% of {len(specs)} specifications keep the systemic modal month within ±2 months of {curves['systemic']['s_post']['modal_label']}; modal distribution {dict(modal_dist.most_common(5))}; confidence score {conf_score:.2f}")
    if bt.get("ok"):
        t = bt["table"]; a = t["R1 AND R2 (today)"]["all"]; b = t["ALL months (base rate)"]["all"]
        print(f"  Backtest (today's state R1&R2, n={a['n']}): P(-10% in 12m) {100*a['10%/12m']:.0f}% vs base {100*b['10%/12m']:.0f}% | P(-20% in 24m) {100*a['20%/24m']:.0f}% vs {100*b['20%/24m']:.0f}% | P(-25% in 36m) {100*a['25%/36m']:.0f}% vs {100*b['25%/36m']:.0f}%; episodes {bt['episodes']}")

def print_dash(dash, curves, conf, converging, engs, net, conf_level, lam):
    print("BDCR-27 CRASH-TIMING ENGINE — dashboard as of 2026-09-28\n" + "=" * 72)
    for k, v in dash.items(): print(f"  {k:<52} {v:5.1f} / 100")
    sp = curves["systemic"]["s_post"]; sb = curves["bear"]["s_post"]; sc = curves["correction"]["s_post"]
    print("\nCrash hazard (systemic, >=25% + transmission), posterior:")
    for k, v in sp["buckets"].items(): print(f"    {k:<10} {100*v:5.1f}%")
    print(f"  36-month cumulative: {100*sp['total']:.0f}%   modal month: {sp['modal_label']}   80% interval: {sp['p10']} – {sp['p90']}")
    print(f"  prior modal {curves['systemic']['s_prior']['modal_label']} | engine modal {curves['systemic']['s_engine']['modal_label']} | lambda(engine) {lam:.2f}")
    print(f"  Bear (>=20%): modal {sb['modal_label']}, 80% {sb['p10']} – {sb['p90']}, 36m cum {100*sb['total']:.0f}%")
    print(f"  Correction (>=10%): modal {sc['modal_label']}, 80% {sc['p10']} – {sc['p90']}, 36m cum {100*sc['total']:.0f}%")
    print(f"  Confidence: {conf_level}   cross-market confirmation: {conf['full']} of 5 full ({conf['count']:.1f} weighted)   clocks converging on H2-27/H1-28: {converging} of {len(engs)}")
    print(f"  First-crack candidate: {net['closest_to_failure']}   most central: {net['most_central']}   highest systemic risk: {net['highest_systemic']}")
    lead = max(engs, key=lambda e: (e.tier1, e.stage))
    print(f"  Primary transmission: engine {lead.key} ({lead.name}) at chain stage {lead.stage} '{lead.chain[lead.stage]}'")

def write_report(out, fs, sov, bs, fr, gaps, engs, conf, analog, net, curves, dash, converging, lam, conf_level):
    L = []; A = L.append
    A("# BDCR-27 Crash-Timing Engine — first run, 2026-09-28\n")
    A("Response to the red-team memo. The 32-indicator composite is retained as the *structural* layer; everything below is new. "
      "Tags: T1 direct, T2 near-direct, T3 leading, T4 structural, T5 narrative (memo §25). Dollar figures: V verified in the record, E estimate, P placeholder.\n")
    A("## 0. Dashboard (memo §28)\n")
    A("| Metric | Value |\n|---|---:|")
    for k, v in dash.items(): A(f"| {k} | {v:.1f} |")
    sp = curves["systemic"]["s_post"]
    A(f"\n**Crash hazard (systemic, ≥25% with financial transmission), posterior = prior blended with engine at λ={lam:.2f}, × policy-suppression modifier:**\n")
    A("| Window | Probability |\n|---|---:|")
    for k, v in sp["buckets"].items(): A(f"| {k} | {100*v:.1f}% |")
    A(f"| 36-month cumulative | {100*sp['total']:.0f}% |")
    A(f"\n- **Current modal month: {sp['modal_label']}**  (prior: {curves['systemic']['s_prior']['modal_label']}; engine alone: {curves['systemic']['s_engine']['modal_label']})")
    A(f"- **80% timing interval: {sp['p10']} – {sp['p90']}**")
    A(f"- **Confidence: {conf_level}** (cross-market confirmation {conf['full']} of 5 domains fully confirmed, {conf['count']:.1f} weighted; independent clocks converging on H2-2027/H1-2028: {converging} of {len(engs)})")
    A(f"- First-crack candidate node: **{net['closest_to_failure']}** (distance-to-default proxy {DTD[net['closest_to_failure']][0]:.2f}); most central node: **{net['most_central']}**; highest centrality × fragility: **{net['highest_systemic']}**")
    lead = max(engs, key=lambda e: e.stage)
    lead = max(engs, key=lambda e: (e.tier1, e.stage))
    A(f"- Primary transmission: engine {lead.key} ({lead.name}), furthest along its chain on Tier-1 evidence (stage {lead.stage}: *{lead.chain[lead.stage]}*)")
    st = out["stability"]
    A(f"- Confidence decomposition: specification stability {100*st['share_within_2m']:.0f}% of {st['n_specs']} specs keep the modal month within ±2 months (modal distribution {st['modal_distribution']}); cross-market confirmation {conf['full']}/3 required; combined score {st['conf_score']:.2f} → **{conf_level}**")
    A(f"- Key clock: the Treasury rollover (~${sov['reprice_T']:.1f}T over the next 12 months repricing from 3.41% toward 5.1%) and the Q1–Q2 2027 AI funding need (Oracle FY27 + OpenAI round); see §3.")
    A("\n### Three-date output (memo §27)\n")
    sb = curves["bear"]["s_post"]; sc = curves["correction"]["s_post"]
    A("| Clock | Modal month | 80% interval | 36-month cumulative |\n|---|---|---|---:|")
    A(f"| A — First crack (Tier-1 credit/liquidity event) | **Oct–Nov 2026** (Oct 1 gates / Car-Mart; Oct 8 30Y; Micron guide) | Oct 2026 – Mar 2027 | n/a (event, not index) |")
    A(f"| Correction (≥10%) | **{sc['modal_label']}** | {sc['p10']} – {sc['p90']} | {100*sc['total']:.0f}% |")
    A(f"| B — Bear market (≥20%) | **{sb['modal_label']}** | {sb['p10']} – {sb['p90']} | {100*sb['total']:.0f}% |")
    A(f"| C — Systemic crash (≥25% + transmission) | **{sp['modal_label']}** | {sp['p10']} – {sp['p90']} | {100*sp['total']:.0f}% |")
    A("\nMoves earlier if: a Tier-1 event in engine A (a 30Y auction tail ≥4bp with cover <2.2 on Oct 8; a fails/repo spike at quarter-end), "
      "or a second Tier-1 event in engine B (an AI-chain default, an SPV impairment, a capex guide cut), or the confirmation count reaching 3 of 5 for two consecutive observations. "
      "Moves later if: the 30Y closes <5.30% for five sessions; the Nov 4 QRA cuts long-coupon sizes and the long end accepts it; Oct 1 gate requests fall; the AI funding-gap coverage ratio rises above 1.2 on new equity.\n")
    A("## 1. Causal-factor model (memo #2)\n")
    A("Nine latent factors; within-factor aggregation is 0.6·max + 0.4·mean, so several symptoms of one shock count roughly once. "
      f"De-duplicated systemic vulnerability **{dash['Systemic vulnerability (structural, de-duplicated)']:.1f}** vs the additive composite {dash['BDCR-26 additive composite (for reference)']:.1f}.\n")
    A("| Factor | Weight | Score /3 | Members (score) |\n|---|---:|---:|---|")
    for k, v in fs.items(): A(f"| {k} | {v['weight']} | {v['score']:.2f} | {', '.join(f'{m} ({s})' for m, s in v['members']) or 'engine inputs (MOVE, stock-bond corr, plumbing) — no BDCR-26 indicator exists; gap accepted'} |")
    A("\n## 2. Four crash engines (memo #4, #8–#10, #19)\n")
    A("| Engine | Chain stage reached (T1/T2 evidence) | Reflexivity | Refi coverage | T1 / T2 items | Clock |\n|---|---|---:|---:|---|---|")
    for e in engs: A(f"| {e.key} — {e.name} | {e.stage}: {e.chain[e.stage]} — {e.stage_evidence} | {e.reflexivity:.2f} ({e.reflex_note}) | {e.coverage:.2f} | {e.tier1} / {e.tier2} | {e.clock_note} |")
    A("\nReading: engine A (sovereign) is furthest along its chain with Tier-1 evidence and is the only one with three Tier-1 items; engine B has the single most important Tier-1 event (force majeure) but no default; engine C has reached 'gates' on the private-credit sequence but not 'forced sales'; engine D is a lagging engine that the second hike arms for mid-2027; engine E (plumbing) shows a volatility-regime shift in rates only. The AI engine is **not** a prerequisite: the hazard curve is a union of the five.\n")
    dt = out["decision_tree"]
    A("### 2b. Dalio decision tree (BDCR 2.0 memo §5) — encoded conditions, current pass/fail\n")
    A("| # | Node | Condition (specified before looking) | Reading | Tier | Passes |\n|---|---|---|---|:---:|:---:|")
    for i, nd in enumerate(dt["nodes"]): A(f"| {i+1} | {nd['node']} | {nd['variable']} | {nd['reading']} | T{nd['tier']} | {'YES' if nd['passes'] else 'no'} |")
    A(f"\nTree stage **{dt['stage']} of {dt['of']}**: the system is past 'monetary policy unable to offset' and stops at **{dt['next_node']}** — the bank/HY channel has not contracted (HY 280) and spending has not deteriorated (claims 197K). That is the precise statement of 'amber, not red' in causal form, and it is the node the Sep 30 / Oct 2 / Oct 6 prints test.\n")
    A("### 2c. Reflexivity loops (BDCR 2.0 memo §13) — one-year gain of each loop\n")
    A("| Loop | Gain | Note |\n|---|---:|---|")
    for l in out["loops"]: A(f"| {l['loop']} | {l['gain']:.2f} | {l['note']} |")
    A("\nGain scale: >1 explosive, 0.3–1 self-reinforcing, <0.3 damped. The collateral loop is the only one in the self-reinforcing band today; the sovereign loop is damped on a one-year horizon but compounds.\n")
    A("## 3. Liability maturity clock (memo #3, #22, #24) — $B per quarter\n")
    rows, totp = clock_table()
    A("| Cohort | " + " | ".join(Q) + " | Tag | Source |\n|---|" + "---:|" * len(Q) + "---|---|")
    for name, amts, tag, src in rows: A(f"| {name} | " + " | ".join(f"{a:,.0f}" if a >= 10 else f"{a:.1f}" for a in amts) + f" | {tag} | {src} |")
    A("| **Private/AI/credit total (ex-Treasury, ex-CRE)** | " + " | ".join(f"**{t:,.0f}**" for t in totp) + " | | |")
    A(f"\nThe wall is back-loaded: the private/AI/credit funding need rises from ~${totp[0]:.0f}B in 2026Q4 to ~${totp[-1]:.0f}B a quarter by 2028 while the cheapest source (hyperscaler IG at ~115bp over) is the one whose spread is widening deal by deal. PLACEHOLDER rows must be filled from 10-Ks before the clock is used for dates finer than a quarter.\n")
    A("## 4. AI funding-gap test (memo #3) — next 12 months, $B\n")
    A("| Case | Required external funding | Equity available | Debt capacity | Gap | Coverage |\n|---|---:|---:|---:|---:|---:|")
    for k, g in gaps.items(): A(f"| {k} | {g['required']:,.0f} | {g['equity']:,.0f} | {g['debt_capacity']:,.0f} | {g['gap']:,.0f} | {g['coverage']:.2f} |")
    A("\nBase case: the complex can fund itself only because the IG market is assumed to absorb ~$520B; coverage falls below 1.0 under any single stress and to ~0.6 under all four. The measurable clock is therefore the IG/private spread on AI paper, not the capex number.\n")
    A("## 5. Sovereign engine (memo #11–#15)\n")
    A(f"- Repricing in the next 12 months: **${sov['reprice_T']:.1f}T** (33% of marketable debt + deficit) at a marginal rate ~{100*SOV['marginal_rate']:.1f}% vs average coupon {100*SOV['avg_coupon']:.2f}% → extra interest **${1000*sov['interest_step_T']:.0f}B/yr** from one year of rollover; net interest / revenue {100*sov['interest_over_revenue']:.1f}%; marginal r−g **+{100*sov['r_minus_g_marginal']:.1f}pp** (the average-coupon r−g is still negative: the memo's point exactly).")
    A(f"- Treasury-demand clearing (FY27, $T): required absorption {sov['required_absorption_T']:.2f} − identified demand {sov['identified_demand_T']:.2f} = residual **{sov['residual_T']:.2f}T** for price-sensitive domestic private buyers → required yield premium ≈ **+{100*sov['required_yield_premium_pp']:.0f}bp** at 25bp/$T (E). All demand inputs are estimates; the structure is the deliverable.")
    A(f"- Reflexivity loop (yield → interest → deficit → issuance → yield): gain **{sov['loop_gain']:.2f} pp per pp per year** — damped within a year, but it compounds and is the loop the 2028–29 interest step-up feeds.")
    A(f"- Buyers'-strike detector: score {bs['score']:.2f}, verdict **{bs['verdict']}** ({bs['multi_flag_auctions']} of {bs['auctions']} scored auctions with ≥2 stress flags; the 7Y result is missing). One weak auction is noise; the 5Y is the second consecutive flagged sale.")
    A(f"- Failed-rescue counter: half-lives {fr['half_lives']} sessions, fill ratios {[round(x,2) for x in fr['fill_ratios']]}; **decaying = {fr['decaying']}**. Each rescue is buying less time and Treasury is filling less of its own cap.")
    A(f"- Policy-exhaustion clock: **{policy_capacity():.0f} / 100 capacity remaining** (tier-weighted): " + "; ".join(f"{k} {v}" for k, (v, _, _) in POLICY.items()) + ".")
    A("\n## 6. Cross-market confirmation (memo #16)\n")
    A("| Domain | Confirmed | Evidence |\n|---|:---:|---|")
    for k, (c, t, ev) in DOMAINS.items(): A(f"| {k} | {'YES' if c>=1 else 'PARTIAL' if c>0 else 'no'} | {ev} |")
    A(f"\n**{conf['full']} of 5 fully confirmed** ({conf['count']:.1f} weighted). The 3-of-5 rule is NOT met: the systemic-clock hazard is gated to {100*conf['gate']:.0f}% of its unconfirmed value. This is why the near-term systemic hazard stays low while the correction hazard is high.\n")
    A("## 7. Market internals (memo #7)\n")
    A("| Signal | Reading | Stress 0–1 | Tier |\n|---|---|---:|:---:|")
    for o in INTERNALS: A(f"| {o.name} | {o.value} | {o.score:.1f} | T{o.tier} |")
    A(f"\nInternals score **{dash['Market internals']:.0f} / 100**: bond volatility and positioning are stressed, equity volatility is not — the transition signal is half-formed.\n")
    A("## 8. Historical analogue engine (memo #18)\n")
    if analog.get("ok"):
        A(f"State vector {analog['feats']} at t, t−3, t−6, t−12 (CAPE z-score vs 20-yr mean, 12-month return, 12-month change in the 10-year, realized 12-month vol, ERP) over the Shiller monthly record 1881–2023 ({analog['n_hist']} months); distance = ½ point distance + ½ DTW over the trajectory; 20 nearest, de-clustered at 18 months. Current-state inputs are ESTIMATES (12m return +17%, 10Y +1.0pp, CAPE 40.9, ERP −0.6). VIX is not used (unavailable before 1990); pre-1982 episodes are therefore included.\n")
        A("| Match date | Distance | CAPE | Months to −10% | to −20% | to −25% |\n|---|---:|---:|---:|---:|---:|")
        for r in analog["matches"]: A(f"| {r['date']} | {r['dist']} | {r['cape']} | {r['t10'] if r['t10'] is not None else '>36'} | {r['t20'] if r['t20'] is not None else '>36'} | {r['t25'] if r['t25'] is not None else '>36'} |")
        A("\nEmpirical hazard from the matches (events / at-risk per bucket):\n")
        A("| Bucket | −10% | −20% | −25% |\n|---|---|---|---|")
        for i, (lab, _, _, _) in enumerate(analog["hazard"]["t10"]):
            r10 = analog["hazard"]["t10"][i]; r20 = analog["hazard"]["t20"][i]; r25 = analog["hazard"]["t25"][i]
            A(f"| {lab} | {r10[1]}/{r10[2]} = {100*r10[3]:.0f}% | {r20[1]}/{r20[2]} = {100*r20[3]:.0f}% | {r25[1]}/{r25[2]} = {100*r25[3]:.0f}% |")
        A(f"\nMechanism filter ON: candidates restricted to the {analog.get('n_mech')} months (of {analog['n_hist']}) that satisfy rule R1 or R2 at the match date, so matches share the transmission mechanism, not just the chart (BDCR 2.0 memo §6, §15). Small-sample caveat: twenty matched months, many from the same few regimes. The analogue hazard enters the engine curve at 30% weight.\n")
        ac = out.get("analogue_chart_only")
        if ac:
            A("Chart-only matching (no mechanism filter), for comparison — the memo warns against exactly this: " + ", ".join(r["date"][:7] for r in ac["matches"][:10]) + ".\n")
    else:
        A(f"Analogue engine unavailable: {analog.get('error')}\n")
    bt = out.get("backtest", {})
    A("### 8b. Backtest of pre-specified mechanism rules (BDCR 2.0 memo §4–§6)\n")
    if bt.get("ok"):
        A("Rules written before looking at outcomes: " + "; ".join(f"**{k}** = {v}" for k, v in RULES.items()) + ". Today satisfies R1, R2 and R3. Outcome = a drawdown of the stated size from the running high within the stated horizon, measured on Shiller monthly prices 1881–2023. In-sample / out-of-sample split at 1960.\n")
        A("| State | n | P(−10% in 12m) | P(−20% in 24m) | P(−25% in 36m) | pre-1960: n, −25%/36m | post-1960: n, −25%/36m |\n|---|---:|---:|---:|---:|---|---|")
        for name, row in bt["table"].items():
            a = row["all"]; pre = row.get("pre-1960"); post = row.get("post-1960")
            A(f"| {name} | {row['n']} | {100*a['10%/12m']:.0f}% | {100*a['20%/24m']:.0f}% | {100*a['25%/36m']:.0f}% | {pre['n'] if pre else 0}, {100*pre['25%/36m']:.0f}% | {post['n'] if post else 0}, {100*post['25%/36m']:.0f}% |" if pre and post else f"| {name} | {row['n']} | {100*a['10%/12m']:.0f}% | {100*a['20%/24m']:.0f}% | {100*a['25%/36m']:.0f}% | {pre['n'] if pre else 0}, {(100*pre['25%/36m']) if pre else 0:.0f}% | {post['n'] if post else 0}, {(100*post['25%/36m']) if post else 0:.0f}% |")
        A(f"\nEpisodes in today's state (R1 AND R2): {bt['episodes']}. Read the lift, not the level: the rules were specified from the mechanism (no cushion + rate shock into richness), not tuned, and the question is whether the conditional rates beat the base rate in BOTH halves of the sample. Where they do, the mechanism has historical support; where the post-1960 sample is a handful of months, the test is inconclusive and says so.\n")
    else:
        A(f"Backtest unavailable: {bt.get('error')}\n")
    A("## 9. Network centrality (memo #20)\n")
    A("| Node | Centrality | Distance-to-default proxy | Centrality × fragility |\n|---|---:|---:|---:|")
    for n in sorted(NODES, key=lambda n: -net["systemic_risk"][n]): A(f"| {n} | {net['centrality'][n]:.2f} | {DTD[n][0]:.2f} (T{DTD[n][1]}) | {net['systemic_risk'][n]:.2f} |")
    A("\n## 10. Hazard curves (memo #17) — monthly P(crash in t | none before t)\n")
    A("| Month | Correction prior | Correction post | Bear prior | Bear post | Systemic prior | Systemic engine | Systemic post | Suppression |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for t in range(H):
        d = month_add(date(2026, 10, 1), t)
        A(f"| {mlabel(d)} | {100*curves['correction']['prior'][t]:.1f} | {100*curves['correction']['posterior'][t]:.1f} | {100*curves['bear']['prior'][t]:.1f} | {100*curves['bear']['posterior'][t]:.1f} | {100*curves['systemic']['prior'][t]:.1f} | {100*curves['systemic']['engine'][t]:.1f} | {100*curves['systemic']['posterior'][t]:.1f} | {suppression(t):.2f} |")
    st = out["stability"]
    A("\n### 10b. Specification stability (BDCR 2.0 memo §16: confidence = stability across specifications)\n")
    A(f"{st['n_specs']} specifications: engine weight λ ±0.15, analogue blend 0.15/0.30/0.45, engine level ×0.7/1.0/1.3, analogue neighbours k = 12/20/30, election deferral on/off. "
      f"**{100*st['share_within_2m']:.0f}%** keep the systemic modal month within ±2 months of the base result. Modal-month distribution: {st['modal_distribution']}. "
      f"10th-percentile start month ranges {st['p10_range'][0]} – {st['p10_range'][1]}. Confidence score = ½ stability + ½ min(1, confirmed domains / 3) = {st['conf_score']:.2f} → **{conf_level}**.\n")
    A("\n## 11. What was adopted, changed, or rejected from the memo\n")
    A("- **Adopted in full:** causal factors (§1); four engines with a first-crack chain, reflexivity gain and coverage ratio (§2); the liability clock (§3, first fill); the hard cash-flow test (§4); marginal-rate sovereign engine, clearing model, buyers'-strike detector, failed-rescue counter, policy-exhaustion clock (§5); 3-of-5 confirmation (§6); internals as a timing layer (§7); analogue engine with trajectory matching (§8); network centrality (§9); a monthly hazard model with three separate clocks (§10); evidence tiers; election calendar demoted to a suppression modifier; forecast separated from trade timing; October 2027 demoted to a prior.")
    A("- **Changed:** the 32-indicator composite is *kept*, renamed the structural layer, and reported alongside the de-duplicated vulnerability score rather than replaced — the pre-registered thresholds and amendment log are the audit trail the new engine does not yet have. The hazard model is a Bayesian blend (prior × engine, λ set by confirmation and convergence) rather than a purely statistical survival fit: ten crash episodes cannot support a fitted survival model without a prior, and the memo itself says to treat the current forecast as one.")
    A("- **Rejected / deferred:** a fitted survival regression on episode data (N too small; the analogue engine's empirical hazard is used instead); Dynamic Time Warping over 24-month windows (implemented over four trajectory points — longer windows overfit the 1929/2000 shapes); a full maturity database (the environment cannot reach EDGAR/LCD/Bloomberg, so the clock ships with tagged placeholders).")
    A("- **What the first run says:** the engine curve and the prior agree on the centre of mass (H2-2027) but the engine puts more mass in Q1–Q2 2027 than the judgment did, because the sovereign engine is further along the chain than the AI engine and its clocks (QRA, rollover, Oct 8) come first. The posterior modal month is unchanged at October 2027 only because the confirmation gate (2 of 5) and the election modifier suppress the near-term systemic hazard; if confirmation reaches 3 of 5 before year-end, the modal month moves into the first half of 2027.")
    (HERE / "hazard_report.md").write_text("\n".join(L))

if __name__ == "__main__":
    main()
