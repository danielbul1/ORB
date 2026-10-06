"""The ADR 0008 engine additions must not change any existing Rule Set: compare against the pre-change engine."""
import importlib.util
import itertools
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb import backtest as new  # noqa: E402
from orb.families import ENSEMBLE_MEMBERS, ENSEMBLE_V3, ORB_V1  # noqa: E402
from tests.synth import make  # noqa: E402


def load_old(path):
    spec = importlib.util.spec_from_file_location("backtest_old", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cases():
    yield ORB_V1
    for om in ENSEMBLE_MEMBERS:
        yield {**ENSEMBLE_V3, "or_min": om}
    grid = dict(entry=["stop", "close", "retest", "candle", "stretch"], stop=["or", "mid", "atr"],
                target_r=[None, 2], be_r=[None, 1], trail_x=[0.0, 0.3])
    for vals in itertools.product(*grid.values()):
        yield dict(zip(grid, vals), or_min=5 if vals[0] == "candle" else 15, gap_dir="with", vwap_side=True)
    yield dict(entry="close", rvol_min=1.2, min_or_atr=0.1, max_or_atr=0.5, nr=7, cost_bp=0.83, cost_floor=0.5)


def check(old_path):
    old = load_old(old_path)
    n = 0
    for seed in (0, 1):
        d_new, d_old = make(seed=seed), make(seed=seed)
        for p in cases():
            a, b = new.run(d_new, **p), old.run(d_old, **p)
            for key in b:
                assert np.array_equal(a[key], b[key], equal_nan=a[key].dtype.kind == "f"), (p, key)
            n += 1
    return n


if __name__ == "__main__":
    # Usage: python tests/test_backtest_regression.py [git rev of the reference engine, default 302d569]
    import subprocess
    import tempfile
    rev = sys.argv[1] if len(sys.argv) > 1 else "302d569"
    src = subprocess.run(["git", "show", f"{rev}:orb/backtest.py"], cwd=ROOT, capture_output=True, text=True, check=True)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(src.stdout)
    print("identical to", rev, "on", check(f.name), "cases")
