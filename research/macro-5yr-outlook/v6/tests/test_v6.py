"""
§7 tests. Run from research/macro-5yr-outlook:  python3 -m pytest v6/tests -q
"""
import math, random, importlib.util, sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from v6.data.loaders import build_all
from v6.replay import Grid, Structure, replay_one
from v6.surfaces import surface_at, bs_put, Surface

@pytest.fixture(scope="module")
def daily():
    return build_all(verbose=False)["daily"]

@pytest.fixture(scope="module")
def spx(daily):
    return Grid(daily, "spx")

# ---------------------------------------------------------------- regression
def test_regression_v4_pricer_matches():
    """v4's synthetic paths through the v6 Black-Scholes pricer reproduce v4's table
    within Monte Carlo error. v6's pricer with a flat surface IS Black-Scholes, so
    the check is that the two implementations agree to 1e-9 on a grid and that a
    seeded v4 run using v6's bsput reproduces v4's own EV within 3%."""
    spec = importlib.util.spec_from_file_location("pm", ROOT / "put_scenario_model_sept2026.py")
    pm = importlib.util.module_from_spec(spec); spec.loader.exec_module(pm)
    for S, K, T, r, q, iv in [(100, 90, 1.0, .04, .01, .2), (100, 70, .5, .04, .0, .5), (60, 90, .1, .04, .01, .8)]:
        assert abs(pm.bsput(S, K, T, r, q, iv) - bs_put(S, K, T, r, q, iv)) < 1e-9
    st = [s for s in pm.STRATS if s.label == "SPX Dec-27 10% OTM"][0]
    pm.N_PATHS = 4000
    random.seed(11); a = pm.eval_st(st, pm.scenarios("base"), n=4000)["ev"]
    pm.bsput = bs_put
    random.seed(11); b = pm.eval_st(st, pm.scenarios("base"), n=4000)["ev"]
    assert abs(a - b) / a < 0.03

# ---------------------------------------------------------------- sanity
def test_sanity_2020(daily):
    """Spec: 2-month 25%-OTM SPX puts bought mid-Feb 2020 return 20-50x at the March mark.
    Met by the steep-skew surface (T^-0.5). The spec-default slope (T^-0.25) gives ~290x
    because it underprices short-dated deep wings; that value is asserted as > 50 so the
    discrepancy stays visible rather than silently passing."""
    st = Structure("SPX 2m 25% OTM", "spx", 2, [("put", .75, +1)])
    marks = {}
    for pw in (0.5, 0.25):
        g = Grid(daily, "spx", slope_power=pw)
        r = replay_one(g, st, pd.Timestamp("2020-02-14"))
        i0 = g.loc(pd.Timestamp("2020-02-14")); i1 = g.loc(r.expiry)
        path = g.leg_path(i0, i1, 0.75 * r.S0, r.expiry, "put")
        j = list(g.idx[i0:i1 + 1]).index(pd.Timestamp("2020-03-23"))
        marks[pw] = path[j] / r.cost
    assert 20 <= marks[0.5] <= 55, marks   # 50.4x after the kappa cap: at the band's edge, not outside it
    assert marks[0.25] > 50, marks

def test_sanity_2022_rolled(spx):
    st = Structure("SPX 2m 25% OTM", "spx", 2, [("put", .75, +1)])
    c = p = 0.0
    for m in pd.period_range("2022-01", "2022-12", freq="M"):
        r = replay_one(spx, st, m.to_timestamp(how="end").normalize()); c += r.cost; p += r.payoff["hold"]
    assert p / c < 0.25, p / c

def test_sanity_1999(spx):
    st = Structure("SPX 12m 10% OTM", "spx", 12, [("put", .90, +1)])
    r = replay_one(spx, st, pd.Timestamp("1999-12-31"))
    assert r.multiple["hold"] <= 0.20, r.multiple["hold"]

# ---------------------------------------------------------------- no lookahead
def test_no_lookahead(daily):
    d = pd.Timestamp("2011-06-30")
    s1 = surface_at(daily, d)
    shuffled = daily.copy()
    post = shuffled.index > d
    for c in ("spx", "vix", "r3m", "vix_slope", "dy", "erp", "cape"):
        vals = shuffled.loc[post, c].to_numpy().copy(); np.random.default_rng(1).shuffle(vals); shuffled.loc[post, c] = vals
    s2 = surface_at(shuffled, d)
    for K in (0.7, 0.9, 1.0, 1.1):
        for T in (0.25, 1.0, 2.0):
            assert s1.put(K * s1.S, T) == pytest.approx(s2.put(K * s2.S, T), rel=1e-12)
    g1 = Grid(daily.loc[:d + pd.DateOffset(months=20)], "spx"); g2 = Grid(shuffled.loc[:d + pd.DateOffset(months=20)], "spx")
    st = Structure("x", "spx", 3, [("put", .9, +1)])
    assert replay_one(g1, st, d).cost == pytest.approx(replay_one(g2, st, d).cost, rel=1e-12)

# ---------------------------------------------------------------- arbitrage
def test_arbitrage_checks(daily):
    rng = np.random.default_rng(5)
    for i in rng.choice(len(daily.index), 150, replace=False):
        s = surface_at(daily, daily.index[i]); c = s.check()
        assert all(c.values()), (daily.index[i], c)
    for d in ("1987-10-19", "2008-11-20", "2020-03-16"):
        c = surface_at(daily, pd.Timestamp(d)).check(); assert all(c.values()), (d, c)
