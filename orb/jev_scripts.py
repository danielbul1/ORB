"""Jev reads every open-source TradingView ORB script and returns its trading rules as typed answers.

Code fetches, cleans, and aggregates; Jev only judges what each script's code does.
Answers are cached per (source hash, questions, model), so reruns are free.

Usage: python -m orb.jev_scripts            -> research/orb_script_profiles.csv
"""
import asyncio
import hashlib
import json
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "research" / "community_orb.json"
CACHE = ROOT / "jev_cache"
OUT = ROOT / "research" / "orb_script_profiles.csv"
MODEL = "jev-latest"
MAX_CHARS = 60_000  # keeps state well under Jev's 32k-token limit
DRAWING = re.compile(r"\b(line\.|label\.|box\.|table\.|plotshape|plotchar|plot\(|fill\(|bgcolor|barcolor|color\.new|hline|linefill\.)")


def clean(src):
    """Drop comments, blank lines and pure drawing code; the trading logic stays."""
    keep = []
    for ln in src.splitlines():
        s = ln.split("//")[0].rstrip() if not ln.lstrip().startswith("//@version") else ln
        if not s.strip() or DRAWING.search(s) and "strategy." not in s:
            continue
        keep.append(s)
    text = "\n".join(keep)
    return text[:MAX_CHARS]


Q = {
    "kind": Choice(
        instructions="What does the Pine Script in `code` actually do with the opening range?",
        criteria={
            "strategy": "A backtestable strategy: it places orders with strategy.entry / strategy.order and exits.",
            "signals": "An indicator that marks buy/sell breakout signals or alerts, without placing orders.",
            "levels": "An indicator that only draws the range and/or target levels, with no entry signal logic.",
            "other": "Something else, or the opening range is not the core of the script.",
        }),
    "or_length": Choice(
        instructions="How long is the opening range the script builds by default (from its default input values)?",
        criteria={
            "1m": "The first 1 minute, or first bar of a 1-minute chart.",
            "5m": "The first 5 minutes.",
            "15m": "The first 15 minutes.",
            "30m": "The first 30 minutes.",
            "60m": "The first 60 minutes (initial balance).",
            "first_bar": "The first bar of the chart's own timeframe, whatever it is.",
            "other": "Another length, or several ranges at once.",
        }),
    "session": Choice(
        instructions="Which session open does the opening range start at by default?",
        criteria={
            "ny_0930": "New York cash open, 09:30 America/New_York (or the exchange's regular session start for US stocks/index futures).",
            "futures_other": "Another futures time such as 08:30 Chicago, 18:00 Globex or midnight New York.",
            "london_asia": "London, Frankfurt or Asia session open.",
            "india": "Indian market open (09:15 IST).",
            "configurable_other": "Something else.",
        }),
    "entry": Choice(
        instructions="By default, what triggers a trade or signal after the range is formed?",
        criteria={
            "touch": "Price trades through the range high/low intrabar (a wick is enough, e.g. stop order or high > rangeHigh).",
            "close": "A candle closes beyond the range high/low.",
            "retest": "Price breaks out, then comes back to retest the range edge (or a level) before entering.",
            "first_candle_direction": "Enter in the direction of the first/opening candle at its close, no breakout needed.",
            "pullback_other": "Some other trigger: pullback to VWAP/EMA/fib, reversal/fade of the breakout, pattern, etc.",
            "none": "No entry trigger; the script only shows levels.",
        }),
    "stop": Choice(
        instructions="By default, where is the stop loss placed?",
        criteria={
            "opposite_side": "At the other side of the opening range.",
            "midpoint": "At the middle of the opening range.",
            "atr": "A multiple of ATR from entry, or an ATR trailing stop.",
            "fixed": "A fixed number of points, ticks, dollars or percent.",
            "candle_or_swing": "Beyond the breakout candle, a recent swing or pivot.",
            "none": "No stop loss is defined.",
        }),
    "target": Choice(
        instructions="By default, how is profit taken?",
        criteria={
            "r_multiple": "A fixed risk:reward multiple of the stop distance.",
            "range_multiple": "Multiples or extensions of the opening range width, including fibonacci extensions of the range.",
            "atr_or_fixed": "An ATR multiple, or a fixed points/percent target.",
            "trailing": "A trailing stop with no fixed target.",
            "session_end": "Held until the end of the session or a time exit.",
            "none": "No target or exit logic.",
        }),
    "f_vwap": Noul(instructions="Does the script require price to be on the trade's side of VWAP (or use VWAP as a filter/confirmation) before a breakout counts?"),
    "f_ma_trend": Noul(instructions="Does the script filter breakouts with a moving average trend (EMA/SMA/supertrend) on the chart timeframe?"),
    "f_htf_trend": Noul(instructions="Does the script filter breakouts with a higher-timeframe trend or bias (request.security of a higher timeframe, daily bias, etc.)?"),
    "f_volume": Noul(instructions="Does the script require above-average or relative volume on the breakout?"),
    "f_range_size": Noul(instructions="Does the script skip days when the opening range is too small or too large (versus ATR, points or percent)?"),
    "f_rsi_momentum": Noul(instructions="Does the script use RSI, MACD, ADX or another momentum oscillator as a breakout filter?"),
    "f_prior_levels": Noul(instructions="Does the script use previous day high/low/close, pre-market or overnight levels as filters or targets?"),
    "f_gap": Noul(instructions="Does the script use the opening gap (open versus prior close) in its logic?"),
    "f_time_window": Noul(instructions="Does the script stop taking new breakouts after a cutoff time (a limited entry window)?"),
    "x_breakeven": Noul(instructions="Does the script move the stop to breakeven or trail it after price moves in favour?"),
    "x_partial": Noul(instructions="Does the script scale out with multiple targets or partial exits?"),
    "x_second_trade": Noul(instructions="Does the script allow a second trade or re-entry on the same day (e.g. after a stop out, or in the opposite direction)?"),
    "x_eod_exit": Noul(instructions="Does the script close open trades at a fixed end-of-day or session-end time?"),
}


