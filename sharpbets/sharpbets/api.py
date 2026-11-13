"""Thin, cached client for Polymarket's public APIs (no keys needed).

Endpoints used (verified Nov 2026):
  Gamma  https://gamma-api.polymarket.com/markets            market metadata + prices
  Data   https://data-api.polymarket.com/v2/leaderboard       top wallets by PnL
         https://data-api.polymarket.com/v2/positions         a wallet's open/closed positions
         https://data-api.polymarket.com/v2/holders           top holders per outcome token
         https://data-api.polymarket.com/v2/trades            recent fills in a market
  CLOB   https://clob.polymarket.com/book                     live order book
         https://clob.polymarket.com/prices-history           price time series
         https://clob.polymarket.com/fee-rate                 taker fee flag per token
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

GAMMA = "https://gamma-api.polymarket.com"
DATA = "https://data-api.polymarket.com/v2"
CLOB = "https://clob.polymarket.com"

DEFAULT_CACHE = Path(os.environ.get("SHARPBETS_CACHE", Path.home() / ".cache" / "sharpbets"))


class ApiError(RuntimeError):
    pass


class Client:
    def __init__(self, cache_dir: Path | None = DEFAULT_CACHE, min_interval: float = 0.12,
                 timeout: float = 25.0, verbose: bool = False):
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.min_interval = min_interval
        self.timeout = timeout
        self.verbose = verbose
        self._last = 0.0
        self.calls = 0

    # ------------------------------------------------------------------ core
    def get(self, base: str, path: str, params: dict[str, Any] | None = None, ttl: float = 0) -> Any:
        q = urllib.parse.urlencode({k: v for k, v in (params or {}).items() if v is not None})
        url = f"{base}{path}" + (f"?{q}" if q else "")
        cache_file = None
        if self.cache_dir and ttl > 0:
            cache_file = self.cache_dir / (hashlib.sha1(url.encode()).hexdigest() + ".json")
            if cache_file.exists() and time.time() - cache_file.stat().st_mtime < ttl:
                return json.loads(cache_file.read_text())
        body = self._fetch(url)
        if cache_file is not None:
            cache_file.write_text(json.dumps(body))
        return body

    def _fetch(self, url: str) -> Any:
        delay = 1.0
        for attempt in range(5):
            wait = self.min_interval - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            self.calls += 1
            if self.verbose:
                print(f"  GET {url}")
            req = urllib.request.Request(url, headers={"User-Agent": "sharpbets/0.1", "Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                    time.sleep(delay)
                    delay *= 2
                    continue
                detail = e.read().decode(errors="replace")[:300]
                raise ApiError(f"HTTP {e.code} for {url}: {detail}") from None
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt < 4:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise ApiError(f"Network error for {url}: {e}") from None
        raise ApiError(f"Gave up on {url}")

    def _paged(self, path: str, params: dict[str, Any], max_items: int, ttl: float) -> list[dict]:
        out: list[dict] = []
        cursor = None
        while len(out) < max_items:
            p = dict(params, limit=min(500, max_items - len(out)))
            if cursor:
                p["cursor"] = cursor
            body = self.get(DATA, path, p, ttl=ttl)
            out.extend(body.get("data", []))
            pg = body.get("pagination") or {}
            cursor = pg.get("next_cursor")
            if not pg.get("has_more") or not cursor:
                break
        return out

    # ------------------------------------------------------------- gamma
    def markets(self, *, closed: bool, limit: int = 100, offset: int = 0, order: str = "volume24hr",
                ascending: bool = False, ttl: float = 300, **extra: Any) -> list[dict]:
        params = {"closed": str(closed).lower(), "limit": limit, "offset": offset,
                  "order": order, "ascending": str(ascending).lower(), **extra}
        if not closed:
            params["active"] = "true"
        return self.get(GAMMA, "/markets", params, ttl=ttl)

    def market_by_slug(self, slug: str) -> dict | None:
        res = self.get(GAMMA, "/markets", {"slug": slug, "include_tag": "true"}, ttl=60)
        return res[0] if res else None

    # -------------------------------------------------------------- data
    def leaderboard(self, period: str = "all", order_by: str = "PNL", limit: int = 200,
                    category: str | None = None) -> list[dict]:
        params = {"timePeriod": period, "orderBy": order_by}
        if category:
            params["category"] = category
        return self._paged("/leaderboard", params, limit, ttl=6 * 3600)

    def positions(self, wallet: str, status: str = "CLOSED", limit: int = 500) -> list[dict]:
        # sort_by=TIMESTAMP => most recent first, an unbiased sample (default order is by PnL).
        return self._paged("/positions", {"user": wallet, "status": status, "sort_by": "TIMESTAMP"},
                           limit, ttl=12 * 3600)

    def resolved_positions(self, wallet: str, limit: int = 500) -> list[dict]:
        """A wallet's recent finished bets, winners AND losers.

        Losing bets held to expiry are never redeemed, so Polymarket keeps them under status=OPEN
        at price 0. Using only status=CLOSED makes every whale look like a 95% winner.
        """
        closed = self.positions(wallet, "CLOSED", limit)
        opened = self.positions(wallet, "OPEN", limit)
        def px(p: dict) -> float:
            v = p.get("current_price")
            return 0.5 if v is None else float(v)  # NB: 0.0 is a real price (a loser), not "missing"

        settled = [p for p in opened if px(p) <= 0.01 or px(p) >= 0.99]
        # Each list is the most recent `limit`; only keep the time window both lists fully cover.
        cutoff = 0
        for lst in (closed, opened):
            if len(lst) >= limit:
                cutoff = max(cutoff, min(int(p.get("last_event_at") or 0) for p in lst))
        return [p for p in closed + settled if int(p.get("last_event_at") or 0) >= cutoff]

    def holders(self, condition_id: str, limit: int = 20) -> list[dict]:
        return self.get(DATA, "/holders", {"condition": condition_id, "limit": limit}, ttl=120).get("data", [])

    def trades(self, condition_id: str, limit: int = 1000) -> list[dict]:
        return self.get(DATA, "/trades", {"condition": condition_id, "limit": limit}, ttl=120).get("data", [])

    # -------------------------------------------------------------- clob
    def book(self, token_id: str) -> dict:
        return self.get(CLOB, "/book", {"token_id": token_id}, ttl=30)

    def price_history(self, token_id: str, *, interval: str | None = None, start_ts: int | None = None,
                      end_ts: int | None = None, fidelity: int = 60, ttl: float = 300) -> list[dict]:
        params = {"market": token_id, "interval": interval, "startTs": start_ts, "endTs": end_ts,
                  "fidelity": fidelity}
        return self.get(CLOB, "/prices-history", params, ttl=ttl).get("history", [])

    def fee_rate(self, token_id: str) -> float:
        try:
            return float(self.get(CLOB, "/fee-rate", {"token_id": token_id}, ttl=3600).get("base_fee", 0))
        except ApiError:
            return 0.0


def parse_json_field(v: Any) -> list:
    """Gamma returns some list fields as JSON-encoded strings."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return []
    return v or []
