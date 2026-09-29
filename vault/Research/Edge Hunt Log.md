---
title: Edge Hunt Log
created: 2026-09-29
tags: [orb, research-log, walk-forward, jev]
---

# Edge Hunt Log

Back to [[ORB]] · Glossary: `CONTEXT.md` · Decisions: `docs/adr/`

## Rules of the hunt (decided 2026-09-29)
- **Score** = yearly profit when sized so the worst drawdown equals the Account Profile cap ($50k account, $2,000 max drawdown, MNQ). Every result also reports the worst losing streak.
- **Judge:** Walk-Forward on 2016–2024 (each test year is tuned only on earlier years), then a **Forward Test** of about 60 paper Sessions. The 2025–26 Holdout is spent (ADR 0001).
- **Goal:** a Portfolio of independent Rule Sets, flat every Session, trading NQ/MNQ, with ES as the robustness test.
- **Jev** works on text only: it labels calendar events and reads research and scripts.

## Results so far (Walk-Forward 2019–2024, $2k DD cap)
| Rule Set | Score/yr | Sharpe | Worst streak | Verdict |
|---|---|---|---|---|
| **ORB v1** (fixed params) | **$5,562** | 1.54 | 16 | ✅ core |
| ORB v1 with stop/target re-tuned each year | $4,379 | 1.39 | 16 | fixed params are better |
| ORB v1 + GEX / FOMC / pre-open-event switches | $4,574 | 1.48 | 15 | ❌ in-sample pattern, not robust |
| Late-day momentum (Gao / Baltussen) | $156 | 0.23 | 8 | ❌ no stable edge on NQ |
| Failed-breakout fade | $16 | 0.02 | 24 | ❌ |

### Regime findings (2016–24, descriptive only)
- ORB v1 is weaker when dealer gamma is high (top GEX tercile: +0.22R/trade) than when it is low or mid (+0.54 / +1.06). This fits the theory that positive gamma damps trends, but the switch lost under walk-forward.
- ORB v1 made −0.03R/trade on FOMC-afternoon days (n = 38), against +0.62R on days without a major event.

### Robustness test: ES ❌
ORB v1 on ES loses: 2016–24 Sharpe −0.46, and 7 of 11 years are negative. Its correlation with NQ ORB is 0.43. So the Edge is either **Nasdaq-specific** (higher beta, momentum and leveraged-ETF flows, as in Zarattini's QQQ vs SPY results) or **partly overfit**. That is decided by the pre-registered NAS100 2003–2015 test (ADR 0002).

## Data added
- **Economic calendar 2007–2026** (Forex Factory history, UTC → ET). Jev labelled all 170 USD event types with a category and a market-impact Score. CPI, FOMC, NFP and Powell rank as Major (≥ 2.5); vehicle sales and DST shifts as negligible. 18.6% of Sessions have a major event.
- **SqueezeMetrics GEX/DIX** (2011–), **CBOE VIX / VIX9D / VVIX**. Every value is taken from the prior day only.
- **LSE:** NQ ticks exist only from 2025-09 and carry no aggressor side, so order flow is deprioritised. NAS100, SOX and NVDA 1m go back to 2003.
