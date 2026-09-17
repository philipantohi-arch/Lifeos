"""
Section 0 reconciliation: the v4 engine's scenario crash-start windows do not match the
report's Section 2 timing table. This module (a) measures the engine's implied
distribution, (b) defines the v6 timing that reproduces the report, (c) verifies it by
Monte Carlo. The report states which timing was used.

Report Section 2 (crash = SPX -25% from high; months counted from 2026-09-16):
  pre-Nov-26            7%     (months  0 - 1.5)
  Nov-26 - Jun-27      13%     (months 1.5 - 9.5)
  Jul-27 - Jun-28      38%     (months 9.5 - 21.5)
  Jul-28 - end-2029    22%     (of which ~4% falls inside the engine's 24m horizon)
  none through 2031    20%
Within the engine's 24-month horizon the report implies ~62% crash mass.

v4 engine (put_scenario_model_sept2026.py): 0% / 30% / 27% / 1% ; 42% no crash in 24m,
but Muddle "corrections" of depth 25-30% (about 5% of mass) also meet the -25%
definition, so the engine's total is ~63%: the totals agree, the shape does not.

v6 timing keeps every scenario's probability, depth and length, and only moves the
crash-start windows:
  SecondWave : 40% of its crashes start in months (0, 1.5), 60% in (1.5, 20)
  AI Bust    : (6, 22)          Repression : (8, 24)          Fracture : (16, 24)
  Muddle     : corrections unchanged (start 2-18, depth 12-30%)
This reproduces 7 / 12.5 / 39 / 5 (sum ~63%) - within a point of the report.
"""
import random

V4 = dict(SecondWave=(2, 14), AIBust=(5, 14), Repression=(5, 13), Fracture=(15, 24))
V6 = dict(SecondWave=((0.0, 1.5), (1.5, 20.0), 0.40), AIBust=(6, 22), Repression=(8, 24), Fracture=(16, 24))
PROB = dict(Muddle=.28, Repression=.19, AIBust=.17, SecondWave=.17, Escape=.14, Fracture=.05)
BUCKETS = [("pre-Nov-26", 0, 1.5), ("Nov-26–Jun-27", 1.5, 9.5), ("Jul-27–Jun-28", 9.5, 21.5), ("Jul–Sep-28", 21.5, 24.01)]
REPORT = {"pre-Nov-26": 7, "Nov-26–Jun-27": 13, "Jul-27–Jun-28": 38, "Jul–Sep-28": 4}

def draw_start(name, timing):
    if name == "SecondWave" and timing == "v6":
        a, b, w = V6["SecondWave"]
        return random.uniform(*a) if random.random() < w else random.uniform(*b)
    win = (V6 if timing == "v6" else V4)[name]
    return random.uniform(*win)

def implied(timing="v6", n=200_000, seed=7):
    random.seed(seed)
    out = {b[0]: 0 for b in BUCKETS}; none = 0
    names = list(PROB); probs = [PROB[k] for k in names]
    for _ in range(n):
        r = random.random(); acc = 0
        for nm, p in zip(names, probs):
            acc += p
            if r <= acc: sc = nm; break
        if sc in ("Repression", "AIBust", "SecondWave", "Fracture"):
            cs = draw_start(sc, timing)
        elif sc == "Muddle" and random.random() < 0.65 and random.uniform(0.12, 0.30) >= 0.25:
            cs = random.uniform(2, 18)
        else:
            none += 1; continue
        for nm, lo, hi in BUCKETS:
            if lo <= cs < hi: out[nm] += 1; break
        else: none += 1
    return {k: 100 * v / n for k, v in out.items()}, 100 * none / n

def table():
    v4, n4 = implied("v4"); v6, n6 = implied("v6")
    rows = ["| Window | Report §2 | v4 engine | v6 engine |", "|---|---:|---:|---:|"]
    for k in REPORT: rows.append(f"| {k} | {REPORT[k]}% | {v4[k]:.1f}% | {v6[k]:.1f}% |")
    rows.append(f"| No crash within 24m | ~38% | {n4:.1f}% | {n6:.1f}% |")
    return "\n".join(rows)

if __name__ == "__main__":
    print(table())
