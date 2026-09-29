"""Backtest the open-source TradingView ORB strategies (NY session) on our NQ data with their default rules.

Rules come from Jev's profile (research/orb_script_profiles.csv) and Jev-selected input defaults
(research/orb_strategy_params.csv). Approximations, applied the same way to every script:
  * all scripts are evaluated on 1-minute NQ bars; "close" entries use 1-minute closes;
  * chart-timeframe ATR stops (e.g. 2 x ATR(14) on 5m) are converted to daily-ATR units (5m ATR ~ 0.08 daily ATR);
  * fixed-point stops/targets are scaled to price (points / 20,000, the NQ level they were written for);
  * "breakout candle" stops are approximated by the OR midpoint; MA filters by EMA(200) of 1m closes;
    volume filters by the OR relative-volume filter (>= 1.0); VWAP filters by session-VWAP side;
  * no stop -> a wide 1.0 x daily-ATR catastrophe stop.
Scripts with trailing / pullback logic we can't express are skipped.

Usage: python research/community_strategies.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb import long as L  # noqa: E402
from orb.backtest import run  # noqa: E402
from orb.families import ORB_V1  # noqa: E402
from orb.grid import load  # noqa: E402
from orb.judge import stats, years_of  # noqa: E402

PT = 1 / 20_000  # one NQ point as a fraction of price at the level the scripts were designed for
C = dict(entry="close", cutoff=120)

STRATEGIES = {
    "ORB Heikin Ashi SPY 5min Correlation (exlux, 2357 likes)":
        dict(C, or_min=30, stop="atr", stop_x=1.0, target_r=None, cutoff=150, exit_min=380, rvol_min=1.0),
    "ORB Strategy [LuciTech] (1251)": dict(C, or_min=15, stop="atr", stop_x=0.16, target_r=2),
    "ORB Pro | Session Breakout Scalper (526)":
        dict(C, or_min=15, stop="or", target_r=1.5, cutoff=389, vwap_side=True, rvol_min=1.0),
    "Drop's ORB (441)": dict(C, or_min=15, stop="mid", target_r=1, exit_min=120),
    "Script_Algo ORB with Filters (412)": dict(C, or_min=5, stop="or", target_r=3, cutoff=60, ema_n=200, rvol_min=1.0),
    "ORB + Key Session Levels +SL (381)": dict(C, or_min=15, stop="mid", target_r=1),
    "Big Daddy Max ORB (273)": dict(C, or_min=15, stop="mid", target_r=1, cutoff=389),
    "ORB Breakout Strategy (chartsquare, 215)": dict(C, or_min=15, stop="mid", target_r=2, cutoff=150, exit_min=380),
    "NY15m ORB fixed SL&TP Nasdaq (195)": dict(C, or_min=15, stop="atr", stop_x=0.16, target_r=2),
    "NY ORB - MA Stop (156)": dict(C, or_min=15, stop="or", target_r=2.5, cutoff=150, ema_n=200),
    "15-Min ORB for NQ (129)": dict(C, or_min=15, stop="or", target_r=1),
    "ORB + VWAP and Volume Filters (123)": dict(C, entry="stop", or_min=15, stop="mid", target_r=1, vwap_side=True, rvol_min=1.0),
    "Initial Balance Breakout (Bnf6082, 47)":
        dict(C, entry="retest", or_min=60, stop="pct", stop_x=60 * PT, target_r=None, target_or=0.5, cutoff=210, exit_min=330),
    "ORB MEEEEEKS (46)": dict(C, entry="retest", or_min=15, stop="atr", stop_x=0.08, target_r=1, cutoff=389, vwap_side=True),
    "ORB AVWAP Retest (43)": dict(C, entry="retest", or_min=15, stop="or", target_r=1, cutoff=389, vwap_side=True),
    "Initial Balance Breakout [samjNQ] v3 (42)":
        dict(C, or_min=60, stop="or", target_r=None, target_or=1.0, cutoff=300, vwap_side=True),
    "NASDAQ ORB Strict Exec RRR 2.0 (30)": dict(C, or_min=15, stop="mid", target_r=2, rvol_min=1.0),
    "MNQ 15m NY Open ORB (30)": dict(C, or_min=15, stop="pct", stop_x=50 * PT, target_r=None, target_pct=50 * PT),
    "MNQ ORB - VWAP + Bias (25)":
        dict(C, entry="stop", or_min=10, stop="pct", stop_x=60 * PT, target_r=None, target_pct=120 * PT, cutoff=90, vwap_side=True),
    "OURS: ORB v1 (5m, gap, VWAP, 0.1 ATR, 10R)": dict(ORB_V1),
}


def main():
    nq = load()
    yn = years_of(nq)
    lg = L.load()
    E = L.eras(lg)
    rows = []
    for name, p in STRATEGIES.items():
        r = run(nq, **{**p, "cost": 1.0})
        x = np.where(r["ok"], r["r"], 0.0)
        rl = run(lg, **{**p, **L.COST})
        xl = np.where(rl["ok"], rl["r"], 0.0)
        a, b, h = stats(x[yn <= 2024]), stats(x[yn >= 2025]), stats(xl[E["A 2003-15"]])
        rows.append({"strategy": name, "trades/yr": round(a["trades"] / 8.6), "win%": round(a["win"] * 100),
                     "avgR": round(float(x[yn <= 2024][x[yn <= 2024] != 0].mean()), 3),
                     "Sharpe 16-24": a["sharpe"], "Score 16-24": a["score"], "Sharpe 25-26": b["sharpe"],
                     "Sharpe 03-15": h["sharpe"], "worst streak": a["streak"]})
    df = pd.DataFrame(rows).sort_values("Sharpe 16-24", ascending=False)
    pd.set_option("display.width", 250)
    print(df.to_string(index=False))
    df.to_csv(ROOT / "research" / "community_strategies_backtest.csv", index=False)


if __name__ == "__main__":
    main()
