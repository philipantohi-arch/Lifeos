# SharpBets — a contrarian edge finder for Polymarket

SharpBets scans live Polymarket markets and ranks the **sharpest contrarian bets**. Each pick bets against the retail crowd, leans on the positions of Polymarket's **most successful accounts after a luck filter**, and is priced against the real order book with fees and sized with fractional Kelly.

```bash
cd sharpbets
python -m sharpbets scan --bankroll 1000          # today's ranked picks
python -m sharpbets explain <market-slug>         # full signal breakdown for one market
python -m sharpbets wallets                       # the skill-scored smart-money roster
python -m sharpbets calibrate                     # refit longshot-bias calibration (~5 min)
python -m sharpbets scan --log  ...  then later:  python -m sharpbets grade
python -m unittest discover -s tests              # offline tests
```

Pure Python 3.10+ standard library. No API keys needed. Everything goes through Polymarket's public Gamma, Data (v2) and CLOB APIs, with responses cached in `~/.cache/sharpbets`.

## How a pick is made

For every binary market (filtered on liquidity, volume, time to close and a 5–95¢ price band), each side gets these signals:

| Signal | What it measures | Contrarian logic |
|---|---|---|
| **Public** | Share of small trades (under $200, from wallets outside the roster) backing each side: the "ticket count" | Fade the side the crowd is piling onto |
| **Smart money** | Skill-weighted dollars on each side, from top holders and recent fills of proven wallets | Follow money that has beaten the odds before |
| **Reverse line move** | The price moved *toward* a side while retail tickets backed the other side | Someone bigger than the crowd is pushing the price |
| **Overreaction fade** | The price ran toward the crowd's side with no smart-money support | Retail momentum tends to overshoot |

Plus a fifth signal for **value disparity**, meaning lopsided action:

| Signal | What it measures | Logic |
|---|---|---|
| **Money/ticket split** | Share of dollars on each side *relative to its price*, minus the retail ticket lean | Big money the crowd isn't on is the classic "sharp side": follow it |

Dollar share is judged against price because on Polymarket a 75¢ favorite naturally attracts ~75% of the dollars even when both sides are evenly backed. A side scores a **value disparity** of 0–1 when either:
- more money backs it than its price and ticket count explain (follow the money), or
- money *and* tickets have both piled onto the other side well beyond its price (fade the frenzy).

Disparity raises a bet's ranking: `score × (1 + disparity_weight × disparity)`, so a fully lopsided market ranks up to 2× by default. When most of the heavy side's dollars come from **one wallet**, the disparity counts at half, because one whale is one opinion. Options:

```bash
python -m sharpbets scan --min-disparity 0.3        # only lopsided-action bets
python -m sharpbets scan --disparity-weight 2       # rank them up even harder (up to 3x)
python -m sharpbets scan --disparity-weight 0       # ignore disparity in ranking
```

The signals combine in log-odds space on top of an **empirically calibrated price**:

```
fair = expit( b·logit(mid) + clip(0.45·smart·conf − 0.20·public·conf + 0.30·split·conf
                                  + 0.25·rlm + 0.20·fade, ±0.35) )
```

Then for the chosen side:
- **Cost** = average fill from walking the live ask book at your stake, plus the taker fee where the market charges one.
- **EV** = fair / cost − 1.
- **Stake** = quarter-Kelly, capped at 5% of bankroll and at half the visible book depth.

A side qualifies only if EV ≥ 2% **and** the retail majority is on the *other* side (`--any-side` turns that off). The ranking score is EV discounted by how strongly the signals agree and boosted by value disparity. The scan keeps only one pick per event or underlying asset, because three bitcoin markets are really one bet.

## Using the most successful Polymarket accounts without copying their luck

The roster starts from the PnL leaderboard (all-time plus last month) and then **re-scores every wallet from its own recent resolved bets**:

- **Losses are counted.** Polymarket never "closes" a losing position held to expiry, because nobody redeems a 0¢ share. These losers sit under `status=OPEN` at price 0. Counting only closed positions made top wallets look like 92–99% winners. Including the losers puts them at a realistic 45–60%.
- **Return z-score**: is the average return per bet consistently positive, or did it come from one bet?
- **Price-beating z-score**: Σ(won − entry price) / √Σp(1−p). Did they beat the implied odds when they entered?
- **One-hit penalty** when a single position supplied more than 50% of gross profit, as with election whales.
- **Market makers are excluded** (volume / |PnL| > 60): their holdings are inventory, not opinions.
- Skill below 0.15 counts as zero (indistinguishable from luck). On the day this was built, 36 of 94 leaderboard wallets passed.

## What the data actually said (fit 2026-11-13, 1,191 resolved markets)

`calibrate` reads each resolved binary market's price 24h before close and fits `logit(true prob) = b·logit(price)`. The slope is then shrunk toward 1 (the market is right) according to its standard error:

- b = 0.883 ± 0.063 raw, **0.917 shrunk**: on Polymarket, **heavy favorites are slightly overpriced and underdogs slightly underpriced**. That is the *reverse* of the classic sportsbook longshot bias, and contrarian in itself: fade the chalk.
- The effect is modest (a 10¢ side is worth about 11.5¢) and only meaningful away from the tails. That is why prices under 5¢ or over 95¢ are excluded.

## Honest limits — read before betting

- **Only the calibration is fit to outcomes.** The signal weights are conservative priors. Polymarket doesn't expose historical holder snapshots, so the smart-money and public signals can't be backtested yet. Validate them yourself: run `scan --log` for a few weeks, then `grade`. It reports P&L and the model's Brier score versus the market's. Under ~100 resolved picks, the results are noise.
- **Fees are estimated.** On fee-enabled markets, observed taker fees were about 2.4% of cost at 50¢, modeled as `0.05·p·(1−p)` per share. Posting limit orders (`--maker`) avoids them.
- The retail/smart split uses the last ~1,000 fills and the top 20 holders per side. Whales trading through fresh wallets are invisible to it.
- Live in-game markets are excluded by default (`--live` includes them). Prices there move faster than this model refreshes.
- This is a research tool, not financial advice. Polymarket is geo-restricted in some jurisdictions, including parts of the US, so check what's legal where you live. Never stake money you can't lose.

## Layout

```
sharpbets/
  api.py          cached client for Gamma / Data v2 / CLOB (incl. the unredeemed-losers fix)
  wallets.py      leaderboard -> luck-filtered skill roster
  calibration.py  resolved-market fit of price -> true probability (shrunk logit slope)
  model.py        signals, fair value, book walking, fees, Kelly sizing, ranking
  cli.py          scan / explain / wallets / calibrate / grade
  data/calibration.json   the committed fit (refresh with `calibrate`)
tests/test_model.py       offline unit tests
```
