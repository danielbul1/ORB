---
title: Community ORB Scripts
created: 2026-09-29
tags: [orb, tradingview, community, jev]
---

# Community ORB Scripts (TradingView)

Back to [[ORB]] · Related: [[ORB Backtest Results]] · [[QuantFlowLabs ORB]]

## What was done
- I searched TradingView's public library with 10 queries (opening range breakout, ORB, initial balance, …). That found **234 unique ORB scripts**, of which **158 are open source**. The code was downloaded with the pine-facade API.
- **Jev (TypeSafe System One)** read each script's code, after comments and drawing code were stripped, and returned typed answers:
  - Choice answers: script kind, opening-range length, session, entry trigger, stop and target.
  - Yes/no answers (Nouls) with probabilities: filters (VWAP, MA trend, HTF trend, volume, range size, RSI/momentum, prior-day levels, gap, time window) and exits (breakeven, partials, second trade, EOD).
  - Code: `orb/jev_scripts.py`. Raw answers: `research/orb_script_profiles.csv`. The whole run took about 1 minute and costs cents.
- **Spot check:** on the simple zzzcrypto123 ORB, Jev had the length and the absence of entry/stop/target right. It labelled the script "other" instead of "levels".

## What the community does
108 scripts have entry logic (34 are real strategies). Weights are like-weighted (log likes).
- **OR length:** 15m 52%, 30m 17%, other 11%, 60m 8%, 5m 6%, first_bar 5%
- **Session:** ny_0930 64%, configurable_other 15%, india 8%, futures_other 7%, london_asia 5%
- **Entry:** close 77%, retest 15%, touch 8%, pullback_other 1%
- **Stop:** none 52%, opposite_side 19%, atr 11%, midpoint 9%, fixed 4%, candle_or_swing 4%
- **Target:** none 37%, r_multiple 31%, range_multiple 18%, atr_or_fixed 7%, trailing 5%, session_end 1%

