# Liability-Event Ledger — Hertz-pattern candidates, 2026-09-28

Schema per entry: obligation · amount · due · missed? · grace · forbearance (who) · **expiry (the date)** · automatic consequence · liquidity vs obligation · put market. Hertz-likeness score /10 = dated obligation 2 + already missed 2 + forbearance with expiry 2 + consequence defined 1 + liquidity short 2 + tradable puts 1.

| Entity | Score | The date | Missed / technical default | Forbearance & expiry | Consequence on expiry | Expression | Next check |
|---|---:|---|---|---|---|---|---|
| **HERTZ (2020) — calibration template** | 10 | 2020-04-27 | YES — missed Apr 27, 2020 | lenders + ABS noteholders: waiver and forbearance agreements signed May 4, 2020 → **2020-05-22** | on expiry, noteholders could enforce against the fleet; no refinancing available in a shut rental market -> Chapter 11 filed on the expiry date | HTZ listed puts, liquid; IV >150% after Apr 27 (the trade was cheapest BEFORE the missed payment was public) | n/a |
| **America's Car-Mart (CRMT)** | 8 | covenant/waiver dates Sep 4 -> Sep 11 -> Sep 25 -> Oct 1 (V) | TECHNICAL: in waiver since early September; lenders 'gave four more days' twice (8-K Sep 24, V) | Silver Point Finance and lender group: four consecutive short waivers (V) → **2026-10-01** | if no further waiver: facility default -> acceleration -> the company said bankruptcy is 'an option' (V); ABS trust triggers on the securitizations would follow (E) | CRMT listed options exist but are THIN (small cap); expect wide spreads and IV >100%; shares already reflect distress -> asymmetric only if a filing is not fully priced (NF: quotes) | Oct 1 8-K: fifth waiver or default notice |
| **Oracle — Project Jupiter (New Mexico, OpenAI capacity)** | 8 | rent commencement tied to construction milestones; gas-pipeline slip to Feb 2027 (V) | CONTRACTUAL: Oracle invoked FORCE MAJEURE Sep 24, 2026 and is seeking a ~3-year rent deferral (V, Bloomberg) | Blue Owl/STACK: 'fully aligned... financial commitments unchanged' (V) = a forbearance in substance; project lenders' response NF → **NF — the lease/loan documents' cure period and the lenders' waiver expiry are the dates to find (EDGAR exhibit or Bloomberg)** | if lenders do not waive: project-loan default -> Blue Owl equity impaired -> Oracle's RPO ($664B) partially unbacked; if they waive: the deferral moves ~$X of rent into 2028-30 (E) | ORCL listed puts, deep and liquid; 30d IV ~60-70 (V, Sep); Dec-27 15%-OTM costs ~14% of spot in the model; spreads (85/55) ~10%. OWL (Blue Owl) puts liquid, lower IV. Also: project-loan marks are the leading indicator (not tradable) | Oracle AI World / investor day (mid-Oct, date NF); any 8-K Item 1.01/2.04; Jupiter loan quotes; Blue Owl BDC Q3 marks |
| **Non-traded BDCs / private-credit funds (BCRED, OBDC, HLEND, ADS, ASIF)** | 8 | Oct 1, 2026 (Q3 windows, V); Jan 1, 2027 | GATES = the forbearance: every tracked perpetual BDC capped at 5% for 2-3 quarters (V) | the funds themselves, by gating; sponsors (Blue Owl, Blackstone, Ares, Apollo) → **each quarter-end; the second wave is Jan 1, 2027 (E)** | sustained gates -> secondary discounts -> fundraising stops -> forced sales into a bid-less market -> marks -> insurer/pension writedowns (the Tier-1 event the credit indicator waits for) | listed proxies: OWL (Blue Owl, the most concentrated node), ARCC, OBDC, BXSL, KKR/APO/BX (managers). Puts liquid on the managers; IV moderate (30-45, E) | Oct 1-10: redemption-request disclosures; Q3 NAV marks (Nov); any insurer 10-Q writedown |
| **US Treasury — long-end clearing (not a default; a forced-action clock)** | 7 | Oct 8 (30Y auction); Nov 4 (refunding); each buyback op | the Sep 24 buyback failed to hold (30Y 5.56 two sessions later, V) = the sovereign version of a missed payment | Treasury (buybacks, $4-6B/op) and the Fed (none) → **Nov 4 QRA: the next chance to change coupon sizes (V)** | a tailed 30Y (>=4bp, cover <2.2) or a QRA that raises long coupons into 5.5% = the auction-stress trigger -> Crisis Gate proximity | TLT/TBT and long-bond futures options: liquid; index puts (SPX/QQQ) for the equity transmission; MOVE cannot be traded directly by retail | Oct 8 auction stats; Nov 4 QRA sizes; buyback fill ratios |
| **OpenAI (private) — via ORCL / SoftBank / MSFT / NVDA / CRWV** | 6 | 2026-10-01 (SoftBank tranche); 2027 mega-round (>$1.2T ask, V); 2028 cash exhaustion (V) | no — Oct 1 is funded; the risk is the 2027 round | SoftBank (junk-funded), sovereign funds; vendors (NVDA/ORCL/MSFT) via prepayments and guarantees (V) → **2027 round; contract milestones NF** | if the 2027 round fails or shrinks: Oracle RPO, MSFT Azure commitment, NVDA 12GW commitments all rest on it (V, deck) | no direct puts; ORCL (largest single dependency), SoftBank 9984 JP (US retail access limited), CRWV, NVDA (least sensitive) | Oct 1 wire confirmation; Q4 round talk; Oracle RPO disclosure Dec |
| **CoreWeave (CRWV) — GPU-collateralized delayed-draw term loans** | 4 | amortization monthly/quarterly per DDTL schedules (NF exact) | no missed payments in the record | none needed yet → **NF — the DDTL collateral-coverage test dates and the 2027 maturities are the dates to find** | collateral-coverage breach -> mandatory prepayment / cash sweep -> equity value to lenders (E) | CRWV puts liquid; IV ~80-88 (model) -> expensive; Dec-27 70/25 spread ~15% of spot for ~1.1x EV in the model | 10-Q covenant disclosures; any DDTL amendment 8-K |
| **Credit Acceptance (CACC) / subprime auto ABS** | 4 | settlement dated Sep 17 (V); ABS trigger tests monthly | no missed payment; a regulatory hit | n/a → **NF — first ABS deal to hit a CNL trigger is the date** | trigger breach -> early amortization -> the originator loses funding (the Tricolor path, V) | CACC puts moderately liquid; IV ~40-50 (E) | monthly ABS servicer reports; Fitch August index (still missing) |
| **Micron / DRAM contract pricing (capital-cycle tell, not a liability)** | 4 | 2026-09-30 | n/a | n/a → **n/a** | a DRAM contract-price rollover confirmed by two producers = a forensic tripwire confirmation (engine B) and the start of the capital-cycle down-leg | MU puts very liquid; IV elevated into the print (level NF); SOXX/SMH puts liquid (IV ~33) | Sep 30 4:30pm ET call; TrendForce 4Q26 numbers |
| **SoftBank (9984 JP) — OpenAI funding chain** | 3 | Oct 1 wire (V); coupon dates semi-annual (E) | no | n/a → **NF** | if OpenAI's 2027 round fails: SoftBank's stake marks -> bond spreads -> ARM margin loans (E) | 9984 puts (Tokyo) — poor access for US retail; proxy: ARM puts (liquid), SFTBY (no options) | Oct 1; ARM lock-up/margin disclosures |

