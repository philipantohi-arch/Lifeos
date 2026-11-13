"""sharpbets CLI.

  python -m sharpbets scan        rank today's sharpest contrarian bets
  python -m sharpbets wallets     show the skill-scored smart-money roster
  python -m sharpbets calibrate   refit the longshot-bias calibration on resolved markets
  python -m sharpbets explain SLUG  full signal breakdown for one market
  python -m sharpbets grade       score previously logged picks against resolutions
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, fields
from pathlib import Path

from . import calibration as calib
from .api import DEFAULT_CACHE, Client, parse_json_field
from .model import Analysis, Config, analyze_market, candidate_markets
from .wallets import build_roster

PICKS_LOG = Path("picks.jsonl")
DISCLAIMER = ("Model output, not financial advice. Signal weights are priors until your own `grade` "
              "history validates them. Check that prediction markets are legal where you live.")


def _client(args) -> Client:
    return Client(cache_dir=None if args.no_cache else DEFAULT_CACHE, verbose=args.verbose)


def _cfg(args) -> Config:
    cfg = Config()
    for f in fields(Config):
        v = getattr(args, f.name, None)
        if v is not None:
            setattr(cfg, f.name, v)
    return cfg


def cmd_wallets(args) -> int:
    client = _client(args)
    roster = build_roster(client, top=args.top, category=args.category)
    rows = sorted(roster.values(), key=lambda w: (-w.skill, -w.lb_pnl))
    print(f"\n{'wallet':<22}{'skill':>6}{'n':>5}{'win%':>6}{'ROI':>8}{'ret z':>7}{'beat z':>7}"
          f"{'conc':>6}{'LB PnL':>13}  note")
    for w in rows[: args.show]:
        print(f"{w.name[:21]:<22}{w.skill:>6.2f}{w.n_positions:>5}{w.win_rate:>6.0%}{w.roi:>8.1%}"
              f"{w.return_z:>7.1f}{w.beat_price_z:>7.1f}{w.concentration:>6.2f}{w.lb_pnl:>13,.0f}  {w.note}")
    n_skilled = sum(w.skill > 0 for w in rows)
    print(f"\n{n_skilled}/{len(rows)} leaderboard wallets pass the skill filter.")
    if args.json:
        Path(args.json).write_text(json.dumps([w.to_dict() for w in rows], indent=1))
    return 0


def cmd_calibrate(args) -> int:
    client = _client(args)
    samples = calib.collect_samples(client, n_markets=args.markets, horizon_h=args.horizon, days_back=args.days)
    if len(samples) < 50:
        print(f"Only {len(samples)} usable samples; not saving.")
        return 1
    model = calib.fit(samples, horizon_h=args.horizon)
    calib.DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    calib.DEFAULT_PATH.write_text(json.dumps(model, indent=1))
    print(f"\n{'price bucket':<14}{'n':>6}{'avg price':>10}{'won':>8}{'model':>8}")
    for b in model["bins"]:
        print(f"{b['lo']:.2f}-{b['hi']:.2f}    {b['n']:>6}{b['price']:>10.1%}{b['freq']:>8.1%}{b['calibrated']:>8.1%}")
    print(f"\n{model['n_markets']} resolved markets, price {args.horizon:g}h before close.")
    print(f"logit slope b = {model['slope_raw']:.3f} +/- {model['slope_se']:.3f}  -> shrunk b = {model['slope']:.3f} "
          f"({'longshots overpriced' if model['slope'] > 1 else 'extremes overconfident' if model['slope'] < 1 else 'no reliable bias'})")
    print(f"Brier: market {model['brier_market']:.4f} -> calibrated {model['brier_calibrated']:.4f}")
    print(f"Saved {calib.DEFAULT_PATH}")
    return 0


def _print_pick(i: int, a: Analysis) -> None:
    s = a.best
    print(f"\n#{i}  {a.question}")
    print(f"    BET {s.outcome!r} @ {s.fill_price:.3f} (+{s.fee_per_share:.3f} fee)  fair {s.fair:.1%}  "
          f"EV {s.ev:+.1%}  stake ${s.stake:,.0f}  ({s.kelly:.1%} full-Kelly)")
    print(f"    closes in {a.days_left:.1f}d · 24h vol ${a.volume24h:,.0f} · retail tickets {a.n_retail} · "
          f"signal agreement {s.agreement:.0%} · value disparity {s.disparity:.2f}")
    for r in s.reasons:
        print(f"      - {r}")
    if a.smart_wallets:
        print(f"      smart wallets in market: {', '.join(a.smart_wallets[:6])}"
              + (" ..." if len(a.smart_wallets) > 6 else ""))
    print(f"    https://polymarket.com/market/{a.slug}")


def _analyses(args, client, markets) -> tuple[list[Analysis], object]:
    cal = calib.Calibrator.load()
    if cal.is_identity:
        print("! No calibration file - longshot-bias correction disabled. Run `python -m sharpbets calibrate`.")
    print("Building smart-money roster from the Polymarket leaderboard ...")
    roster = build_roster(client, top=args.top, category=args.category)
    print(f"  {sum(w.skill > 0 for w in roster.values())} wallets with proven skill")
    cfg = _cfg(args)
    out = []
    for i, m in enumerate(markets, 1):
        print(f"\r  analyzing markets {i}/{len(markets)}", end="", flush=True)
        try:
            out.append(analyze_market(client, m, roster, cal, cfg))
        except Exception as e:
            if args.verbose:
                print(f"\n  skip {m.get('slug')}: {e}")
    print()
    return out, cfg


def cmd_scan(args) -> int:
    client = _client(args)
    markets = candidate_markets(client, limit=args.markets, max_days=args.max_days,
                                min_liquidity=args.min_liquidity, include_live=args.live)
    print(f"{len(markets)} candidate markets")
    results, cfg = _analyses(args, client, markets)
    picks, groups = [], set()
    for a in sorted((a for a in results if a.best), key=lambda a: -a.best.score):
        if a.group in groups and not args.allow_correlated:
            continue  # same event / same underlying asset: one bet, not several
        groups.add(a.group)
        picks.append(a)
    picks = picks[: args.n]
    if not picks:
        print("\nNo bet clears the filters right now. That is a valid answer: no edge, no bet.")
    for i, a in enumerate(picks, 1):
        _print_pick(i, a)
    total = sum(a.best.stake for a in picks)
    print(f"\nTotal suggested exposure ${total:,.0f} of ${cfg.bankroll:,.0f} bankroll "
          f"({client.calls} API calls). {DISCLAIMER}")
    if args.json:
        Path(args.json).write_text(json.dumps([a.to_dict() for a in picks], indent=1))
    if args.log and picks:
        with PICKS_LOG.open("a") as f:
            for a in picks:
                f.write(json.dumps({"ts": time.time(), "slug": a.slug, "condition_id": a.condition_id,
                                    "question": a.question, **{k: getattr(a.best, k) for k in
                                    ("outcome", "token_id", "fair", "mid", "calibrated", "cost", "ev", "stake",
                                     "disparity")}})
                        + "\n")
        print(f"Logged {len(picks)} picks to {PICKS_LOG.resolve()}")
    return 0


def cmd_explain(args) -> int:
    client = _client(args)
    m = client.market_by_slug(args.slug)
    if not m:
        print(f"No market with slug {args.slug!r}")
        return 1
    (a,), _ = _analyses(args, client, [m])
    print(f"\n{a.question}  (closes in {a.days_left:.1f}d)")
    print(f"retail tickets {a.n_retail} · skill-weighted smart $ {a.smart_usd:,.0f} · wallets: "
          f"{', '.join(a.smart_wallets) or 'none'}")
    for s in a.sides:
        print(f"\n  {s.outcome}: mid {s.mid:.3f} -> calibrated {s.calibrated:.3f} -> fair {s.fair:.3f}")
        print(f"    public {s.public:+.2f} smart {s.smart:+.2f} rlm {s.rlm:+.2f} fade {s.fade:+.2f} "
              f"dp24 {s.dp24 * 100:+.1f}c")
        print(f"    $ share {s.money_share:.0%} (excess vs price {s.money_excess:+.2f}) split {s.split:+.2f} "
              f"disparity {s.disparity:.2f}")
        print(f"    cost {s.cost:.3f}  EV {s.ev:+.1%}  kelly {s.kelly:.1%}  stake ${s.stake:,.0f}  "
              f"agreement {s.agreement:.0%}")
        for r in s.reasons:
            print(f"      - {r}")
    print(f"\nPick: {a.best.outcome if a.best else 'none (' + a.skipped + ')'}")
    return 0


def cmd_grade(args) -> int:
    if not PICKS_LOG.exists():
        print(f"No {PICKS_LOG} yet. Run `scan --log` first.")
        return 1
    client = _client(args)
    picks = [json.loads(l) for l in PICKS_LOG.read_text().splitlines() if l.strip()]
    graded = []
    for p in picks:
        m = client.market_by_slug(p["slug"])
        if not m or not m.get("closed"):
            continue
        tokens = [str(t) for t in parse_json_field(m.get("clobTokenIds"))]
        prices = [float(x) for x in parse_json_field(m.get("outcomePrices"))]
        if p["token_id"] not in tokens:
            continue
        y = prices[tokens.index(p["token_id"])]
        graded.append((p, y))
    if not graded:
        print(f"{len(picks)} picks logged, none resolved yet.")
        return 0
    n = len(graded)
    staked = sum(p["stake"] for p, _ in graded) or 1
    pnl = sum(p["stake"] * (y / p["cost"] - 1) for p, y in graded)
    brier_model = sum((p["fair"] - y) ** 2 for p, y in graded) / n
    brier_mkt = sum((p["mid"] - y) ** 2 for p, y in graded) / n
    print(f"{n} resolved picks · hit rate {sum(y for _, y in graded) / n:.0%} · "
          f"avg fair {sum(p['fair'] for p, _ in graded) / n:.0%}")
    print(f"P&L ${pnl:,.2f} on ${staked:,.0f} staked (ROI {pnl / staked:+.1%})")
    print(f"Brier: model {brier_model:.4f} vs market {brier_mkt:.4f} "
          f"({'model better' if brier_model < brier_mkt else 'market better'} - lower is better)")
    if n < 100:
        print("Fewer than ~100 resolved picks: treat these numbers as noise, not proof.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="sharpbets", description="Contrarian Polymarket edge finder.")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--no-cache", action="store_true", help="disable the on-disk API cache")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def roster_opts(p):
        p.add_argument("--top", type=int, default=100, help="leaderboard wallets per period (all-time + month)")
        p.add_argument("--category", help="leaderboard category, e.g. sports, politics, crypto")

    def model_opts(p):
        p.add_argument("--bankroll", type=float)
        p.add_argument("--kelly-mult", dest="kelly_mult", type=float)
        p.add_argument("--max-bet-pct", dest="max_bet_pct", type=float)
        p.add_argument("--min-ev", dest="min_ev", type=float)
        p.add_argument("--any-side", dest="contrarian_only", action="store_false", default=None,
                       help="allow bets on the public side too")
        p.add_argument("--disparity-weight", dest="disparity_weight", type=float,
                       help="how much to rank up lopsided-action bets (default 1.0 = up to 2x; 0 = off)")
        p.add_argument("--min-disparity", dest="min_disparity", type=float,
                       help="only show bets with value disparity >= this (0-1), e.g. 0.3")
        p.add_argument("--maker", action="store_true", default=None,
                       help="assume you post limit orders at mid (no taker fee)")

    p = sub.add_parser("scan", help="rank the sharpest contrarian bets right now")
    roster_opts(p), model_opts(p)
    p.add_argument("-n", type=int, default=10, help="picks to show")
    p.add_argument("--markets", type=int, default=60, help="markets to analyze (by 24h volume)")
    p.add_argument("--max-days", type=float, default=45)
    p.add_argument("--min-liquidity", type=float, default=5000)
    p.add_argument("--live", action="store_true", help="include games already in progress")
    p.add_argument("--allow-correlated", action="store_true",
                   help="allow several picks on the same event / underlying asset")
    p.add_argument("--json", help="write picks to this JSON file")
    p.add_argument("--log", action="store_true", help=f"append picks to {PICKS_LOG} for later grading")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("explain", help="signal breakdown for one market")
    p.add_argument("slug")
    roster_opts(p), model_opts(p)
    p.set_defaults(func=cmd_explain)

    p = sub.add_parser("wallets", help="show the skill-scored smart-money roster")
    roster_opts(p)
    p.add_argument("--show", type=int, default=40)
    p.add_argument("--json")
    p.set_defaults(func=cmd_wallets)

    p = sub.add_parser("calibrate", help="refit the longshot-bias calibration")
    p.add_argument("--markets", type=int, default=600)
    p.add_argument("--horizon", type=float, default=24, help="hours before close to read the price")
    p.add_argument("--days", type=int, default=365)
    p.set_defaults(func=cmd_calibrate)

    p = sub.add_parser("grade", help="grade logged picks against resolutions")
    p.set_defaults(func=cmd_grade)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
