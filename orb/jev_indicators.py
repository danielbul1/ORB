"""Jev reads the code of TradingView's most-liked open-source indicators and says how each one works.

Code fetches and cleans (research/fetch_top_indicators.mjs -> research/top_indicators.json);
Jev only judges what each script's code does. Cached per (state, questions, model).

Usage: python -m orb.jev_indicators [N]     -> research/indicator_profiles.csv (top N open-source, default 150)
"""
import asyncio
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul

from orb.jev_scripts import clean

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "research" / "top_indicators.json"
CACHE = ROOT / "jev_cache"
OUT = ROOT / "research" / "indicator_profiles.csv"
MODEL = "jev-latest"

Q = {
    "family": Choice(
        instructions="What kind of indicator is the Pine Script in `code`, judged by what its code computes?",
        criteria={
            "trend_following": "Follows the trend: moving averages, supertrend/ATR trailing lines, range filters, trend ribbons.",
            "momentum_oscillator": "A bounded or zero-centred oscillator of momentum: RSI, MACD, stochastic, WaveTrend, squeeze momentum, ADX.",
            "mean_reversion_bands": "Bands or envelopes around a centre line used to fade extremes: Bollinger, Keltner, Nadaraya-Watson, regression channels.",
            "market_structure_smc": "Swing-based market structure: BOS/CHoCH, order blocks, fair value gaps, liquidity sweeps, supply/demand zones.",
            "support_resistance_levels": "Horizontal or sloped levels: pivots, trendlines, S/R zones, fibonacci, session or prior-period highs/lows.",
            "volume_based": "Built mainly from volume: volume profile, volume flow, OBV, CVD/delta, high-volume zones.",
            "machine_learning_stats": "A statistical or machine-learning model: classification, clustering, kernel regression, probability estimates.",
            "pattern_or_other": "Candlestick/chart patterns, dashboards, strategy builders, or something else.",
        }),
    "core_math": Choice(
        instructions="What is the main calculation the signal is built on?",
        criteria={
            "moving_average": "Moving averages or their crossovers/slopes.",
            "atr_band": "A line offset from price or an average by a multiple of ATR or range (trailing stop style).",
            "std_band": "Standard deviation bands or regression/kernel envelopes.",
            "normalized_oscillator": "An oscillator normalized to a fixed range or zero line (RSI, stochastic, MACD histogram, linreg momentum).",
            "pivot_swings": "Pivot highs/lows (ta.pivothigh/pivotlow or equivalent swing detection) and what price does at them.",
            "gaps_and_candles": "Candle relationships such as gaps between bars (FVG), engulfing, or specific candle patterns.",
            "volume_aggregation": "Summing or binning volume by price or direction.",
            "model_or_other": "Nearest neighbours, clustering, probabilities, or something else.",
        }),
    "output": Choice(
        instructions="What does the indicator mainly give the trader?",
        criteria={
            "entry_signals": "Explicit buy/sell signals, arrows or alert conditions on specific bars.",
            "trend_state": "A continuous trend/regime state (colored line, ribbon, background) rather than one-off signals.",
            "zones_levels": "Price zones or levels drawn on the chart to trade from.",
            "oscillator_reading": "An oscillator value in a separate pane, read for overbought/oversold, crosses or divergences.",
            "info_dashboard": "Tables, statistics or dashboards.",
        }),
    "market_belief": Choice(
        instructions="Which market behaviour does the indicator bet on to make money? Judge from what its signals do.",
        criteria={
            "trend_persistence": "Moves that have started tend to continue (buy strength, sell weakness).",
            "mean_reversion": "Stretched prices tend to snap back (fade extremes, overbought/oversold).",
            "volatility_expansion": "Quiet, compressed periods are followed by big moves (squeeze, breakout of a range).",
            "levels_hold_or_break": "Prices react at levels where orders cluster (swings, pivots, zones, liquidity).",
            "volume_confirms": "Volume shows where real participation is and confirms or rejects moves.",
            "pattern_recurrence": "Past patterns or similar states repeat (ML, candle patterns).",
            "time_of_day": "Specific sessions or times of day behave differently.",
        }),
    "p_repaints": Noul(instructions="Can the indicator's past signals or drawings change after the fact? (Yes if it uses request.security with lookahead on, draws pivots/zones back in time at bars that were not yet confirmed, uses future bars via negative offsets, or signals on the unclosed bar without barstate.isconfirmed.)"),
    "p_pivot_lag": Noul(instructions="Does the signal only become known several bars after the bar it is drawn on (e.g. pivots that need N right-side bars)?"),
    "p_uses_volume": Noul(instructions="Does the core calculation use volume?"),
    "p_uses_htf": Noul(instructions="Does it use data from a higher or other timeframe/symbol via request.security?"),
    "p_has_alerts": Noul(instructions="Does the script define alertcondition() or alert() calls for its signals?"),
    "p_atr_scaled": Noul(instructions="Are its thresholds scaled by ATR or volatility, so it adapts to how volatile the market is?"),
    "p_ma_crossover": Noul(instructions="Is a crossover between two lines (price vs average, fast vs slow, signal line) the main trigger?"),
    "p_divergence": Noul(instructions="Does it detect divergences between price and an oscillator?"),
    "p_session_time": Noul(instructions="Does it use session times, killzones or time-of-day windows?"),
    "p_many_params": Noul(instructions="Does it have more than about 10 user inputs that change the signals (high risk of curve fitting)?"),
}


def key(state):
    blob = json.dumps({"s": state, "q": sorted(Q), "m": MODEL}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:24]


async def ask(client, sem, item):
    state = {"script_name": item["name"], "author": item["author"], "code": clean(item["source"])}
    path = CACHE / f"ind_{key(state)}.json"
    if path.exists():
        return json.loads(path.read_text())
    async with sem:
        r = await client.system_one(state=state, questions=Q, model=MODEL)
    out = {k: {"choice": a.choice, "conf": a.confidence, "probs": dict(a.probabilities)} for k, a in r.choices.items()}
    out.update({k: {"p": float(a.noul)} for k, a in r.nouls.items()})
    CACHE.mkdir(exist_ok=True)
    path.write_text(json.dumps(out))
    return out


async def main(n):
    load_dotenv(ROOT / ".env")
    items = [x for x in json.loads(SRC.read_text(encoding="utf8"))["items"] if x["access"] == 1 and x["source"]][:n]
    sem = asyncio.Semaphore(8)
    async with AsyncTypeSafeClient(timeout=180.0) as client:
        answers = await asyncio.gather(*(ask(client, sem, it) for it in items), return_exceptions=True)
    rows = []
    for rank, (it, a) in enumerate(zip(items, answers), 1):
        row = {"rank": rank, "id": it["id"], "name": it["name"], "author": it["author"], "likes": it["likes"],
               "kind": it["kind"], "chars": len(it["source"])}
        if isinstance(a, Exception):
            row["error"] = repr(a)[:200]
        else:
            for k, v in a.items():
                row[k] = v.get("choice", round(v.get("p", 0), 2))
                if "conf" in v:
                    row[k + "_conf"] = round(v["conf"], 2)
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    print(f"{len(df)} indicators -> {OUT}; errors: {df['error'].notna().sum() if 'error' in df else 0}")


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 150))