## Detail

### HERTZ (2020) — calibration template — Hertz score 10/10  (historical, V)

- Obligation: operating-lease payment to the vehicle-financing vehicle (HVF II)
- Amount: ~$400M/month lease + ABS amortization
- Due: 2020-04-27
- Missed: YES — missed Apr 27, 2020
- Grace: none effective: missed payment = amortization event on the ABS notes (May 5)
- Forbearance: lenders + ABS noteholders: waiver and forbearance agreements signed May 4, 2020
- **Expiry: 2020-05-22**
- Consequence: on expiry, noteholders could enforce against the fleet; no refinancing available in a shut rental market -> Chapter 11 filed on the expiry date
- Liquidity: cash ~$1B vs ~$17B of vehicle debt with collateral values falling 20-30%; revenue -70%
- Put market: HTZ listed puts, liquid; IV >150% after Apr 27 (the trade was cheapest BEFORE the missed payment was public)
- Rubric: {'dated': 2, 'missed': 2, 'forbearance': 2, 'consequence': 1, 'liquidity': 2, 'puts': 1}
- Next check: n/a
- Note: The lesson: the tradable edge was knowing (a) the obligation date, (b) that the cash was not there, (c) the expiry of the waiver. Price followed the calendar.

### America's Car-Mart (CRMT) — Hertz score 8/10  (V for dates; NF for option liquidity and current cash)

