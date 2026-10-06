"""Pull free Dukascopy 1-minute Nasdaq-100 CFD bars (USATECHIDXUSD, bid) into ORB/data/<name>_1m_duka.csv.

A free public stand-in for the LSE feed when it isn't available (e.g. a cloud session). One LZMA file per UTC
day; only 13:00-21:30 UTC is kept, which covers the 09:30-16:00 ET Session in both summer and winter time.
Usage: python tools/pull_duka.py 2012-01-01 2026-10-05 nas100 [raw_dir]
"""
import datetime as dt
import lzma
import struct
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

URL = "https://datafeed.dukascopy.com/datafeed/USATECHIDXUSD/{y}/{m:02d}/{d:02d}/BID_candles_min_1.bi5"
ROOT = Path(__file__).resolve().parents[1]


def valid(f):
    return f.exists() and (f.stat().st_size == 0 or f.read_bytes()[:1] == b"\x5d")  # LZMA header; empty = no data


def fetch(day, raw):
    """Sequential and polite: the feed answers 429 to bursts, so back off and retry."""
    f = raw / f"{day.isoformat()}.bi5"
    wait = 2.0
    while not valid(f):
        try:
            with urllib.request.urlopen(URL.format(y=day.year, m=day.month - 1, d=day.day), timeout=60) as r:
                f.write_bytes(r.read())
            time.sleep(0.3)
        except urllib.error.HTTPError as e:
            if e.code == 404:  # holidays and gaps are simply missing
                f.write_bytes(b"")
            else:
                time.sleep(wait)
                wait = min(wait * 2, 60)
        except Exception as e:
            print("retry", day, e)
            time.sleep(wait)
    return f


def bars(day, f):
    if not f.exists() or f.stat().st_size == 0:
        return []
    b = lzma.decompress(f.read_bytes())
    t0 = int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp())
    out = []
    for i in range(len(b) // 24):
        s, o, c, lo, hi, v = struct.unpack(">5if", b[i * 24:(i + 1) * 24])
        if 13 * 3600 <= s <= 21 * 3600 + 1800 and v > 0:
            out.append((t0 + s, o / 1000, hi / 1000, lo / 1000, c / 1000, v))
    return out


def main(start, end, name, raw=None):
    raw = Path(raw) if raw else ROOT / "data" / "duka_raw"
    raw.mkdir(parents=True, exist_ok=True)
    d0, d1 = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    days = [d0 + dt.timedelta(i) for i in range((d1 - d0).days + 1)]
    days = [d for d in days if d.weekday() < 5]
    files = [fetch(d, raw) for d in days]
    rows = [r for d, f in zip(days, files) for r in bars(d, f)]
    out = ROOT / "data" / f"{name}_1m_duka.csv"
    pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"]).to_csv(out, index=False)
    print("done", out, len(rows), "bars")


if __name__ == "__main__":
    main(*sys.argv[1:])
