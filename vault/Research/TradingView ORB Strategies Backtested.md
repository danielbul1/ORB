---
title: TradingView ORB Strategies Backtested
created: 2026-09-29
tags: [orb, tradingview, community, backtest, jev]
---

# TradingView ORB Strategies Backtested

Back to [[ORB]] · Related: [[Community ORB Scripts]] · [[Edge Hunt Log]]

## Method
- **Which scripts:** 24 of the 34 open-source ORB *strategies* trade the New York open, and 19 could be expressed in our engine (trailing and pullback logic can't be, so those are skipped).
- **Defaults picked by Jev:** code lists every `input(...)` of a script, Jev selects which input is the OR length, target R, stop ATR, fixed points, cutoff and session end, and code reads the default value (`orb/jev_params.py` → `research/orb_strategy_params.csv`).
- **Approximations**, applied the same way to every script (`research/community_strategies.py`):
  - evaluated on NQ 1-minute bars;
  - chart-ATR stops converted to daily ATR;
  - fixed points scaled to price (points / 20,000);
  - breakout-candle stops approximated by the OR midpoint;
  - MA filter → EMA200, volume filter → relative volume ≥ 1, VWAP filter → session-VWAP side.
- **Costs:** 1 pt round trip; 2003–15 uses the long-base costs.

## Results (sorted by Sharpe 2016–24)
| Strategy (likes) | Trades/yr | Win % | Avg R | Sharpe 16–24 | Sharpe 25–26 | Sharpe 03–15 |
|---|---|---|---|---|---|---|
| OURS: ORB v1 (5m, gap, VWAP, 0.1 ATR, 10R) | 78 | 22% | +0.541 | **1.39** | 1.3 | -0.06 |
| NY ORB - MA Stop (156) | 185 | 42% | +0.051 | **0.55** | 0.48 | -0.61 |
| Initial Balance Breakout (Bnf6082, 47) | 199 | 49% | +0.038 | **0.48** | -0.09 | -0.67 |
| Script_Algo ORB with Filters (412) | 78 | 36% | +0.073 | **0.41** | 0.51 | -0.36 |
| ORB + VWAP and Volume Filters (123) | 122 | 53% | +0.027 | **0.3** | -0.28 | -1.04 |
| Initial Balance Breakout [samjNQ] v3 (42) | 233 | 53% | +0.012 | **0.25** | 0.13 | -0.54 |
| NASDAQ ORB Strict Exec RRR 2.0 (30) | 121 | 36% | +0.010 | **0.08** | -0.92 | -0.59 |
| ORB Pro | Session Breakout Scalper (526) | 124 | 44% | +0.003 | **0.03** | 0.88 | -0.46 |
| MNQ ORB - VWAP + Bias (25) | 248 | 38% | -0.009 | **-0.11** | 0.64 | -0.52 |
| ORB Breakout Strategy (chartsquare, 215) | 252 | 36% | -0.014 | **-0.16** | 0.2 | -1.14 |
| ORB Heikin Ashi SPY 5min Correlation (exlux, 2357 likes) | 116 | 48% | -0.009 | **-0.18** | 0.47 | -0.88 |
| 15-Min ORB for NQ (129) | 250 | 50% | -0.016 | **-0.27** | 0.93 | -1.41 |
| NY15m ORB fixed SL&TP Nasdaq (195) | 250 | 35% | -0.028 | **-0.32** | -0.01 | -0.81 |
| ORB Strategy [LuciTech] (1251) | 250 | 35% | -0.028 | **-0.32** | -0.01 | -0.81 |
| ORB AVWAP Retest (43) | 233 | 50% | -0.021 | **-0.33** | 0.36 | -1.4 |
| MNQ 15m NY Open ORB (30) | 250 | 50% | -0.029 | **-0.47** | -0.2 | -2.08 |
| Drop's ORB (441) | 250 | 48% | -0.067 | **-1.09** | -0.51 | -1.92 |
| ORB + Key Session Levels +SL (381) | 250 | 49% | -0.070 | **-1.1** | -0.33 | -1.77 |
| Big Daddy Max ORB (273) | 254 | 48% | -0.071 | **-1.13** | -0.39 | -1.71 |
| ORB MEEEEEKS (46) | 233 | 51% | -0.081 | **-1.22** | -0.98 | -3.09 |

**Every community strategy is negative in 2003–15.** Only 5 of 19 are above Sharpe 0.1 in 2016–24, and the best, "NY ORB – MA Stop", reaches 0.55.

## Why they fail: what we learn
1. **Small targets (1–2R) cut off the Edge.** ORB's profit sits in the fat tail of trend days: our top 5% of trades make 96% of the profit. A 1R target turns that into a ~50% coin flip, which is negative after costs.
2. **They trade every day** (about 250 trades a year) and pay costs on days with no Edge. Our gap-with filter trades about 78 days a year, and those are the days with an Edge.
3. **OR-midpoint and opposite-side stops** are hit by normal opening noise. An ATR-scaled stop adapts to the regime.
4. **The best of them use a trend filter (MA) and hold longer.** Both are steps toward our design: direction agreement (gap and VWAP) plus letting winners run to 10R or the close.
5. **Likes don't measure Edge:** the most-liked strategy (2,357 likes) has Sharpe −0.18.
