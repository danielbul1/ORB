"""Pull pre-open market headlines per NQ Session from the GDELT DOC 2.0 API (ADR 0003).

One JSON file per Session in data/news/<date>.json with the article titles seen between the previous
Session's 16:00 ET and 09:25 ET. Resumable: existing files are skipped. GDELT allows ~1 request / 5 s.

Usage: .venv/Scripts/python tools/pull_gdelt.py
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb.grid import load  # noqa: E402

OUT = ROOT / "data" / "news"
QUERY = ('(nasdaq OR "stock market" OR "wall street" OR "stock futures" OR "federal reserve" OR tariffs '
         'OR inflation OR earnings) sourcelang:english')
API = "https://api.gdeltproject.org/api/v2/doc/doc"


def window(prev_day, day):
    ny = "America/New_York"
    a = pd.Timestamp(str(prev_day), tz=ny) + pd.Timedelta(hours=16)
    b = pd.Timestamp(str(day), tz=ny) + pd.Timedelta(hours=9, minutes=25)
    f = "%Y%m%d%H%M%S"
    return a.tz_convert("UTC").strftime(f), b.tz_convert("UTC").strftime(f)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = load()
    days = [x for x in d.dates if x >= np.datetime64("2017-02-20")]
    prev = {d.dates[i]: d.dates[i - 1] for i in range(1, len(d.dates))}
    todo = [x for x in days if not (OUT / f"{x}.json").exists()]
    print(f"{len(todo)} Sessions to fetch", flush=True)
    for n, day in enumerate(todo):
        a, b = window(prev[day], day)
        params = dict(query=QUERY, mode="artlist", format="json", maxrecords=75, sort="hybridrel",
                      startdatetime=a, enddatetime=b)
        for attempt in range(6):
            try:
                r = requests.get(API, params=params, timeout=60)
                if r.status_code == 429 or "limit requests" in r.text[:200].lower():
                    time.sleep(20 * (attempt + 1))
                    continue
                arts = r.json().get("articles", []) if r.text.strip().startswith("{") else []
                break
            except Exception as e:  # network blips
                print(f"  retry {day}: {e}", flush=True)
                time.sleep(10 * (attempt + 1))
        else:
            print(f"  gave up {day}", flush=True)
            continue
        titles = [{"title": x.get("title", ""), "domain": x.get("domain", ""), "seen": x.get("seendate", "")}
                  for x in arts]
        (OUT / f"{day}.json").write_text(json.dumps(titles), encoding="utf8")
        if n % 50 == 0:
            print(f"  {n}/{len(todo)} {day}: {len(titles)} headlines", flush=True)
        time.sleep(5.5)
    print("done", flush=True)


if __name__ == "__main__":
    main()
