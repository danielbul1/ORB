"""Exact default parameters of the community ORB strategies, by selection rather than generation.

Code lists every `input.*(default, "title")` in a script as a candidate; Jev picks which candidate is each
parameter (or none); code then reads the default value from the source. Cached like orb.jev_scripts.

Usage: python -m orb.jev_params   -> research/orb_strategy_params.csv
"""
import asyncio
import hashlib
import json
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import AsyncTypeSafeClient, Choice

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "jev_cache"
MODEL = "jev-latest"
INPUT = re.compile(r'(\w+)\s*=\s*input(?:\.\w+)?\(\s*(?:defval\s*=\s*)?([^,\)]+)[^\n]*?(?:title\s*=\s*)?"([^"]*)"')

PARAMS = {
    "or_minutes": "the length of the opening range in minutes (or the opening-range session string)",
    "target_r": "the take-profit expressed as a risk:reward multiple of the stop distance",
    "target_range_mult": "the take-profit expressed as a multiple of the opening-range width",
    "target_points": "the take-profit as a fixed number of points, ticks or percent",
    "stop_atr_mult": "the stop-loss distance as a multiple of ATR",
    "stop_points": "the stop-loss as a fixed number of points, ticks or percent",
    "entry_cutoff": "the last time of day (or window end) at which new breakout entries are allowed",
    "session_end": "the time at which open positions are closed for the day",
}


def candidates(src):
    out = {}
    for var, default, title in INPUT.findall(src):
        out.setdefault(var, {"default": default.strip(), "title": title.strip()})
    return out


def key(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:24]


async def ask(client, sem, item):
    cands = candidates(item["source"])
    if not cands:
        return {}
    crit = {v: f'input "{c["title"]}" (default {c["default"][:40]})' for v, c in list(cands.items())[:200]}
    crit["none"] = "None of these inputs is this parameter."
    qs = {p: Choice(instructions=f"In the ORB strategy `script`, which input sets {desc}?", criteria=crit)
          for p, desc in PARAMS.items()}
    state = {"script": {"name": item["name"], "inputs": [f'{v}: "{c["title"]}" = {c["default"][:40]}'
                                                         for v, c in cands.items()]}}
    path = CACHE / f"params_{key({'s': state, 'q': list(PARAMS), 'm': MODEL})}.json"
    if path.exists():
        picks = json.loads(path.read_text())
    else:
        async with sem:
            r = await client.system_one(state=state, questions=qs, model=MODEL)
        picks = {p: {"var": a.choice, "conf": float(a.confidence)} for p, a in r.choices.items()}
        CACHE.mkdir(exist_ok=True)
        path.write_text(json.dumps(picks))
    return {p: (cands[v["var"]]["default"] if v["var"] in cands else None, v["conf"]) for p, v in picks.items()}


async def main():
    load_dotenv(ROOT / ".env")
    prof = pd.read_csv(ROOT / "research" / "orb_script_profiles.csv")
    strat = prof[(prof.kind == "strategy") & (prof.session == "ny_0930")]
    src = {x["id"]: x for x in json.loads((ROOT / "research" / "community_orb.json").read_text(encoding="utf8"))["items"]}
    items = [src[i] for i in strat.id]
    sem = asyncio.Semaphore(8)
    async with AsyncTypeSafeClient(timeout=120.0) as client:
        res = await asyncio.gather(*(ask(client, sem, it) for it in items))
    rows = []
    for it, r, (_, pr) in zip(items, res, strat.iterrows()):
        row = {"id": it["id"], "name": it["name"], "likes": it["likes"], "entry": pr.entry, "stop": pr.stop,
               "target": pr.target, "or_length": pr.or_length, "f_vwap": pr.f_vwap, "f_ma_trend": pr.f_ma_trend,
               "f_volume": pr.f_volume}
        for p, (val, conf) in r.items():
            row[p] = val
            row[p + "_conf"] = round(conf, 2)
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "research" / "orb_strategy_params.csv", index=False)
    print(df[["name", "or_length", "entry", "stop", "target"] + list(PARAMS)].to_string(index=False))


if __name__ == "__main__":
    asyncio.run(main())
