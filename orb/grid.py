"""Grid search with a fixed time split.

  Train     2016-06 .. 2021-12   parameters are chosen here only
  Validate  2022-01 .. 2024-12   must still hold up
  Holdout   2025-01 .. today     looked at once, for the final pick

Usage: python -m orb.grid core|filters [out.csv]
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from orb.backtest import metrics, run
from orb.data import build

ROOT = Path(__file__).resolve().parents[1]
CSV = Path(r"C:\Users\user\Model\data\nq_1m_lse.csv")
SPLITS = {"train": ("2016-01-01", "2021-12-31"), "val": ("2022-01-01", "2024-12-31"),
          "hold": ("2025-01-01", "2099-01-01")}


def load(csv=CSV, name="nq"):
    """Futures Sessions, back-adjusted at contract rolls (orb.data.back_adjust)."""
    return build(csv, ROOT / "data" / f"{name}_adj_rth.npz", adjust=True)


def masks(d):
    return {k: (d.dates >= np.datetime64(a)) & (d.dates <= np.datetime64(b)) for k, (a, b) in SPLITS.items()}


def evaluate(d, ms, params, splits=("train", "val")):
    res = run(d, **params)
    row = dict(params)
    for s in splits:
        for k, v in metrics(d, res, ms[s]).items():
            row[f"{s}_{k}"] = v
    return row


def product(space):
    keys = list(space)
    for vals in itertools.product(*space.values()):
        yield dict(zip(keys, vals))


CORE = dict(
    or_min=[1, 5, 10, 15, 30, 60],
    entry=["stop", "close", "candle"],
    stop=["or", "mid", ("atr", 0.05), ("atr", 0.1), ("atr", 0.15), ("atr", 0.25)],
    target_r=[None, 1, 2, 3, 5, 10],
    cutoff=[60, 120, 240],
)


BASES = {  # picked from the core grid on train Sharpe, one per family
    "A_candle5": dict(or_min=5, entry="candle", stop="atr", stop_x=0.1, target_r=10),
    "B_stop1": dict(or_min=1, entry="stop", stop="or", cutoff=120),
    "C_stop15mid": dict(or_min=15, entry="stop", stop="mid", target_r=5, cutoff=120),
    "D_stop30atr25": dict(or_min=30, entry="stop", stop="atr", stop_x=0.25, cutoff=120),
    "E_stop30atr15": dict(or_min=30, entry="stop", stop="atr", stop_x=0.15, target_r=10, cutoff=120),
}

FILTERS = dict(
    side=["both", "long"],
    rvol_min=[0, 1.0, 1.25],
    min_or_atr=[0, 0.1, 0.2],
    max_or_atr=[0.3, 0.5, 9.0],
    gap_dir=[None, "with", "against"],
    be_r=[None, 1, 2],
)


def expand(p):
    p = dict(p)
    if isinstance(p.get("stop"), tuple):
        p["stop"], p["stop_x"] = p["stop"]
    return p


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "core"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results" / f"grid_{stage}.csv"
    d = load()
    ms = masks(d)
    rows = []
    if stage == "core":
        for p in product(CORE):
            if p["entry"] == "candle" and p["cutoff"] != 60:
                continue  # candle entry is at end of OR; cutoff is irrelevant
            rows.append(evaluate(d, ms, expand(p)))
    elif stage == "filters":
        for name, base in BASES.items():
            for f in product(FILTERS):
                rows.append({"base": name, **evaluate(d, ms, {**base, **f})})
    else:
        raise SystemExit(f"unknown stage {stage}")
    df = pd.DataFrame(rows)
    out.parent.mkdir(exist_ok=True)
    df.to_csv(out, index=False)
    print(f"{len(df)} runs -> {out}")


if __name__ == "__main__":
    main()
