"""Look-ahead check: does a signal or a Rule Set use bars it could not have seen yet?

Idea from freqtrade's `lookahead-analysis` / `recursive-analysis`. A backtest computes every bar from the full
history; live, bar t is computed from bars 0..t only. For a sample of cut points we rerun on the data a live
chart would have had at the cut and require the same answer:

  * check_signal: per-bar functions fn(o, h, l, c, v, nd) -> array (as in research/indicator_nq_test.py).
    The series is cut after bar t and fn's value at t must equal the full run's value at t.
  * check_rule_set: Rule Sets on the Days matrix, fn(d) -> orb.backtest.run's result dict. The matrix has a
    fixed 390 columns, so later Sessions are dropped and the cut Session from the open of bar j on is replaced by
    a different random path (bar j keeps its open). Every Session before the cut must be unchanged in full; in
    the cut Session, whether a trade entered before bar j or at its open, its direction, entry and stop, and an
    exit before bar j must be unchanged. A stop entry filled inside bar j is not judged at that cut, so a Filter
    that peeks at the close of its own stop-entry bar is not caught.
  * check_build: orb.data.build's per-Session context (prior close, ATR14, ...) must not change when later
    Sessions are dropped.

A pass is evidence, not proof: a look-ahead that no sampled cut exposes is not found.
"""
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from orb.data import RTH_BARS, build


def _same(a, b):
    return np.isclose(np.asarray(a, float), np.asarray(b, float), rtol=1e-9, atol=1e-9, equal_nan=True)


# ---------------------------------------------------------------- per-bar signals
def check_signal(fn, o, h, l, c, v, nd, n_cuts=60, warmup=600, seed=0):
    """Cut the series after sampled bars t; fn on bars 0..t must give the full run's value at t.

    Returns (cuts tested, failures as (t, live value, backtest value))."""
    full = np.nan_to_num(np.asarray(fn(o, h, l, c, v, nd), float))
    n = len(c)
    rng = np.random.default_rng(seed)
    cuts = np.unique(rng.integers(min(warmup, n - 1), n, n_cuts))
    fails = []
    for t in cuts:
        s = slice(0, t + 1)
        live = np.nan_to_num(np.asarray(fn(o[s], h[s], l[s], c[s], v[s], nd[s]), float))[t]
        if not _same(live, full[t]):
            fails.append((int(t), float(live), float(full[t])))
    return len(cuts), fails


# ---------------------------------------------------------------- Rule Sets on the Days matrix
def repath(d, i, j, rng, drift):
    """Sessions 0..i of d, cut at the open of bar j of Session i: bars before j and bar j's open are kept, the rest
    of the Session is a fresh random path.

    drift is in units of the typical 1-minute move, so +-0.3 makes the rest of the day trend hard either way."""
    out = d.slice(np.arange(len(d.dates)) <= i)
    n = RTH_BARS - j
    recent = out.c[max(0, i - 20): i + 1]
    step = np.nanstd(np.diff(recent, axis=1))
    if not np.isfinite(step) or step <= 0:
        step = 1e-4 * out.o[i, j]
    c = out.o[i, j] + np.cumsum(rng.normal(drift * step, step, n))
    o = np.r_[out.o[i, j], c[:-1]]
    wick = np.abs(rng.normal(0, step / 2, (2, n)))
    vol = out.v[i, :j].mean() if j else out.v[max(i - 1, 0)].mean()
    out.o[i, j:] = o
    out.c[i, j:] = c
    out.h[i, j:] = np.maximum(o, c) + wick[0]
    out.l[i, j:] = np.minimum(o, c) - wick[1]
    out.v[i, j:] = vol * rng.uniform(0.2, 3.0, n)
    return out


def _known(res, i, j, open_j):
    """Did the trade of Session i enter before bar j, or at bar j's open (a decision made before bar j traded)?"""
    e = res["e"][i]
    return bool(res["ok"][i] and (e < j or (e == j and _same(res["entry"][i], open_j))))


def _diff_rule_set(full, cut, i, j, open_j):
    """What differs between the full run and the cut run that was already known at the open of bar j of Session i."""
    ok1, ok2 = full["ok"][:i], cut["ok"][:i]
    if not np.array_equal(ok1, ok2):
        return f"Session {np.flatnonzero(ok1 != ok2)[0]} (before the cut): taken / skipped changed"
    for k in ("dir", "entry", "stop", "e", "x", "pnl"):
        bad = ok1 & ~_same(full[k][:i], cut[k][:i])
        if bad.any():
            return f"Session {np.flatnonzero(bad)[0]} (before the cut): {k} changed"
    k1, k2 = _known(full, i, j, open_j), _known(cut, i, j, open_j)
    if k1 != k2:
        return f"cut Session, open of bar {j}: trade entered by then in {'backtest' if k1 else 'live'} only"
    if k1:
        for k in ("dir", "entry", "stop", "e"):
            if not _same(full[k][i], cut[k][i]):
                return f"cut Session, open of bar {j}: {k} {cut[k][i]} live vs {full[k][i]} backtest"
        x1, x2 = bool(full["x"][i] < j), bool(cut["x"][i] < j)
        if x1 != x2 or (x1 and not (_same(full["x"][i], cut["x"][i]) and _same(full["pnl"][i], cut["pnl"][i]))):
            return f"cut Session, open of bar {j}: exit before then differs"
    return None