- Obligation: $300M revolving/ABL facility with Silver Point Finance; covenant compliance and going-concern language
- Amount: $300M facility; going-concern qualification (V)
- Due: covenant/waiver dates Sep 4 -> Sep 11 -> Sep 25 -> Oct 1 (V)
- Missed: TECHNICAL: in waiver since early September; lenders 'gave four more days' twice (8-K Sep 24, V)
- Grace: none beyond the waivers themselves
- Forbearance: Silver Point Finance and lender group: four consecutive short waivers (V)
- **Expiry: 2026-10-01**
- Consequence: if no further waiver: facility default -> acceleration -> the company said bankruptcy is 'an option' (V); ABS trust triggers on the securitizations would follow (E)
- Liquidity: liquidity dependent on the facility; earlier record: covenant runway to Nov 6; 'failed rescue' story substance NF
- Put market: CRMT listed options exist but are THIN (small cap); expect wide spreads and IV >100%; shares already reflect distress -> asymmetric only if a filing is not fully priced (NF: quotes)
- Rubric: {'dated': 2, 'missed': 1, 'forbearance': 2, 'consequence': 1, 'liquidity': 2, 'puts': 0}
- Next check: Oct 1 8-K: fifth waiver or default notice
- Note: The closest live match to the Hertz template on structure. The problem is expression: the equity is small and already distressed, so the put payoff is capped by what is already priced. Its systemic value is as the FIRST-CRACK signal for subprime auto (ledger row below).

### Oracle — Project Jupiter (New Mexico, OpenAI capacity) — Hertz score 8/10  (V for the event; NF for the cure/waiver dates)

- Obligation: rent under the Jupiter lease to the Blue Owl/STACK vehicle; ~$18B of project loans backing the campus
- Amount: $165B campus; ~$18B project loans quoted 89-91 (V)
- Due: rent commencement tied to construction milestones; gas-pipeline slip to Feb 2027 (V)
- Missed: CONTRACTUAL: Oracle invoked FORCE MAJEURE Sep 24, 2026 and is seeking a ~3-year rent deferral (V, Bloomberg)
- Grace: force-majeure clause = the grace period; duration and cure NF
- Forbearance: Blue Owl/STACK: 'fully aligned... financial commitments unchanged' (V) = a forbearance in substance; project lenders' response NF
- **Expiry: NF — the lease/loan documents' cure period and the lenders' waiver expiry are the dates to find (EDGAR exhibit or Bloomberg)**
- Consequence: if lenders do not waive: project-loan default -> Blue Owl equity impaired -> Oracle's RPO ($664B) partially unbacked; if they waive: the deferral moves ~$X of rent into 2028-30 (E)
- Liquidity: Oracle FY27 capex $90-95B vs negative FCF (-$42B guide); ATM exhausted; $3.3B lessor guarantee matured Sep-26 with no refi print (V); CDS at a record (V)
- Put market: ORCL listed puts, deep and liquid; 30d IV ~60-70 (V, Sep); Dec-27 15%-OTM costs ~14% of spot in the model; spreads (85/55) ~10%. OWL (Blue Owl) puts liquid, lower IV. Also: project-loan marks are the leading indicator (not tradable)
- Rubric: {'dated': 1, 'missed': 2, 'forbearance': 1, 'consequence': 1, 'liquidity': 2, 'puts': 1}
- Next check: Oracle AI World / investor day (mid-Oct, date NF); any 8-K Item 1.01/2.04; Jupiter loan quotes; Blue Owl BDC Q3 marks
- Note: The single most important Tier-1 event in the AI chain. The Hertz question is: WHEN does the force-majeure protection lapse and what is the cure date? That date is not in the record yet and is the highest-value research item.

