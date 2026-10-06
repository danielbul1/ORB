"""alttrading.ai ORB skeleton vs Ensemble v3 (information only, not a Hypothesis: no ADR 0006/0007 budget spent).

The skeleton is rebuilt from public descriptions only (their code is invite-only):
  Mike's ORB Signal Pro: 09:30-09:45 range on 1m bars, entry on a 1m close beyond it, stop at the other side,
  target 1-2x (alttrading.ai/education "ORB" card: target 1-2x range width, stop opposite side).
  B1: same, but the break must be "accepted": enter on the retest of the broken edge.
Limitation: the engine takes the first break only, so Signal Pro's second (opposite) trade of a Session is missing.

Data: free Dukascopy NAS100 CFD 1m (tools/pull_duka.py), 2012-2026, so era A is 2012-15 only. Costs are the
research base's (0.83 bp, floor 0.5 pt). Prop Score: each series is rescaled to v3's era-B max drawdown (as in
ADR 0007), then priced at v3's $960 / $640 per R on Flex 150K.
Usage: python research/alt_skeleton.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb import long as L  # noqa: E402
from orb.backtest import run  # noqa: E402
from orb.data import build  # noqa: E402
from orb.families import ENSEMBLE_MEMBERS, ENSEMBLE_V3  # noqa: E402
from orb.judge import stats  # noqa: E402
from orb.propscore import Flex, prop_score  # noqa: E402

FLEX150 = Flex(target=9000, mll=4500, day_min=250, payout_cap=3000)
USD_EVAL, USD_FUNDED, HORIZON = 960, 640, 504

SKELETON = dict(or_min=15, entry="close", stop="or", side="both", **L.COST)
VARIANTS = {
    "Alt 1R (cutoff 11:30)": dict(SKELETON, target_r=1),
    "Alt 2R (cutoff 11:30)": dict(SKELETON, target_r=2),
    "Alt 2R (entries all day)": dict(SKELETON, target_r=2, cutoff=360),
    "Alt B1 retest 2R": dict(SKELETON, entry="retest", target_r=2),
    "Alt 2R + v3 bracket*": dict(SKELETON, stop="atr", stop_x=0.1, target_r=10, trail_x=0.3, trail_start=2,
                                 min_risk_cost=4),
}


def v3(d):
    xs = [np.where((r := run(d, **{**ENSEMBLE_V3, "or_min": om, **L.COST}))["ok"], r["r"], 0.0)
          for om in ENSEMBLE_MEMBERS]
    return sum(xs) / len(xs)


def one(d, p):
    r = run(d, **p)
    return np.where(r["ok"], r["r"], 0.0)


def main():
    d = build(ROOT / "data" / "nas100_1m_duka.csv", ROOT / "data" / "nas100_duka_rth.npz")
    yrs = d.dates.astype("datetime64[Y]").astype(int) + 1970
    E = {"A 2012-15": (yrs >= 2012) & (yrs <= 2015), "B 2016-24": (yrs >= 2016) & (yrs <= 2024),
         "spent 25-26": yrs >= 2025}
    print(f"Sessions {d.dates[0]} .. {d.dates[-1]} ({len(d.dates)})")
    base = v3(d)
    dd_b = stats(base[E["B 2016-24"]])["maxdd"]
    series = {"Ensemble v3": base, **{k: one(d, p) for k, p in VARIANTS.items()}}
    for name, x in series.items():
        scale = dd_b / stats(x[E["B 2016-24"]])["maxdd"]
        print(f"\n=== {name}  (Prop scale {scale:.2f})")
        for k, m in E.items():
            s = stats(x[m])
            h = HORIZON if m.sum() > HORIZON + 21 else 252
            p = prop_score(x[m] * scale, USD_EVAL, USD_FUNDED, FLEX150, horizon=h)["net_per_month"]
            corr = float(np.corrcoef(x[m], base[m])[0, 1]) if x[m].std() and name != "Ensemble v3" else 1.0
            print(f"  {k:12} Sharpe {s['sharpe']:>5} | Score {s['score']:>7,.0f} | R/yr {s['yearly']:>6.1f} | "
                  f"DD {s['maxdd']:>5.1f}R | trades {s['trades']:>5} | win {s['win']:.2f} | streak {s['streak']:>3} | "
                  f"Prop ${p:>5,.0f}/mo | corr v3 {corr:+.2f}")
    print("\n* control: their entry (15m close break, both sides) with v3's stop/target/trail instead of theirs.")


if __name__ == "__main__":
    main()
