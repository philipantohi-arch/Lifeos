"""Sportsbook public betting splits (ticket % and money %) for Polymarket sports markets.

Source: Action Network's public-betting scoreboard, consensus book (id 15), which aggregates
bet counts and handle across US sportsbooks. Covers NFL, NBA, NHL, NCAAF, NCAAB (MLB / WNBA in
season). Each Polymarket game market (moneyline / spread / total) is matched to its Action
Network game by league, start time and team names, and the splits are oriented to the
Polymarket outcome order.

    tickets % = share of bets placed      -> how "public" a side is
    money %   = share of dollars wagered  -> money% >> tickets% means fewer, bigger (sharper) bets
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from .api import Client
from .calibration import _ts

ACTION_NETWORK = "https://api.actionnetwork.com/web/v2/scoreboard/publicbetting"
CONSENSUS_BOOK = "15"
ET = timezone(timedelta(hours=-5))  # AN groups games by US date; +-1 day lookup absorbs DST
# Polymarket slug prefix -> Action Network league
LEAGUES = {"nba": "nba", "nfl": "nfl", "nhl": "nhl", "mlb": "mlb", "wnba": "wnba",
           "cfb": "ncaaf", "cbb": "ncaab"}
AN_TYPES = {"moneyline": "moneyline", "spreads": "spread", "totals": "total"}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def league_for(market: dict) -> str | None:
    return LEAGUES.get((market.get("slug") or "").split("-", 1)[0])


def games_for(client: Client, league: str, start_ts: float) -> list[dict]:
    games: list[dict] = []
    day = datetime.fromtimestamp(start_ts, tz=ET)
    for delta in (-1, 0, 1):
        d = (day + timedelta(days=delta)).strftime("%Y%m%d")
        try:
            body = client.get(ACTION_NETWORK, f"/{league}", {"bookIds": CONSENSUS_BOOK, "date": d}, ttl=600)
        except Exception:
            continue
        games += body.get("games") or []
    return games


def _team_score(outcome: str, team: dict) -> int:
    o = _norm(outcome)
    names = [_norm(team.get(k, "")) for k in ("full_name", "display_name", "short_name", "abbr")]
    if o in names:
        return 3
    short = _norm(team.get("short_name", ""))  # nickname, e.g. "seahawks"
    if short and short in o:
        return 2
    full = names[0]
    if o and full and (o in full or full in o):
        return 1
    return 0


def match_teams(outcomes: list[str], teams: list[dict]) -> list[int] | None:
    """Team id for each Polymarket outcome, or None if the pairing isn't unambiguous."""
    if len(teams) != 2:
        return None
    a = [_team_score(outcomes[0], t) for t in teams]
    b = [_team_score(outcomes[1], t) for t in teams]
    straight, crossed = a[0] + b[1], a[1] + b[0]
    if straight == crossed or min(a[0], b[1]) == 0 and min(a[1], b[0]) == 0:
        return None
    pair = (teams[0], teams[1]) if straight > crossed else (teams[1], teams[0])
    if min(_team_score(outcomes[0], pair[0]), _team_score(outcomes[1], pair[1])) == 0:
        return None
    return [pair[0]["id"], pair[1]["id"]]


def title_teams(market: dict) -> list[str]:
    title = ((market.get("events") or [{}])[0].get("title") or market.get("question") or "").split(":")[0]
    parts = re.split(r"\s+(?:vs\.?|v\.?|@|at)\s+", title, maxsplit=1, flags=re.I)
    return [p.strip() for p in parts] if len(parts) == 2 else ["", ""]


def sportsbook_splits(client: Client, market: dict, outcomes: list[str]) -> dict | None:
    """Ticket/money splits oriented to Polymarket's outcome order, or None if unavailable."""
    league = league_for(market)
    an_type = AN_TYPES.get(market.get("sportsMarketType") or "")
    start = _ts(market.get("gameStartTime"))
    if not league or not an_type or not start or len(outcomes) != 2:
        return None
    for g in games_for(client, league, start):
        gs = _ts(g.get("start_time"))
        if not gs or abs(gs - start) > 3 * 3600:
            continue
        rows = ((g.get("markets") or {}).get(CONSENSUS_BOOK) or {}).get("event", {}).get(an_type) or []
        if an_type == "total":
            if sorted(o.lower() for o in outcomes) != ["over", "under"]:
                continue
            # Over/Under names no team, so identify the game from the title ("Bucks vs. Magic: O/U ...").
            if not match_teams(title_teams(market), g.get("teams") or []):
                continue
            ids = None
        else:
            ids = match_teams(outcomes, g.get("teams") or [])
            if not ids:
                continue
        picked = []
        for i in range(2):
            row = next((r for r in rows if (r.get("side") == outcomes[i].lower() if ids is None
                                              else r.get("team_id") == ids[i])), None)
            if not row:
                break
            bi = row.get("bet_info") or {}
            picked.append((float((bi.get("tickets") or {}).get("percent") or 0),
                           float((bi.get("money") or {}).get("percent") or 0), row.get("value")))
        if len(picked) != 2 or sum(p[0] for p in picked) == 0:
            continue
        return {"tickets": [picked[0][0] / 100, picked[1][0] / 100],
                "money": [picked[0][1] / 100, picked[1][1] / 100],
                "num_bets": int(g.get("num_bets") or 0),
                "book_line": picked[0][2] if an_type != "moneyline" else None,
                "source": "Action Network consensus"}
    return None
