"""Parity check: NinjaTrader 8 ORBEnsembleV3 trades vs the Python engine (Ensemble v3), Leg by Leg.

1. In NinjaTrader: Strategy Analyzer, ORBEnsembleV3 on MNQ (or NQ) 5-minute, ETH or RTH, the last ~30 days.
   Trades tab -> right-click -> Export -> CSV.
2. python tools/nt_parity.py <nt_trades.csv> [--tz America/New_York] [--bars <1m csv>]
   --tz: the time zone NinjaTrader shows (Tools > Options > General). --bars: a 1-minute csv with time,open,
   high,low,close,volume (unix seconds); default downloads recent NQ bars like tools/forward_test.py.

Parity (CONTEXT.md) = same Sessions, same Legs, same direction, entry within 1 tick. Exits are reported but may
differ: NinjaTrader flattens at 15:55 and checks stops on 5-minute bars, the engine at 15:59 on 1-minute bars.
"""
import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb.backtest import TICK, run  # noqa: E402
from orb.data import build  # noqa: E402
from orb.families import ENSEMBLE_MEMBERS, ENSEMBLE_V3  # noqa: E402


def nt_trades(path, tz):
    t = pd.read_csv(path)
    t.columns = [c.strip() for c in t.columns]
    et = pd.to_datetime(t["Entry time"]).dt.tz_localize(tz).dt.tz_convert("America/New_York")
    return pd.DataFrame(dict(
        session=et.dt.date.astype(str),
        leg=t["Entry name"].str.extract(r"E(\d+)")[0].astype(int),
        dir=np.where(t["Market pos."].str.startswith("Long"), 1, -1),
        entry=t["Entry price"].astype(float), exit=t["Exit price"].astype(float),
        exit_name=t["Exit name"].astype(str)))


def py_trades(bars_csv):
    d = build(bars_csv)
    rows = []
    for om in ENSEMBLE_MEMBERS:
        r = run(d, **{**ENSEMBLE_V3, "or_min": om})
        for i in np.flatnonzero(r["ok"]):
            rows.append(dict(session=str(d.dates[i]), leg=om, dir=int(r["dir"][i]), entry=float(r["entry"][i]),
                             exit=float(r["exit"][i]), reason=str(r["reason"][i])))
    return pd.DataFrame(rows), d


def recent_bars(tmp):
    sys.path.insert(0, r"C:\Users\user\Model")
    from dotenv import load_dotenv
    from lse import LSE
    from engine.data_lse import download
    load_dotenv(r"C:\Users\user\Model\.env")
    today = pd.Timestamp.now(tz="America/New_York").normalize()
    csv = Path(tmp) / "nq_recent.csv"
    try:
        download(LSE(), "NQ.F", "1m", f"{today - pd.Timedelta(days=60):%Y-%m-%d}", f"{today:%Y-%m-%d}", out=csv)
    except ValueError:
        pass
    return csv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nt_csv")
    ap.add_argument("--tz", default="America/New_York")
    ap.add_argument("--bars")
    a = ap.parse_args()
    nt = nt_trades(a.nt_csv, a.tz)
    with tempfile.TemporaryDirectory() as tmp:
        py, d = py_trades(a.bars or recent_bars(tmp))
    # compare only Sessions both sides cover (the engine needs 20 days of warm-up for tau)
    lo, hi = max(nt.session.min(), str(d.dates[25])), min(nt.session.max(), str(d.dates[-1]))
    nt = nt[(nt.session >= lo) & (nt.session <= hi)]
    py = py[(py.session >= lo) & (py.session <= hi)]
    m = py.merge(nt, on=["session", "leg"], how="outer", suffixes=("_py", "_nt"), indicator=True)
    both = m[m._merge == "both"]
    same_dir = (both.dir_py == both.dir_nt)
    ticks = ((both.entry_py - both.entry_nt).abs() / TICK).round()
    print(f"Sessions {lo} .. {hi}: engine {len(py)} Leg trades, NinjaTrader {len(nt)}")
    print(f"  matched {len(both)} | engine only {int((m._merge == 'left_only').sum())} | "
          f"NinjaTrader only {int((m._merge == 'right_only').sum())}")
    print(f"  same direction {int(same_dir.sum())}/{len(both)} | entry within 1 tick {int((ticks <= 1).sum())}/{len(both)}")
    bad = m[(m._merge != "both") | ~(m.dir_py == m.dir_nt) | (((m.entry_py - m.entry_nt).abs() / TICK) > 1)]
    if len(bad):
        print("\nMismatches:")
        print(bad[["session", "leg", "dir_py", "dir_nt", "entry_py", "entry_nt", "reason", "exit_name", "_merge"]]
              .to_string(index=False))
    ex = ((both.exit_py - both.exit_nt).abs() / TICK)
    print(f"\nExit difference (ticks): median {ex.median():.0f}, max {ex.max():.0f} (information only)")
    ok = len(bad) == 0 and len(both) > 0
    print("PARITY:", "YES" if ok else "NO")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
