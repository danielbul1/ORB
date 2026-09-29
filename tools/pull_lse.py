"""Pull 1-minute candles from London Strategic Edge into ORB/data/<name>_1m_lse.csv.

Runs with the Model venv (it has the `lse-data` client):
  C:/Users/user/Model/.venv/Scripts/python tools/pull_lse.py "NAS100/USD" index 2003-01-01 2026-09-28 nas100
"""
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\user\Model")
from dotenv import load_dotenv  # noqa: E402
from lse import LSE  # noqa: E402

from engine.data_lse import download  # noqa: E402

load_dotenv(r"C:\Users\user\Model\.env")
symbol, dataset, start, end, name = sys.argv[1:6]
out = Path(__file__).resolve().parents[1] / "data" / f"{name}_1m_lse.csv"
download(LSE(), symbol, "1m", start, end, dataset=dataset, out=out)
print("done", out)
