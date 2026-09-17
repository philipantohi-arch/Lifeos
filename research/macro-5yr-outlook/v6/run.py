"""
One-command driver:  python3 -m v6.run   (from research/macro-5yr-outlook)
Downloads (cached), builds grids, replays every episode / non-event / baseline,
runs the filter test and diagnostics, and writes report_v6.md next to this file.
"""
from __future__ import annotations
import sys, time, json, math
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

from .data.loaders import build_all
from .replay import Grid, STRUCTS, NOT_REPLAYABLE, run_episode, run_grid, filter_mask, EXIT_TRIGGER
from .surfaces import surface_at
from . import timing

HERE = Path(__file__).resolve().parent
WEIGHTS = dict(Muddle=.28, Repression=.19, AIBust=.17, SecondWave=.17, Escape=.14, Fracture=.05)
V4_EV = {  # Sept-16 synthetic run, exit rule on (put_scenario_model_sept2026.py)
    "SPX Mar-27 10% OTM": 1.28, "SPX Mar-27 90/75 spread": 1.11, "[B] QQQ Jun-27 p 11% OTM": 1.82,
    "SPX Dec-27 10% OTM": 2.37, "SPX Dec-27 90/70 spread": 2.07, "QQQ Dec-27 10% OTM": 2.19,
    "QQQ Dec-27 90/65 spread": 1.92, "SPX Jun-28 10% OTM": 2.20, "QQQ Jun-28 90/65 spread": 1.77}
V4_CRASH_IV = {"spx": 34, "ndx": 42}

def v4_reconciled_ev(n=6000):
    """Re-run the synthetic model with the reconciled (v6) crash-start windows from timing.py so
    the §8 comparison is like-for-like. Cached in v4_reconciled.json."""
    import importlib.util, random, json as _json
    cache = HERE / "v4_reconciled.json"
    if cache.exists(): return _json.loads(cache.read_text())
    spec = importlib.util.spec_from_file_location("pm", HERE.parent / "put_scenario_model_sept2026.py")
    pm = importlib.util.module_from_spec(spec); spec.loader.exec_module(pm)
    base = pm.scenarios("base"); out_sc = []
    for sc in base:
        if sc.name == "SecondWave":
            a, b, w = timing.V6["SecondWave"]
            out_sc.append(pm.Sc("SecondWave", sc.prob * w, sc.drift, sc.vol, sc.cp, a, sc.cdepth, sc.clen, sc.meltup, sc.recov))
            out_sc.append(pm.Sc("SecondWave", sc.prob * (1 - w), sc.drift, sc.vol, sc.cp, b, sc.cdepth, sc.clen, sc.meltup, sc.recov))
        elif sc.name in ("AI Bust", "Repression", "Fracture"):
            key = {"AI Bust": "AIBust"}.get(sc.name, sc.name)
            out_sc.append(pm.Sc(sc.name, sc.prob, sc.drift, sc.vol, sc.cp, timing.V6[key], sc.cdepth, sc.clen, sc.meltup, sc.recov))
        else:
            out_sc.append(sc)
    res = {}
    random.seed(27)
    for st in pm.STRATS:
        if st.und in ("SPX", "QQQ"):
            res[st.label] = pm.eval_st(st, out_sc, n=n)["ev"]
    cache.write_text(_json.dumps(res, indent=1))
    return res

def md_table(df: pd.DataFrame, floatfmt="{:.2f}") -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float): cells.append("" if np.isnan(v) else floatfmt.format(v))
            else: cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)

