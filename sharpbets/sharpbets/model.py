"""Contrarian signal model: fade the public, follow proven-skill money, price it, size it.

For each binary market and each side i (j = the other side):

  public_i   in [-1, 1]  retail ticket split: 2 * (share of small-wallet trades backing i) - 1
  smart_i    in [-1, 1]  skill-weighted dollars on i vs j, from top holders + recent trades of
                         roster wallets (see wallets.py)
  rlm_i      in [-1, 1]  reverse line movement: price moved toward i while retail backed j
  fade_i     in [-1, 1]  overreaction: price ran toward i on retail flow with no smart support

  fair_i = expit( logit(calibrated(mid_i)) + clip(b_s*smart*conf_s - b_p*public*conf_p
                                                   + b_r*rlm + b_f*fade, +-max_adj) )

calibrated() is the empirical favorite-longshot correction fit on resolved markets. The b weights
are conservative priors, NOT fit to outcomes (historical holder snapshots are not available);
validate them forward with `sharpbets log` + `sharpbets grade` before trusting them with size.
"""
from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass, field

from .api import Client, parse_json_field
from .calibration import Calibrator, _ts, expit, logit
from .wallets import WalletSkill


@dataclass
class Config:
    bankroll: float = 1000.0
    kelly_mult: float = 0.25        # quarter Kelly: model error makes full Kelly reckless
    max_bet_pct: float = 0.05       # never more than 5% of bankroll on one market
    min_ev: float = 0.02            # 2% expected return after fees to qualify
    contrarian_only: bool = True    # only bet the side retail is NOT on
    retail_max_usd: float = 200.0   # trades below this from non-roster wallets = "public tickets"
    b_smart: float = 0.45
    b_public: float = 0.20
    b_rlm: float = 0.25
    b_fade: float = 0.20
    max_adj: float = 0.35           # cap on log-odds shift from calibrated price (~ +-8.7pp at 50%)
    fee_coef: float = 0.05          # taker fee per share ~= fee_coef * p * (1-p) on fee-enabled markets
    maker: bool = False             # True = you post limit orders (no taker fee, fill at mid)
    min_price: float = 0.05         # ignore sub-5c / over-95c sides: fees + tail calibration noise


@dataclass
class Side:
    outcome: str
    token_id: str
    mid: float
    calibrated: float
    fair: float
    public: float
    smart: float
    rlm: float
    fade: float
    dp24: float
    fill_price: float = 0.0
    fee_per_share: float = 0.0
    cost: float = 0.0
    ev: float = 0.0
    kelly: float = 0.0
    stake: float = 0.0
    depth_usd: float = 0.0
    agreement: float = 0.0
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)


@dataclass
class Analysis:
    question: str
    slug: str
    condition_id: str
    end_date: str
    days_left: float
    volume24h: float
    liquidity: float
    n_retail: int
    smart_wallets: list[str]
    smart_usd: float
    sides: list[Side]
    best: Side | None = None
    group: str = ""
    skipped: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["best"] = asdict(self.best) if self.best else None
        return d


# --------------------------------------------------------------------------- helpers
# Markets whose price is mechanically tied to an observable underlying. Reverse-line / overreaction
# signals are meaningless there: a 30c move in "BTC above 72.5k?" is just BTC moving.
UNDERLYING_TAGS = {"crypto-prices", "hit-price", "up-or-down", "stocks", "equities", "commodities",
                   "forex", "weather", "pre-market"}
ASSET_TAGS = {"bitcoin", "ethereum", "solana", "xrp", "dogecoin", "bnb", "hyperliquid", "gold", "oil",
              "spx", "tesla", "nvidia"}


def market_tags(m: dict) -> set[str]:
    tags = list(m.get("tags") or [])
    for e in m.get("events") or []:
        tags += e.get("tags") or []
    return {t.get("slug", "") for t in tags if isinstance(t, dict)}


def correlation_group(m: dict, tags: set[str]) -> str:
    """Bets in one group move together; the scan keeps only the best pick per group."""
    asset = sorted(tags & ASSET_TAGS)
    if asset and tags & UNDERLYING_TAGS:
        return "asset:" + asset[0]
    ev = (m.get("events") or [{}])[0]
    return "event:" + (ev.get("slug") or m.get("slug", ""))


