"""Empirical price -> true-probability calibration from resolved Polymarket markets.

This is the one part of the model fit directly to outcomes. It measures the favorite-longshot
bias (retail overpays for lottery tickets) on Polymarket itself instead of assuming it:
for every resolved binary market we take the price `horizon` hours before it closed and record
whether that outcome won, then fit  logit(true prob) = b * logit(price)  and shrink b toward 1
by its standard error. The result maps market price -> calibrated probability.
"""
from __future__ import annotations

import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

from .api import Client, parse_json_field

DEFAULT_PATH = Path(__file__).parent / "data" / "calibration.json"
EDGES = [0, .03, .07, .12, .2, .3, .4, .5, .6, .7, .8, .88, .93, .97, 1.0001]


def _ts(s: str | None) -> float | None:
    if not s:
        return None
    s = s.replace("Z", "+00:00").replace(" ", "T")
    if s.endswith("+00"):
        s += ":00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def collect_samples(client: Client, n_markets: int = 600, horizon_h: float = 24, days_back: int = 365,
                    min_volume: float = 50_000, progress: bool = True) -> list[tuple[float, int]]:
    since = datetime.fromtimestamp(time.time() - days_back * 86400, tz=timezone.utc).strftime("%Y-%m-%d")
    samples: list[tuple[float, int]] = []
    offset = 0
    seen = 0
    while seen < n_markets:
        batch = client.markets(closed=True, limit=100, offset=offset, order="volumeNum", ascending=False,
                               end_date_min=since, ttl=86400)
        if not batch:
            break
        offset += len(batch)
        for m in batch:
            if seen >= n_markets:
                break
            outcomes = parse_json_field(m.get("outcomes"))
            prices = [float(x) for x in parse_json_field(m.get("outcomePrices"))]
            tokens = parse_json_field(m.get("clobTokenIds"))
            if len(outcomes) != 2 or len(tokens) != 2 or sorted(prices) != [0.0, 1.0]:
                continue  # skip non-binary, unresolved, or 50-50 voids
            if float(m.get("volumeNum") or 0) < min_volume:
                continue
            close = _ts(m.get("closedTime")) or _ts(m.get("endDate"))
            if not close:
                continue
            seen += 1
            if progress:
                print(f"\r  resolved markets sampled {seen}/{n_markets}", end="", flush=True)
            t = int(close - horizon_h * 3600)
            try:
                hist = client.price_history(tokens[0], start_ts=t - 6 * 3600, end_ts=t, fidelity=60, ttl=30 * 86400)
            except Exception:
                continue
            if not hist:
                continue
            p = float(hist[-1]["p"])
            if 0.005 < p < 0.995:
                samples.append((p, int(prices[0] == 1.0)))
    if progress:
        print()
    return samples


def fit_slope(samples: list[tuple[float, int]]) -> tuple[float, float]:
    """Max-likelihood b in  logit(q) = b * logit(p)  (symmetric Platt scaling) and its std error.

    b > 1: favorites under-priced / longshots over-priced (classic favorite-longshot bias).
    b < 1: the market is over-confident at the extremes.
    """
    xs = [logit(p) for p, _ in samples]
    ys = [y for _, y in samples]
    b = 1.0
    info = 1.0
    for _ in range(50):
        grad = info = 0.0
        for x, y in zip(xs, ys):
            q = expit(b * x)
            grad += x * (y - q)
            info += x * x * q * (1 - q)
        step = grad / info if info else 0.0
        b += step
        if abs(step) < 1e-8:
            break
    return b, (1 / math.sqrt(info) if info else float("inf"))


def fit(samples: list[tuple[float, int]], horizon_h: float = 24) -> dict:
    """Fit the slope, then shrink it toward 1 (= trust the market) by its own uncertainty.

    A 14-bucket table looks richer but on a few hundred markets it is mostly noise, and noise in
    a calibration curve shows up downstream as fake "edges". Two numbers, honestly shrunk, don't.
    """
    b_raw, se = fit_slope(samples)
    dev = b_raw - 1
    shrink = max(0.0, 1 - (se / abs(dev)) ** 2) if dev else 0.0  # James-Stein-style: noise -> 0
    b = 1 + dev * shrink
    bins = []
    for lo, hi in zip(EDGES, EDGES[1:]):
        bb = [(p, y) for p, y in samples if lo <= p < hi]
        if bb:
            n = len(bb)
            bins.append({"lo": lo, "hi": min(hi, 1.0), "n": n, "price": sum(p for p, _ in bb) / n,
                         "freq": sum(y for _, y in bb) / n})
    model = {"fitted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "horizon_h": horizon_h,
             "n_markets": len(samples), "slope_raw": b_raw, "slope_se": se, "slope": b, "bins": bins}
    cal = Calibrator(model)
    for bn in bins:
        bn["calibrated"] = cal(bn["price"])
    model["brier_market"] = sum((p - y) ** 2 for p, y in samples) / max(len(samples), 1)
    model["brier_calibrated"] = sum((cal(p) - y) ** 2 for p, y in samples) / max(len(samples), 1)
    return model


class Calibrator:
    def __init__(self, model: dict | None = None):
        self.model = model
        self.slope = float(model["slope"]) if model else 1.0

    @classmethod
    def load(cls, path: Path = DEFAULT_PATH) -> "Calibrator":
        if path.exists():
            return cls(json.loads(path.read_text()))
        return cls(None)  # identity: no longshot adjustment until `sharpbets calibrate` is run

    @property
    def is_identity(self) -> bool:
        return self.model is None or self.slope == 1.0

    def __call__(self, p: float) -> float:
        return p if self.slope == 1.0 else expit(self.slope * logit(p))


def logit(p: float) -> float:
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def expit(x: float) -> float:
    return 1 / (1 + math.exp(-x))
