"""
v6 data loaders. Every series is downloaded once into data/cache/ and re-read from
there afterwards. Each loader returns a pandas object plus a SOURCE TAG that is
carried into the report ("real" / "parametric" / "spliced" / "proxy").

Reachability in this environment (checked 2026-09-17): FRED, CBOE, Yahoo, Stooq,
Shiller/Yale, Treasury, Fed H.15 and the Internet Archive are all blocked by the
egress proxy. GitHub raw files are reachable. The sources below are therefore
public GitHub-hosted mirrors, and several series are *derived* rather than raw:

  SPX daily     futures back-adjusted continuous (pysystemtrade), re-anchored monthly to
                Shiller's monthly average spot level  -> tag "futures-derived"
  NDX daily     futures back-adjusted (pysystemtrade, 1999-12+), re-anchored at a small
                set of spot closes listed in ANCHORS_NDX (from memory; verify)  -> "futures-derived"
  VIX daily     CBOE via datasets/finance-vix, 1990-01+                          -> "real"
  VIX pre-1990  realized-vol proxy (EWMA 21d x 1.2, floored)                     -> "proxy"
  VIX term      VIX futures front/second contract slope (pysystemtrade, 2006+)   -> "vix-futures"
  3m rate       100 - Eurodollar/SOFR 3m futures continuous (pysystemtrade)      -> "proxy"
  10y yield     datasets/bond-yields-us-10y monthly                              -> "real (monthly)"
  CAPE, D/P, E/P Shiller monthly via datasets/s-and-p-500 (to 2023-09)          -> "real (monthly)"
  SKEW, VXO, VIX3M/6M/1Y, HY OAS: NOT AVAILABLE -> parametric defaults, see surfaces.py
"""
from __future__ import annotations
import io, os, sys, json, gzip, math
from pathlib import Path
import numpy as np
import pandas as pd
import urllib.request

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
CACHE.mkdir(exist_ok=True)

URLS = {
    "vix_daily": "https://raw.githubusercontent.com/datasets/finance-vix/main/data/vix-daily.csv",
    "sp500_fut": "https://raw.githubusercontent.com/robcarver17/pysystemtrade/master/data/futures/adjusted_prices_csv/SP500.csv",
    "ndx_fut":   "https://raw.githubusercontent.com/robcarver17/pysystemtrade/master/data/futures/adjusted_prices_csv/NASDAQ.csv",
    "sofr_fut":  "https://raw.githubusercontent.com/robcarver17/pysystemtrade/master/data/futures/adjusted_prices_csv/SOFR.csv",
    "vix_mult":  "https://raw.githubusercontent.com/robcarver17/pysystemtrade/master/data/futures/multiple_prices_csv/VIX.csv",
    "shiller_m": "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv",
    "us10y_m":   "https://raw.githubusercontent.com/datasets/bond-yields-us-10y/main/data/monthly.csv",
}

# NDX spot closes used to re-anchor the Panama-adjusted futures series. These are
# from memory and must be verified against an exchange source before the NDX rows
# are treated as anything better than "indicative".
ANCHORS_NDX = {
    "1999-12-31": 3707.83, "2000-03-27": 4704.73, "2002-10-07": 804.64,
    "2007-10-31": 2238.98, "2009-03-09": 1043.87, "2020-02-19": 9718.73,
    "2020-03-23": 6994.29, "2021-11-19": 16573.34, "2022-12-28": 10679.34,
    "2024-03-28": 18254.69,
}

