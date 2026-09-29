"""Forward Test recorder (ADR 0001): run the frozen ORB v1 on the latest NQ bars and log every Session
from 2026-09-30 on to results/forward_log.csv. Idempotent; run it any time after the close.

Runs with the Model venv (it has the `lse-data` client):
  C:/Users/user/Model/.venv/Scripts/python tools/forward_test.py
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, r"C:\Users\user\Model")
from dotenv import load_dotenv  # noqa: E402
from lse import LSE  # noqa: E402

from engine.data_lse import download  # noqa: E402
from orb.backtest import run  # noqa: E402
from orb.data import build  # noqa: E402
from orb.families import ORB_V1  # noqa: E402

START = np.datetime64("2026-09-30")
LOG = ROOT / "results" / "forward_log.csv"
MNQ_USD = 2.0

load_dotenv(r"C:\Users\user\Model\.env")
today = pd.Timestamp.now(tz="America/New_York").normalize()
with tempfile.TemporaryDirectory() as tmp:
    csv = Path(tmp) / "nq_recent.csv"
    try:
        download(LSE(), "NQ.F", "1m", f"{today - pd.Timedelta(days=45):%Y-%m-%d}", f"{today:%Y-%m-%d}", out=csv)
    except ValueError:
        pass  # Model's downloader prints the path relative to Model/ after writing; the file is already saved
    d = build(csv)

res = run(d, **ORB_V1)
rows = []
for i, day in enumerate(d.dates):
    if day < START or d.last[i] < 389 and day == np.datetime64(today.date()):
        continue  # before the Forward Test, or today's Session is still open
    traded = bool(res["ok"][i])
    rows.append(dict(
        session=str(day), traded=traded,
        direction=int(res["dir"][i]) if traded else 0,
        entry=round(float(res["entry"][i]), 2) if traded else None,
        stop=round(float(res["stop"][i]), 2) if traded else None,
        exit=round(float(res["exit"][i]), 2) if traded else None,
        reason=str(res["reason"][i]) if traded else "",
        r=round(float(res["r"][i]), 3) if traded else 0.0,
        risk_usd_1mnq=round(float(res["risk"][i]) * MNQ_USD, 2) if traded else None,
    ))
new = pd.DataFrame(rows, columns=["session", "traded", "direction", "entry", "stop", "exit", "reason", "r",
                                   "risk_usd_1mnq"])
old = pd.read_csv(LOG) if LOG.exists() else pd.DataFrame(columns=new.columns)
log = pd.concat([old[~old.session.isin(new.session)], new]).sort_values("session")
LOG.parent.mkdir(exist_ok=True)
log.to_csv(LOG, index=False)
t = log[log.traded == True]  # noqa: E712
print(f"Forward Test: {len(log)} Sessions, {len(t)} trades, total {t.r.sum():+.2f}R, "
      f"win {(t.r > 0).mean() if len(t) else 0:.0%}")