### Non-traded BDCs / private-credit funds (BCRED, OBDC, HLEND, ADS, ASIF) — Hertz score 8/10  (V for gates; E for sizes)

- Obligation: quarterly redemption windows; NAV-based gates at 5% of NAV per quarter (V)
- Amount: ~$500B of non-traded BDC/interval AUM (E); 5%/qtr = ~$25B/qtr (E)
- Due: Oct 1, 2026 (Q3 windows, V); Jan 1, 2027
- Missed: GATES = the forbearance: every tracked perpetual BDC capped at 5% for 2-3 quarters (V)
- Grace: the 5% cap is the structure; no cure
- Forbearance: the funds themselves, by gating; sponsors (Blue Owl, Blackstone, Ares, Apollo)
- **Expiry: each quarter-end; the second wave is Jan 1, 2027 (E)**
- Consequence: sustained gates -> secondary discounts -> fundraising stops -> forced sales into a bid-less market -> marks -> insurer/pension writedowns (the Tier-1 event the credit indicator waits for)
- Liquidity: Fitch PC default 6.3% record (V); OBDC mark at 5c (V); listed BDCs ~25% below NAV (V) = the market's own mark
- Put market: listed proxies: OWL (Blue Owl, the most concentrated node), ARCC, OBDC, BXSL, KKR/APO/BX (managers). Puts liquid on the managers; IV moderate (30-45, E)
- Rubric: {'dated': 2, 'missed': 1, 'forbearance': 2, 'consequence': 1, 'liquidity': 1, 'puts': 1}
- Next check: Oct 1-10: redemption-request disclosures; Q3 NAV marks (Nov); any insurer 10-Q writedown
- Note: Structurally the best Hertz analogue in the system: a dated window, a cap already binding, and a documented consequence. The expression is the managers, not the funds.

### US Treasury — long-end clearing (not a default; a forced-action clock) — Hertz score 7/10  (V for dates)

- Obligation: ~$11.8T repricing over 12 months at ~5.1% vs a 3.41% average coupon (V/E); 30Y auction Oct 8; QRA Nov 4 (V)
- Amount: $2.1T deficit + ~$9.7T rollover (V/E)
- Due: Oct 8 (30Y auction); Nov 4 (refunding); each buyback op
- Missed: the Sep 24 buyback failed to hold (30Y 5.56 two sessions later, V) = the sovereign version of a missed payment
- Grace: n/a
- Forbearance: Treasury (buybacks, $4-6B/op) and the Fed (none)
- **Expiry: Nov 4 QRA: the next chance to change coupon sizes (V)**
- Consequence: a tailed 30Y (>=4bp, cover <2.2) or a QRA that raises long coupons into 5.5% = the auction-stress trigger -> Crisis Gate proximity
- Liquidity: residual private absorption ~$0.75T/yr (E)
- Put market: TLT/TBT and long-bond futures options: liquid; index puts (SPX/QQQ) for the equity transmission; MOVE cannot be traded directly by retail
- Rubric: {'dated': 2, 'missed': 1, 'forbearance': 1, 'consequence': 1, 'liquidity': 1, 'puts': 1}
- Next check: Oct 8 auction stats; Nov 4 QRA sizes; buyback fill ratios
- Note: The engine's primary transmission. Not a bankruptcy, but the same logic: a dated auction, a demonstrated shortfall of demand, and a defined trigger.

### OpenAI (private) — via ORCL / SoftBank / MSFT / NVDA / CRWV — Hertz score 6/10  (V for amounts; NF for contract terms)

