"""
Vol surface per date (surfaces.py).

Priority per the spec: (1) a real surface if licensed, (2) a parametric SVI-lite
calibrated to that date's VIX, term structure and SKEW. No real surface, SKEW,
VXO or VIX3M/6M/1Y series is reachable in this environment, so every surface is
parametric and tagged as such. What the parametric model uses, and from where:

  ATM 30-day vol      VIX close on the date (real 1990+, realized proxy before)
  ATM term structure  mean-reverting variance model
                        v(T) = v_inf + (v_30 - v_inf) * (1 - exp(-kT)) / (kT)
                      v_inf = trailing 3-year median VIX^2 (no lookahead);
                      k calibrated 2006+ to the VIX-futures front/second slope,
                      default k = 1.5/yr before 2006 (flag "default-MR").
                      Deviation from the spec text: the spec's pre-2007 rule
                      (ATM_1y = VIX x 0.90-1.00) would mark 1-year options at
                      ~76% vol when VIX is 80; the MR model gives ~45-50%, which
                      is what 2008 and 2020 surfaces actually showed. The 0.90-1.00
                      band is reported as a sensitivity in the diagnostics.
  Put-wing slope      0.35 * T^-0.25 per unit log-moneyness (spec default, unfitted
                      because SKEW is unavailable). Before 1987-10-19 the slope is
                      0.10 (the pre-crash "flat smile" regime flag).
  Call wing           half the put slope; floored at 0.5 x ATM.
  Rates / dividends   3m futures-implied rate proxy; Shiller D/P.

Validation on every surface: put-call parity (by construction: one IV per
(K,T) for both), calendar (total variance monotone in T on a moneyness grid),
butterfly (put price convex in K on a strike grid). Violations are logged and
counted in the report.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
import numpy as np
import pandas as pd

SQ2 = math.sqrt(2.0)
def _phi(x): return 0.5 * (1.0 + math.erf(x / SQ2))
def _phi_v(x):
    from scipy.special import erf
    return 0.5 * (1.0 + erf(np.asarray(x) / SQ2))

def bs_put(S, K, T, r, q, iv):
    if T <= 0: return max(K - S, 0.0)
    iv = max(iv, 1e-4)
    d1 = (math.log(S / K) + (r - q + 0.5 * iv * iv) * T) / (iv * math.sqrt(T))
    d2 = d1 - iv * math.sqrt(T)
    return K * math.exp(-r * T) * _phi(-d2) - S * math.exp(-q * T) * _phi(-d1)

def bs_call(S, K, T, r, q, iv):
    if T <= 0: return max(S - K, 0.0)
    iv = max(iv, 1e-4)
    d1 = (math.log(S / K) + (r - q + 0.5 * iv * iv) * T) / (iv * math.sqrt(T))
    d2 = d1 - iv * math.sqrt(T)
    return S * math.exp(-q * T) * _phi(d1) - K * math.exp(-r * T) * _phi(d2)

def bs_put_v(S, K, T, r, q, iv):
    """Vectorised over T (and S, iv) with numpy arrays."""
    S = np.asarray(S, float); T = np.asarray(T, float); iv = np.maximum(np.asarray(iv, float), 1e-4)
    out = np.where(T <= 0, np.maximum(K - S, 0.0), 0.0)
    m = T > 0
    if m.any():
        Tm = T[m]; Sm = S[m] if S.shape else S; ivm = iv[m] if iv.shape else iv
        d1 = (np.log(Sm / K) + (r - q + 0.5 * ivm * ivm) * Tm) / (ivm * np.sqrt(Tm))
        d2 = d1 - ivm * np.sqrt(Tm)
        out[m] = K * np.exp(-r * Tm) * _phi_v(-d2) - Sm * np.exp(-q * Tm) * _phi_v(-d1)
    return out

def bs_call_v(S, K, T, r, q, iv):
    S = np.asarray(S, float); T = np.asarray(T, float); iv = np.maximum(np.asarray(iv, float), 1e-4)
    out = np.where(T <= 0, np.maximum(S - K, 0.0), 0.0)
    m = T > 0
    if m.any():
        Tm = T[m]; Sm = S[m] if S.shape else S; ivm = iv[m] if iv.shape else iv
        d1 = (np.log(Sm / K) + (r - q + 0.5 * ivm * ivm) * Tm) / (ivm * np.sqrt(Tm))
        d2 = d1 - ivm * np.sqrt(Tm)
        out[m] = Sm * np.exp(-q * Tm) * _phi_v(d1) - K * np.exp(-r * Tm) * _phi_v(d2)
    return out

PRE_CRASH_SKEW_END = pd.Timestamp("1987-10-19")
KAPPA_CAP = 3.0      # calibrated speed capped: a -4.5pt/month front slope otherwise collapses 1y vol far below observed crisis levels

def default_kappa(vix: float, v_inf_vol: float) -> float:
    """Pre-2006 default: 1.5/yr in calm markets, rising toward the cap when VIX is far above
    its long-run level (crisis backwardation)."""
    ratio = max(vix / max(v_inf_vol, 1e-6), 1.0)
    return float(min(KAPPA_CAP, 1.5 * ratio ** 0.75))

@dataclass
class Surface:
    date: pd.Timestamp
    S: float
    vix: float            # 30d ATM vol, percent
    v_inf: float          # long-run variance (decimal^2)
    kappa: float
    r: float
    q: float
    put_slope: float      # base slope coefficient (0.35 default, 0.10 pre-1987)
    call_slope_ratio: float = 0.5
    slope_power: float = 0.25   # spec default T^-0.25; 'steep' variant uses 0.5
    tag: str = "parametric"
    term_tag: str = "default-MR"

    # ---- ATM term structure
    def atm(self, T: float) -> float:
        v30 = (self.vix / 100.0) ** 2
        T = max(T, 1.0 / 365)
        kT = self.kappa * T
        v = self.v_inf + (v30 - self.v_inf) * (1.0 - math.exp(-kT)) / kT
        return math.sqrt(max(v, 1e-6))

    def slope(self, T: float) -> float:
        return self.put_slope * (max(T, 1 / 52)) ** (-self.slope_power)

    def iv(self, K: float, T: float) -> float:
        F = self.S * math.exp((self.r - self.q) * max(T, 1e-6))
        k = math.log(K / F)
        a = self.atm(T)
        if k < 0:
            return a + self.slope(T) * (-k)
        return max(a - self.call_slope_ratio * self.slope(T) * k, 0.5 * a)

    def put(self, K: float, T: float) -> float:
        return bs_put(self.S, K, T, self.r, self.q, self.iv(K, T))

    def call(self, K: float, T: float) -> float:
        return bs_call(self.S, K, T, self.r, self.q, self.iv(K, T))

    # ---- arbitrage checks
    def check(self) -> dict:
        res = {"parity": True, "calendar": True, "butterfly": True}
        Ts = [1/12, 3/12, 6/12, 12/12, 18/12, 24/12]
        for k in (-0.30, -0.15, -0.05, 0.0, 0.05):
            w = []
            for T in Ts:
                K = self.S * math.exp(k)
                w.append(self.iv(K, T) ** 2 * T)
            if any(w[i+1] < w[i] - 1e-9 for i in range(len(w) - 1)):
                res["calendar"] = False
        for T in (3/12, 12/12):
            Ks = [self.S * m for m in np.linspace(0.5, 1.2, 36)]
            P = [self.put(K, T) for K in Ks]
            d2 = [P[i-1] - 2 * P[i] + P[i+1] for i in range(1, len(P) - 1)]
            if min(d2) < -1e-6 * self.S:
                res["butterfly"] = False
        K = self.S * 0.95; T = 0.5
        lhs = self.call(K, T) - self.put(K, T)
        rhs = self.S * math.exp(-self.q * T) - K * math.exp(-self.r * T)
        res["parity"] = abs(lhs - rhs) < 1e-6 * self.S
        return res


def calibrate_kappa(vix: float, v_inf: float, slope_pts_per_month: float) -> float:
    """Pick kappa so the model's month-2 minus month-1 ATM vol matches the observed
    VIX-futures slope (vol points per month). Grid search on [0.3, 12]."""
    v30 = (vix / 100.0) ** 2
    def diff(k):
        def sig(T):
            kT = k * T
            return 100 * math.sqrt(max(v_inf + (v30 - v_inf) * (1 - math.exp(-kT)) / kT, 1e-6))
        return sig(2 / 12) - sig(1 / 12)
    grid = np.exp(np.linspace(math.log(0.3), math.log(KAPPA_CAP), 60))
    best = min(grid, key=lambda k: abs(diff(k) - slope_pts_per_month))
    return float(best)


def surface_at(daily: pd.DataFrame, d: pd.Timestamp, und: str = "spx",
               put_slope_default: float = 0.35, term_rule: str = "MR", slope_power: float = 0.25) -> Surface:
    """Build the surface for date d using ONLY rows with index <= d."""
    hist = daily.loc[:d]
    row = hist.iloc[-1]
    S = float(row[und])
    vix = float(row["vix"])
    if und == "ndx":
        vix = vix * 1.30   # NDX ATM vol ran ~1.25-1.35x VIX; VXN unavailable here (tag ndx-vol-ratio)
    win = hist.loc[hist.index >= d - pd.DateOffset(years=3), "vix"]
    v_inf_vix = float(win.median()) if len(win) > 250 else 20.0
    if und == "ndx": v_inf_vix *= 1.30
    v_inf = (v_inf_vix / 100.0) ** 2
    slope = row.get("vix_slope", np.nan)
    if term_rule == "spec_0.95":
        # spec's literal pre-2007 rule: ATM_1y = VIX x 0.95 -> choose kappa to hit it
        target = vix * 0.95
        v30 = (vix / 100) ** 2
        def sig1y(k):
            return 100 * math.sqrt(max(v_inf + (v30 - v_inf) * (1 - math.exp(-k)) / k, 1e-6))
        grid = np.exp(np.linspace(math.log(0.05), math.log(12.0), 80))
        kappa = float(min(grid, key=lambda k: abs(sig1y(k) - target))); term_tag = "spec-0.95"
    elif pd.notna(slope):
        kappa = calibrate_kappa(vix, v_inf, float(slope)); term_tag = "vix-futures"
    else:
        kappa = default_kappa(vix, v_inf_vix); term_tag = "default-MR"
    put_slope = put_slope_default if d >= PRE_CRASH_SKEW_END else 0.10
    return Surface(date=d, S=S, vix=vix, v_inf=v_inf, kappa=kappa,
                   r=float(row["r3m"]), q=float(row["dy"]) if und == "spx" else 0.005,
                   put_slope=put_slope, tag="parametric", term_tag=term_tag, slope_power=slope_power)
