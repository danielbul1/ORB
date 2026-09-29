---
title: ORB Backtest Results
created: 2026-09-29
tags: [orb, backtest, nq, results]
---

# ORB Backtest Results (NQ, 2016-06 → 2026-09)

Back to [[ORB]] · Sources: [[ORB Literature Review]]

## Setup
- **Data:** NQ front-month 1-minute bars (London Strategic Edge), 2,652 NY sessions (09:30–15:59 ET).
- **Engine:** `orb/backtest.py`, vectorized. It uses pessimistic fills: stop entries fill at the level or at a gapped open; if a stop and a target land in the same bar, the stop counts. Every trade pays **1.0 pt round trip**.
- **Split:** Train 2016–2021 (chosen here) → Validate 2022–2024 → **Holdout 2025-01 → 2026-09, looked at once**.
- **Score:** Sharpe of daily R (fixed-fractional risk per trade), plus average R per trade and max drawdown in R.
- **Parity:** the `ORB v0` Pine strategy on TradingView (NQ1! 5m) took the **same trades** as the Python engine on all 7 overlapping days. Prices were within 1 tick.

## 🏆 Winner: ORB-5 Candle + Body + Gap

| Rule | Value |
|---|---|
| Opening range | first 5 minutes (09:30–09:35) |
| Direction | sign of the 5-min OR candle (close vs open) |
| Filter 1: body | \|OR close − open\| ≥ **0.05 × ATR14** (RTH daily ATR, prior 14 days) |
| Filter 2: gap | trade only **in the direction of the overnight gap** (09:30 open vs prior 15:59 close) |
| Entry | market at 09:35 open |
| Stop | **0.10 × ATR14** from entry |
| Target | **10R**, otherwise flat at 15:59 |
| Frequency | about 35% of days, about 85 trades/year |

| Period | Trades | Win % | Avg R | Sharpe | Max DD (R) | R / year |
|---|---|---|---|---|---|---|
| Train 2016–21 | 475 | 22% | +0.457 | 1.25 | 24.0 | 38.9 |
| Validate 2022–24 | 259 | 22% | +0.548 | 1.50 | 19.6 | 47.4 |
| **Holdout 2025–26** | 147 | 22% | **+0.379** | **1.12** | 16.3 | 32.1 |

Yearly Sharpe: **positive in all 11 years** (2016: 1.28, 2017: 0.31, 2018: 1.33, 2019: 1.40, 2020: 1.46, 2021: 1.57, 2022: 1.85, 2023: 0.63, 2024: 1.96, 2025: 0.87, 2026: 1.44).

**Sizing example:** at a 1R = 0.5% account risk, 30 R/yr is about 15%/yr before compounding. Stops are about 0.1 × ATR, roughly 35–40 NQ points in 2026. Use **MNQ** for granular sizing.

## Other finalists (holdout Sharpe)
| Variant | Train | Val | Holdout | Note |
|---|---|---|---|---|
| ORB-5 paper (Zarattini/Aziz, no filters) | 0.90 | 0.65 | 0.70 | baseline; works, but is noisy |
| ORB-5 + body ≥ 0.05 ATR | 1.39 | 1.14 | 0.70 | more trades, lower quality recently |
| Noise-area momentum (n=30, VM=1.0) | 1.09 | 1.51 | **0.32** | decayed in 2025–26, as the replications warned |
| Portfolio ORB-body + Noise | 1.56 | 1.66 | 0.64 | correlation only 0.28 |

## What did NOT work
- **Crabel stretch breakout:** train Sharpe 0.1–0.4. NR4/NR7 filters did not rescue it.
- **Volatility-regime filter** (ATR14/ATR100): it hurt in every setting.
- **Trading against the gap:** Sharpe about 0 across the whole grid.
- **Stop at the other end of the range** instead of 0.1 × ATR: Sharpe fell to 0.44.
- **15/30-min ranges:** they work, but they sit on spikes rather than plateaus (for example, 15-min is good and 10/20-min is poor).

## Robustness notes
- Train vs validate Sharpe correlation across 1,512 core-grid variants was **0.95**, so the edge is structural, not a lucky cell.
- The body filter is a plateau: body 0.03–0.10 × ATR with stop 0.10 × ATR all give train Sharpe 1.25–1.39 and validate 1.0–1.3.
- **Cost sensitivity:** at 2 pt round trip, ORB-body falls to about 0.95 Sharpe. Stop-order slippage is the main live risk, so keep costs low (MNQ/NQ commissions plus 1 tick).

## Next ideas
- Live forward-test in TradingView (paper) with alerts.
- Test the same rules on ES (data is already in Model/data) as an out-of-market check.
- Late-day momentum overlay (Gao et al. / Baltussen et al.) for the 15:30–16:00 window.
