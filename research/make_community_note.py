"""Write the Obsidian note for the community ORB script study from research/orb_script_profiles.csv."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "research" / "orb_script_profiles.csv")
trad = df[df.kind.isin(["strategy", "signals"])]
w = np.log1p(trad.likes)


def share(col):
    s = trad.groupby(col).apply(lambda g: np.log1p(g.likes).sum()) / w.sum()
    return ", ".join(f"{k} {v:.0%}" for k, v in s.sort_values(ascending=False).items())


flags = [c for c in df.columns if c.startswith(("f_", "x_")) and not c.endswith("_conf")]
flag_rows = "\n".join(f"| `{c}` | {((trad[c] > 0.5) * w).sum() / w.sum():.0%} |" for c in flags)
yes = lambda r: ", ".join(c[2:] for c in flags if r[c] > 0.5) or "–"
top = df.head(40)
table = "\n".join(
    f"| {str(r['name'])[:55].replace('|', '/')} | {r['author']} | {r['likes']} | {r['kind']} | {r['or_length']} | {r['entry']} | {r['stop']} | {r['target']} | {yes(r)} |"
    for _, r in top.iterrows())

note = f"""---
title: Community ORB Scripts
created: 2026-09-29
tags: [orb, tradingview, community, jev]
---

# Community ORB Scripts (TradingView)

Back to [[ORB]] · Related: [[ORB Backtest Results]] · [[QuantFlowLabs ORB]]

## What was done
- I searched TradingView's public library with 10 queries (opening range breakout, ORB, initial balance, …). That found **234 unique ORB scripts**, of which **{len(df)} are open source**. The code was downloaded with the pine-facade API.
- **Jev (TypeSafe System One)** read each script's code, after comments and drawing code were stripped, and returned typed answers:
  - Choice answers: script kind, opening-range length, session, entry trigger, stop and target.
  - Yes/no answers (Nouls) with probabilities: filters (VWAP, MA trend, HTF trend, volume, range size, RSI/momentum, prior-day levels, gap, time window) and exits (breakeven, partials, second trade, EOD).
  - Code: `orb/jev_scripts.py`. Raw answers: `research/orb_script_profiles.csv`. The whole run took about 1 minute and costs cents.
- **Spot check:** on the simple zzzcrypto123 ORB, Jev had the length and the absence of entry/stop/target right. It labelled the script "other" instead of "levels".

## What the community does
{len(trad)} scripts have entry logic ({(df.kind == 'strategy').sum()} are real strategies). Weights are like-weighted (log likes).
- **OR length:** {share('or_length')}
- **Session:** {share('session')}
- **Entry:** {share('entry')}
- **Stop:** {share('stop')}
- **Target:** {share('target')}

| Filter / exit (P > 0.5) | share |
|---|---|
{flag_rows}

**Takeaway:** the crowd trades a **15-min range with close confirmation**, often with **no stop**, and almost never filters by the **gap (2%)**. Our winner uses a 5-min range, the candle direction, an ATR stop and the gap filter. It sits far from the consensus.

## Backtest of the community ideas (NQ 2016–2024, 1 pt round-trip cost)
| Test | Train Sharpe | Val Sharpe |
|---|---|---|
| **Community consensus**: 15m, close entry, opposite-side stop, 2R | 0.14 | 0.76 |
| consensus + retest entry | −0.08 | 0.89 |
| consensus + 2× OR target | 0.02 | 0.68 |
| consensus + VWAP / EMA / RSI / PDH-PDL filters | −0.10 … 0.38 | 0.57 … 0.84 |
| consensus + gap-with + 0.25 ATR stop, no target | 0.70 | 1.05 |
| **Our winner** (5m candle, body ≥ 0.05 ATR, gap-with, 0.1 ATR stop, 10R) | **1.25** | **1.50** |
| winner + **VWAP side** ✅ adopted | **1.33** | **1.51** (holdout 1.25 vs 1.12) |
| winner + EMA200 side | 1.20 | 1.57 |
| winner + PDH/PDL block 0.25 ATR | 1.41 | 1.28 |
| winner + RSI block 70 | 1.08 | 1.04 ❌ |
| winner + 20-day HTF trend | 1.27 | 0.92 ❌ |

The popular recipe has almost no edge once costs are paid. The ideas that help ours are VWAP side (small but consistent) and, from our own research, the gap.

## Jev as a pre-trade judge: rejected
For each of the winner's 881 trades, Jev saw the 09:35 context: gap, first candle, prior day, 5-day change and volatility. It gave P(trend day) and a conviction Score. The correlation with trade R was **+0.01 to +0.08**, and the terciles were not monotonic across train, validation and holdout. **No edge, so it isn't used.** Jev is a strong reader of code and text, but it doesn't forecast from numeric market state (the same result as in the Model project). Code: `orb/jev_filter.py`.

## Top 40 scripts by likes (Jev profile)
| Script | Author | Likes | Kind | OR | Entry | Stop | Target | Features |
|---|---|---|---|---|---|---|---|---|
{table}
"""
(ROOT / "vault" / "Research" / "Community ORB Scripts.md").write_text(note, encoding="utf8")
print("written")
