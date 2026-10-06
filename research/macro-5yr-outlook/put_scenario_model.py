#!/usr/bin/env python3
"""
Scenario-weighted put-strategy model v2 — live inputs as of 2026-08-14 close.
SPX 7,786 (record), VIX 14.25, SPX skew at 1-yr lows, r~4.0%.
Verified IVs: ORCL 30d ATM ~70 (IVR 62), CRWV 3m ~81, NVDA ~43 (into Aug-26
earnings), PLTR ~55 (post-crush est), HYG ~10, SPX long-dated ~17.5-19.5 (est
from curve; agent-computed 7m 10%OTM cost 1.12-1.50% of spot cross-checks).

Scenario probabilities: BDCR-26 post-adversarial map, timing refreshed for
Aug-2026 confirmations (private-credit gates CROSSED, first negative payroll,
Fed = hike risk, Iran war-risk premium 7.5-10% of hull, QRA coupon bump
deferred to early 2027). NOT INVESTMENT ADVICE — analytical exercise.
"""

import math, random
from dataclasses import dataclass, field

random.seed(27)
N_PATHS = 24000
RISK_FREE = 0.040
HORIZON = 24

@dataclass
class Und:
    name: str
    div: float
    beta: float
    idio: float
    iv: dict
    floor: float = 1.0
    exit_trig: float = 0.22
    crash_iv: float = 0.40

U = {
 "SPX":  Und("SPX 7786", 0.0104, 1.00, 0.000, {4:.16,7:.175,10:.18,16:.19,22:.195}, crash_iv=.34),
 "QQQ":  Und("QQQ 731",  0.005,  1.35, 0.010, {4:.20,7:.215,10:.22,16:.235,22:.24}, crash_iv=.42),
 "SOXX": Und("SOXX 550", 0.005,  1.80, 0.020, {4:.29,7:.30,10:.305,16:.31,22:.315}, crash_iv=.52),
 "NVDA": Und("NVDA 225", 0.000,  2.00, 0.045, {4:.42,7:.43,10:.44,16:.45,22:.45}, floor=.35, crash_iv=.72),
 "ORCL": Und("ORCL 156", 0.013,  1.70, 0.050, {4:.62,7:.60,10:.58,16:.55,22:.53}, floor=.40, crash_iv=.85),
 "PLTR": Und("PLTR 174", 0.000,  2.20, 0.060, {4:.55,7:.56,10:.57,16:.58,22:.58}, floor=.30, crash_iv=.90),
 "CRWV": Und("CRWV 108", 0.000,  2.50, 0.090, {4:.80,7:.82,10:.84,16:.86,22:.88}, floor=.10, crash_iv=1.20),
 "HYG":  Und("HYG 79.7", 0.058,  0.35, 0.004, {4:.09,7:.10,10:.10,16:.11,22:.11}, exit_trig=.08, crash_iv=.22),
 "VRT":  Und("VRT 272",  0.001,  1.90, 0.050, {7:.55,10:.54,16:.52,22:.50}, floor=.45, crash_iv=.75),
 "DLR":  Und("DLR 191",  0.036,  0.90, 0.020, {7:.26,10:.26,16:.27,22:.27}, exit_trig=.18, crash_iv=.40),
}

@dataclass
class Sc:
    name: str; prob: float; drift: float; vol: float
    cp: float; cstart: tuple; cdepth: tuple; clen: tuple
    meltup: float; recov: float; corr: tuple = None

def scenarios(mode="base"):
    if mode == "base":       # post-adversarial map, Aug-2026 timing refresh
        p = dict(mu=.35, rp=.18, ab=.16, sw=.09, es=.19, fr=.03)
    elif mode == "bear":     # pre-adversarial synthesis weights
        p = dict(mu=.30, rp=.22, ab=.17, sw=.15, es=.13, fr=.03)
    elif mode == "benign":   # market-implied-ish: crash mass halved
        p = dict(mu=.45, rp=.12, ab=.10, sw=.06, es=.25, fr=.02)
    return [
        Sc("Muddle",     p['mu'], .004, .035, 0.0, (0,0), (0,0), (0,0), 0, .008, corr=(.65,.12,.30)),
        Sc("Repression", p['rp'], .002, .040, 1.0, (7,15), (.20,.28), (4,7), .002, .012),
        Sc("AI Bust",    p['ab'], .000, .045, 1.0, (5,14), (.35,.45), (5,9), .008, .010),
        Sc("SecondWave", p['sw'], .000, .045, 1.0, (13,22), (.30,.40), (2,4), .010, .004),
        Sc("Escape",     p['es'], .009, .030, 0.0, (0,0), (0,0), (0,0), 0, 0, corr=(.5,.10,.15)),
        Sc("Fracture",   p['fr'], -.001, .050, 1.0, (15,24), (.40,.55), (2,5), 0, .002),
    ]

