"""Pre-registered test (docs/adr/0002): frozen ORB v1 on NAS100 2003-01 .. 2016-05, looked at once.

Usage: python -m orb.holdout_2003
"""
from pathlib import Path

import numpy as np
import pandas as pd

from orb.backtest import run
from orb.data import build
from orb.families import ORB_V1
from orb.judge import stats, years_of

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_nas100():
    parts = sorted(DATA.glob("nas100_[abc]_1m_lse.csv"))
    if len(parts) != 3:
        raise SystemExit(f"expected 3 NAS100 chunks, found {[p.name for p in parts]}")
    full = DATA / "nas100_2003_2016_1m.csv"
    pd.concat(pd.read_csv(p) for p in parts).drop_duplicates("time").sort_values("time").to_csv(full, index=False)
    return build(full, DATA / "nas100_rth.npz")


def main():
    d = load_nas100()
    keep = d.dates <= np.datetime64("2016-05-31")
    d = d.slice(keep)
    print(f"NAS100 Sessions: {len(d.dates)}  {d.dates[0]} .. {d.dates[-1]}")
    yrs = years_of(d)
    verdict = {}
    for case, cost in (("a: 0.83 bp", dict(cost_bp=0.83)), ("b: fixed 0.5 pt", dict(cost=0.5))):
        res = run(d, **{**ORB_V1, **cost})
        x = np.where(res["ok"], res["r"], 0.0)
        s = stats(x)
        per_year = {int(y): stats(x[yrs == y])["score"] for y in np.unique(yrs)}
        pos = np.mean([v > 0 for v in per_year.values()])
        print(f"\ncost {case}: {s}\n  yearly Score: {per_year}\n  positive years: {pos:.0%}")
        verdict[case] = (s, pos)
    a, pos_a = verdict["a: 0.83 bp"]
    b, _ = verdict["b: fixed 0.5 pt"]
    passed = a["sharpe"] >= 0.5 and pos_a >= 0.6 and b["yearly"] > 0
    print(f"\nPRE-REGISTERED VERDICT: {'PASS' if passed else 'FAIL'} "
          f"(Sharpe {a['sharpe']} >= 0.5, positive years {pos_a:.0%} >= 60%, cost-b total {'> 0' if b['yearly'] > 0 else '<= 0'})")


if __name__ == "__main__":
    main()
