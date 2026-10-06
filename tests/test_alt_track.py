"""Unit checks for the ADR 0008 engine additions on synthetic Sessions."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from orb.backtest import TICK, run  # noqa: E402
from tests.synth import make  # noqa: E402

D = make(seed=3)
CH = dict(or_min=15, entry="close", entry_tf=5, stop="or", target_r=2, cutoff=149)  # the chassis
rows = np.arange(len(D.dates))


def test_chassis_trades_and_breaks_on_5m_closes():
    r = run(D, **CH)
    ok = r["ok"]
    assert ok.sum() > 100
    jb = r["e"][ok] - 1  # breakout bar
    assert np.all((jb + 1) % 5 == 0) and np.all(jb >= 19)
    orh, orl = D.h[:, :15].max(1)[ok], D.l[:, :15].min(1)[ok]
    c = D.c[rows[ok], jb]
    assert np.all((c > orh) | (c < orl))
    assert np.all(r["e"][ok] <= 150)


def test_frac_one_equals_or_stop():
    a, b = run(D, **CH), run(D, **{**CH, "stop": "frac", "stop_x": 1.0})
    assert np.allclose(a["stop"], b["stop"], equal_nan=True) and np.array_equal(a["ok"], b["ok"])


def test_midpoint_stop():
    r = run(D, **{**CH, "stop": "frac", "stop_x": 0.5})
    ok = r["ok"]
    mid = (D.h[:, :15].max(1) + D.l[:, :15].min(1)) / 2
    assert np.allclose(r["stop"][ok], mid[ok] - r["dir"][ok] * TICK)


def test_preopen_range():
    r = run(D, **{**CH, "or_start": -15, "or_min": 15})  # 09:15-09:29 only
    ok = r["ok"]
    orh = D.pre_h.max(1)
    assert ok.sum() > 50
    assert np.allclose(r["stop"][ok & (r["dir"] < 0)], orh[ok & (r["dir"] < 0)] + TICK)
    assert np.all(r["e"][ok] >= 5)  # first 5m close of the Session is 09:34
    v4 = run(D, **{**CH, "or_start": -1, "or_min": 12})  # 09:29-09:40
    hi = np.maximum(D.pre_h[:, -1], D.h[:, :11].max(1))
    s = v4["ok"] & (v4["dir"] < 0)
    assert np.allclose(v4["stop"][s], hi[s] + TICK)
    assert np.all(v4["e"][v4["ok"]] >= 15)  # first 5m candle closing after 09:40 ends 09:44
    nopre = make(seed=3)
    nopre.pre_h[:] = np.nan
    nopre.pre_l[:] = np.nan
    assert run(nopre, **{**CH, "or_start": -15})["ok"].sum() == 0


def test_retest_window():
    base = run(D, **{**CH, "entry": "retest"})
    w = run(D, **{**CH, "entry": "retest", "retest_win": 15})
    assert w["ok"].sum() <= base["ok"].sum()
    ok = w["ok"]
    edge = np.where(w["dir"] > 0, D.h[:, :15].max(1), D.l[:, :15].min(1))
    assert np.all(np.where(w["dir"][ok] > 0, w["entry"][ok] <= edge[ok], w["entry"][ok] >= edge[ok]))


def test_bar_stop_and_point_targets():
    r = run(D, **{**CH, "stop": "bar", "target_r": 1.5, "target_min_pts": 10})
    ok = r["ok"]
    jb = r["e"][ok] - 1
    lo = np.array([D.l[i, j - 4:j + 1].min() for i, j in zip(rows[ok], jb)])
    hi = np.array([D.h[i, j - 4:j + 1].max() for i, j in zip(rows[ok], jb)])
    assert np.allclose(r["stop"][ok], np.where(r["dir"][ok] > 0, lo, hi))
    m = run(D, **{**CH, "entry_tf": 1, "stop": "pts", "stop_x": 51, "target_r": None, "target_pts": 51})
    assert np.allclose(m["risk"][m["ok"]], 51)


def test_prev_inside_and_bvol_only_remove_trades():
    base = run(D, **CH)
    for extra in (dict(prev_inside=True), dict(bvol_min=1.5)):
        r = run(D, **{**CH, **extra})
        assert r["ok"].sum() <= base["ok"].sum()
    assert run(D, **{**CH, "bvol_min": 1e9})["ok"].sum() == 0


def test_each_side_takes_both_breaks():
    lo = run(D, **{**CH, "side": "long", "each_side": True})
    sh = run(D, **{**CH, "side": "short", "each_side": True})
    first = run(D, **CH)
    assert lo["ok"].sum() + sh["ok"].sum() > first["ok"].sum()
    assert np.all(lo["dir"][lo["ok"]] > 0) and np.all(sh["dir"][sh["ok"]] < 0)
    assert (lo["ok"] & sh["ok"]).any()


def test_build_keeps_preopen_bars(tmp="/tmp/orb_build_test.csv"):
    import pandas as pd
    from orb.data import build
    t0 = pd.Timestamp("2024-03-04 09:00", tz="America/New_York")
    ts = pd.date_range(t0, periods=7 * 60, freq="min")
    px = 18000 + np.arange(len(ts)) * 0.25
    pd.DataFrame(dict(time=(ts - pd.Timestamp(0, tz="UTC")).total_seconds().astype(int), open=px, high=px + 1, low=px - 1,
                      close=px, volume=1.0)).to_csv(tmp, index=False)
    d = build(tmp)
    assert d.pre_h.shape == (1, 15) and d.pre_h[0, 0] == px[15] + 1 and d.pre_h[0, -1] == px[29] + 1
    assert d.o[0, 0] == px[30]


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f()
            print("ok", name)
