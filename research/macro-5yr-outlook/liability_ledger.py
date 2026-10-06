#!/usr/bin/env python3
"""
Liability-Event Ledger  (v0.1, 2026-09-28)
==========================================

The Hertz 2020 sequence, formalized as a schema and applied to today's leveraged
structures. Hertz was not "a bad credit that went bankrupt"; it was a DATED chain:

  obligation due (Apr 27 lease payment) -> missed -> automatic trigger (May 5
  amortization event on the ABS notes) -> creditors grant a WAIVER/FORBEARANCE
  with an EXPIRY (May 22) -> liquidity need with no viable solution -> filing on
  the expiry date itself (Petition Date May 22, 2020).

Every entry below records the same nine fields. The Hertz-likeness score rewards
exactly the things that made that trade knowable in advance:

  dated obligation (0-2) | already missed / technical default (0-2) |
  forbearance or waiver in place WITH an expiry date (0-2) |
  automatic consequence on expiry defined in the documents (0-1) |
  liquidity demonstrably short of the obligation (0-2) |
  tradable, liquid put market on the entity or a clean proxy (0-1)     -> max 10

Tags: V = verified in the research record (dated source), E = estimate,
NF = not found / must be verified from the filing before acting.
This is an analytical ledger. It is not investment advice.
"""
from dataclasses import dataclass, field
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent

@dataclass
class Liability:
    entity: str
    obligation: str            # what is due
    amount: str                # size
    due: str                   # date it was/is due
    missed: str                # has it been missed / technical default? (with date)
    grace: str                 # grace period / cure period in the documents
    forbearance: str           # who granted an extension / waiver
    expiry: str                # when the extension expires  <- THE DATE
    consequence: str           # what happens automatically on expiry
    liquidity: str             # cash / capacity vs the obligation
    put_market: str            # instrument to express it, liquidity, IV
    score: dict                # the six rubric scores
    tags: str                  # V/E/NF summary
    next_check: str            # the next observable
    note: str = ""

    @property
    def hertz_score(self) -> int:
        return sum(self.score.values())

