"""Per-Session context known before the 09:30 open: volatility and dealer-gamma regimes, and Day Types.

External daily data (data/ext): SqueezeMetrics DIX/GEX, CBOE VIX / VIX9D / VVIX, and a Forex Factory
economic calendar (UTC times). Daily values for date D are only used on Sessions after D.
Jev labels each distinct USD calendar event (a text judgment); code turns labels into Day Types.

Usage: python -m orb.regimes     -> labels events with Jev (cached) and prints Day Type counts
"""
import asyncio
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import AsyncTypeSafeClient, Choice, Score

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "data" / "ext"
CACHE = ROOT / "jev_cache"
MODEL = "jev-latest"

EVENT_Q = {
    "category": Choice(
        instructions="Which kind of US economic event is `event`?",
        criteria={
            "inflation": "Consumer or producer prices: CPI, PPI, PCE, import prices, wages growth figures.",
            "jobs": "Labour market: non-farm payrolls, unemployment rate, jobless claims, ADP, JOLTS.",
            "fed": "Federal Reserve policy: rate decision, FOMC statement, minutes, press conference, projections, Fed chair or member speeches and testimony.",
            "growth": "Activity and sentiment: GDP, retail sales, ISM/PMI, durable goods, consumer confidence, housing, industrial production.",
            "other": "Anything else: government speeches, auctions, oil inventories, holidays, trade data, flows.",
        }),
    "market_impact": Score(
        instructions=("How much does the release of `event` typically move US stock index futures (S&P 500 / Nasdaq-100) "
                      "in the minutes and hours after it, in a normal year?"),
        criteria=[
            "Negligible: markets rarely react.",
            "Minor: a small, short-lived move at most.",
            "Moderate: often moves index futures noticeably for a while.",
            "Major: one of the few releases that regularly sets the direction of the whole session (CPI, NFP, FOMC decision/press conference).",
        ]),
}


def _key(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:24]


async def _label(client, sem, name):
    state = {"event": name}
    path = CACHE / f"event_{_key({'s': state, 'q': sorted(EVENT_Q), 'm': MODEL})}.json"
    if path.exists():
        return json.loads(path.read_text())
    async with sem:
        r = await client.system_one(state=state, questions=EVENT_Q, model=MODEL)
    out = {"category": r.choices["category"].choice, "cat_conf": float(r.choices["category"].confidence),
           "impact": float(r.scores["market_impact"].score)}
    CACHE.mkdir(exist_ok=True)
    path.write_text(json.dumps(out))
    return out


def label_events(names):
    load_dotenv(ROOT / ".env")

    async def go():
        sem = asyncio.Semaphore(16)
        async with AsyncTypeSafeClient(timeout=120.0) as client:
            return await asyncio.gather(*(_label(client, sem, n) for n in names))
    return dict(zip(names, asyncio.run(go())))


def calendar():
    """USD events with ET timestamps and Jev labels."""
    ff = pd.read_csv(EXT / "forexfactory_calendar.csv")
    u = ff[(ff.currency == "USD") & ff.time.str.match(r"^\d{1,2}:\d{2}$", na=False)].copy()
    ts = pd.to_datetime(u.date + " " + u.time, format="%a %b %d %Y %H:%M", utc=True).dt.tz_convert("America/New_York")
    u["et"] = ts.dt.tz_localize(None)
    u["day"] = u.et.dt.normalize().values.astype("datetime64[D]")
    u["minute"] = u.et.dt.hour * 60 + u.et.dt.minute
    labels = label_events(sorted(u.event.unique()))
    u["category"] = u.event.map(lambda e: labels[e]["category"])
    u["impact"] = u.event.map(lambda e: labels[e]["impact"])
    return u


def _prior(dates, series_dates, values):
    """Value from the last series date strictly before each Session date."""
    i = np.searchsorted(series_dates, dates, side="left") - 1
    out = np.full(len(dates), np.nan)
    ok = i >= 0
    out[ok] = values[i[ok]]
    return out


def build(d, major=2.5):
    """Context arrays aligned to d.dates. `major`: Jev impact Score threshold (0..3) for a major event."""
    dix = pd.read_csv(EXT / "DIX.csv", parse_dates=["date"])
    vix = pd.read_csv(EXT / "VIX_History.csv", parse_dates=["DATE"])
    v9 = pd.read_csv(EXT / "VIX9D_History.csv", parse_dates=["DATE"])
    vv = pd.read_csv(EXT / "VVIX_History.csv", parse_dates=["DATE"])
    ds = d.dates
    dd = lambda s: s.values.astype("datetime64[D]")
    ctx = {
        "gex": _prior(ds, dd(dix.date), dix.gex.values),
        "dix": _prior(ds, dd(dix.date), dix.dix.values),
        "vix": _prior(ds, dd(vix.DATE), vix.CLOSE.values),
        "vix9d": _prior(ds, dd(v9.DATE), v9.CLOSE.values),
        "vvix": _prior(ds, dd(vv.DATE), vv.iloc[:, 1].values),
    }
    # GEX relative to its own trailing year: robust to the series' growth over time.
    g = pd.Series(ctx["gex"])
    ctx["gex_rank"] = g.rolling(252, min_periods=120).rank(pct=True).values
    ctx["vix_ts"] = ctx["vix9d"] / ctx["vix"]  # > 1 = inverted short-term stress

    cal = calendar()
    big = cal[cal.impact >= major]
    for name, lo, hi in (("pre_open", 0, 9 * 60 + 29), ("morning", 9 * 60 + 30, 11 * 60 + 59),
                         ("afternoon", 12 * 60, 16 * 60)):
        days = set(big[(big.minute >= lo) & (big.minute <= hi)].day.values)
        ctx[f"event_{name}"] = np.isin(ds, list(days))
    for cat in ("inflation", "jobs", "fed"):
        days = set(big[big.category == cat].day.values)
        ctx[f"event_{cat}"] = np.isin(ds, list(days))
    ctx["event_any"] = ctx["event_pre_open"] | ctx["event_morning"] | ctx["event_afternoon"]
    return ctx, cal


if __name__ == "__main__":
    from orb.grid import load
    d = load()
    ctx, cal = build(d)
    lab = cal.drop_duplicates("event")[["event", "category", "impact"]].sort_values("impact", ascending=False)
    print(lab.head(30).to_string(index=False))
    print("...\n", lab.tail(8).to_string(index=False))
    for k, v in ctx.items():
        if v.dtype == bool:
            print(f"{k:18} {v.mean():.1%} of Sessions")