def _sign(x: float) -> int:
    return (x > 0) - (x < 0)


def walk_book(asks: list[dict], usd: float) -> tuple[float, float, float]:
    """Spend `usd` lifting asks. Returns (avg_price, usd_filled, total_depth_usd)."""
    levels = sorted(((float(a["price"]), float(a["size"])) for a in asks), key=lambda x: x[0])
    depth = sum(p * s for p, s in levels)
    spent = shares = 0.0
    for p, s in levels:
        take = min(s, (usd - spent) / p)
        if take <= 0:
            break
        spent += take * p
        shares += take
    return (spent / shares if shares else (levels[0][0] if levels else 0.0)), spent, depth


def kelly_fraction(p: float, cost: float) -> float:
    """Kelly for a contract costing `cost` that pays 1 with probability p."""
    return max(0.0, (p - cost) / (1 - cost)) if 0 < cost < 1 else 0.0


def flow_features(trades: list[dict], tokens: list[str], roster: dict[str, WalletSkill],
                  retail_max: float) -> tuple[list[int], list[float], set[str]]:
    """Retail ticket counts per outcome and skill-weighted smart $ per outcome from recent fills."""
    tickets = [0, 0]
    smart = [0.0, 0.0]
    names: set[str] = set()
    for t in trades:
        try:
            i = tokens.index(t["token_id"])
        except ValueError:
            continue
        size, price = float(t.get("size") or 0), float(t.get("price") or 0)
        buy = t.get("side") == "BUY"
        toward = i if buy else 1 - i
        usd = size * price if buy else size * (1 - price)  # dollars effectively staked on `toward`
        w = roster.get((t.get("proxy_wallet") or "").lower())
        if w and w.skill > 0:
            smart[toward] += usd * w.skill
            names.add(w.name)
        elif usd < retail_max:
            tickets[toward] += 1
    return tickets, smart, names


def holder_features(holders: list[dict], tokens: list[str], mids: list[float],
                    roster: dict[str, WalletSkill]) -> tuple[list[float], set[str]]:
    smart = [0.0, 0.0]
    names: set[str] = set()
    for block in holders:
        try:
            i = tokens.index(block.get("token_id"))
        except ValueError:
            continue
        for h in block.get("holders", []):
            w = roster.get((h.get("proxy_wallet") or "").lower())
            if w and w.skill > 0:
                smart[i] += float(h.get("amount") or 0) * mids[i] * w.skill
                names.add(w.name)
    return smart, names


# --------------------------------------------------------------------------- core
def score_sides(mid0: float, dp0: float, tickets: list[int], smart_usd: list[float], cal: Calibrator,
                cfg: Config, price_signals: bool = True) -> tuple[float, list[dict]]:
    """Pure function: signals -> fair probability for outcome 0, plus per-side signal breakdown."""
    n_retail = sum(tickets)
    public0 = (tickets[0] - tickets[1]) / n_retail if n_retail else 0.0
    conf_p = min(1.0, n_retail / 100)
    tot_smart = sum(smart_usd)
    smart0 = (smart_usd[0] - smart_usd[1]) / tot_smart if tot_smart else 0.0
    conf_s = 1 - math.exp(-tot_smart / 5000)

    if not price_signals:
        dp0 = 0.0  # price tracks an observable underlying (e.g. BTC): moves are news, not crowd error
    mag = min(abs(dp0) / 0.08, 1.0)
    rlm0 = 0.0
    if abs(dp0) > 0.02 and abs(public0) > 0.1 and _sign(dp0) == -_sign(public0):
        rlm0 = _sign(dp0) * mag * conf_p  # price went against the crowd -> follow the price
    fade0 = 0.0
    if abs(dp0) > 0.05 and abs(public0) > 0.1 and _sign(dp0) == _sign(public0) and _sign(smart0) != _sign(dp0):
        fade0 = -_sign(dp0) * min(abs(dp0) / 0.15, 1.0) * conf_p  # crowd chased it, sharps didn't

    terms = {
        "smart": cfg.b_smart * smart0 * conf_s,
        "public": -cfg.b_public * public0 * conf_p,
        "rlm": cfg.b_rlm * rlm0,
        "fade": cfg.b_fade * fade0,
    }
    adj = max(-cfg.max_adj, min(cfg.max_adj, sum(terms.values())))
    cal0 = cal(mid0)
    fair0 = expit(logit(cal0) + adj)
    sides = []
    for i, s in ((0, 1), (1, -1)):
        sides.append({"mid": mid0 if i == 0 else 1 - mid0,
                      "calibrated": cal0 if i == 0 else 1 - cal0,
                      "fair": fair0 if i == 0 else 1 - fair0,
                      "public": s * public0, "smart": s * smart0, "rlm": s * rlm0, "fade": s * fade0,
                      "dp24": s * dp0, "terms": {k: s * v for k, v in terms.items()},
                      "conf_s": conf_s, "conf_p": conf_p})
    return fair0, sides


