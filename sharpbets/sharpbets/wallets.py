"""Smart-money roster: start from Polymarket's most successful accounts, keep only proven skill.

Leaderboard PnL alone is a bad signal: it is dominated by (a) one-hit whales who sized up on a
single coin flip (e.g. one election) and (b) market makers whose holdings are inventory, not views.
So every leaderboard wallet is re-scored from its own recent closed positions:

  * return z-score     mean(position return) / standard error   -- consistent profit, not one bet
  * price-beating z    sum(won - entry_price) / sqrt(sum p(1-p)) -- beat the implied odds at entry
  * concentration      share of gross profit from the single best position (one-hit penalty)
  * turnover           leaderboard volume / |PnL|  (very high => liquidity provider, down-weighted)

skill in [0, 1] is what every downstream signal multiplies wallet dollars by.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from .api import Client

MIN_SKILL = 0.15


@dataclass
class WalletSkill:
    wallet: str
    name: str
    lb_pnl: float
    lb_volume: float
    n_positions: int
    n_resolved: int
    win_rate: float
    roi: float
    return_z: float
    beat_price_z: float
    concentration: float
    turnover: float
    skill: float
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def score_wallet(wallet: str, name: str, lb_pnl: float, lb_volume: float, positions: list[dict],
                 min_positions: int = 15) -> WalletSkill:
    rets: list[float] = []
    costs: list[float] = []
    pnls: list[float] = []
    won_minus_p = 0.0
    var_p = 0.0
    n_resolved = 0
    wins = 0
    for p in positions:
        size = float(p.get("total_size") or 0)
        avg = float(p.get("avg_price") or 0)
        cost = size * avg
        if cost < 10 or not 0 < avg < 1:
            continue
        pnl = float(p.get("total_pnl") if p.get("total_pnl") is not None else p.get("realized_pnl") or 0)
        rets.append(_clip(pnl / cost, -1.0, 10.0))
        costs.append(cost)
        pnls.append(pnl)
        wins += pnl > 0
        cur = p.get("current_price")
        if cur is not None and (float(cur) >= 0.99 or float(cur) <= 0.01):
            won = 1.0 if float(cur) >= 0.99 else 0.0
            won_minus_p += won - avg
            var_p += avg * (1 - avg)
            n_resolved += 1

    n = len(rets)
    turnover = lb_volume / abs(lb_pnl) if lb_pnl else float("inf")
    if n < 2:
        return WalletSkill(wallet, name, lb_pnl, lb_volume, n, n_resolved, 0, 0, 0, 0, 1, turnover, 0.0,
                           "too few positions")

    mean = sum(rets) / n
    sd = math.sqrt(sum((r - mean) ** 2 for r in rets) / (n - 1)) or 1e-9
    return_z = mean / (sd / math.sqrt(n))
    beat_z = won_minus_p / math.sqrt(var_p) if var_p > 0 else 0.0
    gross_profit = sum(x for x in pnls if x > 0)
    concentration = max(pnls) / gross_profit if gross_profit > 0 else 1.0
    roi = sum(pnls) / sum(costs)

    # Combine the two skill tests; the price-beating test only counts positions held to resolution.
    w_beat = n_resolved / (n_resolved + 10)
    z = (1 - w_beat) * return_z + w_beat * beat_z if n_resolved else return_z
    skill = _clip((z - 1.0) / 3.0, 0.0, 1.0)  # z<=1 -> 0 (indistinguishable from luck); z>=4 -> 1

    notes = []
    if n < min_positions:
        skill *= n / min_positions
        notes.append("small sample")
    if concentration > 0.5:
        skill *= (1 - concentration) * 2
        notes.append("one-hit")
    if turnover > 60:
        skill = 0.0  # liquidity provider: its holdings are inventory, not a view on the outcome
        notes.append("market-maker")
    if roi < 0:
        skill = 0.0
        notes.append("losing recently")
    if skill < MIN_SKILL:
        skill = 0.0  # below this the wallet is not distinguishable from a lucky one
    return WalletSkill(wallet, name, lb_pnl, lb_volume, n, n_resolved, wins / n, roi, return_z, beat_z,
                       concentration, turnover, round(skill, 4), ", ".join(notes))


def build_roster(client: Client, top: int = 100, category: str | None = None,
                 positions_per_wallet: int = 500, progress: bool = True) -> dict[str, WalletSkill]:
    """Union of all-time and last-month PnL leaders, each re-scored for skill."""
    pool: dict[str, dict] = {}
    for period in ("all", "month"):
        for row in client.leaderboard(period=period, order_by="PNL", limit=top, category=category):
            w = row["user_id"].lower()
            if w not in pool or period == "all":
                pool[w] = row
    roster: dict[str, WalletSkill] = {}
    for i, (w, row) in enumerate(pool.items(), 1):
        if progress:
            print(f"\r  scoring wallets {i}/{len(pool)}", end="", flush=True)
        try:
            positions = client.resolved_positions(w, limit=positions_per_wallet)
        except Exception as e:  # one bad wallet should not kill the run
            positions = []
            if client.verbose:
                print(f"\n  skip {w}: {e}")
        roster[w] = score_wallet(w, (row.get("user_name") or w)[:22], float(row.get("pnl") or 0),
                                 float(row.get("volume") or 0), positions)
    if progress:
        print()
    return roster
