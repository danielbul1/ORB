"""ADR 0008: Alt Baseline (information only) and the 5 pre-registered Hypotheses H1-H5 on the breakout chassis.

Every rule, grid and pass bar is fixed by the registration in vault/Research/Edge Hunt Log.md (2026-10-06).
Grids (<= 3 values) are chosen by Walk-Forward (orb.judge, test years 2019-24); every value counts for the DSR.
Pass (all): Walk-Forward Score above the stronger of Ensemble v3 and ORB v1 over the same years;
  Prop Score (rescaled to ORB v1's era-B max drawdown, Flex 150K at ORB v1's 6 -> 3 MNQ) above ORB v1's;
  ES Sharpe > 0 over 2016-24 with the NQ Walk-Forward picks. (A Portfolio Member pass is reported beside it.)
Data: the 23-year base rebuilt with pre-open bars (orb.long.load(pre=True)); ES from data/es_1m.csv or
  data/es_adj_rth_pre.npz (H3 and Sniper V1-V3 need ES pre-open bars too).
Alt Baseline fidelity limits: Sniper's first candle after 09:30 cannot pass "previous close inside" (the engine
  keeps no pre-open closes), and Mike's "never both open" is not enforced (long and short run independently).
Usage: python research/alt_track.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb import long as L  # noqa: E402
from orb.backtest import run  # noqa: E402
from orb.data import build  # noqa: E402
from orb.families import ENSEMBLE_MEMBERS, ENSEMBLE_V3, ORB_V1  # noqa: E402
from orb.judge import WF_END, WF_START, deflated_sharpe, grid, stats, walk_forward, years_of  # noqa: E402
from orb.propscore import Flex, prop_score  # noqa: E402

FEE = 245 * 0.6
FLEX150 = Flex(target=9000, mll=4500, day_min=250, payout_cap=3000, eval_fee=FEE, reset_fee=FEE)
USD_EVAL, USD_FUNDED = 6 * 80, 3 * 80  # ORB v1 on Flex 150K: 6 MNQ in the Evaluation, 3 funded ($80 per MNQ per R)
DSR_BEFORE = 15  # trials counted before this track (Edge Hunt Log, H11)

# ---------------------------------------------------------------- registered rules
CHASSIS = dict(or_min=15, entry="close", entry_tf=5, stop="or", target_r=2, cutoff=149, exit_min=389, **L.COST)
HYPOTHESES = {
    "H1 acceptance / retest": ({**CHASSIS, "entry": "retest"}, dict(retest_win=[15, 30, 60])),
    "H2 midpoint stop": ({**CHASSIS, "stop": "frac"}, dict(stop_x=[0.5, 0.75, 0.4])),
    "H3 pre-open range": (CHASSIS, dict(window=[(-15, 15), (-15, 30), (-1, 12)])),
    "H4 Initial Balance + volume": ({**CHASSIS, "or_min": 60, "cutoff": 269}, dict(bvol_min=[1.0, 1.5, 2.0])),
    "H5 narrow OR": (CHASSIS, dict(max_or_atr=[0.15, 0.25, 0.35])),
}
SNIPER = dict(entry="close", prev_inside=True, stop="bar", target_min_pts=10, cutoff=148, exit_min=149, **L.COST)
SNIPER["each_side"] = True  # 1 long + 1 short per Session
ALT_BASELINE = {
    "Sniper V1 (09:15-09:29, 5m, 1.5R)": dict(SNIPER, or_start=-15, or_min=15, entry_tf=5, target_r=1.5),
    "Sniper V2 (09:15-09:45, 15m, 0.3R)": dict(SNIPER, or_start=-15, or_min=31, entry_tf=15, target_r=0.3),
    "Sniper V3 (09:15-09:45, 5m, 0.3R)": dict(SNIPER, or_start=-15, or_min=31, entry_tf=5, target_r=0.3),
    "Sniper V4 (09:29-09:40, 5m, 1.5R)": dict(SNIPER, or_start=-1, or_min=12, entry_tf=5, target_r=1.5),
    "Mike's Signal Pro (09:30-09:45, 51/51 pt)": dict(or_min=15, entry="close", stop="pts", stop_x=51, target_pts=51,
                                                      cutoff=388, exit_min=389, each_side=True, **L.COST),
    "Chassis (info)": CHASSIS,
}


def daily_r(d, p):
    if "window" in p:
        p = {k: v for k, v in p.items() if k != "window"} | dict(or_start=p["window"][0], or_min=p["window"][1])
    if p.get("each_side"):
        lo, sh = (run(d, **{**p, "side": s}) for s in ("long", "short"))
        return np.where(lo["ok"], lo["r"], 0.0) + np.where(sh["ok"], sh["r"], 0.0)
    r = run(d, **p)
    return np.where(r["ok"], r["r"], 0.0)


def v3(d):
    return sum(daily_r(d, {**ENSEMBLE_V3, "or_min": om, **L.COST}) for om in ENSEMBLE_MEMBERS) / len(ENSEMBLE_MEMBERS)


def prop(x, m, scale):
    return prop_score(x[m] * scale, USD_EVAL, USD_FUNDED, FLEX150, horizon=252)["net_per_month"]


def load_es():
    for src, cache in ((None, ROOT / "data" / "es_adj_rth_pre.npz"), (ROOT / "data" / "es_1m.csv", None)):
        if (cache and cache.exists()) or (src and src.exists()):
            return build(src, cache or ROOT / "data" / "es_adj_rth_pre.npz", adjust=src is not None)
    if (ROOT / "data" / "es_adj_rth.npz").exists():
        print("ES: only the RTH cache exists, so H3 / Sniper V1-V3 cannot trade ES (they will show 0 trades)")
        return build(None, ROOT / "data" / "es_adj_rth.npz")
    return None


def apply_picks(d, base, picks):
    """Stitch the NQ Walk-Forward picks, year by year, on another market."""
    yrs = years_of(d)
    out = np.zeros(len(d.dates))
    for y, p, _, _ in picks:
        m = yrs == y
        out[m] = daily_r(d, {**base, **p})[m]
    return out


def main(d=None, es=None):
    d = L.load(pre=True) if d is None else d
    E = L.eras(d)
    yrs = years_of(d)
    wf = (yrs >= WF_START) & (yrs <= WF_END)
    eb = E["B 2016-24"]
    print(f"Sessions {d.dates[0]} .. {d.dates[-1]} ({len(d.dates)}); pre-open bars on "
          f"{np.isfinite(d.pre_h).any(1)[eb].mean():.0%} of era-B Sessions")

    inc = {"Ensemble v3": v3(d), "ORB v1": daily_r(d, {**ORB_V1, **L.COST})}
    v1_dd = stats(inc["ORB v1"][eb])["maxdd"]
    v1_dd_wf = stats(inc["ORB v1"][wf])["maxdd"]  # Walk-Forward series only exist in 2019-24: rescale on those years
    ref_prop = prop(inc["ORB v1"], wf, 1.0)
    bar_score = max(stats(x[wf])["score"] for x in inc.values())
    print(f"\nIncumbents over the Walk-Forward years {WF_START}-{WF_END}:")
    for k, x in inc.items():
        s = stats(x[wf])
        print(f"  {k:12} Score {s['score']:>7,.0f} | Sharpe {s['sharpe']:>5} | trades {s['trades']} | "
              f"Prop ${prop(x, wf, v1_dd / stats(x[eb])['maxdd']):,.0f}/mo")
    print(f"  bar: Score > {bar_score:,.0f} and Prop > ${ref_prop:,.0f}/mo (ORB v1, Flex 150K 6->3 MNQ)")

    print("\n## Alt Baseline (information only, spends nothing)")
    for name, p in ALT_BASELINE.items():
        x = daily_r(d, p)
        print(f"\n=== {name}")
        for k, m in E.items():
            s = stats(x[m])
            sc = v1_dd / s["maxdd"] if s["maxdd"] else 0.0
            print(f"  {k:12} Sharpe {s['sharpe']:>5} | Score {s['score']:>7,.0f} | R/yr {s['yearly']:>6.1f} | "
                  f"DD {s['maxdd']:>5.1f}R | trades {s['trades']:>5} | win {s.get('win', 0):.2f} | "
                  f"Prop ${prop(x, m, sc) if m.sum() > 273 else 0:>5,.0f}/mo")

    es = load_es() if es is None else es
    print("\n## Hypotheses (ADR 0008)")
    trials, verdicts = [], {}
    for name, (base, space) in HYPOTHESES.items():
        fam = lambda dd, **p: daily_r(dd, {**base, **p})  # noqa: E731
        for p in grid(space):
            trials.append(stats(fam(d, **p)[eb])["sharpe"])
        oos, picks, s = walk_forward(d, fam, space)
        sc = v1_dd_wf / stats(oos[wf])["maxdd"] if stats(oos[wf])["maxdd"] else 0.0
        pr = prop(oos, wf, sc)
        es_s = stats(apply_picks(es, base, picks)[(years_of(es) >= 2016) & (years_of(es) <= 2024)])["sharpe"] \
            if es is not None else float("nan")
        port = (oos + inc["Ensemble v3"]) / 2
        port_ok = stats(port[wf])["score"] > stats(inc["Ensemble v3"][wf])["score"] and \
            prop(port, wf, v1_dd_wf / stats(port[wf])["maxdd"]) > \
            prop(inc["Ensemble v3"], wf, v1_dd_wf / stats(inc["Ensemble v3"][wf])["maxdd"])
        gates = dict(score=s["score"] > bar_score, prop=pr > ref_prop, es=es_s > 0)
        verdicts[name] = (all(gates.values()), port_ok and gates["es"], pr)
        print(f"\n=== {name}\n  Walk-Forward Score {s['score']:,.0f} (bar {bar_score:,.0f}) | Sharpe {s['sharpe']} | "
              f"trades {s['trades']} | win {s.get('win')} | streak {s['streak']}\n  Prop ${pr:,.0f}/mo (bar ${ref_prop:,.0f}) | "
              f"ES Sharpe 2016-24 {es_s} | gates {gates} | Portfolio Member with v3: {'yes' if port_ok else 'no'}")
        for y, p, tv, te in picks:
            print(f"    {y}: {p} (train Score {tv:,.0f} -> test {te:,.0f})")

    n = DSR_BEFORE + len(trials)
    print(f"\n## Verdict  (DSR trial count now N = {n})")
    passed = {k: v for k, v in verdicts.items() if v[0]}
    for k, (ok, member, pr) in verdicts.items():
        print(f"  {k:30} {'PASS' if ok else 'fail'}{' (Portfolio Member pass)' if member and not ok else ''}")
    if passed:
        best = max(passed, key=lambda k: passed[k][2])
        print(f"  Winner by Prop Score: {best}. Next: Forward Test >= 60 Sessions beside ORB v1 / v3.")
        base, space = HYPOTHESES[best]
        oos, _, _ = walk_forward(d, lambda dd, **p: daily_r(dd, {**base, **p}), space)
        print("  DSR:", deflated_sharpe(oos[wf], n, trials))
    else:
        print("  None passes: the incumbents stay. That is a valid outcome (ADR 0008).")


if __name__ == "__main__":
    main()
