"""Rebuild the 23-year research base from the LSE vault (no Model venv needed, e.g. in a cloud session).

Needs `pip install "lse-data[frames]" pyarrow` and LSE_API_KEY in the environment. Writes data/nq_1m_lse.csv,
data/nas100_2003_2016_1m.csv, data/long_1m.csv and the cache data/long_adj_rth.npz that orb.long.load() reads.
Vault exports are capped at 2.5M rows, so NQ is pulled in two parts.
Usage: python tools/pull_lse_vault.py [end, default 2026-09-29]
"""
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd
from lse import LSE
from lse.client import LSEError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb.data import back_adjust, build  # noqa: E402

PARTS = {"nq": [("NQ.F", "futures", "2016-05-01", "2023-08-15"), ("NQ.F", "futures", "2023-08-15", None)],
         "nas100": [("NAS100/USD", "index", "2003-01-01", "2016-06-02")]}


def pull(client, parts, end, tmp):
    frames = []
    for i, (sym, ds, start, stop) in enumerate(parts):
        dest = Path(tmp) / f"{ds}{i}"
        dest.mkdir()
        for attempt in range(4):  # the vault allows only a few export jobs at a time (HTTP 429)
            try:
                path = client.history(sym, dataset=ds, timeframe="1m", start=start, end=stop or end,
                                      dest=str(dest), dataframe=False, timeout=3000)
                break
            except LSEError as e:
                if e.status != 429 or attempt == 3:
                    raise
                time.sleep(60 * (attempt + 1))
        df = pd.read_parquet(path)
        df["time"] = (df.ts - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)
        frames.append(df[["time", "open", "high", "low", "close", "volume"]])
    return pd.concat(frames).drop_duplicates("time").sort_values("time").reset_index(drop=True)


def main():
    end = sys.argv[1] if len(sys.argv) > 1 else "2026-09-29"
    client = LSE()
    data = ROOT / "data"
    with tempfile.TemporaryDirectory() as tmp:
        nq = pull(client, PARTS["nq"], end, tmp)
        nas = pull(client, PARTS["nas100"], end, tmp)
    nq.to_csv(data / "nq_1m_lse.csv", index=False)
    nas.to_csv(data / "nas100_2003_2016_1m.csv", index=False)
    seam = pd.Timestamp("2016-06-01", tz="UTC").timestamp()
    both = pd.concat([nas[nas.time < seam], back_adjust(nq).query("time >= @seam")]).sort_values("time")
    both.to_csv(data / "long_1m.csv", index=False)
    cache = data / "long_adj_rth.npz"
    cache.unlink(missing_ok=True)
    d = build(data / "long_1m.csv", cache)
    print(f"NQ {len(nq)} rows, NAS100 {len(nas)} rows, {len(d.dates)} Sessions {d.dates[0]} .. {d.dates[-1]}")


if __name__ == "__main__":
    main()
