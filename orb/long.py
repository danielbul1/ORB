"""The 23-year research base: NAS100 index 2003-03 .. 2016-05, then NQ futures 2016-06 .. today.

Era A = 2003-2015 (index), Era B = 2016-2024 (futures), 2025-26 is spent (ADR 0001).
Costs: 0.83 bp of price round trip, at least 0.5 pt, in both eras.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from orb.data import back_adjust, build

ROOT = Path(__file__).resolve().parents[1]
COST = dict(cost_bp=0.83, cost_floor=0.5)
ERA_A = (2003, 2015)
ERA_B = (2016, 2024)


def load():
    cache = ROOT / "data" / "long_adj_rth.npz"
    if cache.exists():
        return build(None, cache)
    nas = pd.read_csv(ROOT / "data" / "nas100_2003_2016_1m.csv")
    nq = back_adjust(pd.read_csv(r"C:\Users\user\Model\data\nq_1m_lse.csv"))
    seam = pd.Timestamp("2016-06-01", tz="UTC").timestamp()
    both = pd.concat([nas[nas.time < seam], nq[nq.time >= seam]]).sort_values("time")
    tmp = ROOT / "data" / "long_1m.csv"
    both.to_csv(tmp, index=False)
    return build(tmp, cache)


def eras(d):
    y = d.dates.astype("datetime64[Y]").astype(int) + 1970
    return {"A 2003-15": (y >= ERA_A[0]) & (y <= ERA_A[1]), "B 2016-24": (y >= ERA_B[0]) & (y <= ERA_B[1]),
            "spent 25-26": y >= 2025}
