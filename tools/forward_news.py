"""Forward arm of the Jev news-catalyst test (ADR 0003 addendum, 2026-09-30).

For every Forward Test Session: collect the pre-open headlines (previous Session 16:00 ET .. 09:25 ET) from
TradingView's public news feed (SPX, NDX and NQ1! feeds, merged), ask Jev the two pre-registered questions
(`catalyst`, `aligned`) and log the answers to results/forward_news.csv. Headlines are kept in
results/forward_news/<session>.json so the scores can be reproduced. Nothing here changes a trade.

Called at the end of tools/forward_test.py; can also be run on its own after forward_test.py:
  C:/Users/user/Model/.venv/Scripts/python tools/forward_news.py
"""
import asyncio
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "results" / "forward_news"
LOG = ROOT / "results" / "forward_news.csv"
FEEDS = ("SP:SPX", "NASDAQ:NDX", "CME_MINI:NQ1!")
API = "https://news-mediator.tradingview.com/news-flow/v2/news"
MODEL = "jev-latest"
START = np.datetime64("2026-09-30")


def questions():
    from typesafe_sdk import Noul
    # Word for word from docs/adr/0003-jev-news-catalyst-test.md.
    return {
        "catalyst": Noul(instructions=(
            "Is there major market-moving news in `headlines` that plausibly explains a large overnight move in "
            "US stock index futures?")),
        "aligned": Noul(instructions="Do the news in `headlines` point toward US stocks moving in `gap_direction`?"),
    }


def fetch_feed(symbol, oldest_ts):
    items, cursor = [], None
    for _ in range(20):
        params = [("filter", "lang:en"), ("filter", f"symbol:{symbol}"), ("client", "web"), ("streaming", "false")]
        if cursor:
            params.append(("cursor", cursor))
        r = requests.get(API, params=params, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        j = r.json()
        page = j.get("items", [])
        items += page
        cursor = (j.get("pagination") or {}).get("cursor")
        if not cursor or not page or min(x.get("published", 0) for x in page) < oldest_ts:
            break
        time.sleep(0.5)
    return items


def headlines(sessions, prev):
    """{session: [headline dicts]} for the pre-open window of each Session."""
    ny = "America/New_York"
    win = {s: ((pd.Timestamp(str(prev[s]), tz=ny) + pd.Timedelta(hours=16)).timestamp(),
               (pd.Timestamp(str(s), tz=ny) + pd.Timedelta(hours=9, minutes=25)).timestamp()) for s in sessions}
    oldest = min(a for a, _ in win.values())
    seen = {}
    for f in FEEDS:
        for x in fetch_feed(f, oldest):
            seen.setdefault(x["id"], x)
    out = {}
    for s, (a, b) in win.items():
        hs = sorted((x for x in seen.values() if a <= x.get("published", 0) <= b), key=lambda x: x["published"])
        out[s] = [{"title": x.get("title", ""), "provider": (x.get("provider") or {}).get("name", ""),
                   "published": x["published"]} for x in hs]
    return out


async def ask_all(states):
    from typesafe_sdk import AsyncTypeSafeClient
    q = questions()
    async with AsyncTypeSafeClient(timeout=120.0) as client:
        async def one(st):
            r = await client.system_one(state=st, questions=q, model=MODEL)
            return {k: float(r.nouls[k].noul) for k in q}
        return await asyncio.gather(*(one(s) for s in states))


def update(d):
    """Score every Forward Test Session in `d` (a Days object with the latest bars) not yet in the log."""
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    old = pd.read_csv(LOG) if LOG.exists() else pd.DataFrame(columns=["session"])
    idx = [i for i in range(1, len(d.dates)) if d.dates[i] >= START and str(d.dates[i]) not in set(old.session)]
    if not idx:
        print("Forward news: nothing new")
        return
    sessions = [str(d.dates[i]) for i in idx]
    prev = {str(d.dates[i]): d.dates[i - 1] for i in idx}
    hl = headlines(sessions, prev)
    OUT.mkdir(parents=True, exist_ok=True)
    rows, states = [], []
    for i, s in zip(idx, sessions):
        (OUT / f"{s}.json").write_text(json.dumps(hl[s], indent=0), encoding="utf8")
        gap = d.o[i, 0] - d.prev_close[i]
        gdir = "up" if gap > 0 else "down"
        rows.append(dict(session=s, headlines=len(hl[s]), gap_direction=gdir,
                         gap_atr=round(float(gap / d.atr14[i]), 3)))
        states.append({"headlines": [h["title"] for h in hl[s]] or ["(no headlines)"], "gap_direction": gdir,
                       "gap_size": f"{gap / d.atr14[i]:+.2f} ATR ({(d.o[i, 0] / d.prev_close[i] - 1) * 100:+.2f}%)"})
    ans = asyncio.run(ask_all(states))
    for r, a in zip(rows, ans):
        r.update(catalyst=round(a["catalyst"], 3), aligned=round(a["aligned"], 3),
                 news_pass=bool(a["catalyst"] >= 0.5 and a["aligned"] >= 0.5))
    log = pd.concat([old, pd.DataFrame(rows)]).sort_values("session")
    log.to_csv(LOG, index=False)
    for r in rows:
        print(f"Forward news {r['session']}: {r['headlines']} headlines, gap {r['gap_direction']} {r['gap_atr']:+.2f} ATR, "
              f"catalyst {r['catalyst']:.2f}, aligned {r['aligned']:.2f} -> {'PASS' if r['news_pass'] else 'no'}")


if __name__ == "__main__":
    import tempfile
    sys.path.insert(0, r"C:\Users\user\Model")
    from dotenv import load_dotenv
    from lse import LSE
    from engine.data_lse import download
    from orb.data import build
    load_dotenv(r"C:\Users\user\Model\.env")
    today = pd.Timestamp.now(tz="America/New_York").normalize()
    with tempfile.TemporaryDirectory() as tmp:
        csv = Path(tmp) / "nq_recent.csv"
        try:
            download(LSE(), "NQ.F", "1m", f"{today - pd.Timedelta(days=45):%Y-%m-%d}", f"{today:%Y-%m-%d}", out=csv)
        except ValueError:
            pass
        update(build(csv))