LEDGER = [
    Liability("HERTZ (2020) — calibration template", "operating-lease payment to the vehicle-financing vehicle (HVF II)", "~$400M/month lease + ABS amortization",
              "2020-04-27", "YES — missed Apr 27, 2020", "none effective: missed payment = amortization event on the ABS notes (May 5)",
              "lenders + ABS noteholders: waiver and forbearance agreements signed May 4, 2020", "2020-05-22",
              "on expiry, noteholders could enforce against the fleet; no refinancing available in a shut rental market -> Chapter 11 filed on the expiry date",
              "cash ~$1B vs ~$17B of vehicle debt with collateral values falling 20-30%; revenue -70%",
              "HTZ listed puts, liquid; IV >150% after Apr 27 (the trade was cheapest BEFORE the missed payment was public)",
              dict(dated=2, missed=2, forbearance=2, consequence=1, liquidity=2, puts=1), "historical, V",
              "n/a", "The lesson: the tradable edge was knowing (a) the obligation date, (b) that the cash was not there, (c) the expiry of the waiver. Price followed the calendar."),
    Liability("America's Car-Mart (CRMT)", "$300M revolving/ABL facility with Silver Point Finance; covenant compliance and going-concern language",
              "$300M facility; going-concern qualification (V)", "covenant/waiver dates Sep 4 -> Sep 11 -> Sep 25 -> Oct 1 (V)",
              "TECHNICAL: in waiver since early September; lenders 'gave four more days' twice (8-K Sep 24, V)", "none beyond the waivers themselves",
              "Silver Point Finance and lender group: FIVE consecutive short waivers; 8-K dated Sep 30 extends the scheduled termination date and minimum-liquidity / collateral-coverage relief (V)", "2026-10-08 (fifth extension; was Oct 1)",
              "if no further waiver: facility default -> acceleration -> the company said bankruptcy is 'an option' (V); ABS trust triggers on the securitizations would follow (E)",
              "liquidity dependent on the facility; earlier record: covenant runway to Nov 6; 'failed rescue' story substance NF",
              "CRMT listed options exist but are THIN (small cap); expect wide spreads and IV >100%; shares already reflect distress -> asymmetric only if a filing is not fully priced (NF: quotes)",
              dict(dated=2, missed=1, forbearance=2, consequence=1, liquidity=2, puts=0), "V for dates; NF for option liquidity and current cash",
              "Oct 8: sixth waiver or default notice (weekly waivers are now the pattern; Hertz's lenders also extended before they stopped)", "The closest live match to the Hertz template on structure. The problem is expression: the equity is small and already distressed, so the put payoff is capped by what is already priced. Its systemic value is as the FIRST-CRACK signal for subprime auto (ledger row below)."),
    Liability("Oracle — Project Jupiter (New Mexico, OpenAI capacity)", "rent under the Jupiter lease to the Blue Owl/STACK vehicle; ~$18B of project loans backing the campus",
              "$165B campus; ~$18B project loans quoted 89-91 (V)", "rent commencement tied to construction milestones; gas-pipeline slip to Feb 2027 (V)",
              "CONTRACTUAL: Oracle invoked FORCE MAJEURE Sep 24, 2026 and is seeking a ~3-year rent deferral (V, Bloomberg)",
              "force-majeure clause = the grace period; duration and cure NF", "Blue Owl/STACK: 'fully aligned... financial commitments unchanged' (V) = a forbearance in substance; project lenders' response NF",
              "NF — the lease/loan documents' cure period and the lenders' waiver expiry are the dates to find (EDGAR exhibit or Bloomberg)",
              "if lenders do not waive: project-loan default -> Blue Owl equity impaired -> Oracle's RPO ($664B) partially unbacked; if they waive: the deferral moves ~$X of rent into 2028-30 (E)",
              "Oracle FY27 capex $90-95B vs negative FCF (-$42B guide); ATM exhausted; a separate $2.2B lessor guarantee matured Sep-26 (outcome NF) alongside the $3.3B guarantee (V); CDS record ~227bp Sep 25 (V); 2046/2056 bonds >8% YTM, ~50bp wide of B2 paper (V); AI World Oct 25-28",
              "ORCL listed puts, deep and liquid; 30d IV ~60-70 (V, Sep); Dec-27 15%-OTM costs ~14% of spot in the model; spreads (85/55) ~10%. OWL (Blue Owl) puts liquid, lower IV. Also: project-loan marks are the leading indicator (not tradable)",
              dict(dated=1, missed=2, forbearance=1, consequence=1, liquidity=2, puts=1), "V for the event; NF for the cure/waiver dates",
              "Oracle AI World / investor day (mid-Oct, date NF); any 8-K Item 1.01/2.04; Jupiter loan quotes; Blue Owl BDC Q3 marks", "The single most important Tier-1 event in the AI chain. The Hertz question is: WHEN does the force-majeure protection lapse and what is the cure date? That date is not in the record yet and is the highest-value research item."),
    Liability("OpenAI (private) — via ORCL / SoftBank / MSFT / NVDA / CRWV", "$10B tranche from SoftBank due Oct 1 (funded by SoftBank's $11.1B junk bond, priced Sep 23, V); compute commitments ~$856B through 2030 (V, deck)",
              "$10B Oct 1; FCF -$278B 2026-30; 'cash out by 2028' (V)", "2026-10-01 (SoftBank tranche); 2027 mega-round (>$1.2T ask, V); 2028 cash exhaustion (V)",
              "no — the $10B tranche FUNDED Oct 1 (SoftBank release, V): $30B program complete, ~13% stake; the risk is the 2027 round", "n/a (equity rounds have no grace period; compute contracts do — terms NF)",
              "SoftBank (junk-funded), sovereign funds; vendors (NVDA/ORCL/MSFT) via prepayments and guarantees (V)", "2027 round; contract milestones NF",
              "if the 2027 round fails or shrinks: Oracle RPO, MSFT Azure commitment, NVDA 12GW commitments all rest on it (V, deck)",
              "burning >$50B/yr against a $10B tranche; the vendors ARE the liquidity (circular)",
              "no direct puts; ORCL (largest single dependency), SoftBank 9984 JP (US retail access limited), CRWV, NVDA (least sensitive)",
              dict(dated=1, missed=0, forbearance=1, consequence=1, liquidity=2, puts=1), "V for amounts; NF for contract terms",
              "Oct 1 wire confirmation; Q4 round talk; Oracle RPO disclosure Dec", "Not a Hertz pattern yet: nothing has been missed. It becomes one the day a compute-contract milestone or a round closing date slips."),
    Liability("CoreWeave (CRWV) — GPU-collateralized delayed-draw term loans", "DDTL amortization tied to contracted GPU revenue; $4.2B 2.875% convert (V); tenant paper at 9.25% (V)",
              "~$12-15B of secured debt (E); convert $4.2B (V)", "amortization monthly/quarterly per DDTL schedules (NF exact)",
              "no missed payments in the record", "typical 30-day cure on interest; collateral-coverage tests quarterly (E)",
              "none needed yet", "NF — the DDTL collateral-coverage test dates and the 2027 maturities are the dates to find",
              "collateral-coverage breach -> mandatory prepayment / cash sweep -> equity value to lenders (E)",
              "CDS ~855bp (V); bonds ~13% (V); tenant paper 9.25% = the market is already pricing it",
              "CRWV puts liquid; IV ~80-88 (model) -> expensive; Dec-27 70/25 spread ~15% of spot for ~1.1x EV in the model",
              dict(dated=1, missed=0, forbearance=0, consequence=1, liquidity=1, puts=1), "V for prices; NF for schedules",
              "10-Q covenant disclosures; any DDTL amendment 8-K", "Priced. The Hertz edge requires a date the market has not found; CRWV's dates are in its filings and the CDS says the market has read them."),
    Liability("Non-traded BDCs / private-credit funds (BCRED, OBDC, HLEND, ADS, ASIF)", "quarterly redemption windows; NAV-based gates at 5% of NAV per quarter (V)",
              "~$500B of non-traded BDC/interval AUM (E); 5%/qtr = ~$25B/qtr (E)", "Oct 1, 2026 (Q3 windows, V); Jan 1, 2027",
              "GATES = the forbearance: Oct 1 windows all capped at 5% again -- OTIC 39% requested (flat), OCIC 16.8%, BCRED ~10%, ADS 14.7%, HLEND ~11.5%, ASIF 11.6%; requests easing except AI/tech lending (V)", "the 5% cap is the structure; no cure",
              "the funds themselves, by gating; sponsors (Blue Owl, Blackstone, Ares, Apollo)", "each quarter-end; the second wave is Jan 1, 2027 (E)",
              "sustained gates -> secondary discounts -> fundraising stops -> forced sales into a bid-less market -> marks -> insurer/pension writedowns (the Tier-1 event the credit indicator waits for)",
              "Fitch PC default 6.3% record (V); OBDC mark at 5c (V); listed BDCs ~25% below NAV (V) = the market's own mark",
              "listed proxies: OWL (Blue Owl, the most concentrated node), ARCC, OBDC, BXSL, KKR/APO/BX (managers). Puts liquid on the managers; IV moderate (30-45, E)",
              dict(dated=2, missed=1, forbearance=2, consequence=1, liquidity=1, puts=1), "V for gates; E for sizes",
              "Oct 1-10: redemption-request disclosures; Q3 NAV marks (Nov); any insurer 10-Q writedown", "Structurally the best Hertz analogue in the system: a dated window, a cap already binding, and a documented consequence. The expression is the managers, not the funds."),
    Liability("Credit Acceptance (CACC) / subprime auto ABS", "$710M 40-AG settlement incl. $634M balance waivers (V); ABS BB-tranche spreads; Fitch subprime 60+ 6.13% (V)",
              "$710M (V)", "settlement dated Sep 17 (V); ABS trigger tests monthly",
              "no missed payment; a regulatory hit", "ABS deals: cumulative-net-loss and delinquency triggers (deal-specific, NF)",
              "n/a", "NF — first ABS deal to hit a CNL trigger is the date",
              "trigger breach -> early amortization -> the originator loses funding (the Tricolor path, V)",
              "adequate for CACC; the issue is the WEAKER issuers (Car-Mart first)",
              "CACC puts moderately liquid; IV ~40-50 (E)",
              dict(dated=1, missed=0, forbearance=0, consequence=1, liquidity=1, puts=1), "V for settlement; NF for ABS triggers",
              "monthly ABS servicer reports; Fitch August index (still missing)", "Second-order. The Hertz date here is a trustee report, not a court filing."),
    Liability("US Treasury — long-end clearing (not a default; a forced-action clock)", "~$11.8T repricing over 12 months at ~5.1% vs a 3.41% average coupon (V/E); 30Y auction Oct 8; QRA Nov 4 (V)",
              "$2.1T deficit + ~$9.7T rollover (V/E)", "Oct 8 (30Y auction); Nov 4 (refunding); each buyback op",
              "the Sep 24 buyback failed to hold (30Y 5.56 two sessions later, V) = the sovereign version of a missed payment", "n/a",
              "Treasury (buybacks, $4-6B/op) and the Fed (none)", "Nov 4 QRA: the next chance to change coupon sizes (V)",
              "a tailed 30Y (>=4bp, cover <2.2) or a QRA that raises long coupons into 5.5% = the auction-stress trigger -> Crisis Gate proximity",
              "residual private absorption ~$0.75T/yr (E)", "TLT/TBT and long-bond futures options: liquid; index puts (SPX/QQQ) for the equity transmission; MOVE cannot be traded directly by retail",
              dict(dated=2, missed=1, forbearance=1, consequence=1, liquidity=1, puts=1), "V for dates",
              "Oct 8 auction stats; Nov 4 QRA sizes; buyback fill ratios", "The engine's primary transmission. Not a bankruptcy, but the same logic: a dated auction, a demonstrated shortfall of demand, and a defined trigger."),
    Liability("SoftBank (9984 JP) — OpenAI funding chain", "$11.1B junk bond (largest ever, sub-10%, V) funding a $10B OpenAI tranche Oct 1; margin loans against ARM stake (E)",
              "$11.1B (V)", "Oct 1 wire (V); coupon dates semi-annual (E)",
              "no", "30-day cure on bonds (E)", "n/a", "NF",
              "if OpenAI's 2027 round fails: SoftBank's stake marks -> bond spreads -> ARM margin loans (E)",
              "funding equity with 9-10% junk (V) = the Lucent/Nortel vendor-finance shape",
              "9984 puts (Tokyo) — poor access for US retail; proxy: ARM puts (liquid), SFTBY (no options)",
              dict(dated=1, missed=0, forbearance=0, consequence=1, liquidity=1, puts=0), "V for the bond",
              "Oct 1; ARM lock-up/margin disclosures", "Circular-funding node; expression is indirect."),
    Liability("Micron / DRAM contract pricing (capital-cycle tell, not a liability)", "FQ4 print Sep 30 AMC; guide vs $50B/$31 (V); consensus above guide (V); Acer CEO 'no shortage' (V); Burry short in size (V)",
              "n/a", "2026-09-30", "n/a", "n/a", "n/a", "n/a",
              "a DRAM contract-price rollover confirmed by two producers = a forensic tripwire confirmation (engine B) and the start of the capital-cycle down-leg",
              "n/a", "MU puts very liquid; IV elevated into the print (level NF); SOXX/SMH puts liquid (IV ~33)",
              dict(dated=2, missed=0, forbearance=0, consequence=1, liquidity=0, puts=1), "V",
              "Sep 30 4:30pm ET call; TrendForce 4Q26 numbers", "An event clock, not a liability clock. Included because it is the first dated test of the capital-cycle indicator."),
]

