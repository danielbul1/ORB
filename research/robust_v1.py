"""Robustness of frozen ORB v1 before real money: costs, missed trend days, drawdown paths, parameter plateau.

Nothing here selects or changes a rule. ORB v1's parameters stay frozen (orb.families.ORB_V1), so these runs
don't spend the Hypothesis budget (ADR 0006). They ask how much of the Edge survives worse conditions than the
backtest assumes. Pass bars are fixed here, before the first run:

  1. Costs: with 1 extra tick of slippage per side on every trade, plus 2 extra ticks on every stop exit,
     the Sharpe stays > 0.5 and the Prop Score (Flex 150K, 6 -> 3 MNQ) stays > 0 in era A, era B and 2025-26.
  2. Missed trend days: with the best 5 trades of each era removed, the era's total R stays > 0.
     A random 5% of trades missed (1,000 draws) keeps the median Sharpe > 0.5 in each era.
  3. Drawdown paths: block bootstrap of era B (20-Session blocks, 5,000 one-year paths). Reported: the
     drawdown percentiles in R and the chance that a year's drawdown exceeds the evaluation's max loss
     (Flex 150K $4,500 at $480/R = 9.4R) and 1.5x the historical worst (ADR 0005 kill switch). Descriptive.
  4. Plateau: one parameter at a time at -50/-25/+25/+50% (or_min at 3/10/15). Pass = every neighbour keeps
     >= 50% of the base Sharpe and stays > 0 in era A and era B.

Usage: python research/robust_v1.py [--npz data/long_adj_rth.npz]   (writes results/robust_v1.txt)
"""
import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb import long as L  # noqa: E402
from orb.backtest import TICK, run  # noqa: E402
from orb.data import build  # noqa: E402
from orb.families import ORB_V1  # noqa: E402
from orb.judge import stats  # noqa: E402
from orb.propscore import Flex, prop_score  # noqa: E402

FLEX_150K = Flex(target=9000, mll=4500, day_min=250, payout_cap=3000, eval_fee=245 * 0.6, reset_fee=245 * 0.6)
USD_EVAL, USD_FUNDED = 6 * 80, 3 * 80   # research/prop_search.py: 1 MNQ ~ $80/R
HIST_WORST_DD_R = 18.2                  # results/monthly_review.txt, ORB v1
MIN_SESSIONS = 300                      # skip an era with less data (prop windows are 252 Sessions)


def daily_r(res, extra_side_ticks=0, extra_stop_ticks=0):
    """ORB v1 daily R with extra slippage: per side on every trade, and on top of that on stop exits."""
    risk = np.where(res["ok"], res["risk"], np.nan)
    extra = 2 * extra_side_ticks * TICK + np.where(res["reason"] == "stop", extra_stop_ticks * TICK, 0.0)
    return np.where(res["ok"], res["r"] - extra / risk, 0.0)


def era_line(x, m):
    s = stats(x[m])
    p = prop_score(x[m], USD_EVAL, USD_FUNDED, FLEX_150K, horizon=252)
    return s, p


def max_dd(x):
    eq = np.cumsum(x, axis=-1)
    z = np.zeros(eq.shape[:-1] + (1,))
    eq = np.concatenate([z, eq], axis=-1)
    return (np.maximum.accumulate(eq, axis=-1) - eq).max(-1)


