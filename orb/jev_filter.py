"""Jev as a pre-trade judge for ORB trades.

For every day the rule set trades, code describes the market as known at 09:35 ET (no future data);
Jev returns the probability that the day trends in the trade's direction into the close.
We then check, split by split, whether that probability separates good trades from bad ones.

Usage: python -m orb.jev_filter
"""
import asyncio
import hashlib
import json
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from typesafe_sdk import AsyncTypeSafeClient, Noul, Score

from orb.backtest import daily, run
from orb.grid import load, masks

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "jev_cache"
MODEL = "jev-latest"
WINNER = dict(or_min=5, entry="candle", stop="atr", stop_x=0.1, target_r=10, body_min=0.05, gap_dir="with")

QUESTIONS = {
    "trend_day": Noul(instructions=(
        "NQ (Nasdaq-100 futures) just finished its first 5 minutes after the New York open, described in `market`. "
        "A trade is being opened in `market.trade_direction`. Is today likely to be a trend day that keeps moving "
        "in that direction into the close, rather than chopping or reversing?")),
    "conviction": Score(
        instructions=("How strong is the case, from `market` alone, for holding a `market.trade_direction` intraday "
                      "position from 09:35 to the close in NQ?"),
        criteria=[
            "Weak: the context argues against the direction or is mixed; a reversal or chop is at least as likely.",
            "Moderate: the opening move and gap point the same way but nothing else stands out.",
            "Strong: gap, opening drive and prior-day context all line up behind the direction.",
            "Very strong: an unusually forceful opening in line with a clear multi-day move; continuation is the obvious read.",
        ]),
}


def describe(d, ctx, i, direction):
    atr = d.atr14[i]
    o = d.o[i, 0]
    orc = d.c[i, 4]
    pdh, pdl, pc = ctx["pdh"][i], ctx["pdl"][i], d.prev_close[i]
    c5 = d.c[i - 5, d.last[i - 5]] if i >= 5 else np.nan
    side = "long" if direction > 0 else "short"
    return {
        "trade_direction": side,
        "day_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][int(d.dow[i]) % 5],
        "overnight_gap": f"{(o - pc) / atr:+.2f} ATR ({(o / pc - 1) * 100:+.2f}%)",
        "first_5min_candle": f"moved {(orc - o) / atr:+.2f} ATR from the open; range {(d.h[i, :5].max() - d.l[i, :5].min()) / atr:.2f} ATR",
        "open_vs_previous_day_range": f"{(o - pdl) / (pdh - pdl):.2f} (0 = previous low, 1 = previous high, outside 0..1 = gapped beyond it)",
        "previous_day": f"closed {(pc / d.c[i - 2, d.last[i - 2]] - 1) * 100:+.2f}%, at {(pc - pdl) / (pdh - pdl):.2f} of its range",
        "last_5_days_change": f"{(pc / c5 - 1) * 100:+.2f}%",
        "volatility": f"ATR14 is {atr / o * 100:.2f}% of price; {atr / ctx['atr100'][i]:.2f}x its 100-day average",
    }


def key(state):
    return hashlib.sha256(json.dumps({"s": state, "q": sorted(QUESTIONS), "m": MODEL, "v": 1}, sort_keys=True).encode()).hexdigest()[:24]


async def ask(client, sem, state):
    path = CACHE / f"filter_{key(state)}.json"
    if path.exists():
        return json.loads(path.read_text())
    async with sem:
        r = await client.system_one(state={"market": state}, questions=QUESTIONS, model=MODEL)
    out = {"trend_day": float(r.nouls["trend_day"].noul), "conviction": float(r.scores["conviction"].score)}
    CACHE.mkdir(exist_ok=True)
    path.write_text(json.dumps(out))
    return out


async def grade_all(d, res):
    ctx = daily(d)
    days = np.flatnonzero(res["ok"])
    states = [describe(d, ctx, i, res["dir"][i]) for i in days]
    sem = asyncio.Semaphore(16)
    async with AsyncTypeSafeClient(timeout=120.0) as client:
        ans = await asyncio.gather(*(ask(client, sem, s) for s in states))
    p = np.full(len(d.dates), np.nan)
    sc = np.full(len(d.dates), np.nan)
    p[days] = [a["trend_day"] for a in ans]
    sc[days] = [a["conviction"] for a in ans]
    return p, sc


def main():
    load_dotenv(ROOT / ".env")
    d = load()
    ms = masks(d)
    res = run(d, **WINNER)
    p, sc = asyncio.run(grade_all(d, res))
    np.savez(ROOT / "results" / "jev_filter.npz", p=p, score=sc, r=res["r"], ok=res["ok"], dates=d.dates)
    ok = res["ok"]
    # Thresholds are fixed on TRAIN terciles, then applied unchanged to val and holdout.
    for name, x in (("trend_day P", p), ("conviction", sc)):
        lo, hi = np.nanquantile(x[ok & ms["train"]], [1 / 3, 2 / 3])
        print(f"\n{name}: train tercile cuts {lo:.3f} / {hi:.3f}")
        for s in ("train", "val", "hold"):
            m = ok & ms[s]
            parts = {"low": m & (x <= lo), "mid": m & (x > lo) & (x <= hi), "high": m & (x > hi)}
            txt = "  ".join(f"{k}: n{v.sum():>3} avgR {res['r'][v].mean():+.3f}" for k, v in parts.items())
            corr = np.corrcoef(x[m], res["r"][m])[0, 1]
            print(f"  {s:5} {txt}   corr(x, R) {corr:+.3f}")


if __name__ == "__main__":
    main()