def check_rule_set(fn, d, n_cuts=40, seed=0, drifts=(-0.3, 0.3), first=0.25):
    """Cut at the open of sampled (Session i, bar j) and compare everything known by then. fn(d) -> run()-style
    dict. A trade filled at bar j's open was decided before bar j traded, so it must not change either.

    Half the cuts are in Sessions the backtest traded: half of those at the open of the entry bar, where a
    one-bar-early decision shows, the rest at the exit bar, the bar after either, or in between.
    Returns (cuts tested, failures as (i, j, drift, what differed))."""
    full = fn(d)
    D = len(d.dates)
    rng = np.random.default_rng(seed)
    traded = np.flatnonzero(full["ok"][int(D * first):]) + int(D * first)
    cuts = []
    for k in range(n_cuts):
        if k % 2 and len(traded):
            i = int(rng.choice(traded))
            e, x = int(full["e"][i]), int(full["x"][i])
            j = e if rng.random() < 0.5 else int(rng.choice([e + 1, x, x + 1, rng.integers(e, max(x, e) + 1)]))
        else:
            i, j = int(rng.integers(int(D * first), D)), int(rng.integers(0, RTH_BARS))
        cuts.append((i, int(np.clip(j, 0, RTH_BARS - 1))))
    fails = []
    for i, j in cuts:
        for drift in drifts:
            what = _diff_rule_set(full, fn(repath(d, i, j, rng, drift)), i, j, d.o[i, j])
            if what:
                fails.append((i, j, drift, what))
                break
    return len(cuts), fails


# ---------------------------------------------------------------- data.build's per-Session context
def check_build(df, n_cuts=8, seed=0):
    """Build from all bars and from the bars up to the end of sampled Sessions; Sessions <= cut must match."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bars.csv"
        df.to_csv(path, index=False)
        full = build(path)
        day = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
        day = day.dt.normalize().values.astype("datetime64[D]")
        rng = np.random.default_rng(seed)
        cuts = np.unique(rng.integers(len(full.dates) // 4, len(full.dates) - 1, n_cuts))
        fails = []
        for i in cuts:
            df[day <= full.dates[i]].to_csv(path, index=False)
            part = build(path)
            for k in ("dates", "prev_close", "atr14", "last", "dow", "o", "h", "l", "c", "v"):
                a, b = getattr(full, k)[: i + 1], getattr(part, k)[: i + 1]
                if a.shape != b.shape or not (np.array_equal(a, b) if k == "dates" else _same(a, b).all()):
                    fails.append((int(i), k))
                    break
    return len(cuts), fails


# ---------------------------------------------------------------- data with no edge by construction
def synthetic(n_days=160, seed=0, start="2024-01-02", price=15000.0):
    """Random-walk 1-minute RTH bars in orb.data.build's CSV format. Nothing here is predictable."""
    rng = np.random.default_rng(seed)
    days = pd.bdate_range(start, periods=n_days, tz="America/New_York")
    minute = np.arange(RTH_BARS)
    shape = 1.5 - np.sin(np.pi * minute / (RTH_BARS - 1))  # busy open and close, quiet lunch
    epoch = pd.Timestamp("1970-01-01", tz="UTC")
    out, p = [], price
    for day in days:
        step = price * 4e-4 * rng.lognormal(0, 0.3)
        p += rng.normal(0, 25 * step)  # overnight gap
        c = p + np.cumsum(rng.normal(0, step, RTH_BARS))
        o = np.r_[p, c[:-1]]
        wick = np.abs(rng.normal(0, step / 2, (2, RTH_BARS)))
        t = day + pd.Timedelta(hours=9, minutes=30) + pd.to_timedelta(minute, unit="min")
        out.append(pd.DataFrame({
            "time": (t - epoch) // pd.Timedelta(seconds=1),
            "open": o, "high": np.maximum(o, c) + wick[0], "low": np.minimum(o, c) - wick[1], "close": c,
            "volume": np.round(1000 * shape * rng.lognormal(0, 0.5, RTH_BARS)),
        }))
        p = c[-1]
    return pd.concat(out, ignore_index=True)