| Filter / exit (P > 0.5) | share |
|---|---|
| `f_vwap` | 8% |
| `f_ma_trend` | 13% |
| `f_htf_trend` | 8% |
| `f_volume` | 12% |
| `f_range_size` | 7% |
| `f_rsi_momentum` | 6% |
| `f_prior_levels` | 15% |
| `f_gap` | 2% |
| `f_time_window` | 40% |
| `x_breakeven` | 20% |
| `x_partial` | 17% |
| `x_second_trade` | 60% |
| `x_eod_exit` | 22% |

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
| Opening Range with Breakouts & Targets [LuxAlgo] | LuxAlgo | 20612 | signals | 30m | close | none | range_multiple | second_trade |
| ORB Algo / Flux Charts | fluxchart | 16369 | signals | 30m | retest | midpoint | atr_or_fixed | breakeven, partial |
| ORB - Opening Range Breakout | zzzcrypto123 | 11621 | other | 5m | none | none | none | – |
| Opening Range Breakout with 2 Profit Targets. | ChrisMoody | 10067 | levels | 60m | touch | none | range_multiple | time_window, partial |
| Ultimate Opening Range Breakout [LuxAlgo] | LuxAlgo | 9789 | signals | 30m | close | atr | trailing | time_window, breakeven, second_trade |
| Initial Balance Breakout Signals [LuxAlgo] | LuxAlgo | 7663 | signals | 60m | close | none | none | second_trade |
| Luxy BIG beautiful Dynamic ORB | orenluxy | 6205 | signals | other | close | atr | r_multiple | ma_trend, prior_levels, partial, second_trade |
| ORB with Price Targets | getthatcashmoney | 4377 | signals | 15m | close | none | range_multiple | second_trade |
| Timely Opening Range Breakout Strategy [TORB] (Zeiierma | Zeiierman | 3270 | signals | 60m | close | none | none | volume, second_trade |
| Basic ORB [MOT] | TheBigDaddyMax | 3035 | levels | 15m | none | none | none | – |
| New Indicator!!! Opening Range_V1 | ChrisMoody | 2712 | other | 60m | none | none | none | – |
| ORB 15 Min By EquityDurai | equitydurai81 | 2585 | other | 15m | none | none | none | – |
| Opening Range Breakout with Price Targets | TradeSeekers | 2412 | signals | 15m | close | none | range_multiple | second_trade |
| QuantCrawler ORB Break & Retest 15m - Opening Range Str | QuantCrawler | 2410 | signals | 15m | retest | none | none | time_window, second_trade |
| ORB Heikin Ashi SPY 5min Correlation Strategy | exlux | 2357 | strategy | 30m | close | none | session_end | volume, time_window, second_trade, eod_exit |
| ORB - Opening Range Breakout + Alerts | VeroTradeX | 2166 | signals | 15m | close | none | none | – |
| ORB with ATR Trailing SL [Bluechip Algos] | BlueChip_Algos | 2078 | signals | 5m | close | atr | trailing | breakeven |
| CM Opening Range-Asia and Europe Session | ChrisMoody | 1967 | levels | other | touch | none | range_multiple | time_window, partial |
| Opening Range Breakout Lines | tretgothacks | 1809 | signals | first_bar | close | none | none | second_trade |
| Opening Range & Prior Day High/Low [Gorb] | GorbAlgo | 1808 | levels | 15m | none | none | none | prior_levels |
| Orb breakout  | Shauryam_or | 1784 | signals | 15m | close | none | none | second_trade |
| Michigandolf's 30min Opening Range | Michigandolf | 1737 | other | 30m | none | none | none | – |
| Opening Range + Session Windows + Volume Profile | WealthLearn | 1515 | signals | 15m | close | none | none | – |
| Opening Range Fibonaccis | colejustice | 1467 | levels | 30m | none | none | none | – |
| Opening Range Gaps [TFO] | tradeforopp | 1415 | levels | other | none | none | none | gap |
| ORB with Range Context | VishalSubandh | 1321 | signals | 5m | close | none | range_multiple | – |
| ORB Strategy [LuciTech] | TradesLuci | 1251 | strategy | 15m | close | atr | r_multiple | time_window, breakeven, second_trade |
| ORB Current Timeframe | SushilKothawade | 1148 | other | other | none | none | none | – |
| NY 5m & 15m Orb - Statistics & LTF Candle structure | lucymatos | 1095 | levels | other | none | none | range_multiple | – |
| [RS]Open Range Breakout V3 | RicardoSantos | 1087 | levels | 60m | none | none | none | – |
| Gold ORB Strategy (15-min Range, 5-min Entry) | krypson | 1077 | strategy | other | close | opposite_side | range_multiple | time_window, second_trade |
| Open Range Breakout (ORB) with Alerts | ChartsAlgo | 1041 | signals | 15m | close | none | none | second_trade |
| ORB With Buffer, Target & Stop Loss | Tamil_FNO_Trader | 1019 | levels | other | none | fixed | atr_or_fixed | prior_levels |
| ORB + Fib Breakout Signals 1.0 | chadsingh | 1018 | signals | 15m | close | none | range_multiple | – |
| ORB Engine / ANONYCRYPTOUS | Anonycryptous | 1006 | signals | 15m | retest | opposite_side | r_multiple | volume, time_window, partial, second_trade |
| ORB Breakouts with alerts | row004 | 913 | signals | 15m | close | none | range_multiple | partial |
| ORB SESSIONS | VONKAR | 896 | strategy | 15m | close | opposite_side | r_multiple | time_window, breakeven, partial, second_trade, eod_exit |
| NTrades [ORBDD Advanced] - Working | Nishann | 896 | signals | 15m | retest | midpoint | r_multiple | ma_trend, htf_trend, prior_levels, time_window, second_trade, eod_exit |
| Pivot Points + Day First Candle Breakout + VWAP + Super | rupatil | 860 | signals | 15m | close | none | none | ma_trend, rsi_momentum, prior_levels, second_trade |
| Opening Range Gap + Std Dev [starclique] | fytte | 859 | levels | other | none | none | none | – |
