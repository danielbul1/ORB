"""Look-ahead check of the signals and Rule Sets the research uses (orb/lookahead.py).

Checks the 13 indicators of research/indicator_nq_test.py (5-minute bars), ORB v1, the four Ensemble v3 Legs,
every entry type and Filter of orb.backtest.run, and orb.data.build's per-Session context. Two planted
look-aheads must fail, or the checker itself is broken (exit code 1):
  * "pivot arrows drawn on the pivot bar": buy every swing low, sell every swing high, drawn where the swing is
    rather than where it becomes known (5 bars later). This is how a "Too easy" screenshot is made.
  * ORB v1 trading in the direction of the Session's own close.

The demo at the end runs the pivot arrows on the same random walk both ways: drawn on the pivot vs. traded when
known. A random walk has no edge, so any profit in the first is the look-ahead alone.

Default data is a synthetic random walk, so this runs anywhere. --real checks the last --days Sessions of the
23-year base (orb/long.py), which needs the data on this machine.

Usage: python research/lookahead_check.py [--real] [--days 400]  -> research/lookahead_check.csv
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from indicator_nq_test import INDICATORS, bars, hold, pivots  # noqa: E402

from orb.backtest import run  # noqa: E402
from orb.data import build  # noqa: E402
from orb.families import ENSEMBLE_MEMBERS, ENSEMBLE_V3, ORB_V1  # noqa: E402
from orb.lookahead import check_build, check_rule_set, check_signal, synthetic  # noqa: E402

OUT = ROOT / "research" / "lookahead_check.csv"
COST = dict(cost_bp=0.83, cost_floor=0.5)  # orb/long.py


def pivot_arrows(n=5, drawn_on_pivot=True):
    def fn(o, h, l, c, v, nd):
        hi, lo = pivots(h, n, n, True), pivots(l, n, n, False)  # known n bars after the swing
        if drawn_on_pivot:
            hi, lo = np.r_[hi[n:], np.full(n, np.nan)], np.r_[lo[n:], np.full(n, np.nan)]
        return hold(np.isfinite(lo), np.isfinite(hi), None, None, nd)
    return fn


SIGNALS = dict(INDICATORS, **{
    "Pivot arrows when known (5 bars late)": pivot_arrows(drawn_on_pivot=False),
    "PLANTED: pivot arrows drawn on the pivot bar": pivot_arrows(drawn_on_pivot=True),
})

# Every entry type and every Filter / exit option of orb.backtest.run at least once.
RUN_OPTIONS = {
    "entry=stop, OR stop, 2R": dict(entry="stop", target_r=2),
    "entry=close, mid stop, BE 1R": dict(entry="close", stop="mid", be_r=1.0),
    "entry=retest, OR-width target": dict(entry="retest", target_or=1.0),
    "entry=stretch, pct target": dict(entry="stretch", target_pct=0.003),
    "entry=candle, rvol/gap/NR4/dow": dict(entry="candle", rvol_min=0.8, gap_min=0.1, gap_dir="against", nr=4,
                                           dows=(0, 1, 2, 3), stop="atr", stop_x=0.2),
    "entry=stop, htf/rsi/pdhl/vol regime": dict(entry="stop", htf_side=True, rsi_block=70, pdhl_block=0.5,
                                                vol_regime=0.5, min_or_atr=0.05),
}


def rule_sets():
    out = {"ORB v1": lambda d: run(d, **ORB_V1, **COST)}
    for om in ENSEMBLE_MEMBERS:
        out[f"Ensemble v3 Leg {om}m"] = lambda d, om=om: run(d, **{**ENSEMBLE_V3, "or_min": om, **COST})
    for name, p in RUN_OPTIONS.items():
        out[f"run(): {name}"] = lambda d, p=p: run(d, **{**p, **COST})
    out["PLANTED: ORB v1 in the direction of the Session close"] = lambda d: run(
        d, **ORB_V1, **COST, dir_override=np.sign(d.c[np.arange(len(d.dates)), d.last] - d.o[:, 0]))
    out["PLANTED: ORB v1, entry bar must close in the trade's favour"] = entry_bar_peek
    return out


def entry_bar_peek(d):
    """ORB v1 fills at the open of bar e but keeps only trades whose bar e closes in their favour: one bar early."""
    res = dict(run(d, **ORB_V1, **COST))
    rows, e = np.arange(len(d.dates)), np.minimum(res["e"], d.c.shape[1] - 1)
    res["ok"] = res["ok"] & (res["dir"] * (d.c[rows, e] - d.o[rows, e]) > 0)
    return res


def demo(o, h, l, c, v, nd):
    """Gross points per Session of the pivot arrows on the random walk, drawn on the pivot vs. when known."""
    last = np.r_[nd[1:], True]
    rows = []
    for name, fn in (("drawn on the pivot bar", pivot_arrows(drawn_on_pivot=True)),
                     ("traded when known", pivot_arrows(drawn_on_pivot=False))):
        p = fn(o, h, l, c, v, nd)
        p[last] = 0
        pts = p * np.r_[c[1:] - c[:-1], 0]
        day = np.cumsum(nd) - 1
        per_day = np.bincount(day, pts)
        turns = np.abs(np.diff(np.r_[0, p])).sum() / 2 / (day[-1] + 1)
        rows.append((name, per_day.mean(), per_day.mean() / per_day.std() * np.sqrt(252), turns))
    return rows


def main(real, days):
    if real:
        from orb.long import load
        d = load()
        d = d.slice(np.arange(len(d.dates)) >= len(d.dates) - days)
        df = None
        print(f"data: last {len(d.dates)} Sessions of the 23-year base")
    else:
        df = synthetic()
        d = build_from(df)
        print(f"data: synthetic random walk, {len(d.dates)} Sessions")

    rows = []
    def report(kind, name, n, fails, first):
        planted = name.startswith("PLANTED")
        verdict = ("caught" if fails else "MISSED") if planted else ("LOOK-AHEAD" if fails else "pass")
        rows.append(dict(kind=kind, name=name, cuts=n, fails=len(fails), verdict=verdict,
                         first_fail=first(fails[0]) if fails else ""))
        print(f"  {verdict:10s} {name:62s} {len(fails):3d}/{n} cuts")

    print("signals (5-minute bars, cut after bar t):")
    o, h, l, c, v, day = bars(d, 5)
    nd = np.r_[True, day[1:] != day[:-1]]
    for name, fn in SIGNALS.items():
        n, fails = check_signal(fn, o, h, l, c, v, nd)
        report("signal", name, n, fails, lambda f: f"bar {f[0]}: live {f[1]:+g}, backtest {f[2]:+g}")

    print("Rule Sets (cut at Session i, bar j):")
    for name, fn in rule_sets().items():
        n, fails = check_rule_set(fn, d)
        report("rule_set", name, n, fails, lambda f: f"Session {f[0]} bar {f[1]} drift {f[2]:+}: {f[3]}")

    if df is not None:
        print("data.build per-Session context (cut after Session i):")
        n, fails = check_build(df)
        report("data", "orb.data.build", n, fails, lambda f: f"Session {f[0]}: {f[1]}")

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("->", OUT)

    print("\nPivot arrows on the same bars (gross, no costs):")
    for name, pts, sharpe, turns in demo(o, h, l, c, v, nd):
        print(f"  {name:24s} {pts:+8.1f} pts/Session   Sharpe {sharpe:+6.2f}   {turns:4.1f} trades/Session")

    bad = [r for r in rows if r["verdict"] in ("LOOK-AHEAD", "MISSED")]
    return 1 if bad else 0


def build_from(df):
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bars.csv"
        df.to_csv(path, index=False)
        return build(path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--days", type=int, default=400)
    a = ap.parse_args()
    with np.errstate(divide="ignore", invalid="ignore"):  # flat stretches divide by zero inside the indicators
        sys.exit(main(a.real, a.days))