def price_side(side: Side, asks: list[dict], fee_enabled: bool, terms: dict, cfg: Config) -> None:
    stake = cfg.bankroll * cfg.max_bet_pct
    for _ in range(3):  # stake depends on price, price depends on stake: iterate to a fixed point
        if cfg.maker:
            fill, _, depth = side.mid, stake, walk_book(asks, 0)[2]
            fee = 0.0
        else:
            fill, _, depth = walk_book(asks, max(stake, 1.0))
            fee = cfg.fee_coef * fill * (1 - fill) if fee_enabled else 0.0
        cost = fill + fee
        k = kelly_fraction(side.fair, cost)
        new_stake = min(cfg.kelly_mult * k * cfg.bankroll, cfg.max_bet_pct * cfg.bankroll, 0.5 * depth)
        if abs(new_stake - stake) < 0.5:
            stake = new_stake
            break
        stake = max(new_stake, 1.0)
    side.fill_price, side.fee_per_share, side.cost, side.depth_usd = fill, fee, cost, depth
    side.ev = side.fair / cost - 1 if cost > 0 else 0.0
    side.kelly = k
    side.stake = round(max(0.0, stake if k > 0 else 0.0), 2)
    pushing = [v for v in terms.values() if abs(v) > 1e-6]
    side.agreement = sum(v for v in pushing if v > 0) / sum(abs(v) for v in pushing) if pushing else 0.0
    # Rank: EV, discounted when the signals disagree or the call rests on calibration alone.
    side.score = side.ev * (0.5 + 0.5 * side.agreement)


def explain(side: Side, terms: dict, conf_s: float, n_smart: int) -> list[str]:
    r = []
    if abs(side.calibrated - side.mid) > 0.004:
        r.append(f"longshot-bias calibration: {side.mid:.1%} priced -> {side.calibrated:.1%} historically")
    if side.public < -0.1:
        r.append(f"public fade: {(1 - side.public) / 2:.0%} of retail tickets on the other side")
    elif side.public > 0.1:
        r.append(f"WITH the public: {(1 + side.public) / 2:.0%} of retail tickets on this side")
    if abs(side.smart) > 0.05 and conf_s > 0.05:
        who = "for" if side.smart > 0 else "against"
        r.append(f"smart money {who}: {(1 + side.smart) / 2:.0%} of skill-weighted $ ({n_smart} proven wallets)")
    if side.rlm > 0:
        r.append(f"reverse line move: price +{side.dp24 * 100:.1f}c in 24h despite retail on the other side")
    if side.fade > 0:
        r.append(f"overreaction fade: other side ran {abs(side.dp24) * 100:.1f}c on retail flow, sharps absent")
    return r


