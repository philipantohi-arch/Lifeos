"""
replay.py - prices each structure at each entry date on that date's surface, walks
forward daily marking on each day's surface, applies the exit rules, and aggregates.

Conventions
  cost      = entry premium x (1 + haircut)            (haircut 7% of premium)
  exit      = value x (1 - haircut) when closed before expiry; intrinsic at expiry
  multiple  = payoff / cost for net-debit put structures (0 = total loss, 1 = breakeven)
              for seagulls: 1 + (payoff - cost) / max_risk, where max_risk is the larger
              of the net debit and the short call's loss on a +20% rally over the tenor
  entry grid = month-ends from 24 months before the episode peak to the peak
  timing miss = the structure expired before the episode trough
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from .surfaces import bs_put_v, bs_call_v, PRE_CRASH_SKEW_END, calibrate_kappa, default_kappa

HAIRCUT = 0.07
EXIT_TRIGGER = 0.22
TIERED_FIRST = 0.12
IPS_TRIMS = (3.0, 5.0)
IPS_TRAIL = 0.40
IPS_ACTIVATE = 2.0
TIME_STOP_DTE = 60
NDX_VOL_RATIO = 1.30

@dataclass
class Structure:
    label: str
    und: str            # "spx" | "ndx"
    tenor_m: int
    legs: list          # [(kind, strike_mult, qty)]
    burry: bool = False
    seagull: bool = False
    v4: bool = True

STRUCTS = [
    Structure("SPX Mar-27 10% OTM",             "spx", 7,  [("put", .90, +1)]),
    Structure("SPX Mar-27 90/75 spread",        "spx", 7,  [("put", .90, +1), ("put", .75, -1)]),
    Structure("[B] QQQ Jun-27 p 11% OTM",       "ndx", 10, [("put", .89, +1)], burry=True),
    Structure("SPX Dec-27 10% OTM",             "spx", 16, [("put", .90, +1)]),
    Structure("SPX Dec-27 90/70 spread",        "spx", 16, [("put", .90, +1), ("put", .70, -1)]),
    Structure("QQQ Dec-27 10% OTM",             "ndx", 16, [("put", .90, +1)]),
    Structure("QQQ Dec-27 90/65 spread",        "ndx", 16, [("put", .90, +1), ("put", .65, -1)]),
    Structure("SPX Jun-28 10% OTM",             "spx", 22, [("put", .90, +1)]),
    Structure("QQQ Jun-28 90/65 spread",        "ndx", 22, [("put", .90, +1), ("put", .65, -1)]),
    # v5 seagulls: v5 is not present in this environment; definitions reconstructed
    # classic seagull: put spread part-financed by a far-OTM short call (call strike chosen so the
    # structure is a small net debit at typical vol; the call's rally risk is the "max risk")
    Structure("SPX Dec-27 seagull 90/70 -125c", "spx", 16, [("put", .90, +1), ("put", .70, -1), ("call", 1.25, -1)], seagull=True, v4=False),
    Structure("QQQ Dec-27 seagull 90/65 -135c", "ndx", 16, [("put", .90, +1), ("put", .65, -1), ("call", 1.35, -1)], seagull=True, v4=False),
    Structure("SPX Mar-27 seagull 90/75 -115c", "spx", 7,  [("put", .90, +1), ("put", .75, -1), ("call", 1.15, -1)], seagull=True, v4=False),
]
NOT_REPLAYABLE = ["SOXX (no index history here)", "NVDA, ORCL, PLTR, CRWV, VRT, DLR (single names: no price/vol history)",
                  "HYG (no credit-ETF history)"]

# ------------------------------------------------------------------ surface grid
class Grid:
    """Per-day surface parameters for one underlying, computed with trailing data only."""
    def __init__(self, daily: pd.DataFrame, und: str, put_slope_default=0.35, term_rule="MR", slope_power=0.25):
        self.slope_power = slope_power
        d = daily.dropna(subset=[und]).copy()
        self.idx = d.index
        self.S = d[und].to_numpy(float)
        vix = d["vix"].to_numpy(float) * (NDX_VOL_RATIO if und == "ndx" else 1.0)
        self.vix = vix
        vinf_vix = d["vix"].rolling(756, min_periods=250).median().bfill().to_numpy(float) * (NDX_VOL_RATIO if und == "ndx" else 1.0)
        self.v_inf = (vinf_vix / 100.0) ** 2
        self.r = d["r3m"].to_numpy(float)
        self.q = (d["dy"].to_numpy(float) if und == "spx" else np.full(len(d), 0.005))
        slope = d["vix_slope"].to_numpy(float)
        kap = np.array([default_kappa(vix[i], vinf_vix[i]) for i in range(len(d))])
        self.term_tag = np.where(np.isfinite(slope), "vix-futures", "default-MR")
        if term_rule == "spec_0.95":
            self.term_tag[:] = "spec-0.95"
        for i in range(len(d)):
            if term_rule == "spec_0.95":
                target = vix[i] * 0.95; v30 = (vix[i] / 100) ** 2; vi = self.v_inf[i]
                grid = np.exp(np.linspace(math.log(0.05), math.log(12.0), 60))
                def sig1y(k): return 100 * math.sqrt(max(vi + (v30 - vi) * (1 - math.exp(-k)) / k, 1e-6))
                kap[i] = float(min(grid, key=lambda k: abs(sig1y(k) - target)))
            elif np.isfinite(slope[i]):
                kap[i] = calibrate_kappa(vix[i], self.v_inf[i], slope[i])
        self.kappa = kap
        self.put_slope = np.where(self.idx >= PRE_CRASH_SKEW_END, put_slope_default, 0.10)
        self.und = und

    def loc(self, ts): return self.idx.get_indexer([ts], method="pad")[0]

    def leg_path(self, i0: int, i1: int, K: float, expiry: pd.Timestamp, kind: str) -> np.ndarray:
        sl = slice(i0, i1 + 1)
        days = (expiry - self.idx[sl]).days.to_numpy(float)
        T = np.maximum(days, 0) / 365.0
        S = self.S[sl]; v30 = (self.vix[sl] / 100.0) ** 2; vi = self.v_inf[sl]; k = self.kappa[sl]
        Tm = np.maximum(T, 1 / 365)
        kT = k * Tm
        atm = np.sqrt(np.maximum(vi + (v30 - vi) * (1 - np.exp(-kT)) / kT, 1e-6))
        r = self.r[sl]; q = self.q[sl]
        F = S * np.exp((r - q) * Tm)
        lk = np.log(K / F)
        sl_T = self.put_slope[sl] * np.maximum(Tm, 1 / 52) ** (-self.slope_power)
        iv = np.where(lk < 0, atm + sl_T * (-lk), np.maximum(atm - 0.5 * sl_T * lk, 0.5 * atm))
        out = np.empty(len(S))
        for j in range(len(S)):
            if kind == "put":
                out[j] = bs_put_v(S[j], K, T[j], r[j], q[j], iv[j])
            else:
                out[j] = bs_call_v(S[j], K, T[j], r[j], q[j], iv[j])
        return out

# ------------------------------------------------------------------ one replay
@dataclass
class Result:
    structure: str; und: str; entry: pd.Timestamp; expiry: pd.Timestamp
    cost: float; risk: float; S0: float
    payoff: dict = field(default_factory=dict)      # rule -> payoff
    multiple: dict = field(default_factory=dict)    # rule -> multiple
    peak_mult: float = 0.0; peak_date: pd.Timestamp = None; months_to_peak: float = 0.0
    max_dd: float = 0.0
    truncated: bool = False
    exit22_date: pd.Timestamp = None
    iv_entry_atm: float = 0.0

def replay_one(g: Grid, st: Structure, entry: pd.Timestamp) -> Result | None:
    i0 = g.loc(entry)
    if i0 < 0: return None
    entry = g.idx[i0]
    expiry = entry + pd.DateOffset(months=st.tenor_m)
    i1 = g.loc(expiry)
    truncated = g.idx[i1] < expiry - pd.Timedelta(days=5)
    S0 = g.S[i0]
    legs = []
    for kind, km, qty in st.legs:
        K = S0 * km
        legs.append((kind, K, qty, g.leg_path(i0, i1, K, expiry, kind)))
    V = sum(qty * path for _, _, qty, path in legs)     # net value path, per unit of S0-scaled contract
    prem = V[0]
    cost = prem * (1 + HAIRCUT) if prem > 0 else prem * (1 - HAIRCUT)   # credit received is haircut too
    if st.seagull:
        call = [l for l in legs if l[0] == "call"][0]
        # max risk = short-call loss on a +35% rally by expiry, net of the credit received (stress convention)
        call_loss = max(0.0, 1.35 * S0 - call[1]) - call[3][0]
        risk = max(cost, call_loss, 0.01 * S0)
    else:
        risk = max(cost, 1e-9)
    S = g.S[i0:i1 + 1]
    n = len(S)
    at_exp = not truncated
    def mult(pay):
        return (pay / cost) if not st.seagull else 1.0 + (pay - cost) / risk
    res = Result(st.label, st.und, entry, expiry, cost, risk, S0, truncated=truncated)
    # --- hold
    pay_hold = V[-1] if at_exp else V[-1] * (1 - HAIRCUT)
    # --- v4: exit all at -22%
    trig = np.where(S <= (1 - EXIT_TRIGGER) * S0)[0]
    if len(trig) and trig[0] > 0:
        t = trig[0]; pay_v4 = V[t] * (1 - HAIRCUT); res.exit22_date = g.idx[i0 + t]
    else:
        pay_v4 = pay_hold
    # --- v6 addition: exit all at -22% from the running peak since entry (not from entry spot)
    runmax = np.maximum.accumulate(S)
    trig_p = np.where(S <= (1 - EXIT_TRIGGER) * runmax)[0]
    if len(trig_p) and trig_p[0] > 0:
        pay_pk = V[trig_p[0]] * (1 - HAIRCUT)
    else:
        pay_pk = pay_hold
    # --- tiered
    t1 = np.where(S <= (1 - TIERED_FIRST) * S0)[0]
    if len(t1) and t1[0] > 0:
        a = t1[0]; first = 0.5 * V[a] * (1 - HAIRCUT)
        t2 = np.where(S[a:] <= (1 - EXIT_TRIGGER) * S0)[0]
        second = 0.5 * (V[a + t2[0]] * (1 - HAIRCUT) if len(t2) else pay_hold)
        pay_tier = first + second
    else:
        pay_tier = pay_hold
    # --- IPS
    rem = 1.0; realized = 0.0; peak = -1e9; trimmed = 0; active = False
    dte = (expiry - g.idx[i0:i1 + 1]).days.to_numpy()
    base = cost if cost > 0 else risk
    done = False
    for t in range(1, n):
        v = V[t]
        if v >= IPS_ACTIVATE * base: active = True
        peak = max(peak, v)
        if trimmed < 2 and v >= IPS_TRIMS[trimmed] * base:
            realized += (1 / 3) * v * (1 - HAIRCUT); rem -= 1 / 3; trimmed += 1
        if active and v <= (1 - IPS_TRAIL) * peak and rem > 0:
            realized += rem * v * (1 - HAIRCUT); rem = 0; done = True; break
        if dte[t] <= min(TIME_STOP_DTE, 0.25 * dte[0]) and rem > 0:
            realized += rem * v * (1 - HAIRCUT); rem = 0; done = True; break
    if rem > 0:
        realized += rem * pay_hold
    pay_ips = realized
    for rule, pay in (("hold", pay_hold), ("v4_-22", pay_v4), ("peak_-22", pay_pk), ("tiered", pay_tier), ("IPS", pay_ips)):
        res.payoff[rule] = pay; res.multiple[rule] = mult(pay)
    m_path = np.array([mult(v * (1 - HAIRCUT)) for v in V])
    j = int(np.argmax(m_path)); res.peak_mult = float(m_path[j]); res.peak_date = g.idx[i0 + j]
    res.months_to_peak = (res.peak_date - entry).days / 30.44
    res.max_dd = float(m_path.min())
    res.iv_entry_atm = float(math.sqrt(g.v_inf[i0] + ((g.vix[i0] / 100) ** 2 - g.v_inf[i0]) * (1 - math.exp(-g.kappa[i0] * st.tenor_m / 12)) / (g.kappa[i0] * st.tenor_m / 12)))
    return res

# ------------------------------------------------------------------ grids of entries
def month_ends(start: pd.Timestamp, end: pd.Timestamp, idx: pd.DatetimeIndex) -> list:
    out = []
    for per in pd.period_range(start, end, freq="M"):
        me = per.to_timestamp(how="end").normalize()
        i = idx.get_indexer([me], method="pad")[0]
        if i >= 0 and idx[i] >= start and idx[i] <= end:
            out.append(idx[i])
    return sorted(set(out))

def run_episode(grids: dict, ep: dict, structs=STRUCTS) -> pd.DataFrame:
    peak = pd.Timestamp(ep["peak"]); trough = pd.Timestamp(ep["trough"])
    rows = []
    for st in structs:
        g = grids[st.und]
        entries = month_ends(peak - pd.DateOffset(months=24), peak, g.idx)
        for e in entries:
            r = replay_one(g, st, e)
            if r is None: continue
            offset = round((peak - e).days / 30.44)
            for rule, m in r.multiple.items():
                rows.append(dict(episode=ep["id"], analog=ep["analog"], structure=st.label, und=st.und,
                                 seagull=st.seagull, burry=st.burry, entry=e, offset_m=offset, rule=rule,
                                 cost_pct=100 * r.cost / r.S0, multiple=m, payoff=r.payoff[rule], pnl_pct=100 * (r.payoff[rule] - r.cost) / r.S0,
                                 peak_mult=r.peak_mult, months_to_peak=r.months_to_peak, max_dd=r.max_dd,
                                 timing_miss=bool(r.expiry < trough), truncated=r.truncated,
                                 exit22_before_trough=bool(r.exit22_date is not None and r.exit22_date < trough),
                                 exit22_fired=bool(r.exit22_date is not None), iv_entry=100 * r.iv_entry_atm))
    return pd.DataFrame(rows)

def run_grid(grids: dict, start: pd.Timestamp, end: pd.Timestamp, structs=STRUCTS, tag="baseline") -> pd.DataFrame:
    rows = []
    for st in structs:
        g = grids[st.und]
        for e in month_ends(start, end, g.idx):
            if e + pd.DateOffset(months=st.tenor_m) > g.idx[-1]: continue
            r = replay_one(g, st, e)
            if r is None: continue
            for rule, m in r.multiple.items():
                rows.append(dict(episode=tag, analog="NonEvent", structure=st.label, und=st.und, seagull=st.seagull,
                                 burry=st.burry, entry=e, offset_m=np.nan, rule=rule, cost_pct=100 * r.cost / r.S0,
                                 multiple=m, payoff=r.payoff[rule], pnl_pct=100 * (r.payoff[rule] - r.cost) / r.S0, peak_mult=r.peak_mult, months_to_peak=r.months_to_peak,
                                 max_dd=r.max_dd, timing_miss=False, truncated=r.truncated,
                                 exit22_before_trough=False, exit22_fired=bool(r.exit22_date is not None), iv_entry=100 * r.iv_entry_atm))
    return pd.DataFrame(rows)

# ------------------------------------------------------------------ entry filter
def filter_mask(daily: pd.DataFrame, dates, erp_max=0.0, cape_min=32.0, vix_max=18.0) -> pd.Series:
    """Tranche rule: (ERP <= erp_max or CAPE > cape_min) AND VIX < vix_max. HY OAS leg
    unavailable in this environment and therefore not applied."""
    rows = daily.reindex(pd.DatetimeIndex(dates), method="pad")
    val = ((rows["erp"] <= erp_max) | (rows["cape"] > cape_min)) & (rows["vix"] < vix_max)
    val[rows["erp"].isna() & rows["cape"].isna()] = False
    return val
