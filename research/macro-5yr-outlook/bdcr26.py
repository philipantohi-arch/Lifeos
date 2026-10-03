#!/usr/bin/env python3
"""
BDCR-26 — US Big Debt Cycle Regime Algorithm
=============================================

A 32-indicator, 7-pillar mechanical implementation of Ray Dalio's
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

Baseline readings as of 2026-07-28; RE-SCORED 2026-09-10, 09-16, 09-22, 09-28 and 10-02 (see RE-SCORE LOGS at end) (sources in each
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
        6, "[Sep-16] net interest >$1T FY26 (AAF, Aug MTS); ratio ~19-20% | ~18.6% FY26 ($857B net interest in 9mo, +13% y/y)", 3,
        "Interest now exceeds defense AND Medicare; the debt compounds on itself"),
    Indicator(
        "Deficit % of GDP", "1. Fiscal",
        "FRED FYFSGDA188S; CBO Monthly Budget Review",
        "0:<3 (Dalio's 3% solution) | 1:3-5 | 2:5-7 | 3:>=7",
        6, "[Oct-2] CR to Dec 11 SIGNED (no shutdown); TGA ~$984B Sep 30 (vs $950B assumed); IEEPA refunds ~$122B certified, CAPE phase 3 Oct 6; FY26 closed ~$2.1T (~6.6% GDP); Q2 GDP revised up to 2.2% improves the denominator marginally. Held 2 | [Sep-28] CR to Dec 11 passed the House 370-48; IEEPA refunds ~$122B disbursed and tapering; FY26 closes Sep 30 at ~$2.1T (~6.6% GDP). Held 2 (3 requires >=7%) | [Sep-22] CBO lifts FY26 to $2.1T on a ~$250B tariff shortfall (~6.6% GDP); IEEPA refunds $135B paid | [Sep-16] FYTD (11mo) $2.0T, ~6.3-6.5% GDP; CR funds govt to Dec 11 | 5.8-6.1% (FY26 tracking $1.9-2.0T; tariff offset gutted by SCOTUS IEEPA ruling)", 2,
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
        4, "[Oct-2] BEAR-STEEPENING on weak data: 2Y 4.92 -> 4.84 while the 10Y held 5.28-5.30 and the 30Y 5.63; 2s10s ~32 -> ~44bp in a week as the October hike was priced out -- a long end that does not rally on a +29K payroll is term premium by construction. ACM/Kim-Wright still not retrievable; 0.5-1.0 band assumed intact. Held 2; -> 3 if ACM prints >=1.0 or 2s10s >60bp with the 2Y falling | [Sep-28] 10Y 5.17% close Sep 25 / 5.23% intraday Sep 28 (highest since June 2007); 2Y 4.81-4.90 (highest since 2023); 2s10s flattest of the year (~31bp Sep 24) then +36bp; ACM/Kim-Wright TP still not retrieved -- the 2Y moved almost as much as the 10Y, so the rise is largely expected-path, not term premium. Held 2 | [Sep-16] 10Y 5.008% post-FOMC (intraday >5.04%, highest since 2007); ACM TP not retrieved — score held | 0.73% (Jul 2026) — highest since 2014 after a decade near zero", 2,
        "The restored price of supply outrunning price-insensitive demand"),
    Indicator(
        "Auction stress composite", "2. Supply/Demand",
        "TreasuryDirect results: tails vs when-issued, bid-to-cover, dealer takedown",
        "0:none | 1:occasional | 2:>=6 serial tails OR dealer 2x norm | 3:tail>=4bp & BTC<2.2 at 10/30Y",
        5, "[Oct-2] 7Y (Sep 24) $44B at 5.085% (vs 4.512% in Aug), ~3bp above WI, BTC 2.42, indirects 57.2%, dealers 12.5% = 'below average'; 5Y tail now reported as 0.7bp by one outlet vs 3.1bp carried (CONFLICT; indirects 61.6% from 74.9% agree it was weak); Oct 1 bills covered 2.7-2.8x and SOFR 3.90% at quarter-end = the SHORT end is fine. Serial belly weakness continues (2Y average, 5Y weak, 7Y weak); no >=4bp tail with BTC <2.2 at the 10/30Y. Oct 7 $39B 10Y and Oct 8 $22B 30Y reopenings are the test. Held 2 | [Sep-28] Sep 23 $70B 5Y auction stopped 5.033% (first >5% since 2007): 3.1bp TAIL, bid-to-cover 2.21 -- the closest any auction has come to the 3-clause (needs >=4bp tail AND BTC <2.2 at the 10Y/30Y; this was the 5Y). 7Y (Sep 24) result not retrieved. Oct 8 30Y auction is the test. Held 2 | [Sep-22] 2Y auction 4.787% (highest since 2024), 0.2bp tail, indirects 57.8% (from 66%), dealers 13.2% (highest since Mar); 20Y Sep 15 stopped 5.42%; no >=4bp tail | [Sep-10] Score rests on the '>=6 consecutive tails in any tenor' clause: 5Y tail streak continued (Aug 26 +0.2bp). NOT on the 10Y: Sep 9 10Y BTC 2.71 (best since 2019), dealers 4.3%, stop-through — demand clears at a higher price. No failed-adjacent auction", 2,
        "Bifurcated demand: belly buyers' strike vs record indirects at the long end"),
    Indicator(
        "Foreign official demand", "2. Supply/Demand",
        "Treasury TIC major-holders + official/private split",
        "0:official buying >$100B/y | 1:flat | 2:official selling, private offset | 3:broad selling >$300B/y",
        3, "[Oct-2] Japan: MOF weekly (wk to Sep 26) net SOLD JPY684.5B of foreign bonds; Aug intervention dollars came via the Fed's FIMA repo (borrowing against USTs, not outright sales) -- the Sep-10 rule holds: intervention-funded flows are not scored as new stress; Katayama + Bessent jointly call the yen 'undervalued' (Sep 29) = intervention risk live; JGB 10Y 3.11%, 30Y ~4.21%. Oct 1 USTs rallied on FRENCH haven flows (OAT-Bund widest since 2012) -- foreign demand still arrives, episodically and at a price. Aug TIC ~Oct 16. Held 2 | [Sep-28] Xi-Trump summit (Sep 24-25): truce extended ~2 months to early 2027, tariff cuts on ~$30B of goods, purchase pledges -- no Treasury-holdings language; Trump reportedly flagged yen weakness to Takaichi (Sep 22/25); JGB 30Y 4.13%, 10Y 3.06% (since 1996) keeps Japanese repatriation risk live; Aug TIC due mid-Oct. Held 2 | [Sep-22] July TIC: holdings -$50.4B to $9.25T (Japan -$12.8B, 3rd straight); LT flows: PRIVATE net sellers -$3.7B, official net buyers +$44.4B (intervention-funding pattern, per the Sep-10 rule not scored as new stress). Held 2 | Official SOLD $39.9B May-26; China $652B (-$113B y/y); private +$172B offset", 2,
        "Dalio Stage-4 marker: owned demand replaced by rented (levered basis-trade) demand"),
    Indicator(
        "30Y yield stress level", "2. Supply/Demand",
        "FRED DGS30",
        "0:<4.5 | 1:4.5-5.0 | 2:5.0-5.5 | 3:>=5.5% (forced-intervention zone)",
        4, "[Oct-2] The ORIGINAL >=5.5% CLOSE rule is now CONFIRMED independently of the amendment: every 30Y close this week >=5.50 (Sep 28 5.56, Sep 29 5.585, Sep 30 5.632 = highest since 2002, Oct 1 5.613, Oct 2 ~5.63); 10Y intraday 5.342% Sep 30 (highest since Apr 2002), close 5.28 Oct 2 after a 6bp payroll rally fully reversed within hours. Oct 1 buyback: FULL $6B accepted of $46.4B offered (7.7x; Sep ops ~$10.5B) in two 2041-42 issues at 67-76c -- holders want out; the 30Y regained its pre-op level within 2 sessions (fourth rescue, shortest half-life yet). Cap unchanged at $6B to Nov 4. Score 3 on both routes; reversion rule (5 closes <5.30) unchanged | [Sep-28 UPGRADE 2 -> 3 under the Sep-10 amendment's intervention-fails clause] Treasury's 20-30Y buyback Sep 24 took $4.08B of a $6B cap ($10.47B offered) with the 30Y at 5.44-5.50% intraday; two sessions later (Sep 28) the 30Y traded 5.56% (CNBC intraday; highest since 2004) -- yields at/above the pre-intervention level within 5 sessions = the clause as written. Also: Sep 23 ~5.40% close (highest since 2004), Sep 24 intraday 5.501%, MOVE 80 -> 104.6 (Sep 24). The original >=5.5% CLOSE rule is NOT yet confirmed (Sep 25/28 closes not retrieved; one source has Sep 24 at 5.438%) -- flagged. Reverts to 2 if the 30Y closes <5.30% for 5 sessions | [Sep-22] 5.29% (high close 5.33% Sep 18; 20Y 5.39% Sep 16); 10Y back to 4.95-4.97% on oil; 2s10s ~20bp (bear-flattening). Amendment clauses still unmet (no 5 closes >5.40; ops $4-6B; Fed hiking; the Sep-10 op's pre-op level was regained only on session 6). Held 2 | [Sep-16] 5.25% last verified (Sep 15); ~5.35-5.40 implied by 10Y 5.01 + 30-37bp 10s30s (5.37% headline UNVERIFIED). Amendment clauses: >5.40 x5 sessions NO; buybacks >$10B/op NO ($4-6B); Fed duration NO; intervention-fails clause NOT met on the 30Y itself (5.31 pre-op -> 5.25). Held at 2 | [Sep-10] 5.31% (2007 high; 5.33% Aug-18 peak) after TWO Treasury buyback escalations (Aug 19 $4B/op, Sep 9 $6B/op) each retraced within sessions. WATCH: score held at 2 under the unamended >=5.5% rule; see prospective amendment in log", 3,
        "The long end is where repression regimes break (US-1951, UK-1976, Japan-2025)"),

    # ------------------------------------------------------------------
    # PILLAR 3 — MONETARY / INFLATION (weight 13)
    # ------------------------------------------------------------------
    Indicator(
        "Core PCE y/y", "3. Monetary",
        "FRED PCEPILFE",
        "0:<2.5 | 1:2.5-3.0 | 2:3.0-4.0 | 3:>=4.0%",
        4, "[Oct-2] Aug core PCE 3.0% y/y (July revised 3.3 -> 3.0 by the annual deflator update: software/portfolio-fee methodology, ~-0.15 to -0.18pp; a methodology artifact, not disinflation); headline 3.4%; ISM prices paid 77.9 (highest since the Iran war began); Q2 GDP revised 1.5 -> 2.2%. 3.0 sits ON the band-2 floor [3.0, 4.0) -> held 2; reverts to 1 only on a print <3.0 with the methodology effect excluded | [Sep-28] Aug PCE + saving rate + Q2 GDP third estimate + annual revision all land Sep 30; gasoline $4.49 (record for late Sept) and Brent back to $105-107 after the Iran plan was rejected; Barr: inflation 'not clearly trending toward target'. Held 2 pending the print | 3.4% (May-26, m/m highest since Oct-23); headline PCE 4.1%", 2,
        "Tariff pass-through (+0.8pp per Dallas Fed) + Hormuz oil = classic wave one"),
    Indicator(
        "Inflation expectations (survey vs market)", "3. Monetary",
        "UMich 5-10yr; FRED T10YIE; +1 notch if survey-market gap >1pp",
        "0:<2.9 | 1:2.9-3.2 | 2:3.2-3.5 or gap>1pp | 3:>=3.5 or breakeven>2.8",
        3, "[Oct-2] UMich 5-10y FINAL 3.4% (one tick from the 3.5 trigger), 1y 4.6%; Conference Board 12-m expectations 6.1% avg / 5.1% median, confidence 81.9 (lowest since 2014), expectations 63.6; 10Y breakeven ~2.3-2.4% (TIPS 2.89 vs 10Y 5.23) = survey-market gap >1pp persists. Held 2 | [Sep-28] UMich final 48.1 (prelim 47.8), 1y 4.6%, 5-10y final NOT retrieved (prelim 3.4 = one tick from 3.5); flash PMI price components hot (Sep 23); Brent reversed back to $105-107 (Sep 28). Held 2 | [Sep-22] Philly Fed prices paid 48.6; CFO survey +4.1% planned price increases; UMich final Sep 25; Brent -10% to ~$97 eases the impulse | [Sep-16] UMich 5-10y 3.4% (one tick from the 3.5 trigger), 1y 4.6%; import prices +7.0% y/y, PPI 5.4%; breakeven not retrieved | UMich 5-10y 3.3%, 1y 4.2%; 10Y breakeven anchored 2.28% — ~1pp gap", 2,
        "Households de-anchored, market not: the breakeven following is THE tell"),
    Indicator(
        "Fed independence stress", "3. Monetary",
        "Event index: removals/litigation (Trump v. Cook), probes, confirmation margins",
        "0:none | 1:rhetoric | 2:attempted removals/probes/accord machinery | 3:commanded easing",
        4, "[Oct-2] Trump: Powell 'should be forced to resign' from the Board (Sep 30, after the Fed IG found no misconduct on the renovation) = continued pressure, no removal action, no commanded easing. Payrolls +29K (revisions -60K, July now -10K), UR 4.2%, AHE 3.0%: Oct hike odds collapsed to ~17% (from ~36% a week earlier, 72% on Sep 28); December still the base case per the SEP; no removal action, no commanded easing. The hike cycle may be over on data, not on pressure -> held 2 | [Sep-28] Oct hike odds 55% -> 72% (CME, Sep 28) after Barr ('out of position', 'further adjustments likely needed') and Musalem; the Fed is tightening INTO the president's 1%-rates demand with no removal action -- the firewall is functioning, so no 3. Held 2 | [Sep-22] Trump: rates 'should be 1% or less', board 'very hostile... political', told Warsh to 'vote with the board'; no removal action; Barr seen as next target; Fed speakers (Collins, Goolsbee, Musalem, Barkin) all keep hikes on the table; Oct hike ~55% | [Sep-16] Fed HIKED 25bp 12-0 (incl. Cook) despite Trump 'clowns' / 'I won't allow that' / trade-halt threats — independence functioning; pressure at 2, not 3 (no commanded easing) | Cook firing blocked 5-4; criminal probe of a Fed chair; Warsh confirmed 54-45 — but FOMC is HIKE-biased", 2,
        "The firewall held by one vote; board tilts through 2028"),
    Indicator(
        "Monetization & real-rate stance (Stage-5 GATE)", "3. Monetary",
        "Real EFFR (EFFR - PCEPILFE); H.4.1 composition (bills vs coupons vs YCC)",
        "0:real>=+1%, no buys | 1:0-1%, bills-only | 2:real<0 w/ PCE>3 OR coupon QE | 3:YCC / real<-1% + QE",
        2, "[Oct-2] Oct hike ~17% after the +29K payroll; real EFFR vs core PCE 3.0 = ~+0.9% (revised core flatters it); RMPs bills-only; Treasury buybacks $4-6B/op, TGA ~$984B (no TGA drawdown for buybacks found); CR to Dec 11 signed. Gate CLOSED; the first gate test now moves to the Oct 27-28 statement language (a hold with easing bias into 3.4% headline = Burns proximity, not the gate) | [Sep-28] Oct hike 72% priced (a second hike in 2027 implied by the 2Y at 4.90%); real EFFR ~+0.4-0.5%; Treasury's Sep 24 20-30Y buyback UNDER-filled ($4.08B of $6B) -- the fiscal side did not chase the market either; Fed duration purchases zero. Gate CLOSED and, if anything, further from opening | [Sep-22] Oct 27-28 hike priced ~55%, Dec ~90%; real EFFR ~+0.4%; RMPs zero this cycle; Treasury still buying long end ($4-6B/op, next sizing at Nov 4 QRA). Gate CLOSED | [Sep-16] Fed hiked to 3.75-4.00%, median one more 2026 hike; real EFFR ~+0.3-0.5%; bills-only RMPs. Gate more firmly CLOSED; Treasury still buying duration ($4-6B/op) — pre-Accord conflict persists | [Sep-10] Fed: real EFFR ~+0.3%, bills-only, ~59% priced to HIKE Sep 16 = affirmative evidence AGAINST the gate. Treasury buying duration ($6B/op, bill-funded 'Treasury Twist') counts toward 30Y stress (market forcing fiscal action) but NOT toward this gate, which requires the FED to accommodate: documented trigger = Fed duration purchases or a formal cap", 1,
        "THE gate indicator: Dalio Stage 5 has demonstrably NOT begun — the key 'not yet'"),

    # ------------------------------------------------------------------
    # PILLAR 4 — MARKET FRAGILITY (weight 12)
    # ------------------------------------------------------------------
    Indicator(
        "Shiller CAPE", "4. Fragility",
        "Shiller/Yale (multpl.com)",
        "0:<25 | 1:25-32 | 2:32-40 (>1929's 32.6) | 3:>=40 (only Dec-1999's 44.2 higher)",
        5, "[Oct-2] S&P 7,726 (-0.9% from the Aug 26-27 record), NDX NEW RECORD close 30,808 (Oct 2) on the soft payroll, NVDA record $234 (~$5.6T); breadth the worst seen at a near-record index: NYSE new lows > new highs 23 straight sessions, 43-49% above the 200dma, 75% of the S&P fell in September, RSP -1.9% in Q3 vs SPX +2.0%. CAPE ~40-41 unchanged -> 3 | ~40.9 (live 40.6-40.9, Jul 2026); Buffett indicator 234% of GDP (record; dot-com peak 172%)", 3,
        "From CAPE 41 the base rate is ~0%/yr real 10-yr returns; 1966-82 is the template"),
    Indicator(
        "Equity risk premium", "4. Fragility",
        "S&P fwd E/P minus FRED DGS10",
        "0:>=+3pp | 1:+1-3 | 2:0-1 | 3:<=0",
        3, "[Oct-2] 10Y 5.29% close (intraday high 5.34%, highest since 2002) vs fwd E/P ~4.45-4.65% at S&P 7,726 = -0.65 to -0.85pp, a new cycle low; the 10Y ROSE 6bp on a +29K payroll (bonds refused the dovish read). Stays 3 | [Sep-28] 10Y 5.17% close (Sep 25) / 5.23% intraday (Sep 28) vs fwd E/P ~4.45-4.65% at S&P 7,743 = -0.5 to -0.8pp: the most negative reading of the cycle; stock-bond correlation positive on every session of the week (bonds not hedging). Stays 3 | [Sep-22] 10Y 4.95-4.97% (>4.85 revert line) vs fwd E/P ~4.45-4.65% at S&P 7,776 = -0.3 to -0.5pp. Stays 3 | [Sep-16] 10Y 5.008% vs fwd E/P 4.55-4.85% (21-22x fwd carried from Jul; S&P ~7,600) = -0.45 to -0.15pp; midpoint -0.3 -> band 3. Single-input change (10Y). REVERTS to 2 if 10Y <4.85% or fwd P/E <20x. Was: straddled zero at 10Y 4.63", 3,
        "Zero cushion: term-premium shocks transmit one-for-one into multiples"),
    Indicator(
        "Credit complacency/stress (two-sided)", "4. Fragility",
        "FRED BAMLH0A0HYM2 / BAMLC0A0CM; private-credit true-default indices",
        "0:HY 350-500 | 1:300-350/500-600 | 2:<300 (complacency) or 600-800 | 3:>800 or PC defaults>6%",
        4, "[Oct-2 DOWNGRADE 2 -> 1 under the written threshold] FRED BAMLH0A0HYM2 (this indicator's declared series) printed 308bp Sep 29 / 312bp Sep 30: the '<300 complacency' clause no longer holds and no stress band is reached -> band 1 (300-350). Caveat: the Bloomberg 2%-capped HY index sits at 294 and the readings carried since Sep 10 (265-280) appear to have mixed series; on a consistent FRED basis the Sep 22 reading was likely ~290. Private credit: Fitch 6.3% record, all gates repeat 5% (OTIC 39% requested; BCRED ~10%; ADS 14.7%; HLEND ~11.5%), no insurer writedown / BDC bond >600 / covenant breach; CCC 1,179bp. The two-sided design scores a normalizing spread as benign even while private-credit defaults sit above the original 3-clause -- PROSPECTIVE AMENDMENT logged: score = max(spread band, private-credit band) from the next review | [Sep-28] HY OAS 268 -> 280bp (first widening since the Sep 16 hike; CCC 1,112bp); SoftBank priced the largest junk deal ever ($11.1B, sub-10%) to wire $10B to OpenAI Oct 1; CoreWeave-tenant DC paper 9.25% (+270bp vs comps) vs Meta-tenant 8.25% five days earlier -- the AI credit curve is tiering by tenant. No insurer/pension writedown, BDC bond >600, covenant breach, or HY >500. Oct 1 gate/redemption notices ahead. Held 2 | [Sep-22] HY OAS 268bp; Fitch private-credit TTM default 6.3% (record, from 6.1%); ALL tracked perpetual BDCs capped at 5% in 2Q; OBDC marked Loparex ~5c; public BDCs ~25% below NAV; no insurer writedown / BDC bond >600 / covenant breach / HY >500. NOTE: the original written clause 'PC defaults >6%' is now exceeded; the Sep-10 amendment (which made the four listed triggers the scoring rule) governs -- held 2; flagged for the next rule review | [Sep-16] HY OAS 265bp (Sep 11); BCRED capped 5% for 2nd straight qtr; Blue Owl/HLEND Q3 ~Oct 1; no insurer writedown / BDC >600 / covenant breach / HY >500 — held at 2 | [Sep-10] HY OAS 265bp / IG ~78bp richest decile; Fitch private-credit default rate RECORD 6.1% (headline incl. extensions); BCRED capped 3rd qtr, Cliffwater capped; BDC median discount ~26%, non-accruals highest since 2017; LL defaults 0.87%. 'High 2' — the 3-clause's transmission-to-insurers/pensions leg is NOT evidenced", 1,
        "Tightest-decile spreads offer zero cushion against the AI-credit or consumer channels"),

    # ------------------------------------------------------------------
    # PILLAR 5 — BUBBLE DYNAMICS: Kindleberger/Minsky (weight 14)
    # ------------------------------------------------------------------
    Indicator(
        "Top-10 S&P concentration", "5. Bubble",
        "S&P DJ factsheets; GS/JPM concentration work",
        "0:<22 | 1:22-27 (2000 peak) | 2:27-35 | 3:>=35%",
        1, "[Oct-2] NDX record with the S&P 0.9% below its own and 75% of its members down in September: concentration at a cycle extreme; NVDA ~$5.6T, AMD crossed $1T. Held 3 | [Sep-28 AMENDMENT] weight 2 -> 1 (redundant with CAPE/ERP; weight moved to the new capital-cycle indicator) | ~38% top-10 (top-5 ~30%, most in 50+ yrs); AI names = 75% of returns since Nov-22", 3,
        "Index outcomes hinge on ~$545B/yr of AI capex earning its cost of capital"),
    Indicator(
        "AI capex-to-revenue gap", "5. Bubble",
        "Big-4 hyperscaler TOTAL capex guidance minus annualized genAI end-market revenue (disclosed cloud-AI run-rates + lab ARR; Sequoia/Bain aggregation)",
        "0:<$100B | 1:100-300 | 2:300-500 | 3:>=$500B",
        2, "[Oct-2] Micron FQ4 $54.2B (+379% y/y), FQ1 guide $61.5B, FY27 capex RAISED to >$40B (from ~$26B): the supply response the capital-cycle indicator predicts is now funded; hyperscaler 2026 capex unchanged ~$700-725B; no revenue-side update. Held 2 | [Sep-28 AMENDMENT] weight 3 -> 2 (net investment/GDP now carries the capital-cycle signal) | ~$455-525B: big-4 2026 capex $725B (+77% y/y, confirmed) vs genAI revenue ~$200-270B; midpoint ~$490B -> band 2 by tiebreak; divergence 46% vs 32% at telecom-2001 peak", 2,
        "AI revenue does not yet cover the ~$110B/yr depreciation on the installed base"),
    Indicator(
        "Circular / vendor-financed revenue share", "5. Bubble",
        "NVDA 10-Q concentration + deal map (OpenAI/Oracle/CoreWeave/SPVs); Lucent = 21% benchmark",
        "0:<5 | 1:5-15 | 2:15-30 (Lucent zone) | 3:>=30% or vendor debt guarantees at scale",
        2, "[Oct-2] SoftBank FUNDED the final $10B OpenAI tranche Oct 1 ($30B program complete, ~13% stake) with 8.6-9.75% junk; SB CDS >400bp; Broadcom seeking >$60B of debt (up to ~$100B incl. junior) with Apollo/Blackstone for Anthropic chips, Broadcom guaranteeing part of the senior; Anthropic targeting a mid-Nov IPO at up to $2T; AMD $5B into Anthropic. Vendor credit support at scale keeps widening -> held 3 | [Sep-28] ORCL 10-Q: $11.4B of customer prepayments with a 'significant financing component' (ASC 606) — Oracle books interest on them and later recognizes ~$1.9B more cloud revenue than collected, cost in interest expense (Burry). Vendor-side financing now embedded in revenue recognition; candidate rule for next review | [Sep-10] SIGNED: NVDA $105B residual-value guarantee on OpenAI's 20-yr Ohio lease (8-K Aug 17; cut from $250B) = vendor credit support >= 1 quarter of revenue and > NVDA's $99B equity book (stakes in its own customers). Watch, not counted: $500B platform (no deal), $36B rev-share (paused), Broadcom ~$100B (assembling)", 3,
        "Lucent/Nortel at 10x scale — mitigated by funders' ~$475B/yr real operating cash flow"),
    Indicator(
        "Debt/SPV-financed share of AI capex", "5. Bubble",
        "AI IG issuance + private-credit DC loans + DC ABS/CMBS over total AI capex",
        "0:<10 (2024 cash phase) | 1:10-20 | 2:20-35 | 3:>=35% (JST regime-flip)",
        2, "[Oct-2] Hyperscaler IG issuance Sep-Oct running >2x the sector's annual average (Bloomberg); Broadcom/Anthropic >$60B debt package in the market; CoreWeave $35.6B debt principal, ~6.8x net leverage, 2031s low-teens yield; no new SPV this week. Held 2 (approaching 35%) | [Sep-28] Burry tally: ~$3T of off-balance-sheet purchase commitments, uncommenced leases (MSFT >$300B, AMZN ~$267B), guarantees, CIP and SPVs (META ~$700B, GOOGL ~$900B commitments/exposures) across the big five; replaces the ~$2.4T carried since Sep 10; Moody's: uncommenced leases = 113% of on-BS debt | [Sep-22] AI-related USD debt YTD $568B ($259B IG, $256B private, $40B HY); GS $420B hyperscaler bonds 2027; AI-issuer spread ~115bp vs IG 78bp; Meta DC ladder pricing wider each deal (7.5% -> 8.25%). Approaching 35%; held 2 | [Sep-16] ORCL $20B ATM exhausted, FCF -$5.4B/qtr, FY27 capex $90-95B now debt/lease-only; GS est hyperscaler bonds $250B 2026 / $400B 2027 — approaching 35% band | ~25-35% 2026E vs ~10% 2024: $175B bonds, >$200B private credit, >$120B SPV in 18mo", 2,
        "THE damage variable: decides whether an AI bust is 2001-shaped or 1873/2008-shaped"),
    Indicator(
        "Forensic first-credit-event tripwires", "5. Bubble",
        "NVDA DSO>60d / 2-cust>40% / inv>$25B; ORCL CDS>150; capex guide CUT; B200 spot<$4/hr; SPV impairment; depreciation-life cut",
        "0:none | 1:warning proximity >=2 | 2:1-2 confirmed | 3:>=3 confirmed or any AI credit default",
        3, "[Oct-2] Still 2 confirmed. ORCL 5Y CDS record ~227bp (Sep 25; Oct print NF) -- 23bp from the 250 watch level; ORCL 2046/2056 bonds >8% YTM (~50bp wide of B2 paper) at BBB-; NVDA DSO = 60 (A/R $63.1B, extended terms to IG customers) AT threshold; DRAM rollover NOT confirmed (TrendForce 4Q26 +10-15%, Samsung +30% notices; only mobile/consumer +0-5%); Micron RAISED FY27 capex >$40B (no cut anywhere); no AI default/impairment. Jupiter cure/waiver terms still NF. Held 2 | [Sep-28] 2 CONFIRMED: (1) ORCL CDS >150bp; (2) Project Jupiter — ~$18B project loans 89-91c AND Oracle force majeure notice to the Blue Owl vehicle (Bloomberg): first hyperscaler-linked project debt in contractual distress. At threshold: NVDA DSO = 60. NEW watch item added to the list: DRAM/HBM contract-price rollover (Acer CEO: China DDR4 oversupply; Micron guide Sep 30) — the capital-cycle tell that precedes GPU-rental declines. Still 2 (needs >=3 confirmed for 3) | [Sep-22] Oracle Project Jupiter ~$18B project loans quoted 89-91c, syndication stalled (first sub-90 hyperscaler-linked project loan); NVDA DSO 60 (=threshold, not >); lenders reportedly declined Oracle as Abilene tenant (single source); ORCL CDS 190-215bp. Still 1 confirmed -> held 2 with proximity at maximum | [Sep-16] still 1 confirmed (ORCL CDS ~200bp regime). NOT on list but regime-relevant: labs' 'pace the frontier' (Sep 12-14), OpenAI IPO deferred to 2027, Moody's Baa2 NEG on ORCL, CRWV -8% — proximity up, held at 2 | [Sep-10] 1 CONFIRMED on list: ORCL 5Y CDS >150bp (record ~215bp Aug; BBB-, FY27 FCF -$42B guided). Adjacent/not listed: NVDA Q3 GM guide -100bp, top-3 customers 44% of rev, CRWV CDS ~855bp. NOT: no capex cut (3 raises/0 cuts), MSFT LENGTHENED DC lives 15->25y, no AI credit default", 2,
        "Minsky Stage 4 starts with funding failures; first-distress-to-peak ran 6-18 months historically"),
    Indicator(
        "Retail froth (margin debt + 0DTE)", "5. Bubble",
        "FINRA margin debt / GDP; Cboe 0DTE share",
        "0:<2.5 | 1:2.5-3.0 (2000 ~2.8) | 2:3.0-3.5 | 3:>3.5% GDP or 0DTE>55%",
        2, "[Oct-2] Burry (Sep 28) converted shorts to PUTS: NVDA/QQQ rolled to Jun-27/Feb-27, MU Jun-27 ~$500 (50% OTM), PLTR/TSLA/SOXX puts, exited ORCL/MSFT longs; Oct 1: markets 'should tank hard' to block the OpenAI/Anthropic IPOs. Sept margin debt due ~Oct 15. Held 3 | [Sep-28] Burry added 'in some size' to MU/PLTR/NBIS/SOXX shorts on the day NDX made its ATH (Sep 22); MU +17% in 7 sessions into the Sep 30 print; Sept margin debt due ~Oct 15. Held 3 | [Sep-22] FINRA Aug margin debt $1.45T record (+2.6% m/m, +37% y/y) | Record $1.53T margin debt (+51.5% y/y, ~4.0% GDP > 2021 peak ratio); 0DTE 59-65% of SPX volume", 3,
        "Every prior margin-debt record (1929, 2000, 2007, 2021) preceded major drawdowns by 6-18mo"),
    Indicator(
        "Net investment / GDP (capital-cycle position)", "5. Bubble",
        "S&P 500 aggregate capex minus depreciation, divided by nominal GDP (quarterly; Bloomberg/Compustat aggregates; Burry/Cassandra Unchained series)",
        "0:<1.0 | 1:1.0-1.5 | 2:1.5-2.0 (2007 and 2014 peak zone) | 3:>=2.0% (2000-01 aftermath zone)",
        2, "[Sep-28 ADDED, prospective] 2.07% as of 2026-06-30 — above every prior peak (2000 ~2.0 at the Nasdaq top, 2007 ~1.6, 2014 ~1.9) except the 2000-01 aftermath; prior peaks coincided with or slightly lagged the equity tops; 2003-06 ran NEGATIVE for 12 quarters as depreciation overwhelmed capex", 3,
        "The capital-cycle position: returns collapse after capital floods in; the depreciation hangover follows the equity peak by 1-3 years"),

    # ------------------------------------------------------------------
    # PILLAR 6 — HOUSEHOLD / CONSUMER CREDIT (weight 13)
    # ------------------------------------------------------------------
    Indicator(
        "Card + auto 90+ delinquency transitions", "6. Consumer",
        "NY Fed HHDC transition rates (quarterly)",
        "Card 0:<5.5 | 1:5.5-6.5 | 2:6.5-9.0 | 3:>=9.0 (GFC 13.7). Auto 0:<2.4 | 1:2.4-2.7 | 2:2.7-3.3 | 3:>=3.3",
        4, "[Oct-2] LABOR TURNED: payrolls +29K vs ~85K exp, two-month revisions -60K, July -10K (first negative print of the cycle), UR 4.2% (participation-driven), AHE 3.0% y/y = real wages ~-0.4%; Challenger hiring plans weakest Sept in 15 yrs; but claims 197K / continuing 1.701M (lowest since Mar-23) and Aug real PCE +0.6%. Card: COF Aug 30+ 4.54% per 8-K (CONFLICTS with the 3.57% carried Sep 22 -- different metric definitions; reconcile), NCO 4.16%; SYF 30+ 4.3%; AXP 1.0%; industry DQ creeping. No transition re-acceleration -> held 2; the hires/claims flip signal is NOT met (claims falling) | [Sep-28] claims 197K (lowest since mid-July), continuing 1.719M; industry card DQ 2.50% creeping; AXP 1.1% flat; ICE Aug mortgage DQ 3.53% (below every pre-pandemic Aug); UPST/AFRM -4% Sep 23. No re-acceleration -> held 2 | [Sep-22] COF Aug 30+ 3.57% per 8-K (vs 3.73% carried Sep 16 -- reconcile); claims 196K, continuing 1.73M lowest since Jan-24; Redbook decelerating 8.5 -> 7.6% | [Sep-16] NY Fed Q2 card transition 6.97% steady; COF Aug 30+ 3.73% (Jul 3.67%) drifting up; retail sales +1.2%/control +1.4% Aug vs UMich 47.8 & real AHE -0.1% y/y | Card ~7.0% (peak 7.2% mid-24, plateaued - highest since 2011, ~half the GFC's 13.7%); auto ~2.9-3.0% - NY Fed Q1-26: auto delinquency highest ever recorded", 2,
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
        2, "[Oct-2] Car-Mart: FIFTH extension, Oct 1 -> Oct 8 (8-K dated Sep 30: scheduled termination date, minimum-liquidity and collateral-coverage relief); Fitch Aug index still unpublished (July 6.13% / prime 0.49% stand); CACC extended a $500M warehouse to 2028 at SOFR+175 (tighter) and printed $600M ABS at 5.0-5.5% = funding OPEN for the top tier. Held 2 | [Sep-28] Fitch Aug index still not published; Car-Mart lenders extended waivers a 4th time to Oct 1; CACC settlement ~$710M incl. $634M balance waivers; prime 0.49% vs 0.6% trigger unchanged. Held 2 | [Sep-16] no Aug index yet; 6.13% Jul / prime 0.49% stand | [Sep-10] RE-ACCELERATING: 6.13% Jul (from 5.80% Jun; record 6.90% Jan); Fitch guides 'weaken further in H2'; PRIME 60+ 0.49% vs 0.6% escape trigger (closest yet); America's Car-Mart at going-concern (non-fraud failure candidate #1, covenant runway to Nov 6)", 2,
        "Above GFC-era levels but confined to the bottom quartile; PRIME contamination is the systemic signal"),
    Indicator(
        "Student loan 90+ share", "6. Consumer",
        "NY Fed HHDC; Dept. of Education default/garnishment counts",
        "0:<6 | 1:6-9 | 2:9-12 | 3:>=12% or >15% of portfolio garnished",
        1, "[Oct-2] CONFLICT: secondary sources this week describe wage garnishment of defaulted borrowers as 'underway since Jan 2026 and scaling monthly' (~9M in default, 7.9M delinquent), contradicting the Sep-10 correction (collections paused since Jan 16); neither is primary-sourced. Held 2 pending an ED/Treasury primary statement | [Sep-10 CORRECTION] involuntary collections PAUSED since Jan 16 2026 (not scaling); ~5.3-5.5M in default = latent drag; 90+ share ~10%", 2,
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
        2, "[Oct-2] Car-Mart did NOT file on Oct 1 either: fifth extension to Oct 8 (weekly waivers from Silver Point are now the pattern); CACC funding at tighter spreads. Held 1; a filing on/after Oct 8 = failure #2 -> 2 | [Sep-28] Car-Mart did NOT file: waivers extended a 4th time, to Oct 1 (from Sep 25); a filing = failure #2 -> 2. Held 1 | [Sep-22] Credit Acceptance $694M 40-AG settlement (Sep 17); America's Car-Mart $300M facility deadline extended to Sep 25, bankruptcy 'an option'. A Car-Mart filing would be failure #2 in 12 months -> 2 | Tricolor Ch.7 (Sep-25, $1.4B ABS, fraud, >$1B bank hit) + First Brands; spreads re-tightened; no verified 2026 failures", 1,
        "Dimon's cockroach rule: fraud DISCOVERY, not credit deterioration, is the likely surprise vector"),

    # ------------------------------------------------------------------
    # PILLAR 7 — BIG CYCLE / CONFLICT / GLOBAL (weight 15)
    # ------------------------------------------------------------------
    Indicator(
        "Internal disorder index", "7. Big Cycle",
        "Political-violence counts; election-machinery events; DFA top-1% share; Dalio Stage-5/6 checklist",
        "0:normal | 1:polarized | 2:Stage-5 markers | 3:Stage-6 onset (contested election, organized violence)",
        5, "[Oct-2] Fed IG cleared Powell on the HQ renovation (Sep 30); Trump same day: Powell 'should be forced to resign' from the Board 'at a minimum'; AP-NORC approval 31/69, aggregates ~37/60; generic D+7; prediction markets: Dem House 92%, Dem Senate ~64%, D sweep 62%; Guard: DC through 2026, Memphis patrols from Oct 10; no new violence. Still Stage-5 markers, not Stage 6 -> held 2 | [Sep-28] Trump approval 33/63 (new low); generic ballot D+7-10; CR to Dec 11 passed House 370-48 (Oct 1 shutdown risk removed); Austin protests continuing (~160, chemical agents, arrests), no new Guard deployment found; Section 232 100% pharma tariff + Canada import bans effective Sep 29. Held 2 | [Sep-22] ICE officer shot a delivery driver in Austin (Sep 20), multi-day protests; three outlets banned from the White House; approval 32-41%; 3,073 Guard in DC to 2029; Russia/Iran sanctions law signed Sep 18 | [Sep-16] Fed hike delivered under open WH attack; midterms D+7-9, Dem Senate odds ~59%; no violence in window | Stage 5: political attacks at 30-yr high; two assassinations + one attempt; top-1% wealth 31.7% (record); Nov-26 midterms ahead", 2,
        "Markets priced this twice (Apr-25 'Sell America', Jan-26 Fed-probe spike) — episodically, not persistently"),
    Indicator(
        "External conflict index", "7. Big Cycle",
        "Hormuz/Iran status (Brent); US-China truce (expiry Nov-10-26); Taiwan posture; capital-war provisions",
        "0:none | 1:trade war | 2:regional war + commodity disruption OR truce fraying | 3:great-power confrontation",
        3, "[Oct-2] Iranian delegation EXPELLED (Rubio), US counter-proposal via Qatar Sep 30, Trump: 'big decision very soon'; Pentagon ordering a THIRD carrier group + ~10K troops to arrive by end-Nov; SIX tankers struck in a week (VLCC Kazimah III on fire Oct 1), Hormuz ~1 transit/day vs 85 baseline, 147 vessels holding; yet Brent fell to $99.7 (market reads 'strikes deferred past midterms'). Russia's largest grid strike since last winter (Sep 30). Xi summit: truce to Jan 10, no export-control text, Taiwan $14B package 'in abeyance'. Still no great-power confrontation -> held 2 (high) | [Sep-28] Trump REJECTED Iran's 7-day/60-day Hormuz plan (Sep 26) and per WSJ told aides he expects to RESUME BOMBING IRAN AFTER NOV 3; Brent $97 -> $105-107 (intraday $108.8); Xi summit constructive (truce extended ~2 months to early 2027; tariff cuts ~$30B; Taiwan 'red line'; no chip-export relief); Ukraine drone strikes on Russian refineries; no new NATO-Russia incident. Oil channel re-armed but no great-power confrontation -> held 2 (high) | [Sep-22] Two-track: new US strikes on IRGC targets Sep 22 AND a 3-hr US-Iran meeting in NY ('very productive'; Trump: deal 'right after' Nov 3); Hormuz transits still <=15/day; Saudi E-W pipeline restarted at low rate; Brent ~$97 (-10%); sanctions law with up-to-100% secondary tariffs on top-5 Russian-oil buyers (China, India) SIGNED; CCG-Philippine collision Sep 18; DPRK SRBMs Sep 20. Held 2 | [Sep-16] Hormuz transits single digits; US destroyed 5 Iranian tankers (Sep 8-9); Houthis seized 2 Red Sea islands, Saudi East-West pipeline out for weeks; Brent $108; first NATO drone shoot-down over Lithuania (Sep 15); India-Pak naval collision; secondary-tariff bill (100% on top-5 Russian-oil buyers) advancing. Offsets: Xi state visit Sep 23-25, truce extension expected. HIGH 2; 3 requires great-power confrontation | Iran war since Feb-26, Brent $86.6 (>$90 in July); new 12.5% S.301 tariff Jul-23-26; truce expires Nov-10-26", 2,
        "The oil channel is the live stagflation transmitter; reserve transitions tip on wars (Suez 1956)"),
    Indicator(
        "Reserve erosion & gold signal", "7. Big Cycle",
        "IMF COFER USD share; gold vs USTs in CB reserves (WGC/ECB); Dalio triple check",
        "0:COFER>60 | 1:57.5-60 drifting | 2:55-57.5 + gold>USTs + CB>700t/y + gold+20%y/y | 3:<55 falling fast or triple confirmed 3mo",
        4, "[Oct-2] COFER Q2 (Sep 30): USD share 56.7% (from 57.2%; mostly valuation) -- BELOW the 57.5% downgrade line, so the Sep-16 prospective downgrade does NOT execute even though gold y/y (~+8.5%, spot $4,217) fails the +20% clause. CB gold Q2 record 289t, PBOC +20t in Aug. DXY 17-month high 102.2 (Oct 1); Dalio triple NOT confirmed (yields up, dollar up, gold down). Held 2 on the COFER clause alone; weakest 2 in the model | [Sep-28] gold $4,310 -> ~$4,150 (-3.8%, 7-week low; ~+12% y/y -- the +20% clause now FAILS); silver -9%; DXY 101.1 (2-month high); Dalio triple 1 of 3 (yields up, dollar UP, gold DOWN) -- the market is doing the OPPOSITE of a reserve exit this week. Downgrade to 1 executes if COFER Q2 (Sep 30) prints >57.5%. Held 2 pending | [Sep-22] gold ~$4,310 spot / $4,409 Dec fut (+17% y/y; -23% from ATH) through a Fed hike and DXY ~100.6; BTC $86K (+14% wk); July TIC -$50B; COFER Q2 due Sep 30. Held 2, weakening | [Sep-16] gold $4,263-4,348 (6-wk low, -24% from ATH, ~+17-19% y/y — the +20% clause is now borderline); PBOC +20.2t Aug (largest since Oct-23), CB Q2 record 289t; DXY 99.6 firming; Japan funding intervention via FIMA repo not UST sales. Held 2, WEAKENING; downgrade to 1 if COFER Q2 (Sep 30) >57.5 AND gold y/y <20% | [Sep-10 CORRECTION] gold ATH was $5,596 (Jan 28 2026); ~$4,400 now = -20% from record, ~+20% y/y. Score rests on LEVEL clauses that survive: COFER 57.13% (in 55-57.5 band, though UP q/q), gold > USTs in CB reserves, gold +~20% y/y; CB buying slower YTD. Dalio triple 2 of 3 (yields up, DXY 98.8 down; gold NOT up since Jun 1). Low end of 2", 2,
        "Hedging the dollar system without leaving it: no successor exists (euro 20%, RMB 2%)"),
    Indicator(
        "China / global contagion index", "7. Big Cycle",
        "NBS China FAI cumulative y/y; 30Y JGB + BOJ; global mfg PMI; CNY/JPY tail checks",
        "0:FAI>+4, JGB30<2, PMI>52 | 1:FAI 0-4 or JGB 2-3 | 2:FAI contracting + JGB30>3 + PMI<=50.5 | 3:China credit event / CNY>7.5 / carry unwind 2.0 / JP repatriation>$200B/y",
        3, "[Oct-2] France: EUR43B austerity budget (Oct 1), 2027 deficit target 5.0%, debt 121.7%, OAT-Bund 130bp (+13bp on the day; WIDER THAN ITALY AND GREECE); UK 30Y gilt ~6.0% (highest since 1998), 10Y 5.34%; Bund 3.46-3.51%; JGB 10Y ~3.0%, yen 157.7 after a record JPY15T intervention; China official PMI 50.1 (first >50 in 3 months), LPR held 16th month, land sales -30%; Korea Sept exports RECORD +83.5% (chips +263%); India rupee record lows, FPI outflows. Held 2 | [Sep-28] GLOBAL LONG END BROKE OUT Sep 24: JGB 10Y 3.055% (since 1996), 30Y 4.134%; Bund 10Y 3.64% (since 2009); UK 10Y 5.36%; Norges hiked to 4.50%; EZ PMI 53.1 (3-yr high) feeds ECB hikes; France budget slips to Oct 1 (2026 deficit 5.4%), OAT-Bund ~105bp; China EPMI 52.3, PBOC fixing weaker than est. into Golden Week; Korea chips +259%. JGB30 >3 and PMI clauses unchanged -> held 2 | [Sep-22] LPR held 16th month ('no need to cut'); banks told to keep Vanke loans off NPL books; property investment -19.9% YTD; CNY 6.70 (strongest since Jan-23); OAT-Bund 105bp (first >100 since 2012; Scope cut France to A+); UK 30Y ~5.75%; JGB 30Y 4.07%; MOF cutting super-long issuance for lack of insurer demand. Held 2 | [Sep-16] China Jan-Aug FAI -7.2% y/y (CNBC; deepening), retail +0.4%, Aug new loans RMB 60bn vs 400bn exp, M2 17-mo low, home prices -39th month; JGB 30Y 4.15% (near record), 30Y auction cover 2.92 worst since 2023; CNY 6.71 STRONG (opposite of the 7.5 trigger); Korea chips +270% y/y. Held 2 | China FAI -5.7% y/y H1-26 (property -14%, PPI negative ~39mo); 30Y JGB ~3.5% record, yen ~164; global PMI ~49.7-50.8", 2,
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
    print("BDCR-26 dashboard — baseline 2026-07-28, re-scored 2026-10-02")
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

# ======================================================================
# SEPT 16 2026 RE-SCORE LOG (2026-09-16, post-FOMC)
# ======================================================================
# Composite 69.0 -> 70.0 (raw 207 -> 210). ONE mechanical change: Equity risk
# premium 2 -> 3 because the 10Y broke 5% (5.008% post-hike) against a forward
# E/P of 4.55-4.85% — the pre-registered '<=0pp' clause is crossed on a single
# input change. Every other indicator was tested against its written threshold
# and the Sept-10 prospective amendments and HELD (30Y intervention-fails clause
# not met on the 30Y itself; credit amendment clauses all unmet; consumer
# tripwires at-threshold but not below).
#
# CLASSIFICATION: composite sits exactly on the 70 line -> R4 band, but the
# Monetization Gate is NOT met (Fed just hiked; real rate positive; bills-only),
# so the model reports "R3-upper — repression-lite onset (R4 band, gate unmet)".
# This is the correct output: the market is PRICING fiscal dominance (long end
# sold off on a hike) while the Fed is behaving as if it does not exist.
#
# THIS WEEK'S EVIDENCE (Sept 10-16):
#   Fed +25bp to 3.75-4.00%, 12-0, median one more 2026 hike; 10Y 5.008%
#   (highest since 2007) — the long end ROSE on the hike (the 1994 counter-read
#   did not materialize). ECB +25bp Sep 10; BOJ ~80% for Sep 18; JGB 30Y 4.15%.
#   Aug CPI 3.4% / PPI 5.4% / import prices +7.0% y/y; UMich 47.8, 1y 4.6%,
#   5-10y 3.4%. Retail sales +1.2% (control +1.4%) vs real AHE -0.1% y/y.
#   ORCL Q1 FY27: OCI +121%, RPO $664B, FCF -$5.4B, ATM exhausted; labs' 'pace
#   the frontier' + OpenAI IPO deferred to 2027; BCRED 2nd consecutive 5% cap.
#   Hormuz transits single digits, 5 Iranian tankers destroyed, Houthis seized
#   islands, Saudi East-West pipeline down; Brent $108. NATO drone shoot-down
#   over Lithuania; India-Pakistan naval collision. China FAI -7.2% YTD, new
#   loans RMB 60bn. Gold 6-wk low $4,263 (-24% from ATH); DXY 99.6.
#   Burry closed Dec-26 NVDA/PLTR puts, kept 2027 PLTR/QQQ puts. BofA FMS: cash
#   3.9%, AI capex = #1 credit fear, semis most crowded; CTAs 100% max long with
#   -$73.7B sell trigger; buyback blackout ~half the index.
#
# PROBABILITIES (game-theory-adjusted, see artifact 'Game theory' panel):
#   Muddle 28 | Repression 19 | AI Bust 17 | Second Wave/Long-End Accident 17 |
#   Productivity Escape 14 | Fracture 5   (Sep 10: 31/20/16/13/16/4)
#   Second Wave +4: three G3 hikes in nine days into a long end at 19-yr highs,
#   10Y >5%, import prices +7%, 5-10y expectations one tick from 3.5 — and the
#   hike-then-rally counter-read FAILED (long end sold off on the hike).
#   Muddle -3: the 'election put' still holds the near term together, but the
#   long end no longer cooperates. AI Bust +1: first top-down slowdown signal
#   from the labs themselves + IPO liquidity event removed. Escape -2: hikes,
#   $108 oil, negative real wages, 10Y 5%. Repression -1 near-term (positive
#   real rates), but its 5-yr mass is preserved because the accident that
#   legitimizes it just became likelier. Fracture +1: NATO shoot-down,
#   India-Pak, secondary tariffs on China/India advancing; netted against the
#   Xi visit and 'de-risking not de-dollarization' BRICS language.
#
# PROSPECTIVE (never retroactive): ERP reverts to 2 if 10Y <4.85% or fwd P/E
#   <20x. Reserve erosion -> 1 if COFER Q2 >57.5 AND gold y/y <20%. Consumer
#   'weak-3' flag escalates on Aug JOLTS hires <3.2% (Oct 6) or Aug saving
#   <3.0% (Sep 26). External conflict -> 3 only on great-power confrontation
#   (Taiwan/NATO-Russia kinetic), NOT on oil price alone.
#
# TIMING: near-term correction window (>=10% from the 7,799 record) live
#   through the Nov 4 QRA, now ~40% (from ~30%) on: 10Y >5%, CTAs max-long with
#   a $74B sell trigger, buyback blackout, triple witching Sep 18, BOJ Sep 18,
#   Oct 8 30Y auction, Oct 27-28 second hike. Probability the Aug 26-27 record
#   was THE cycle high: ~30% (from ~20%). Center of mass for the full crash
#   (>25%) unchanged at 2027-28; the political calendar (midterms) is the reason
#   it is not Q4 2026.

# ======================================================================
# SEPT 22 2026 RE-SCORE LOG (2026-09-22)
# ======================================================================
# Composite 70.0 -> 70.0 (raw 210). NO indicator crossed a written threshold in
# the Sept 16-22 window. Eighteen indicators re-annotated. Tests worth recording:
#   ERP stays 3: the 10Y (4.95-4.97%) is above the 4.85% revert line.
#   30Y stress stays 2: high close 5.33% (Sep 18); no clause of the Sep-10 amendment met.
#   Credit stays 2 under the Sep-10 amendment even though Fitch's private-credit
#     default rate (6.3%) now exceeds the ORIGINAL '>6%' clause -- a rule conflict
#     flagged for the next review; not re-scored mid-stream.
#   Forensic tripwires stay 2: Jupiter loans at 89-91c and DSO = 60 are proximity,
#     not confirmations under the list as written.
#   Subprime lenders stay 1: a Car-Mart filing (deadline Sep 25) would make it 2.
#
# THIS WEEK'S EVIDENCE (Sept 16-22):
#   Equities fully reversed the FOMC selloff: S&P 7,776 (-0.3% from record), Nasdaq
#   record, semis up six straight sessions, MU >$1,000; VIX 14.25; breadth narrow
#   (NYSE Comp flat, R2K -4% 1M, XLF -1.9% on the day); CTAs modelled as sellers in
#   every one-week scenario; Aug margin debt record $1.45T; buyback blackout.
#   Rates: 2Y 4.77 / 10Y 4.96 / 30Y 5.29; 2s10s ~20bp; Oct hike ~55%, Dec ~90%.
#   BOJ +25bp to 1.25% (7-2, dovish); yen 158, rate check; Japan closed Sep 21-23.
#   July TIC -$50.4B; Japan -$12.8B; private foreigners net sellers of LT securities.
#   Oil: Brent $108 -> ~$97 on US-Iran talks (3 hrs, 'very productive'; deal 'after
#   Nov 3'), a disputed 7-day Hormuz offer, Saudi pipeline restart -- while new US
#   strikes hit IRGC targets the same day and transits stayed <=15/day.
#   AI: Oracle Jupiter loans 89-91c; OpenAI deck FCF -$278B 2026-30, cash out by
#   2028, seeking >$1.2T; SoftBank funding its stake with ~10% junk; Fitch PC default
#   6.3%; all perpetual BDCs capped 5%; CleanSpark/Meta DC bond 8.25%; Rothschild
#   Sells on CRWV/NBIS; vs Korea chips +259%, Taiwan orders +71%, NVDA $227.
#   Consumer: claims 196K; mortgage 6.95% (>7% daily); Lennar orders -9%, ~50% of
#   visitors cannot qualify; CACC $694M settlement; Car-Mart Sep 25; CBO FY26 $2.1T.
#   Europe: OAT-Bund 105bp, Scope cut; CDU below 5% in a state election; UK PSNB
#   overshoot. Gold ~$4,310-4,409 (+17% y/y); BTC $86K; DXY ~100.6; CNY 6.70.
#   Politics: Trump 'rates should be 1%', board 'hostile'; Russia/Iran sanctions
#   law signed with up-to-100% secondary tariffs on China/India; Xi arrives Sep 23.
#
# PROBABILITIES: Muddle 29 | Repression 19 | AI Bust 18 | Second Wave 16 |
#   Escape 14 | Fracture 4   (Sep 16: 28/19/17/17/14/5)
#   Muddle +1: oil -10%, labor strong, equities at highs -- the election put is
#     working exactly as the game-theory layer said it would (Trump: deal after Nov 3).
#   AI Bust +1: the financing channel cracked in three places (Jupiter <90, OpenAI
#     cash-out-by-2028, SoftBank junk) while demand data stayed record-strong -- the
#     railroad/Lucent shape, not a demand bust.
#   Second Wave -1: the oil impulse eased; the policy-error leg (hikes into a
#     flattening curve) is unchanged. Fracture -1: Iran talks + Xi summit outweigh
#     France's spread and the sanctions law this week.
#
# TIMING: crash distribution unchanged (modal Q4 2027; 7/13/38/22/20). Correction
#   >=10% before the Nov 4 QRA ~40% (unchanged): the bounce was oil-driven and
#   breadth-poor, with CTA sell asymmetry, blackout, quarter-end pension selling,
#   Oct 1 gates, Oct 8 30Y auction and a 55%-priced Oct hike ahead. Probability the
#   Aug 26-27 record is THE cycle high: ~20% (from 30%) with the S&P 0.3% below it;
#   probability the cycle high is in by Dec 31 2026: ~35%.
# NEXT: Sep 23 flash PMIs/5Y auction; Sep 24 Xi-Trump + 7Y auction + 20-30Y buyback;
#   Sep 25 UMich final + Car-Mart deadline; Sep 30 PCE/saving rate, Micron, COFER Q2,
#   France budget, quarter-end; Oct 1 gates; Oct 2 payrolls; Oct 6 JOLTS hires.

# ======================================================================
# SEPT 28 2026 RE-SCORE LOG (2026-09-28)
# ======================================================================
# Composite 70.0 -> 71.7 (raw 210 -> 215). Indicator count 31 -> 32. Two changes:
#
#   (a) STRUCTURAL AMENDMENT (prospective, applied this cycle for the first time):
#       new Pillar-5 indicator 'Net investment / GDP (capital-cycle position)',
#       weight 2, thresholds 0:<1.0 | 1:1.0-1.5 | 2:1.5-2.0 | 3:>=2.0%. Reading
#       2.07% (2026-06-30, S&P 500 capex minus depreciation over nominal GDP; Burry/
#       Cassandra Unchained series from Bloomberg aggregates) -> score 3. Weight
#       funded by Top-10 concentration 2->1 and AI capex-to-revenue gap 3->2 so the
#       total stays 100. Net effect of the amendment alone: raw +1 (211), +0.3 pts.
#       Rationale: capital-cycle theory (Marathon; Burry's 'Capital Cycle IQ') --
#       returns collapse after capital floods in; the 2000, 2007 and 2014 peaks in
#       this ratio coincided with or slightly lagged equity tops, and the 2003-06
#       negative stretch shows the depreciation hangover. The existing capex-gap
#       indicator measures the same phenomenon less precisely, hence its de-weight.
#       Also: the forensic watch-list gains 'DRAM/HBM contract-price rollover' (not
#       a scoring change); the circularity note records the $11.4B ASC-606 prepayment
#       financing component; the debt/SPV note carries the ~$3T off-balance-sheet tally.
#
#   (b) 30Y YIELD STRESS 2 -> 3 under the Sep-10 amendment's fourth clause ('an
#       official long-end intervention fails to hold: yields at/above the pre-
#       intervention level within 5 sessions'). Treasury's 20-30Y buyback on Sep 24
#       took $4.08B of a $6B cap with the 30Y at 5.44-5.50%; on Sep 28 (session +2)
#       the 30Y traded 5.56%. Raw +4, +1.3 pts. The ORIGINAL >=5.5% rule is a CLOSE
#       test and is not yet confirmed (Sep 25/28 closes not retrieved; one source has
#       Sep 24 at 5.438% while Bloomberg has an intraday high of 5.501%) -- recorded
#       so the upgrade is auditable as an amendment-clause call, not a level call.
#       Reversion rule (prospective): back to 2 if the 30Y closes <5.30% for 5 sessions.
#
# TESTED AND HELD (evidence in each indicator's note): auction stress 2 (5Y tail 3.1bp,
#   BTC 2.21 -- the 3-clause needs >=4bp AND <2.2 at the 10Y/30Y); ERP 3 (10Y 5.17-5.23
#   vs E/P ~4.5); credit 2 (HY 280, no listed trigger); forensic 2 (Jupiter force
#   majeure + CDS record = 2 confirmed; needs 3); reserve erosion 2 (gold +20% clause
#   FAILS at ~+12% y/y; COFER Sep 30 decides the downgrade); external conflict 2
#   (Iran plan rejected, post-midterm bombing report; no great-power confrontation);
#   subprime lender 1 (Car-Mart waivers to Oct 1); consumer transitions 2 (claims 197K).
#
# CLASSIFICATION: 71.7 -> R4 band, Monetization Gate NOT met (Fed 72% to hike in
#   October; Treasury under-filled its own buyback). Output: 'R3-upper -- repression-
#   lite onset'. The gap between what the market is pricing (fiscal dominance: the
#   long end sells off on hikes) and what the Fed is doing (tightening) is now the
#   widest of the cycle. That gap is the Second-Wave mechanism.
#
# THIS WEEK'S EVIDENCE (Sept 22-28):
#   Rates: whole curve 2Y-30Y +16-28bp in four sessions; 5Y >5% (first since 2007),
#   10Y 5.17 close / 5.23 intraday (since 2007), 30Y 5.56 intraday (since 2004), 2Y
#   4.90 (since 2023); MOVE 80 -> 104.6 (biggest weekly jump since Apr-25; a second
#   source has 96 on Sep 25); Oct hike 55% -> 72%. Global long end broke out the same
#   day: JGB 10Y 3.06 (since 1996), Bund 3.64 (since 2009), UK 5.36.
#   Equities: S&P 7,776 -> 7,704 (Sep 24) -> 7,743 (Sep 25) -> lower Sep 28 (-0.7% to
#   -1% from the Aug 26-27 record); NDX ATH Sep 22 not extended; VIX 14.9; stock-bond
#   correlation positive every session; quarter-end pension rebalance = sell equities.
#   AI: Oracle FORCE MAJEURE on Project Jupiter (Sep 24), ORCL CDS record, ORCL -8.5%
#   w/w, WSJ 'cracks' at the New Mexico site; SoftBank $11.1B junk to fund OpenAI's
#   $10B Oct 1 call; CoreWeave-tenant DC paper 9.25%; Burry 'moving timelines up'
#   (Sep 28); Micron Sep 30 with consensus above guide; Acer CEO: no memory shortage.
#   Oil/geo: Trump rejected Iran's Hormuz plan (Sep 26), WSJ: bombing resumes after
#   Nov 3; Brent $97 -> $105-107; Xi summit constructive, truce extended to ~Jan 2027.
#   Consumer: claims 197K; mortgage 7.03%; UMich 48.1; gasoline $4.49 (late-Sept
#   record); Car-Mart waivers to Oct 1; CR to Dec 11 passed House.
#   Reserve: gold -3.8% to ~$4,150, silver -9%, DXY 101.1 -- the dollar was bought.
#
# PROBABILITIES: Muddle 26 | Repression 19 | AI Bust 19 | Second Wave 19 |
#   Escape 12 | Fracture 5   (Sep 22: 29/19/18/16/14/4)
#   Second Wave +3: the intervention-fails clause fired; the global long end broke
#     out in one session; oil reversed up; the Fed is 72% to hike into a flattening
#     curve with MOVE at a 6-month high. This is the accident scenario's setup.
#   Muddle -3: the election put still works (Trump: Iran after Nov 3, truce extended),
#     but the long end is no longer cooperating at any level of oil.
#   AI Bust +1: force majeure is the first CONTRACTUAL distress event in the
#     hyperscaler chain; capital-cycle indicator added at 3; credit tiering by tenant.
#   Escape -2: 10Y 5.2%, oil $105, real wages negative, tariffs escalating Sep 29.
#   Fracture +1: Iran plan rejected + post-midterm bombing intent; France budget slip;
#     netted against a genuinely constructive Xi summit.
#
# TIMING: crash (>=25%) distribution: pre-Nov-26 8 | Nov-26-Jun-27 14 |
#   Jul-27-Jun-28 38 | Jul-28-2029 21 | none-to-2031 19 (was 7/13/38/22/20).
#   Modal month UNCHANGED: October 2027. Correction >=10% before the Nov 4 QRA:
#   ~45% (from 40%) on the 30Y at 5.56, MOVE >100, oil >$105, quarter-end selling,
#   Oct 1 gates, Oct 8 30Y auction, Oct 27-28 hike at 72%. Modal correction month
#   unchanged: October 2026. P(Aug 26-27 record is THE cycle high): ~25% (from 20%).
#   P(cycle high in by Dec 31 2026): ~40% (from 35%).
#
# PROSPECTIVE (never retroactive): 30Y reverts to 2 on 5 closes <5.30%. Reserve
#   erosion -> 1 if COFER Q2 (Sep 30) >57.5% (gold clause already failed). Forensic
#   -> 3 on any ONE more listed confirmation (ORCL CDS >250 verified, NVDA DSO >60,
#   capex guide cut, DRAM contract-price rollover confirmed by two producers).
#   Capital-cycle indicator re-reads quarterly (next: Q3 aggregates, ~mid-Nov).
#   Credit rule conflict (PC defaults 6.3% > original '>6%' clause) still open.
# NEXT: Sep 29 Conf Board, 7Y results; Sep 30 PCE/saving/GDP revision, Micron, COFER,
#   France budget, quarter-end; Oct 1 Car-Mart, gates, OpenAI $10B; Oct 2 payrolls;
#   Oct 6 JOLTS; Oct 8 30Y auction; Oct 13-14 banks; Oct 27-28 FOMC; Nov 3; Nov 4 QRA.

# ======================================================================
# RED-TEAM RESPONSE (2026-09-28, same day) — ARCHITECTURE CHANGE, PROSPECTIVE
# ======================================================================
# A red-team memo ("BDCR Crash-Timing Engine: Red-Team Analysis, Counterpoints &
# Proposed Next-Generation Model") was received and accepted in substance:
#   (1) this composite answers "how dangerous", not "what breaks, when";
#   (2) it is additive over correlated symptoms (five faces of one sovereign-
#       funding shock can count five times);
#   (3) it scores levels, not clocks; (4) the AI thesis was treated as the
#       prerequisite transmission; (5) the election calendar moved the timing
#       judgment on narrative grounds; (6) 10% / 20% / 25% events were conflated;
#   (7) market internals and liquidity had no place in the score;
#   (8) 'October 2027' was a judgment, not a hazard-model output.
# DISPOSITION: this file is RETAINED UNCHANGED as the STRUCTURAL-REGIME layer
# (its pre-registered thresholds and amendment log are the audit trail). The
# scenario probabilities and timing distribution logged above are RE-CLASSIFIED
# as a PRIOR. Timing now comes from bdcr27_timing_engine.py, which adds: a
# 9-factor de-duplicated vulnerability score; four independent crash engines
# (sovereign, AI capital cycle, private credit, consumer) with first-crack
# stage, reflexivity gain and refinancing coverage; a liability maturity clock;
# an AI funding-gap test; a marginal-rate sovereign engine with a Treasury-
# demand clearing model, buyers'-strike detector, failed-rescue counter and
# policy-exhaustion clock; 3-of-5 cross-market confirmation; a market-internals
# layer (the liquidity/plumbing factor this file lacks); a historical analogue
# engine on the 1881-2023 Shiller record; network centrality; and a monthly
# hazard model with THREE separate clocks (correction, bear, systemic) in which
# the election calendar is a policy-suppression (deferral) modifier only.
# HONESTY NOTE recorded by the first engine run: the judgment prior placed 8% of
# crash mass in the ~5 weeks before Nov 4, a higher single-month density than
# any month of the 'modal' Jul-27..Jun-28 bucket, so 'October 2027' was a
# modal-BUCKET claim. The engine now reports modal month, 80% interval and
# confidence from the hazard curve. Output: hazard_report.md / hazard_curve.json.
# v0.2 (same day, second memo "Dalio's Methodology & BDCR 2.0"): adds an encoded
# Dalio decision tree (pass/fail per node), three reflexivity loops with gains, a
# fifth engine (market plumbing), +200bp / asset-value / financing stresses, a
# backtest of pre-specified mechanism rules on 1881-2023 (in/out of sample, nothing
# fitted), mechanism-matched analogues, and confidence defined as stability across
# 162 model specifications. First v0.2 run: systemic modal month SEPTEMBER 2027
# (prior October), 80% interval Feb 2027 - Mar 2029, confidence MEDIUM.

# ======================================================================
# OCT 2 2026 RE-SCORE LOG (2026-10-02)
# ======================================================================
# Composite 71.7 -> 70.3 (raw 215 -> 211). ONE change: credit complacency/stress
# 2 -> 1 under the written threshold -- the indicator's declared series (FRED
# BAMLH0A0HYM2) printed 308/312bp on Sep 29-30, leaving the '<300 complacency'
# clause without reaching any stress band. Caveats recorded in the note: the
# Bloomberg 2%-capped index is 294 and the 265-280 readings carried since Sep 10
# appear to have mixed series; private-credit defaults (6.3%) still exceed the
# original '>6%' 3-clause. PROSPECTIVE AMENDMENT: from the next review the score
# is max(spread band, private-credit band), private-credit band = 2 when the
# Fitch TTM default rate >6% with gates binding, 3 on a named insurer/pension
# writedown. This is the second time the two-sided design has produced a
# counter-intuitive move; the amendment removes the asymmetry prospectively.
#
# CONFIRMED, NO SCORE CHANGE: 30Y stress 3 now also under the ORIGINAL rule (five
#   closes >=5.50, high 5.632 Sep 30, highest since 2002) -- the Sep-28 amendment-
#   clause call is validated. ERP 3 at -0.65 to -0.85pp (10Y 5.29, S&P 7,726).
#   Reserve erosion stays 2: COFER Q2 56.7% is BELOW the 57.5% downgrade line, so
#   the gold-clause failure (+8.5% y/y) does not execute the downgrade.
# TESTED AND HELD: auction stress 2 (7Y ~3bp tail, BTC 2.42; bills 2.7-2.8x; no
#   10/30Y trigger; Oct 7-8 reopenings are the test); forensic 2 (ORCL CDS record
#   227 <250; NVDA DSO = 60; no DRAM rollover -- TrendForce 4Q26 +10-15%, Samsung
#   +30%; Micron RAISED FY27 capex >$40B); subprime lender 1 (Car-Mart fifth
#   extension to Oct 8); consumer transitions 2 (claims 197K / 1.70M vs payrolls
#   +29K, July -10K, real AHE -0.4%); monetization gate CLOSED (Oct hike dead,
#   no easing; RMP paused to Oct 14); Fed independence 2 (Trump: Powell 'should
#   be forced to resign'; no action); external conflict 2 (delegation expelled,
#   third carrier, six tankers struck; no great-power confrontation).
# SAVING-RATE TRIGGER RE-BASED (prospective): the BEA annual revision lifted the
#   saving-rate history ~1.6pp (June 2.7 -> ~4.3; Aug 4.1 on the new series).
#   The consumer 'weak-3' clause 'saving <3.0%' is restated as '<4.0% on the
#   revised series' from the next reading; Aug 4.1% is therefore NOT a trigger
#   but is 0.1pp from it with spending outrunning income by 0.7pp.
#
# THIS WEEK'S EVIDENCE (Sept 28 - Oct 2):
#   Rates: 30Y closes 5.56/5.585/5.632/5.613/5.63; 10Y 5.342 intraday (since
#   2002), 5.28 close; 2Y 4.92 -> 4.84; 2s10s ~44bp (bear-steepening on weak
#   data); MOVE 108; Oct 1 buyback full $6B of $46.4B offered; 7Y weak; bills
#   fine, SOFR 3.90 at quarter-end; Oct hike odds ~17% after payrolls; Williams/
#   Jefferson: one more hike 'later this year'. France OAT-Bund widest since 2012
#   (94.7bp per one source, 130bp per another -- CONFLICT), UK 30Y 6.00%, JGB 10Y
#   3.11%, Bund 3.46-3.60.
#   Macro: payrolls +29K, revisions -60K, July -10K, UR 4.2, AHE 3.0 (real -0.4);
#   core PCE 3.0 (methodology), headline 3.4; ISM 54.5 / prices 77.9; Conf Board
#   81.9 (lowest since 2014), expectations 63.6, inflation exp 6.1; Q2 GDP 2.2;
#   mortgage 7.28; gasoline $4.41; CR signed; TGA $984B.
#   Equities: S&P 7,726 (-0.9% from record), NDX RECORD 30,808 (Oct 2), NVDA
#   record $234 (~$5.6T), MU ~$1,097; breadth: lows>highs 23 sessions, 43-49%
#   above 200dma, 75% of S&P down in Sept, RSP -1.9% vs SPX +2.0% in Q3; VIX
#   15.5; $30-33B pension sell executed Sep 30; CTA now asymmetric to the upside;
#   blackout reopens ~Oct 13.
#   AI/credit: Micron $54.2B / guide $61.5B / FY27 capex >$40B; no DRAM rollover;
#   ORCL CDS 227 record, 2046/2056 bonds >8%; SoftBank $10B to OpenAI funded Oct 1
#   (SB CDS >400); Broadcom >$60B debt for Anthropic chips; Anthropic IPO mid-Nov
#   up to $2T; gates all 5% again (OTIC 39%, BCRED ~10%, ADS 14.7%); OWL -46% YTD;
#   FRED HY 312, CCC 1,179; Burry rolled shorts into 2027 puts.
#   Geo: Iran plan rejected, delegation expelled, US counter via Qatar, third
#   carrier + 10K troops ordered, six tankers struck, Hormuz ~1 transit/day;
#   Brent nonetheless $99.7 (-5.7% w/w); Russia's largest grid strike; Xi truce to
#   Jan 10; Taiwan $14B package 'in abeyance'; COFER 56.7%; DXY 102.2 high; gold
#   $4,217 (+8.5% y/y); Powell 'should be forced to resign' (Trump, after the IG
#   cleared him); AP-NORC approval 31/69.
#
# FACT-CHECK (a viral post claiming 'US bonds have no buyers'): Goldman's TRADING
#   DESK (Privorotsky) called long bonds 'completely unwanted'/'bidless' = desk
#   colour, not research, and 'no buyers' is contradicted by the 7Y cover of 2.42
#   and $46.4B of buyback offers (PARTLY TRUE). Bessent's quotes are real but
#   spliced from three dates: 'I am the house' (SMU, Sep 8, about the YEN),
#   'illiquid period' (House FSC Sep 15 / CNBC Sep 10), buybacks $2B -> $4B ->
#   $6B (TRUE as a sequence; not raised again; no confirmed discrete TGA draw).
#   10Y toward 5.3 / 30Y higher: TRUE. Japan selling: TRUE in direction (TIC -$106B
#   May-Jul) with the FIMA-repo nuance. 'Yuto Kanzaki' / 'Bessent took over BoJ
#   operations': FALSE -- no such official exists; the only source is the post.
#   'Bidless short end': FALSE -- bills covered 2.7-2.8x, MMF assets record $7.98T.
#
# PROBABILITIES: Muddle 26 | Repression 20 | AI Bust 18 | Second Wave 19 |
#   Escape 12 | Fracture 5   (Sep 28: 26/19/19/19/12/5)
#   Repression +1: the Fed stopped hiking on a +29K payroll with headline PCE 3.4
#     and consumer inflation expectations at 6.1 -- the Burns move is one meeting
#     closer, and a long end that bear-steepens on weak data is how the market
#     prices that. AI Bust -1: no tripwire crossed, Micron/DRAM pricing firm, NDX at
#     a record; the capital-cycle supply response (Micron capex >$40B) is a 2027-28
#     story, which the timing engine already carries. Second Wave unchanged at 19:
#     the intervention-fails clause fired a fourth time and the original 30Y rule
#     confirmed, offset by the hike leg of the policy-error path dropping out.
#     Muddle unchanged: NDX record, oil <$100, no shutdown, CTA upside asymmetry
#     and the blackout ending mid-Oct against the worst breadth at a near-record
#     index in decades and 7.28% mortgages.
#
# TIMING (judgment prior; the engine's posterior is in hazard_report.md): crash
#   distribution unchanged 8/14/38/21/19, modal month October 2027. Correction
#   >=10% before the Nov 4 QRA: ~40% (from 45%) -- the October hike is dead, oil
#   is under $100, the pension sell is done and the blackout lifts Oct 13, against
#   the Oct 7-8 auctions and a 30Y at 5.63. Modal correction month moves to
#   NOVEMBER 2026 (post-QRA / post-election) from October. P(Aug 26-27 record is
#   THE cycle high): ~20% (from 25%) with NDX at a record and the S&P 0.9% below.
#
# PROSPECTIVE (never retroactive): credit = max(spread band, PC band) (above);
#   saving-rate clause <4.0% on the revised series; 30Y reverts on 5 closes <5.30;
#   forensic -> 3 on any one more confirmation; reserve erosion -> 1 if COFER Q3
#   (Dec) >57.5% with gold y/y <20%. Data conflicts open: 5Y tail 0.7 vs 3.1bp;
#   OAT-Bund 94.7 vs 130bp; COF 30+ 4.54 vs 3.57; student-loan garnishment status.
# NEXT: Oct 6 3Y; Oct 7 $39B 10Y; Oct 8 $22B 30Y + Car-Mart sixth deadline; ~Oct 13
#   banks + blackout lifts; Oct 14 CPI; Oct 15 margin debt / COF; Oct 16 Aug TIC;
#   Oct 25-28 Oracle AI World; Oct 27-28 FOMC; Oct 30 BOJ; Nov 3-4.