def index_path(sc):
    path = [1.0]; lvl = 1.0
    crash = random.random() < sc.cp
    cs = random.uniform(*sc.cstart) if crash else 1e9
    cd = random.uniform(*sc.cdepth) if crash else 0
    cl = random.uniform(*sc.clen) if crash else 1
    corr, cos, cod, col = False, 1e9, 0, 3.0
    if sc.corr and random.random() < sc.corr[0]:
        corr, cos, cod = True, random.uniform(2,18), random.uniform(sc.corr[1], sc.corr[2])
    for t in range(1, HORIZON+1):
        z = random.gauss(0, sc.vol)
        if crash and cs <= t < cs+cl:
            lvl *= (1-cd)**(1/cl) * math.exp(random.gauss(0, sc.vol*1.8))
        elif crash and t >= cs+cl:
            lvl *= math.exp(sc.recov + random.gauss(0, sc.vol*1.2))
        elif corr and cos <= t < cos+col:
            lvl *= (1-cod)**(1/col) * math.exp(random.gauss(0, sc.vol*1.5))
        elif corr and cos+col <= t < cos+col+6:
            lvl *= math.exp(.012 + z)
        else:
            lvl *= math.exp(sc.drift + (sc.meltup if crash and t < cs else 0) + z)
        path.append(lvl)
    return path

def name_path(u, idx, sc):
    out = [1.0]
    for t in range(1, len(idx)):
        r = math.log(idx[t]/idx[t-1])
        amp = u.beta if r < 0 else max(1.0, u.beta*0.8)
        out.append(out[-1]*math.exp(r*amp + random.gauss(0, u.idio)))
    if sc.name in ("AI Bust","Fracture") and u.floor < 1.0:
        tt = min(range(len(idx)), key=lambda t: idx[t])
        if idx[tt] < 0.75:
            target = u.floor * random.uniform(0.8, 1.3)
            sc_f = min(1.0, target / max(out[tt], 1e-9))
            out = [o*(sc_f**(t/max(tt,1)) if t <= tt else sc_f) for t,o in enumerate(out)]
    return out

def phi(x): return .5*(1+math.erf(x/math.sqrt(2)))
def bsput(S,K,T,r,q,iv):
    if T <= 0: return max(K-S,0)
    d1 = (math.log(S/K)+(r-q+.5*iv*iv)*T)/(iv*math.sqrt(T))
    return K*math.exp(-r*T)*phi(-(d1-iv*math.sqrt(T))) - S*math.exp(-q*T)*phi(-d1)

@dataclass
class St:
    label: str; und: str; em: int; k: float; klo: float = None; burry: bool = False

def eval_st(st, scs, n=N_PATHS, use_exit=True):
    u = U[st.und]; iv = u.iv[st.em]; S0 = 100.0; K = st.k*100; T0 = st.em/12
    cost = bsput(S0,K,T0,RISK_FREE,u.div,iv)
    if st.klo: cost -= bsput(S0,st.klo*100,T0,RISK_FREE,u.div,iv*1.06)
    if cost <= 0.03: cost = max(cost, 0.03)
    pays, scpay = [], {s.name: [] for s in scs}
    for _ in range(n):
        r0, acc = random.random(), 0
        for s in scs:
            acc += s.prob
            if r0 <= acc: sc = s; break
        idx = index_path(sc)
        up = name_path(u, idx, sc) if st.und not in ("SPX",) else idx
        if st.und in ("QQQ","SOXX","HYG","DLR") :
            up = [v**u.beta if v < 1 else v**(u.beta*0.8) if v>1 else v for v in idx]
        pay = None
        if use_exit:
            for t in range(1, st.em+1):
                S = up[t]*100
                if S <= (1-u.exit_trig)*100:
                    rem = max(T0 - t/12, 0)
                    v = bsput(S,K,rem,RISK_FREE,u.div,u.crash_iv)
                    if st.klo:
                        v -= bsput(S,st.klo*100,rem,RISK_FREE,u.div,u.crash_iv*1.06)
                        v = min(v,(st.k-st.klo)*100)
                    pay = max(v,0); break
        if pay is None:
            S = up[st.em]*100
            pay = max(K-S,0) - (max(st.klo*100-S,0) if st.klo else 0)
        pays.append(pay); scpay[sc.name].append(pay)
    ev = sum(pays)/len(pays)
    return dict(label=st.label, burry=st.burry, cost=cost, ev=ev/cost,
                pz=sum(1 for p in pays if p < .01*cost)/len(pays),
                p3=sum(1 for p in pays if p >= 3*cost)/len(pays),
                p10=sum(1 for p in pays if p >= 10*cost)/len(pays),
                cond={k:(sum(v)/len(v)/cost if v else 0) for k,v in scpay.items()})