def _fetch(key: str) -> Path:
    p = CACHE / f"{key}.csv"
    if p.exists() and p.stat().st_size > 0:
        return p
    req = urllib.request.Request(URLS[key], headers={"User-Agent": "bdcr26-v6/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    p.write_bytes(data)
    return p

# ----------------------------------------------------------------------------- raw
def vix_daily() -> pd.Series:
    df = pd.read_csv(_fetch("vix_daily"), parse_dates=["DATE"]).set_index("DATE").sort_index()
    s = df["CLOSE"].astype(float); s.name = "vix"; return s

def _fut(key: str) -> pd.Series:
    df = pd.read_csv(_fetch(key), parse_dates=["DATETIME"])
    df["DATE"] = df["DATETIME"].dt.normalize()
    s = df.groupby("DATE")["price"].last().astype(float).sort_index()
    return s

def shiller_monthly() -> pd.DataFrame:
    df = pd.read_csv(_fetch("shiller_m"), parse_dates=["Date"]).set_index("Date").sort_index()
    df = df.rename(columns={"SP500": "price", "Dividend": "div", "Earnings": "earn",
                            "Long Interest Rate": "gs10", "PE10": "cape"})
    for c in ("div", "earn", "cape"):
        df.loc[df[c] <= 0, c] = np.nan
    df["dy"] = df["div"] / df["price"]
    df["ep"] = df["earn"] / df["price"]
    return df[["price", "div", "earn", "gs10", "cape", "dy", "ep"]]

def us10y_monthly() -> pd.Series:
    df = pd.read_csv(_fetch("us10y_m"), parse_dates=["Date"]).set_index("Date").sort_index()
    s = df["Rate"].astype(float) / 100.0; s.name = "gs10"; return s

# ----------------------------------------------------------------------- derived
def spx_daily() -> tuple[pd.Series, str]:
    """Daily SPX spot level reconstructed from the Panama (difference) back-adjusted
    futures series. Difference adjustment preserves point changes but not ratios, so
    each month the series is shifted by a constant so that its monthly mean equals
    Shiller's monthly average spot price. Returns inside a month are then exact
    futures point changes divided by the true level; month boundaries carry a small
    jump equal to one month of carry drift (typically 0.1-0.3%)."""
    fut = _fut("sp500_fut")
    sh = shiller_monthly()["price"]
    out = fut.copy()
    ym = fut.index.to_period("M")
    for per, grp in fut.groupby(ym):
        ts = per.to_timestamp()
        if ts in sh.index and not np.isnan(sh.loc[ts]):
            c = grp.mean() - sh.loc[ts]
            out.loc[grp.index] = grp - c
        else:
            out.loc[grp.index] = np.nan
    out = out.dropna()
    # Published spot returns for days when the futures basis dislocated by >5%.
    # Only the three October-1987 sessions are overridden; every other day is the
    # futures point change over the reconstructed level. Tagged "manual-override".
    OVERRIDES = {"1987-10-19": -0.2047, "1987-10-20": 0.0533, "1987-10-21": 0.0910}
    lv = np.log(out)
    r = lv.diff()
    for k, v in OVERRIDES.items():
        d = pd.Timestamp(k)
        if d in r.index: r.loc[d] = math.log1p(v)
    lv2 = r.cumsum() + lv.iloc[0]; lv2.iloc[0] = lv.iloc[0]
    out = np.exp(lv2)
    # re-anchor once more so monthly means still match Shiller after the overrides
    ym = out.index.to_period("M")
    for per, grp in out.groupby(ym):
        ts = per.to_timestamp()
        if ts in sh.index and not np.isnan(sh.loc[ts]):
            out.loc[grp.index] = grp * (sh.loc[ts] / grp.mean())
    out.name = "spx"
    return out, "futures-derived (Panama-adjusted continuous, re-anchored monthly to Shiller spot average; 3 Oct-1987 sessions overridden with published spot returns)"

def ndx_daily() -> tuple[pd.Series, str]:
    fut = _fut("ndx_fut")
    anchors = pd.Series({pd.Timestamp(k): v for k, v in ANCHORS_NDX.items()}).sort_index()
    # shift c(t) = fut - spot at anchors, linearly interpolated in time between anchors
    c_at = {}
    for d, spot in anchors.items():
        i = fut.index.get_indexer([d], method="nearest")[0]
        c_at[fut.index[i]] = fut.iloc[i] - spot
    c = pd.Series(c_at).reindex(fut.index).interpolate(method="time").bfill().ffill()
    out = (fut - c); out.name = "ndx"
    return out, "futures-derived (Panama-adjusted, re-anchored to 10 remembered spot closes; VERIFY anchors)"

def vix_full(spx: pd.Series) -> tuple[pd.Series, pd.Series]:
    """VIX 1990+ real; before 1990 a realized-vol proxy. Returns (series, tag_series)."""
    v = vix_daily()
    r = np.log(spx).diff()
    rv = r.ewm(span=21).std() * math.sqrt(252) * 100
    proxy = (rv * 1.2).clip(lower=16.0, upper=150.0)   # VXO's 1986-87 floor was ~16, 1987 peak ~150
    idx = spx.index.union(v.index)
    out = pd.Series(index=idx, dtype=float); tag = pd.Series(index=idx, dtype=object)
    out.loc[v.index] = v; tag.loc[v.index] = "real"
    pre = proxy.loc[proxy.index < v.index.min()]
    out.loc[pre.index] = pre; tag.loc[pre.index] = "proxy(realized)"
    out = out.reindex(spx.index).ffill()
    tag = tag.reindex(spx.index).ffill()
    return out, tag

def vix_term_slope() -> pd.Series:
    """Front-to-second VIX futures slope in vol points per month of tenor, 2006+.
    Positive = contango."""
    df = pd.read_csv(_fetch("vix_mult"), parse_dates=["DATETIME"])
    df["DATE"] = df["DATETIME"].dt.normalize()
    df = df.groupby("DATE").last()
    def months(a, b):
        a = pd.Period(str(int(a))[:6], "M"); b = pd.Period(str(int(b))[:6], "M"); return (b - a).n
    m = df.apply(lambda r: months(r["PRICE_CONTRACT"], r["FORWARD_CONTRACT"]) if pd.notna(r["FORWARD_CONTRACT"]) else np.nan, axis=1)
    slope = (df["FORWARD"] - df["PRICE"]) / m.replace(0, np.nan)
    return slope.dropna()

def rate_3m() -> tuple[pd.Series, str]:
    s = 100.0 - _fut("sofr_fut")
    s = (s / 100.0).clip(lower=0.0); s.name = "r3m"
    return s, "proxy (100 - Eurodollar/SOFR 3m futures, continuous)"

def monthly_filters() -> pd.DataFrame:
    """CAPE, trailing E/P, D/P, 10y, and an ERP proxy (trailing E/P - 10y), monthly."""
    sh = shiller_monthly()
    g = us10y_monthly()
    df = sh.join(g, rsuffix="_ds", how="outer")
    df["gs10"] = (df["gs10_ds"].combine_first(df["gs10"] / 100.0))
    df["erp"] = df["ep"] - df["gs10"]
    return df[["price", "cape", "dy", "ep", "gs10", "erp"]]

def build_all(verbose=True) -> dict:
    spx, spx_tag = spx_daily()
    ndx, ndx_tag = ndx_daily()
    vix, vix_tag = vix_full(spx)
    slope = vix_term_slope()
    r3m, r3m_tag = rate_3m()
    mf = monthly_filters()
    daily = pd.DataFrame({"spx": spx, "vix": vix, "vix_tag": vix_tag}).join(ndx, how="left").join(r3m, how="left").join(slope.rename("vix_slope"), how="left")
    daily["r3m"] = daily["r3m"].ffill().bfill()
    daily["vix_slope_tag"] = np.where(daily["vix_slope"].notna(), "vix-futures", "default")
    # monthly filters forward-filled onto daily (values known at month start; no lookahead: use previous month)
    mfd = mf.shift(1).reindex(daily.index, method="ffill")
    for c in ("cape", "dy", "ep", "gs10", "erp"):
        daily[c] = mfd[c]
    daily["dy"] = daily["dy"].ffill().fillna(0.014)
    meta = {"spx": spx_tag, "ndx": ndx_tag, "r3m": r3m_tag, "vix": "real 1990+, realized proxy before",
            "vix_term": "VIX futures slope 2006+, default mean-reversion before",
            "skew": "NOT AVAILABLE -> parametric default 0.35*T^-0.25 (flat 0.10 before 1987-10 per regime flag)",
            "hy_oas": "NOT AVAILABLE -> entry filter run without the HY leg",
            "cape_ep_dy": "Shiller monthly to 2023-09; NaN after (2025 episode excluded)"}
    if verbose:
        print(f"daily rows {len(daily)}  {daily.index.min().date()} -> {daily.index.max().date()}")
        for k, v in meta.items(): print(f"  {k:<10} {v}")
    return {"daily": daily, "monthly": mf, "meta": meta}

if __name__ == "__main__":
    d = build_all()
    df = d["daily"]
    print(df.loc["1987-10-15":"1987-10-22", ["spx", "vix", "vix_tag"]])
    print(df.loc["2020-02-18":"2020-03-24", ["spx", "vix", "ndx", "vix_slope", "r3m"]].iloc[[0, 5, 10, 15, 20, -1]])
    print("largest daily moves:"); print(np.log(df["spx"]).diff().nsmallest(5))