def analyze_market(client: Client, m: dict, roster: dict[str, WalletSkill], cal: Calibrator,
                   cfg: Config) -> Analysis:
    outcomes = parse_json_field(m.get("outcomes"))
    tokens = [str(t) for t in parse_json_field(m.get("clobTokenIds"))]
    prices = [float(x) for x in parse_json_field(m.get("outcomePrices"))]
    end = _ts(m.get("endDate"))
    days_left = (end - time.time()) / 86400 if end else float("nan")
    a = Analysis(m.get("question", ""), m.get("slug", ""), m.get("conditionId", ""), m.get("endDate", ""),
                 round(days_left, 2), float(m.get("volume24hr") or 0), float(m.get("liquidityNum") or 0),
                 0, [], 0.0, [])
    if len(tokens) != 2 or len(prices) != 2:
        a.skipped = "not binary"
        return a

    books = [client.book(t) for t in tokens]
    mids = []
    for b, px in zip(books, prices):
        bids = [float(x["price"]) for x in b.get("bids", [])]
        asks = [float(x["price"]) for x in b.get("asks", [])]
        mids.append((max(bids) + min(asks)) / 2 if bids and asks else px)
    mid0 = mids[0] / (mids[0] + mids[1]) if sum(mids) else prices[0]  # normalise away the spread
    if not cfg.min_price <= mid0 <= 1 - cfg.min_price:
        a.skipped = "price outside tradable band"
        return a

    hist = client.price_history(tokens[0], start_ts=int(time.time() - 86400), end_ts=int(time.time()),
                                fidelity=30, ttl=120)
    dp0 = (mid0 - float(hist[0]["p"])) if hist else 0.0

    tickets, smart_trades, n1 = flow_features(client.trades(m["conditionId"]), tokens, roster, cfg.retail_max_usd)
    smart_hold, n2 = holder_features(client.holders(m["conditionId"]), tokens, mids, roster)
    smart_usd = [smart_trades[0] + smart_hold[0], smart_trades[1] + smart_hold[1]]
    a.n_retail = sum(tickets)
    a.smart_wallets = sorted(n1 | n2)
    a.smart_usd = round(sum(smart_usd), 2)

    tags = market_tags(m)
    a.group = correlation_group(m, tags)
    _, raw = score_sides(mid0, dp0, tickets, smart_usd, cal, cfg,
                         price_signals=not tags & UNDERLYING_TAGS)
    fee_enabled = client.fee_rate(tokens[0]) > 0
    for i, r in enumerate(raw):
        s = Side(str(outcomes[i]), tokens[i], r["mid"], r["calibrated"], r["fair"], r["public"], r["smart"],
                 r["rlm"], r["fade"], r["dp24"])
        price_side(s, books[i].get("asks", []), fee_enabled, r["terms"], cfg)
        s.reasons = explain(s, r["terms"], r["conf_s"], len(a.smart_wallets))
        a.sides.append(s)

    eligible = [s for s in a.sides if s.ev >= cfg.min_ev and s.stake > 0
                and (not cfg.contrarian_only or s.public < 0)]
    a.best = max(eligible, key=lambda s: s.score) if eligible else None
    if not a.best:
        a.skipped = "no side clears EV/contrarian filters"
    return a


def candidate_markets(client: Client, limit: int = 60, max_days: float = 45, min_liquidity: float = 5000,
                      min_volume24h: float = 5000, include_live: bool = False) -> list[dict]:
    now = time.time()
    out, offset = [], 0
    while len(out) < limit and offset < 1000:
        batch = client.markets(closed=False, limit=100, offset=offset, order="volume24hr", ascending=False,
                               include_tag="true")
        if not batch:
            break
        offset += len(batch)
        for m in batch:
            prices = [float(x) for x in parse_json_field(m.get("outcomePrices"))]
            end = _ts(m.get("endDate"))
            start = _ts(m.get("gameStartTime"))
            if (len(prices) != 2 or not m.get("acceptingOrders") or not m.get("enableOrderBook")
                    or not end or end < now + 3600 or end > now + max_days * 86400
                    or float(m.get("liquidityNum") or 0) < min_liquidity
                    or float(m.get("volume24hr") or 0) < min_volume24h
                    or not 0.05 <= prices[0] <= 0.95
                    or (not include_live and start and start < now)):
                continue
            out.append(m)
            if len(out) >= limit:
                break
    return out