- Obligation: $10B tranche from SoftBank due Oct 1 (funded by SoftBank's $11.1B junk bond, priced Sep 23, V); compute commitments ~$856B through 2030 (V, deck)
- Amount: $10B Oct 1; FCF -$278B 2026-30; 'cash out by 2028' (V)
- Due: 2026-10-01 (SoftBank tranche); 2027 mega-round (>$1.2T ask, V); 2028 cash exhaustion (V)
- Missed: no — Oct 1 is funded; the risk is the 2027 round
- Grace: n/a (equity rounds have no grace period; compute contracts do — terms NF)
- Forbearance: SoftBank (junk-funded), sovereign funds; vendors (NVDA/ORCL/MSFT) via prepayments and guarantees (V)
- **Expiry: 2027 round; contract milestones NF**
- Consequence: if the 2027 round fails or shrinks: Oracle RPO, MSFT Azure commitment, NVDA 12GW commitments all rest on it (V, deck)
- Liquidity: burning >$50B/yr against a $10B tranche; the vendors ARE the liquidity (circular)
- Put market: no direct puts; ORCL (largest single dependency), SoftBank 9984 JP (US retail access limited), CRWV, NVDA (least sensitive)
- Rubric: {'dated': 1, 'missed': 0, 'forbearance': 1, 'consequence': 1, 'liquidity': 2, 'puts': 1}
- Next check: Oct 1 wire confirmation; Q4 round talk; Oracle RPO disclosure Dec
- Note: Not a Hertz pattern yet: nothing has been missed. It becomes one the day a compute-contract milestone or a round closing date slips.

### CoreWeave (CRWV) — GPU-collateralized delayed-draw term loans — Hertz score 4/10  (V for prices; NF for schedules)

- Obligation: DDTL amortization tied to contracted GPU revenue; $4.2B 2.875% convert (V); tenant paper at 9.25% (V)
- Amount: ~$12-15B of secured debt (E); convert $4.2B (V)
- Due: amortization monthly/quarterly per DDTL schedules (NF exact)
- Missed: no missed payments in the record
- Grace: typical 30-day cure on interest; collateral-coverage tests quarterly (E)
- Forbearance: none needed yet
- **Expiry: NF — the DDTL collateral-coverage test dates and the 2027 maturities are the dates to find**
- Consequence: collateral-coverage breach -> mandatory prepayment / cash sweep -> equity value to lenders (E)
- Liquidity: CDS ~855bp (V); bonds ~13% (V); tenant paper 9.25% = the market is already pricing it
- Put market: CRWV puts liquid; IV ~80-88 (model) -> expensive; Dec-27 70/25 spread ~15% of spot for ~1.1x EV in the model
- Rubric: {'dated': 1, 'missed': 0, 'forbearance': 0, 'consequence': 1, 'liquidity': 1, 'puts': 1}
- Next check: 10-Q covenant disclosures; any DDTL amendment 8-K
- Note: Priced. The Hertz edge requires a date the market has not found; CRWV's dates are in its filings and the CDS says the market has read them.

### Credit Acceptance (CACC) / subprime auto ABS — Hertz score 4/10  (V for settlement; NF for ABS triggers)

- Obligation: $710M 40-AG settlement incl. $634M balance waivers (V); ABS BB-tranche spreads; Fitch subprime 60+ 6.13% (V)
- Amount: $710M (V)
- Due: settlement dated Sep 17 (V); ABS trigger tests monthly
- Missed: no missed payment; a regulatory hit
- Grace: ABS deals: cumulative-net-loss and delinquency triggers (deal-specific, NF)
- Forbearance: n/a
- **Expiry: NF — first ABS deal to hit a CNL trigger is the date**
- Consequence: trigger breach -> early amortization -> the originator loses funding (the Tricolor path, V)
- Liquidity: adequate for CACC; the issue is the WEAKER issuers (Car-Mart first)
- Put market: CACC puts moderately liquid; IV ~40-50 (E)
- Rubric: {'dated': 1, 'missed': 0, 'forbearance': 0, 'consequence': 1, 'liquidity': 1, 'puts': 1}
- Next check: monthly ABS servicer reports; Fitch August index (still missing)
- Note: Second-order. The Hertz date here is a trustee report, not a court filing.

### Micron / DRAM contract pricing (capital-cycle tell, not a liability) — Hertz score 4/10  (V)

- Obligation: FQ4 print Sep 30 AMC; guide vs $50B/$31 (V); consensus above guide (V); Acer CEO 'no shortage' (V); Burry short in size (V)
- Amount: n/a
- Due: 2026-09-30
- Missed: n/a
- Grace: n/a
- Forbearance: n/a
- **Expiry: n/a**
- Consequence: a DRAM contract-price rollover confirmed by two producers = a forensic tripwire confirmation (engine B) and the start of the capital-cycle down-leg
- Liquidity: n/a
- Put market: MU puts very liquid; IV elevated into the print (level NF); SOXX/SMH puts liquid (IV ~33)
- Rubric: {'dated': 2, 'missed': 0, 'forbearance': 0, 'consequence': 1, 'liquidity': 0, 'puts': 1}
- Next check: Sep 30 4:30pm ET call; TrendForce 4Q26 numbers
- Note: An event clock, not a liability clock. Included because it is the first dated test of the capital-cycle indicator.

### SoftBank (9984 JP) — OpenAI funding chain — Hertz score 3/10  (V for the bond)

- Obligation: $11.1B junk bond (largest ever, sub-10%, V) funding a $10B OpenAI tranche Oct 1; margin loans against ARM stake (E)
- Amount: $11.1B (V)
- Due: Oct 1 wire (V); coupon dates semi-annual (E)
- Missed: no
- Grace: 30-day cure on bonds (E)
- Forbearance: n/a
- **Expiry: NF**
- Consequence: if OpenAI's 2027 round fails: SoftBank's stake marks -> bond spreads -> ARM margin loans (E)
- Liquidity: funding equity with 9-10% junk (V) = the Lucent/Nortel vendor-finance shape
- Put market: 9984 puts (Tokyo) — poor access for US retail; proxy: ARM puts (liquid), SFTBY (no options)
- Rubric: {'dated': 1, 'missed': 0, 'forbearance': 0, 'consequence': 1, 'liquidity': 1, 'puts': 0}
- Next check: Oct 1; ARM lock-up/margin disclosures
- Note: Circular-funding node; expression is indirect.

## Search protocol — where the dates live (run weekly)

1. **SEC 8-K Item 2.04** "Triggering Events That Accelerate or Increase a Direct Financial Obligation" — the missed-payment / acceleration filing. Item 1.01 for waiver, forbearance and amendment agreements (the expiry date is in the exhibit). Item 2.03 for new obligations.
2. **EDGAR full-text search** (efts): `"forbearance agreement"`, `"waiver" AND "credit agreement" AND "through"` (the date follows "through"), `"going concern"`, `"substantial doubt"`, `"cure period"`, `"amortization event"`, `"rapid amortization"`, `"force majeure"`, `"rent deferral"`, `"payment-in-kind" AND "election"`, `NT 10-Q` / `NT 10-K` (late filings are the Hertz-April-27 of reporting).
3. **ABS trustee / servicer reports** (monthly, on the trustee's site or Bloomberg): cumulative-net-loss and delinquency triggers, early-amortization events, overcollateralization tests. The auto-ABS and data-center-ABS triggers are where Tricolor and the DC paper will show first.
4. **Indenture mechanics**: 30-day interest grace (bonds), 5-business-day (loans); quarter-end covenant tests reported ~45 days later (10-Q); springing maturities (a 2028 bond that springs to 2027 if the 2027 loan is not refinanced 91 days before) — the springing date is the real date.
5. **Private credit**: BDC 10-Q/10-K non-accruals and PIK share; quarterly redemption-request disclosures (first two weeks of the quarter); gate press releases; insurer statutory filings (Schedule BA) for private-credit marks.
6. **Project finance / SPVs**: lender syndication status (Bloomberg/LevFin), rent-commencement dates in lease exhibits, completion guarantees and their maturity (Oracle's $3.3B lessor guarantee is this).
7. **Sovereign**: TreasuryDirect auction results (tail, cover, dealer take), buyback results (fill ratio), QRA (coupon sizes), primary-dealer positioning (NY Fed), fails (DTCC).
8. **Rating actions and CDS**: a downgrade to CCC or a CDS above 1,000bp is the market reading the calendar; the edge is gone by then. The edge is items 1-6 BEFORE item 8.

Rule from Hertz: buy the puts on the missed payment, not on the filing. On April 27, 2020 the obligation was missed; on May 22 the waiver expired. The cheap entry was the day the obligation was known to be unpayable, which was visible in the March 10-K and the April 8-K, weeks before the price finished moving.