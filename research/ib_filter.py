"""H15 (ADR 0007, pre-registered in the Edge Hunt Log 2026-10-14): IB formation-order filter on v3's 60-minute Leg.

A 60-minute Leg long is kept only if the 09:30-10:29 low printed before the high; a short only if the high printed
first; same-bar prints leave the Leg unchanged. Judged as a Filter vs Ensemble v3 (beat_v3.judge_filter).
Usage: python research/ib_filter.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research"))
import beat_v3 as B  # noqa: E402
from orb import long as L  # noqa: E402


def order_ok(d, direction, n, quadrant=False):
    """Formation order of the first n bars agrees with the trade direction (optionally plus H13's quadrant)."""
    hi_at, lo_at = d.h[:, :n].argmax(1), d.l[:, :n].argmin(1)
    ok = np.where(direction > 0, lo_at < hi_at, np.where(direction < 0, hi_at < lo_at, True)) | (hi_at == lo_at)
    if quadrant:
        hi, lo = d.h[:, :n].max(1), d.l[:, :n].min(1)
        pos = (d.c[:, n - 1] - lo) / np.where(hi > lo, hi - lo, np.nan)
        ok &= np.where(direction > 0, pos >= 0.75, np.where(direction < 0, pos <= 0.25, True))
    return ok


def main():
    d = L.load()
    E = L.eras(d)
    res = B.legs(d)
    v3 = B.combine(res)
    m60 = order_ok(d, res[60]["dir"], 60)
    verdict = B.judge_filter("H15 IB formation-order filter (60-min Leg)", B.combine(res, leg_on={60: m60}), v3, E)
    for label, leg_on in [
        ("  info: also on the 30-min Leg", {60: m60, 30: order_ok(d, res[30]["dir"], 30)}),
        ("  info: plus H13 quadrant (60-min Leg)", {60: order_ok(d, res[60]["dir"], 60, quadrant=True)}),
    ]:
        B.judge_filter(label, B.combine(res, leg_on=leg_on), v3, E)
    print("\n  info: 60-min Leg R per trade, order agrees vs disagrees")
    r60 = res[60]
    for k, m in E.items():
        t = r60["ok"] & m
        a, b = r60["r"][t & m60], r60["r"][t & ~m60]
        print(f"    {k:12} agree {a.mean():+.3f}R (n={len(a)}) | disagree {b.mean():+.3f}R (n={len(b)})")
    print(f"\nH15 VERDICT (registered rule only): {'PASS' if verdict else 'FAIL'} | DSR count N = {30 + 3}")


if __name__ == "__main__":
    main()
