"""H12 (ADR 0007, pre-registered in the Edge Hunt Log 2026-10-14): second-chance re-entry after an ORB v1 stop-out.

On a Session where frozen ORB v1 exited by its stop, the first 1-minute bar after the stop-out bar, up to bar
`cutoff`, that closes beyond the 5-minute OR extreme on the original side triggers one re-entry in the original
direction at the next bar's open. ORB v1's exits: stop `stop_x` x ATR14, 10R target, no trail, flat 15:59.
Judged as a Portfolio Member against Ensemble v3 (beat_v3.judge_member); v1 + Member vs v1 is information only.
Usage: python research/second_trade.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research"))
import beat_v3 as B  # noqa: E402
from orb import long as L  # noqa: E402
from orb.backtest import run  # noqa: E402
from orb.families import ORB_V1  # noqa: E402
from orb.judge import stats  # noqa: E402

BIG = B.BIG


def v1_result(d):
    return run(d, **ORB_V1, **L.COST)


def h12(d, v1, cutoff=120, stop_x=0.10):
    D, Bn = d.o.shape
    rows = np.arange(D)
    idx = np.arange(Bn)[None, :]
    k = ORB_V1["or_min"]
    orh, orl = d.h[:, :k].max(1), d.l[:, :k].min(1)
    direction = np.where(v1["ok"] & (v1["reason"] == "stop"), v1["dir"], 0)
    after = (idx > v1["x"][:, None]) & (idx <= np.minimum(cutoff, d.last - 1)[:, None])
    beyond = np.where(direction[:, None] > 0, d.c > orh[:, None], d.c < orl[:, None])
    trig = after & beyond & (direction[:, None] != 0)
    j = trig.argmax(1)
    e = np.where(trig.any(1), j + 1, BIG)
    entry = d.o[rows, np.minimum(e, Bn - 1)]
    stop = entry - direction * stop_x * d.atr14
    tgt = entry + direction * ORB_V1["target_r"] * stop_x * d.atr14
    return B.level_trade(d, direction, entry, e, stop, tgt=tgt, trail=False)


def main():
    d = L.load()
    E = L.eras(d)
    v3 = B.combine(B.legs(d))
    res = v1_result(d)
    v1 = np.where(res["ok"], res["r"], 0.0)
    verdict = None
    for label, p in [("H12 second-chance re-entry", {}), ("  plateau cutoff 60", dict(cutoff=60)),
                     ("  plateau cutoff 180", dict(cutoff=180)), ("  plateau stop 0.05", dict(stop_x=0.05)),
                     ("  plateau stop 0.15", dict(stop_x=0.15))]:
        y = h12(d, res, **p)
        ok = B.judge_member(label, y, v3, E)
        if verdict is None:
            verdict = ok
        print("  info, v1 + Member vs v1:")
        for k, m in E.items():
            a, b = stats((v1 + y)[m]), stats(v1[m])
            pa, pb = B.prop(v1 + y, m)["net_per_month"], B.prop(v1, m)["net_per_month"]
            print(f"    {k:12} Score {a['score']:>7,.0f} vs {b['score']:>7,.0f} | Sharpe {a['sharpe']:>5} vs {b['sharpe']:>5} | "
                  f"Prop ${pa:>5,.0f} vs ${pb:>5,.0f} (v3 sizing) | re-entries {int((y[m] != 0).sum())}")
    print(f"\nH12 VERDICT (registered rule only): {'PASS' if verdict else 'FAIL'}  | DSR count N = {15 + 5}")


if __name__ == "__main__":
    main()