def block_bootstrap(x, n_paths=5000, length=252, block=20, seed=7):
    rng = np.random.default_rng(seed)
    n_blocks = -(-length // block)
    starts = rng.integers(0, len(x) - block, size=(n_paths, n_blocks))
    idx = (starts[:, :, None] + np.arange(block)).reshape(n_paths, -1)[:, :length]
    return x[idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", help="cached Days matrix (default: orb.long.load())")
    a = ap.parse_args()
    d = build(None, a.npz) if a.npz else L.load()
    eras = {k: m for k, m in L.eras(d).items() if m.sum() >= MIN_SESSIONS}
    out = []
    say = out.append
    say(f"ORB v1 robustness ({d.dates[0]} .. {d.dates[-1]}, {len(d.dates)} Sessions). Eras: {', '.join(eras)}")
    say(f"Frozen params: {ORB_V1} + costs {L.COST}\n")

    base_res = run(d, **ORB_V1, **L.COST)
    base = daily_r(base_res)
    verdict = {}

    # 1. costs ---------------------------------------------------------------------------------------------
    say("== 1. Costs: extra slippage ticks per side / extra ticks on stop exits")
    say(f"{'side':>4} {'stop':>4} | " + " | ".join(f"{k:^34}" for k in eras))
    say(f"{'':>4} {'':>4} | " + " | ".join(f"{'Sharpe':>7} {'R/yr':>7} {'Prop $/mo':>9} {'p10':>7}" for _ in eras))
    for side, stop in [(0, 0), (1, 0), (1, 2), (2, 2), (2, 4), (3, 4)]:
        x = daily_r(base_res, side, stop)
        cells = []
        for k, m in eras.items():
            s, p = era_line(x, m)
            cells.append(f"{s['sharpe']:>7.2f} {s['yearly']:>7.1f} {p['net_per_month']:>9.0f} {p['p10']:>7.0f}")
            if (side, stop) == (1, 2):
                verdict.setdefault("1 costs", []).append(s["sharpe"] > 0.5 and p["net_per_month"] > 0)
        say(f"{side:>4} {stop:>4} | " + " | ".join(cells))

    # 2. missed trend days -----------------------------------------------------------------------------------
    say("\n== 2. Missed trend days")
    rng = np.random.default_rng(11)
    for k, m in eras.items():
        x = base[m]
        traded = np.flatnonzero(x != 0)
        top = traded[np.argsort(x[traded])[::-1]]
        row = [f"{k}: total {x.sum():.1f}R over {len(traded)} trades"]
        for n in (1, 2, 5, 10):
            y = x.copy()
            y[top[:n]] = 0
            row.append(f"-top{n} {y.sum():.1f}R")
            if n == 5:
                verdict.setdefault("2 missed", []).append(y.sum() > 0)
        sh = []
        for _ in range(1000):
            y = x.copy()
            y[traded[rng.random(len(traded)) < 0.05]] = 0
            sh.append(stats(y)["sharpe"])
        verdict.setdefault("2 missed", []).append(np.median(sh) > 0.5)
        row.append(f"| random 5% missed: Sharpe median {np.median(sh):.2f}, p5 {np.percentile(sh, 5):.2f} "
                   f"(base {stats(x)['sharpe']:.2f})")
        say("  " + " ".join(row))

    # 3. drawdown paths --------------------------------------------------------------------------------------
    say("\n== 3. One-year drawdown paths (block bootstrap, 20-Session blocks, 5,000 paths)")
    eval_r = FLEX_150K.mll / USD_EVAL
    for k, m in eras.items():
        x = base[m]
        if len(x) < 252 + 20:
            continue
        paths = block_bootstrap(x)
        dd = max_dd(paths)
        yr = paths.sum(1)
        say(f"  {k}: drawdown R p50 {np.percentile(dd, 50):.1f} | p90 {np.percentile(dd, 90):.1f} | "
            f"p99 {np.percentile(dd, 99):.1f} | P(dd > {eval_r:.1f}R eval max loss) {np.mean(dd > eval_r):.1%} | "
            f"P(dd > {1.5 * HIST_WORST_DD_R:.1f}R kill switch) {np.mean(dd > 1.5 * HIST_WORST_DD_R):.1%} | "
            f"P(losing year) {np.mean(yr < 0):.1%}")

    # 4. plateau ---------------------------------------------------------------------------------------------
    say("\n== 4. Plateau: one parameter at a time (Sharpe by era; base first)")
    base_sh = {k: stats(base[m])["sharpe"] for k, m in eras.items()}
    say(f"  {'base':<22} " + " ".join(f"{k} {v:>5.2f}" for k, v in base_sh.items()))
    plateau_ok = []
    steps = (0.5, 0.75, 1.25, 1.5)
    variants = [("stop_x", ORB_V1["stop_x"] * f) for f in steps] + \
               [("target_r", ORB_V1["target_r"] * f) for f in steps] + \
               [("body_min", ORB_V1["body_min"] * f) for f in steps] + \
               [("or_min", n) for n in (3, 10, 15)]
    for key, val in variants:
        x = daily_r(run(d, **{**ORB_V1, key: val}, **L.COST))
        cells = []
        for k, m in eras.items():
            sh = stats(x[m])["sharpe"]
            cells.append(f"{k} {sh:>5.2f}")
            if k != "spent 25-26":
                plateau_ok.append(sh > 0 and sh >= 0.5 * base_sh[k])
        say(f"  {key + ' = ' + format(val, 'g'):<22} " + " ".join(cells))
    verdict["4 plateau"] = plateau_ok

    say("\n== Verdict (pass bars in the module docstring)")
    for k, v in verdict.items():
        say(f"  {k}: {'PASS' if all(v) else 'FAIL'} ({sum(v)}/{len(v)} checks)")
    text = "\n".join(out)
    print(text)
    (ROOT / "results" / "robust_v1.txt").write_text(text + "\n")


if __name__ == "__main__":
    main()