STRATS = [
    # ---- Burry's actual disclosed book (replicas) ----
    St("[B] PLTR Mar-27 p~105 (40% OTM)",   "PLTR", 7, .60, burry=True),
    St("[B] PLTR Dec-26 p~105 (40% OTM)",   "PLTR", 4, .60, burry=True),
    St("[B] NVDA Dec-26 p~105 (53% OTM)",   "NVDA", 4, .47, burry=True),
    St("[B] NVDA Jun-27 p~105 (53% OTM)",   "NVDA", 10, .47, burry=True),
    St("[B] QQQ Jun-27 p~655 (11% OTM)",    "QQQ", 10, .89, burry=True),
    St("[B] SOXX Mar-27 p~425 (23% OTM)",   "SOXX", 7, .77, burry=True),
    # ---- Mar-27 alternatives ----
    St("SPX Mar-27 10% OTM",               "SPX", 7, .90),
    St("SPX Mar-27 90/75 spread",          "SPX", 7, .90, .75),
    St("ORCL Mar-27 85/60 spread",         "ORCL", 7, .85, .60),
    # ---- Dec-27: the map-aligned tenor ----
    St("SPX Dec-27 10% OTM",               "SPX", 16, .90),
    St("SPX Dec-27 90/70 spread",          "SPX", 16, .90, .70),
    St("QQQ Dec-27 10% OTM",               "QQQ", 16, .90),
    St("QQQ Dec-27 90/65 spread",          "QQQ", 16, .90, .65),
    St("SOXX Dec-27 85/55 spread",         "SOXX", 16, .85, .55),
    St("NVDA Dec-27 80/45 spread",         "NVDA", 16, .80, .45),
    St("ORCL Dec-27 15% OTM",              "ORCL", 16, .85),
    St("ORCL Dec-27 85/55 spread",         "ORCL", 16, .85, .55),
    St("PLTR Dec-27 25% OTM",              "PLTR", 16, .75),
    St("CRWV Dec-27 70/25 spread",         "CRWV", 16, .70, .25),
    St("VRT Dec-27 85/50 spread",          "VRT", 16, .85, .50),
    St("DLR Dec-27 12% OTM",               "DLR", 16, .88),
    St("HYG Dec-27 5% OTM",                "HYG", 16, .95),
    St("HYG Dec-27 95/87 spread",          "HYG", 16, .95, .87),
    # ---- Jun-28: max tenor ----
    St("SPX Jun-28 10% OTM",               "SPX", 22, .90),
    St("QQQ Jun-28 90/65 spread",          "QQQ", 22, .90, .65),
    St("SOXX Jun-28 85/55 spread",         "SOXX", 22, .85, .55),
    St("ORCL Jun-28 85/55 spread",         "ORCL", 22, .85, .55),
    St("HYG Jun-28 95/85 spread",          "HYG", 22, .95, .85),
]

def run(mode="base", use_exit=True, tag=""):
    scs = scenarios(mode)
    print(f"\n### {tag or mode}  (exit rule: {'on' if use_exit else 'off'})")
    print(f"{'strategy':<36}{'cost%':>7}{'EVx':>6}{'P0':>5}{'>=3x':>6}{'>=10x':>7}  Mu/Rp/AB/SW/Es/Fr")
    rows = [eval_st(s, scs, use_exit=use_exit) for s in STRATS]
    for r in sorted(rows, key=lambda x: -x['ev']):
        c = r['cond']
        cs = "/".join(f"{c[k]:.1f}" for k in ("Muddle","Repression","AI Bust","SecondWave","Escape","Fracture"))
        mark = "*" if r['burry'] else " "
        print(f"{mark}{r['label']:<35}{r['cost']:>6.2f}%{r['ev']:>6.2f}{r['pz']:>5.0%}{r['p3']:>6.0%}{r['p10']:>7.0%}  {cs}")

if __name__ == "__main__":
    run("base", True, "BASE: post-adversarial probs, exit-at-trigger with crash IV")
    run("bear", True, "BEAR: pre-adversarial (Dalio-ish) probs")
    run("benign", True, "BENIGN: market-implied-ish probs (crash mass halved)")
    run("base", False, "BASE, hold-to-expiry only (no exit rule)")
