"""Monthly review (ADR 0005): compare the Forward Test with what the backtest says is normal.

Reads results/forward_log.csv (written daily by tools/forward_test.py) and reports, for ORB v1 and
Ensemble v3: trades, total R, win rate, current and worst losing streak, drawdown in R, each versus the
historical norms from the NQ 2016-2024 backtest. Prints KILL-SWITCH lines only for the ADR 0005 conditions
it can check from the log (drawdown > 1.5x the historical worst). Fill-quality and trade-matching checks need
the broker's fills (add them to results/live_fills.csv when live trading starts).

Usage: .venv/Scripts/python tools/monthly_review.py
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

HIST = {  # NQ 2016-2024 backtest norms (1 pt cost); see vault/Research/Edge Hunt Log.md
    "ORB v1": dict(col="r", worst_dd=18.2, worst_streak=16, avg_r=0.54, win=0.22, trades_per_month=6.5),
    "Ensemble v3": dict(col="ensemble_v3_r", worst_dd=14.6, worst_streak=18, avg_r=None, win=None,
                        trades_per_month=None),
}


def streaks(x):
    losing = [k for k, _ in itertools.groupby(v < 0 for v in x if v != 0)]
    runs = [len(list(g)) for k, g in itertools.groupby(v < 0 for v in x if v != 0) if k]
    current = 0
    for v in reversed([v for v in x if v != 0]):
        if v < 0:
            current += 1
        else:
            break
    return (max(runs) if runs else 0), current, losing


def main():
    log = ROOT / "results" / "forward_log.csv"
    if not log.exists():
        print("No forward_log.csv yet: the Forward Test has not recorded any Sessions.")
        return
    df = pd.read_csv(log)
    print(f"Forward Test {df.session.min()} .. {df.session.max()}: {len(df)} Sessions\n")
    for name, h in HIST.items():
        x = df[h["col"]].fillna(0).values
        traded = x[x != 0]
        eq = np.cumsum(x)
        dd = float((np.maximum.accumulate(np.r_[0, eq]) - np.r_[0, eq]).max())
        worst, current, _ = streaks(x)
        print(f"== {name}")
        print(f"   trades {len(traded)} | total {x.sum():+.2f}R | win {(traded > 0).mean() if len(traded) else 0:.0%}"
              f" | drawdown {dd:.1f}R (historical worst {h['worst_dd']}R)"
              f" | losing streak now {current}, worst {worst} (historical worst {h['worst_streak']})")
        if dd > 1.5 * h["worst_dd"]:
            print(f"   KILL-SWITCH: drawdown {dd:.1f}R > 1.5x historical worst ({1.5 * h['worst_dd']:.1f}R). Stop and investigate.")
        elif current >= 25:
            print("   NOTE: losing streak >= 25 (ADR 0005 review threshold). Investigate, don't retune.")
        else:
            print("   OK: within historical norms. No changes (ADR 0005).")
    fills = ROOT / "results" / "live_fills.csv"
    print("\nLive fill checks:", "see live_fills.csv" if fills.exists() else "no live fills recorded yet.")


class _Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for s in self.streams:
            s.write(text)

    def flush(self):
        for s in self.streams:
            s.flush()


if __name__ == "__main__":
    out = ROOT / "results" / "monthly_review.txt"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", encoding="utf8") as f:
        sys.stdout = _Tee(sys.__stdout__, f)
        try:
            print(f"Monthly review, generated {pd.Timestamp.now():%Y-%m-%d %H:%M}")
            print()
            main()
        finally:
            sys.stdout = sys.__stdout__