def key(state):
    blob = json.dumps({"s": state, "q": sorted(Q), "m": MODEL}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:24]


async def ask(client, sem, item):
    state = {"script_name": item["name"], "author": item["author"], "code": clean(item["source"])}
    path = CACHE / f"script_{key(state)}.json"
    if path.exists():
        return json.loads(path.read_text())
    async with sem:
        r = await client.system_one(state=state, questions=Q, model=MODEL)
    out = {k: {"choice": a.choice, "conf": a.confidence, "probs": dict(a.probabilities)} for k, a in r.choices.items()}
    out.update({k: {"p": float(a.noul)} for k, a in r.nouls.items()})
    CACHE.mkdir(exist_ok=True)
    path.write_text(json.dumps(out))
    return out


async def main():
    load_dotenv(ROOT / ".env")
    items = [x for x in json.loads(SRC.read_text(encoding="utf8"))["items"] if x["source"]]
    sem = asyncio.Semaphore(8)
    async with AsyncTypeSafeClient(timeout=120.0) as client:
        answers = await asyncio.gather(*(ask(client, sem, it) for it in items), return_exceptions=True)
    rows = []
    for it, a in zip(items, answers):
        row = {"id": it["id"], "name": it["name"], "author": it["author"], "likes": it["likes"] or 0,
               "chars": len(it["source"])}
        if isinstance(a, Exception):
            row["error"] = repr(a)[:200]
        else:
            for k, v in a.items():
                row[k] = v.get("choice", v.get("p"))
                if "conf" in v:
                    row[k + "_conf"] = round(v["conf"], 2)
        rows.append(row)
    df = pd.DataFrame(rows).sort_values("likes", ascending=False)
    df.to_csv(OUT, index=False)
    print(f"{len(df)} scripts -> {OUT}; errors: {df.get('error', pd.Series(dtype=str)).notna().sum()}")


if __name__ == "__main__":
    asyncio.run(main())
