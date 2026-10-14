"""H13 and H14 (ADR 0007, pre-registered in the Edge Hunt Log 2026-10-14), both judged as Portfolio Members vs v3.

H13 IB quadrant continuation: IB = 09:30-10:29. Long if the 10:29 close is in the top quarter of the IB and the IB
    low printed first (short: bottom quarter, high first). Limit entry at the 75% / 25% level on its first touch
    10:30-12:00, stop at the IB midpoint, half out at IBH + 0.5 IBR and half at IBH + 1.0 IBR (mirrored), flat 15:59.
H14 stop-and-reverse: after frozen ORB v1 exits by its stop on bar x (x + 1 <= 120), enter the opposite way at the
    open of bar x + 1 with ORB v1's exits (0.10 ATR stop, 10R, no trail, flat 15:59).
Usage: python research/ib_reverse.py [H13] [H14]
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research"))
import beat_v3 as B  # noqa: E402
from orb import long as L  # noqa: E402
from orb.families import ORB_V1  # noqa: E402
from second_trade import v1_result  # noqa: E402

BIG = B.BIG
IB = 60  # bars 0..59 = 09:30..10:29


def h13(d, zone=0.75, end=150):
    D, Bn = d.o.shape
    rows = np.arange(D)
    idx = np.arange(Bn)[None, :]
    ibh, ibl = d.h[:, :IB].max(1), d.l[:, :IB].min(1)
    ibr = ibh - ibl
    low_first = d.l[:, :IB].argmin(1) < d.h[:, :IB].argmax(1)
    close = d.c[:, IB - 1]
    up_lvl, dn_lvl = ibl + zone * ibr, ibl + (1 - zone) * ibr
    direction = np.where((close >= up_lvl) & low_first, 1, np.where((close <= dn_lvl) & ~low_first, -1, 0))
    direction = np.where((ibr > 0) & (d.last > IB), direction, 0)
    lvl = np.where(direction > 0, up_lvl, dn_lvl)
    win = (idx >= IB) & (idx <= np.minimum(end, d.last - 1)[:, None])
    touch = win & np.where(direction[:, None] > 0, d.l <= lvl[:, None], d.h >= lvl[:, None])
    j = touch.argmax(1)
    e = np.where(touch.any(1) & (direction != 0), j, BIG)
    o_e = d.o[rows, np.minimum(e, Bn - 1)]
    entry = np.where(direction > 0, np.minimum(lvl, o_e), np.maximum(lvl, o_e))  # limit: the level or better
    stop = ibl + 0.5 * ibr
    ext = np.where(direction > 0, ibh, ibl)
    halves = [B.level_trade(d, direction, entry, e, stop, tgt=ext + direction * k * ibr, trail=False) for k in (0.5, 1.0)]
    return (halves[0] + halves[1]) / 2


def h14(d, v1, cutoff=120, stop_x=0.10):
    rows = np.arange(len(d.dates))
    stopped = v1["ok"] & (v1["reason"] == "stop") & (v1["x"] + 1 <= np.minimum(cutoff, d.last - 1))
    direction = np.where(stopped, -v1["dir"], 0)
    e = np.where(stopped, v1["x"] + 1, BIG)
    entry = d.o[rows, np.minimum(e, d.o.shape[1] - 1)]
    risk = stop_x * d.atr14
    return B.level_trade(d, direction, entry, e, entry - direction * risk,
                         tgt=entry + direction * ORB_V1["target_r"] * risk, trail=False)


def main(which):
    d = L.load()
    E = L.eras(d)
    v3 = B.combine(B.legs(d))
    res = v1_result(d)
    runs = {
        "H13": [("H13 IB quadrant continuation", lambda: h13(d)),
                ("  plateau zone 0.70", lambda: h13(d, zone=0.70)), ("  plateau zone 0.80", lambda: h13(d, zone=0.80)),
                ("  plateau window to 11:00", lambda: h13(d, end=90)), ("  plateau window to 13:00", lambda: h13(d, end=210))],
        "H14": [("H14 stop-and-reverse", lambda: h14(d, res)),
                ("  plateau cutoff 60", lambda: h14(d, res, cutoff=60)), ("  plateau cutoff 180", lambda: h14(d, res, cutoff=180)),
                ("  plateau stop 0.05", lambda: h14(d, res, stop_x=0.05)), ("  plateau stop 0.15", lambda: h14(d, res, stop_x=0.15))],
    }
    verdicts = {}
    for h in which:
        for i, (label, f) in enumerate(runs[h]):
            ok = B.judge_member(label, f(), v3, E)
            if i == 0:
                verdicts[h] = ok
    print("\n==== SUMMARY (registered rules only):", {h: "PASS" if v else "FAIL" for h, v in verdicts.items()},
          f"| DSR count N = {20 + 5 * len(which)}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["H13", "H14"])