def render() -> str:
    L = []; A = L.append
    A("# Liability-Event Ledger — Hertz-pattern candidates, 2026-09-28\n")
    A("Schema per entry: obligation · amount · due · missed? · grace · forbearance (who) · **expiry (the date)** · automatic consequence · liquidity vs obligation · put market. Hertz-likeness score /10 = dated obligation 2 + already missed 2 + forbearance with expiry 2 + consequence defined 1 + liquidity short 2 + tradable puts 1.\n")
    A("| Entity | Score | The date | Missed / technical default | Forbearance & expiry | Consequence on expiry | Expression | Next check |\n|---|---:|---|---|---|---|---|---|")
    for l in sorted(LEDGER, key=lambda x: -x.hertz_score):
        A(f"| **{l.entity}** | {l.hertz_score} | {l.due} | {l.missed} | {l.forbearance} → **{l.expiry}** | {l.consequence} | {l.put_market} | {l.next_check} |")
    A("\n## Detail\n")
    for l in sorted(LEDGER, key=lambda x: -x.hertz_score):
        A(f"### {l.entity} — Hertz score {l.hertz_score}/10  ({l.tags})\n")
        A(f"- Obligation: {l.obligation}\n- Amount: {l.amount}\n- Due: {l.due}\n- Missed: {l.missed}\n- Grace: {l.grace}\n- Forbearance: {l.forbearance}\n- **Expiry: {l.expiry}**\n- Consequence: {l.consequence}\n- Liquidity: {l.liquidity}\n- Put market: {l.put_market}\n- Rubric: {l.score}\n- Next check: {l.next_check}\n- Note: {l.note}\n")
    A("## Search protocol — where the dates live (run weekly)\n")
    A("""1. **SEC 8-K Item 2.04** "Triggering Events That Accelerate or Increase a Direct Financial Obligation" — the missed-payment / acceleration filing. Item 1.01 for waiver, forbearance and amendment agreements (the expiry date is in the exhibit). Item 2.03 for new obligations.
2. **EDGAR full-text search** (efts): `"forbearance agreement"`, `"waiver" AND "credit agreement" AND "through"` (the date follows "through"), `"going concern"`, `"substantial doubt"`, `"cure period"`, `"amortization event"`, `"rapid amortization"`, `"force majeure"`, `"rent deferral"`, `"payment-in-kind" AND "election"`, `NT 10-Q` / `NT 10-K` (late filings are the Hertz-April-27 of reporting).
3. **ABS trustee / servicer reports** (monthly, on the trustee's site or Bloomberg): cumulative-net-loss and delinquency triggers, early-amortization events, overcollateralization tests. The auto-ABS and data-center-ABS triggers are where Tricolor and the DC paper will show first.
4. **Indenture mechanics**: 30-day interest grace (bonds), 5-business-day (loans); quarter-end covenant tests reported ~45 days later (10-Q); springing maturities (a 2028 bond that springs to 2027 if the 2027 loan is not refinanced 91 days before) — the springing date is the real date.
5. **Private credit**: BDC 10-Q/10-K non-accruals and PIK share; quarterly redemption-request disclosures (first two weeks of the quarter); gate press releases; insurer statutory filings (Schedule BA) for private-credit marks.
6. **Project finance / SPVs**: lender syndication status (Bloomberg/LevFin), rent-commencement dates in lease exhibits, completion guarantees and their maturity (Oracle's $3.3B lessor guarantee is this).
7. **Sovereign**: TreasuryDirect auction results (tail, cover, dealer take), buyback results (fill ratio), QRA (coupon sizes), primary-dealer positioning (NY Fed), fails (DTCC).
8. **Rating actions and CDS**: a downgrade to CCC or a CDS above 1,000bp is the market reading the calendar; the edge is gone by then. The edge is items 1-6 BEFORE item 8.

Rule from Hertz: buy the puts on the missed payment, not on the filing. On April 27, 2020 the obligation was missed; on May 22 the waiver expired. The cheap entry was the day the obligation was known to be unpayable, which was visible in the March 10-K and the April 8-K, weeks before the price finished moving.""")
    return "\n".join(L)

if __name__ == "__main__":
    (HERE / "liability_ledger.md").write_text(render())
    (HERE / "liability_ledger.json").write_text(json.dumps([dict(entity=l.entity, score=l.hertz_score, expiry=l.expiry, due=l.due, next_check=l.next_check, put_market=l.put_market) for l in LEDGER], indent=1))
    for l in sorted(LEDGER, key=lambda x: -x.hertz_score):
        print(f"{l.hertz_score:>2}/10  {l.entity:<70} expiry: {l.expiry}")