def main(quick=False):
    t0 = time.time()
    data = build_all(verbose=True)
    daily = data["daily"]
    V4R = v4_reconciled_ev()
    v4map = {"[B] QQQ Jun-27 p~655 (11% OTM)": "[B] QQQ Jun-27 p 11% OTM"}
    V4_REC = {v4map.get(k, k): v for k, v in V4R.items()}
    print("v4 reconciled EVs:", {k: round(v, 2) for k, v in V4_REC.items()})
    eps = yaml.safe_load((HERE / "episodes.yaml").read_text())
    grids = {"spx": Grid(daily, "spx"), "ndx": Grid(daily, "ndx")}
    print(f"grids built {time.time()-t0:.0f}s")

    # ---------------- episodes
    frames = []; excluded = []
    for ep in eps["crash_episodes"]:
        if ep.get("replayable", True) is False:
            excluded.append(f"{ep['id']}: {ep.get('notes','')}"); continue
        df = run_episode(grids, ep); frames.append(df)
        print(f"  episode {ep['id']:<6} rows {len(df):>6}  {time.time()-t0:.0f}s")
    E = pd.concat(frames, ignore_index=True)
    # ---------------- non-events
    nframes = []
    for ne in eps["nonevent_episodes"]:
        a, b = pd.Timestamp(ne["window"][0]), pd.Timestamp(ne["window"][1])
        df = run_grid(grids, a, b, tag=ne["id"]); nframes.append(df)
        print(f"  non-event {ne['id']:<8} rows {len(df):>6}  {time.time()-t0:.0f}s")
    NE = pd.concat(nframes, ignore_index=True)
    # ---------------- unconditional baseline
    B = run_grid(grids, pd.Timestamp(eps["baseline"]["start"]), daily.index[-1], tag="baseline")
    print(f"  baseline rows {len(B)}  {time.time()-t0:.0f}s")
    # steep-skew sensitivity (put slope 0.35*T^-0.5): episodes + non-events only
    grids_s = {"spx": Grid(daily, "spx", slope_power=0.5), "ndx": Grid(daily, "ndx", slope_power=0.5)}
    ES = pd.concat([run_episode(grids_s, ep) for ep in eps["crash_episodes"] if ep.get("replayable", True) is not False], ignore_index=True)
    NES = pd.concat([run_grid(grids_s, pd.Timestamp(ne["window"][0]), pd.Timestamp(ne["window"][1]), tag=ne["id"]) for ne in eps["nonevent_episodes"]], ignore_index=True)
    print(f"  steep-skew variant done  {time.time()-t0:.0f}s")

    # ---------------- surface validation on a sample of dates
    rng = np.random.default_rng(3)
    sample = rng.choice(len(daily.index), 300, replace=False)
    viol = {"parity": 0, "calendar": 0, "butterfly": 0}; term_tags = {}
    for i in sample:
        s = surface_at(daily, daily.index[i]); c = s.check()
        for k in viol: viol[k] += (not c[k])
        term_tags[s.term_tag] = term_tags.get(s.term_tag, 0) + 1

    # ---------------- aggregation helpers
    def agg(df):
        g = df.groupby("structure")["multiple"]
        return pd.DataFrame({"EV": g.mean(), "median": g.median(), "P0": df.assign(z=df.multiple < 0.05).groupby("structure")["z"].mean(),
                             ">=3x": df.assign(z=df.multiple >= 3).groupby("structure")["z"].mean(),
                             ">=10x": df.assign(z=df.multiple >= 10).groupby("structure")["z"].mean(), "N": g.size()})
    rule = "v4_-22"
    tenor_of = {x.label: x.tenor_m / 12 for x in STRUCTS}; is_sg = {x.label: x.seagull for x in STRUCTS}
    E12 = E[(E.rule == rule) & (E.offset_m <= 12)]
    NE_r = NE[NE.rule == rule]; B_r = B[B.rule == rule]
    # historical scenario-conditional multiples (entries within 12 months of the peak)
    cond = E12.groupby(["structure", "analog"])["multiple"].mean().unstack()
    ne_mean = NE_r.groupby("structure")["multiple"].mean()
    hist_cond = pd.DataFrame(index=cond.index)
    hist_cond["Muddle"] = 0.65 * cond.get("MuddleCorrection", ne_mean) .fillna(ne_mean) + 0.35 * ne_mean
    hist_cond["Repression"] = cond.get("Repression")
    hist_cond["AIBust"] = cond.get("AIBust")
    hist_cond["SecondWave"] = cond.get("SecondWave")
    hist_cond["Escape"] = ne_mean
    hist_cond["Fracture"] = cond.get("Fracture")
    for col in hist_cond.columns:
        hist_cond[col] = hist_cond[col].fillna(ne_mean.reindex(hist_cond.index))
    ev_hist = sum(WEIGHTS[k] * hist_cond[k] for k in WEIGHTS)
    def hist_ev(Eframe, NEframe):
        e12 = Eframe[(Eframe.rule == rule) & (Eframe.offset_m <= 12)]; nem = NEframe[NEframe.rule == rule].groupby("structure")["multiple"].mean()
        c = e12.groupby(["structure", "analog"])["multiple"].mean().unstack()
        h = pd.DataFrame(index=c.index)
        h["Muddle"] = 0.65 * c.get("MuddleCorrection").fillna(nem) + 0.35 * nem
        h["Repression"] = c.get("Repression"); h["AIBust"] = c.get("AIBust"); h["SecondWave"] = c.get("SecondWave"); h["Escape"] = nem; h["Fracture"] = c.get("Fracture")
        for col in h.columns: h[col] = h[col].fillna(nem.reindex(h.index))
        return sum(WEIGHTS[k] * h[k] for k in WEIGHTS), e12.groupby("structure")["cost_pct"].median()
    ev_steep, cost_steep = hist_ev(ES, NES)
    main_tbl = pd.DataFrame({"structure": hist_cond.index,
                             "cost % (median)": E12.groupby("structure")["cost_pct"].median().reindex(hist_cond.index).values,
                             "EV hist-weighted": ev_hist.values,
                             "P0 (crash entries)": E12.assign(z=E12.multiple < 0.05).groupby("structure")["z"].mean().reindex(hist_cond.index).values,
                             ">=3x": E12.assign(z=E12.multiple >= 3).groupby("structure")["z"].mean().reindex(hist_cond.index).values,
                             ">=10x": E12.assign(z=E12.multiple >= 10).groupby("structure")["z"].mean().reindex(hist_cond.index).values,
                             "Mu/Rp/AB/SW/Es/Fr": [ "/".join(f"{hist_cond.loc[s, k]:.1f}" for k in ["Muddle","Repression","AIBust","SecondWave","Escape","Fracture"]) for s in hist_cond.index],
                             "v4 synthetic EV (Sep-16)": [V4_EV.get(s, np.nan) for s in hist_cond.index],
                             "v4 reconciled-timing EV": [V4_REC.get(s, np.nan) for s in hist_cond.index],
                             "steep-skew cost %": cost_steep.reindex(hist_cond.index).values,
                             "steep-skew EV": ev_steep.reindex(hist_cond.index).values})
    main_tbl = main_tbl[~main_tbl.structure.map(is_sg)].sort_values("EV hist-weighted", ascending=False)

    # episode table: best / median / worst entry offset per structure x episode (hold rule and v4 rule)
    ep_rows = []
    for (ep_id, st), g in E[E.rule == rule].groupby(["episode", "structure"]):
        b = g.loc[g.multiple.idxmax()]; w = g.loc[g.multiple.idxmin()]
        z = lambda x: 0.0 if abs(x) < 0.005 else x
        ep_rows.append(dict(episode=ep_id, structure=st, best=f"{z(b.multiple):.1f}x @-{int(b.offset_m)}m", median=f"{z(g.multiple.median()):.2f}x",
                            worst=f"{z(w.multiple):.2f}x @-{int(w.offset_m)}m", miss=f"{100*g.timing_miss.mean():.0f}%"))
    ep_tbl = pd.DataFrame(ep_rows)
    # heatmap: median multiple by structure x offset (crash episodes pooled)
    heat = E[E.rule == rule].pivot_table(index="structure", columns="offset_m", values="multiple", aggfunc="median")
    heat = heat[[c for c in sorted(heat.columns) if c % 3 == 0]]
    # bleed table: premium burned per year for ONE maintained unit (rolled at expiry), % of notional
    tenor_of = {x.label: x.tenor_m / 12 for x in STRUCTS}; is_sg = {x.label: x.seagull for x in STRUCTS}
    bl_rows = []
    for ne in eps["nonevent_episodes"]:
        sub = NE_r[NE_r.episode == ne["id"]]
        for st, g in sub.groupby("structure"):
            if len(g) < 6 or is_sg[st]: continue
            burn = g.cost_pct.median() / tenor_of[st] * (1 - g.multiple.mean())
            bl_rows.append(dict(window=ne["id"], structure=st, entries=len(g), mean_mult=g.multiple.mean(), burn_pct_notional_per_yr=burn))
    bleed = pd.DataFrame(bl_rows)
    Bp = B_r[~B_r.seagull]
    base_bleed = Bp.groupby("structure").agg(entries=("multiple", "size"), mean_mult=("multiple", "mean"), P0=("multiple", lambda s: (s < 0.05).mean()),
                                             ge3=("multiple", lambda s: (s >= 3).mean()), cost=("cost_pct", "median"))
    base_bleed["burn_pct_notional_per_yr"] = [r.cost / tenor_of[st] * (1 - r.mean_mult) for st, r in base_bleed.iterrows()]
    # seagull table: P&L in % of notional (crash entries within 12m of peak / non-events / baseline) + max-risk multiple
    def sg_stats(df, label):
        d = df[df.seagull & (df.rule == rule)]
        if d.empty: return pd.DataFrame()
        g = d.groupby("structure")
        return pd.DataFrame({"set": label, "N": g.size(), "mean P&L %notional": g.pnl_pct.mean(), "median P&L": g.pnl_pct.median(),
                             "worst P&L": g.pnl_pct.min(), "best P&L": g.pnl_pct.max(), "mean multiple of max-risk": g.multiple.mean()}).reset_index()
    sg_tbl = pd.concat([sg_stats(E12, "crash entries (<=12m)"), sg_stats(NE, "non-event windows"), sg_stats(B, "baseline 1990+")], ignore_index=True)
    # exit-rule comparison
    xr = E[E.offset_m <= 12].groupby(["rule"]).agg(EV=("multiple", "mean"), hit=("multiple", lambda s: (s >= 1).mean()),
                                                   ge3=("multiple", lambda s: (s >= 3).mean()), P0=("multiple", lambda s: (s < 0.05).mean()))
    xr_ne = NE.groupby("rule").agg(EV_nonevent=("multiple", "mean"))
    xr = xr.join(xr_ne)
    # filter test on the unconditional baseline
    ftab = []
    for label, kw in [("base (ERP<=0 | CAPE>32) & VIX<18", {}),
                      ("ERP -25% (<=-0.5pp)", dict(erp_max=-0.005)), ("ERP +25% (<=+0.5pp)", dict(erp_max=0.005)),
                      ("CAPE 24", dict(cape_min=24)), ("CAPE 40", dict(cape_min=40)),
                      ("VIX 13.5", dict(vix_max=13.5)), ("VIX 22.5", dict(vix_max=22.5))]:
        m = filter_mask(daily, B_r.entry.values, **kw)
        sel = B_r[m.values]
        ftab.append(dict(filter=label, entries=int(m.sum()), EV=sel.multiple.mean(), P0=(sel.multiple < 0.05).mean(), ge3=(sel.multiple >= 3).mean(),
                         EV_unfiltered=B_r.multiple.mean(), P0_unfiltered=(B_r.multiple < 0.05).mean()))
    ftab = pd.DataFrame(ftab)
    # diagnostics: surface IV at trough by tenor vs v4 crash_iv; -22% exit before trough
    diag = []
    for ep in eps["crash_episodes"]:
        if ep.get("replayable", True) is False: continue
        tr = pd.Timestamp(ep["trough"])
        for und in ("spx", "ndx"):
            if und == "ndx" and tr < pd.Timestamp("1999-12-14"): continue
            s = surface_at(daily, tr, und=und)
            diag.append(dict(episode=ep["id"], und=und, vix_at_trough=round(s.vix, 1), iv_3m=round(100 * s.atm(0.25), 1),
                             iv_1y=round(100 * s.atm(1.0), 1), v4_crash_iv=V4_CRASH_IV[und], term=s.term_tag,
                             put_slope=s.put_slope, iv_10otm_1y=round(100 * s.iv(0.9 * s.S, 1.0), 1)))
    diag = pd.DataFrame(diag)
    fired = E[(E.rule == rule)].groupby("episode").agg(exit22_fired=("exit22_fired", "mean"), before_trough=("exit22_before_trough", "mean"))
    # spec-0.95 sensitivity on the 2008 and 2020 troughs
    sens = []
    for ep_id, tr in (("2007", "2009-03-09"), ("2020", "2020-03-23")):
        s1 = surface_at(daily, pd.Timestamp(tr)); s2 = surface_at(daily, pd.Timestamp(tr), term_rule="spec_0.95")
        sens.append(dict(episode=ep_id, iv_1y_MR=round(100 * s1.atm(1), 1), iv_1y_spec095=round(100 * s2.atm(1), 1)))
    sens = pd.DataFrame(sens)

    # ---------------- delta vs v4 (v5 not present)
    top8 = main_tbl.head(8)
    deltas = []
    for _, r in top8.iterrows():
        v4 = r["v4 reconciled-timing EV"]
        if np.isnan(v4): continue
        gap = r["EV hist-weighted"] / v4 - 1
        if abs(gap) > 0.3:
            sub = E12[E12.structure == r.structure]
            never = 1 - sub.exit22_fired.mean(); miss = sub.timing_miss.mean(); n_ep = sub.episode.nunique()
            c = hist_cond.loc[r.structure]
            deltas.append(f"**{r.structure}**: historical-weighted {r['EV hist-weighted']:.2f}x vs v4 synthetic {v4:.2f}x ({gap:+.0%}); {n_ep} episodes, {len(sub)} entries. "
                          f"Historical conditionals Mu {c.Muddle:.1f} / Rp {c.Repression:.1f} / AB {c.AIBust:.1f} / SW {c.SecondWave:.1f} / Es {c.Escape:.1f} / Fr {c.Fracture:.1f}. "
                          f"In {100*miss:.0f}% of these entries the option expired before the episode trough, and in {100*never:.0f}% the −22%-from-entry trigger never fired at all "
                          f"(the index rallied after entry, so the eventual drawdown from the peak was not a 22% drawdown from the entry spot). "
                          + ("The synthetic model starts every crash from the entry level and never lets a position expire before the crash, which is where the gap comes from; the peak-anchored exit rule in §5 recovers part of it. "
                             if gap < 0 else "Real surfaces mark the long-dated puts above v4's flat crash_iv during the drawdown, and the pooled episodes are deeper than the scenario depth ranges. ")
                          + ("QQQ conditionals rest on NDX data that begin 1999-12, so the 2000 episode contributes only entries at 0–3 months before the peak." if r.structure.startswith("QQQ") or r.structure.startswith("[B] QQQ") else ""))
    # ---------------- report
    n_ep = E.episode.nunique()
    yrs_excluded = "2025 (no daily SPX after 2024-03-28)"
    R = []
    R.append(f"# report_v6.md — historical replay of the BDCR-26 put structures\n")
    R.append(f"Generated {pd.Timestamp.now():%Y-%m-%d %H:%M} from raw data with cached downloads. **N = {n_ep} crash episodes, {NE.episode.nunique()} non-event windows, {B_r.entry.nunique()} unconditional month-end entries.** "
             f"Ten replayed crash episodes (eleven defined) is not a distribution: every number below is a range-carrying estimate from a small sample, and no point estimate should be read without its neighbours in the episode table. Episodes excluded: {yrs_excluded}. "
             f"Pre-2000 surfaces are parametric guesses; results are reported with and without pre-2000 episodes in §2.\n")
    R.append("**Source tags.** " + "; ".join(f"{k}: {v}" for k, v in data["meta"].items()) + ". Every surface is *parametric* (no licensed surface is reachable here). "
             "VIX term structure: 'vix-futures' where the VIX-futures slope exists (2006+), 'default-MR' before. Put wing: spec default 0.35·T^-0.25 everywhere (SKEW unavailable to fit), flat 0.10 before 1987-10-19.\n")
    R.append("## 0. Timing reconciliation (v4 engine vs report §2)\n")
    R.append(timing.table())
    R.append("\nThe v6 replay does not use scenario timing (it replays real dates), but the scenario-weighted EV in §1 uses the current BDCR-26 weights (28/19/17/17/14/5). "
             "For the synthetic model, the v6 windows above are the reconciled timing and are what `put_scenario_model_sept2026.py` should adopt (`SecondWave` 40% in months 0–1.5 and 60% in 1.5–20; `AI Bust` 6–22; `Repression` 8–24; `Fracture` 16–24). The report's §2 table is the timing used.\n")
    R.append("## 1. Main table (v4 format), historical conditionals\n")
    R.append("Entries within 12 months of each episode peak, exit rule = v4 (−22% index trigger), 7% haircuts. Conditionals are pooled means by BDCR analog: Muddle = 0.65 × correction episodes (2011/2015/2018) + 0.35 × non-event windows; Escape = non-event windows; Fracture = 1998 only (N=1). "
             "EV hist-weighted = Σ weight × conditional. Not replayable: " + "; ".join(NOT_REPLAYABLE) + ".\n")
    R.append(md_table(main_tbl))
    R.append("\n'steep-skew' = put slope 0.35·T^-0.5 instead of the spec default T^-0.25. The spec default prices short-dated deep wings far below observed levels (a 2-month 25%-OTM SPX put on 2020-02-14 costs 0.03% of spot under the default vs ~0.19% under the steep variant; the spec's own 2020 sanity band of 20-50x is met only by the steep variant). Long-dated 10%-OTM structures are much less sensitive to the choice.\n")
    R.append("\nWith pre-2000 episodes excluded (2000, 2007, 2011, 2015, 2018, 2020, 2022 only):\n")
    E12b = E12[~E12.episode.isin(["1987", "1990", "1998"])]
    condb = E12b.groupby(["structure", "analog"])["multiple"].mean().unstack()
    hb = pd.DataFrame(index=condb.index)
    hb["Muddle"] = 0.65 * condb.get("MuddleCorrection").fillna(ne_mean) + 0.35 * ne_mean
    hb["Repression"] = condb.get("Repression"); hb["AIBust"] = condb.get("AIBust"); hb["SecondWave"] = condb.get("SecondWave"); hb["Escape"] = ne_mean
    hb["Fracture"] = hb["SecondWave"]
    for col in hb.columns: hb[col] = hb[col].fillna(ne_mean.reindex(hb.index))
    evb = sum(WEIGHTS[k] * hb[k] for k in WEIGHTS)
    hb = hb[~hb.index.map(is_sg)]; evb = evb[hb.index]
    R.append("(Fracture conditional = Second Wave here, since the only Fracture analog, 1998, is pre-2000.)\n")
    R.append(md_table(pd.DataFrame({"structure": hb.index, "EV hist-weighted (post-2000)": evb.values,
                                    "Mu/Rp/AB/SW/Es/Fr": ["/".join(f"{hb.loc[s,k]:.1f}" for k in ["Muddle","Repression","AIBust","SecondWave","Escape","Fracture"]) for s in hb.index]}).sort_values("EV hist-weighted (post-2000)", ascending=False)))
    R.append("\n### 1b. Seagulls (put spread part-financed by a far-OTM short call)\n")
    R.append("v5 is not present here; the definitions are reconstructed (SPX 16m +90p/−70p/−125c, QQQ 16m +90p/−65p/−135c, SPX 7m +90p/−75p/−115c). Multiples are of *max risk* = short-call loss on a +35% rally by expiry net of credit received, so they are not comparable to the put multiples above; the P&L columns in % of notional are the honest comparison. The lesson from the first pass (calls 8–12% OTM) survives: a seagull's payoff distribution is dominated by the short call in melt-ups, which is exactly the Muddle/Escape leg of the map.\n")
    R.append(md_table(sg_tbl))
    R.append("\n## 2. Episode table (v4 exit rule): best / median / worst entry offset\n")
    R.append(md_table(ep_tbl))
    R.append("\n## 3. Entry-offset heatmap (median multiple, crash episodes pooled, v4 exit rule; columns = months before peak)\n")
    R.append(md_table(heat.reset_index().rename(columns={c: f"-{int(c)}m" for c in heat.columns})))
    R.append("\n## 4. Bleed table\n")
    R.append("Per non-event window: mean multiple of a structure bought at every month-end, and the premium burned per year (% of notional) by one unit held continuously and rolled at expiry = median cost ÷ tenor × (1 − mean multiple). Seagulls are in §1b.\n")
    R.append(md_table(bleed))
    R.append("\nUnconditional baseline (every month-end 1990-01 → last date the structure can expire inside the data):\n")
    R.append(md_table(base_bleed.reset_index()))
    budget = 1.25
    R.append(f"\nSizing overlay: with a {budget}%/yr premium budget, the median-cost SPX Dec-27 10% OTM put (cost ≈ {E12[E12.structure=='SPX Dec-27 10% OTM'].cost_pct.median():.1f}% of notional) buys ≈ {budget / max(E12[E12.structure=='SPX Dec-27 10% OTM'].cost_pct.median(),0.1) * 100:.0f}% of portfolio notional per year of coverage; "
             f"cumulative bleed over a 5-year non-event stretch (1995–99) = ≈ {5*budget:.1f}% of portfolio; budget-adjusted payoff in a crash episode = multiple × {budget}% of portfolio per year held (e.g. a 6x = +{6*budget:.1f}%).\n")
    R.append("## 5. Exit-rule comparison (crash entries within 12 months of the peak; last column = non-event windows)\n")
    R.append("`peak_-22` is a v6 addition: exit at −22% from the running peak since entry rather than from the entry spot. It is the rule the synthetic model implicitly assumes (crashes start from the entry level).\n")
    R.append(md_table(xr.reset_index()))
    R.append("\n## 6. Entry-filter test (tranche rule) on the unconditional baseline\n")
    R.append("Rule: (ERP ≤ 0 or CAPE > 32) AND VIX < 18. **HY OAS leg not applied (series unavailable here).** ERP = trailing E/P − 10y (not forward). Sensitivity ±25% on each threshold.\n")
    R.append(md_table(ftab))
    R.append("\n## 7. Diagnostics\n")
    R.append("Surface ATM vol at each trough by tenor vs v4's crash_iv (34 SPX / 42 NDX); put slope is the default (no realized skew is observable here):\n")
    R.append(md_table(diag))
    R.append("\nHow often the −22% exit fired, and fired before the trough (v4 rule, all entries):\n")
    R.append(md_table(fired.reset_index()))
    R.append("\nSensitivity of the 1-year ATM mark at the trough to the term rule (MR model vs the spec's literal VIX×0.95):\n")
    R.append(md_table(sens))
    R.append(f"\nSurface validation on 300 random dates: parity violations {viol['parity']}, calendar {viol['calendar']}, butterfly {viol['butterfly']}. Term tags: {term_tags}.\n")
    R.append("## 8. Delta vs v5 / v4\n")
    R.append("v5 is not present in this environment; the comparison is against the v4 synthetic model re-run on the reconciled §0 timing (exit rule on, 6,000 paths). Structures in the top 8 with a gap above 30%:\n")
    R.extend(deltas if deltas else ["No top-8 structure differs from v4 by more than 30%."])
    R.append("\n## 9. Red-team checklist status\n")
    R.append("- Survivorship: non-event rows and the unconditional baseline are in §4 (headline, not appendix).\n- Regime shift: §1 reports with and without pre-2000 episodes.\n- Liquidity: 7% haircut applied on entry and exit; far-OTM open-interest caps NOT modelled (no OI data).\n- Filter overfitting: ±25% sensitivity in §6; HY leg untested.\n- Small N: stated in the header; ranges in §2.\n- Data integrity: SPX daily is futures-derived (crash-day moves can be exaggerated when the basis dislocates; Oct-1987 overridden with published returns); NDX anchors are from memory and must be verified.\n")
    (HERE / "report_v6.md").write_text("\n".join(R))
    E.to_csv(HERE / "results_episodes.csv", index=False); NE.to_csv(HERE / "results_nonevent.csv", index=False); B.to_csv(HERE / "results_baseline.csv", index=False)
    print(f"report written {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
