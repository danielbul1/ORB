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

## Round 2: research-led candidates (see [[Intraday Edges Research]])
| Rule Set | WF Score/yr | Sharpe | Trades | Verdict |
|---|---|---|---|---|
| Late-day momentum, only when dealer gamma is low (GEX rank ≤ 0.2–0.5) | −$38 | −0.07 | 134 | ❌ Baltussen's effect doesn't hold year to year on NQ 2019–24 |
| High-gamma midday VWAP fade | −$58 | −0.16 | 166 | ❌ loses in both high- and low-gamma regimes |
| FOMC reversal (fade the move into 14:00) | +$369 | 0.23 | 52 | ⚠️ 5 of 6 years positive but tiny and too few trades; watch only |

**Lesson:** each candidate had tuned-period Scores of $500–$6,600, then failed on the next unseen year. That is the overfitting trap the Walk-Forward is built to catch. So far ORB v1 is the only Rule Set that survives.

## How much luck is in ORB v1? (Deflated Sharpe Ratio, Bailey & López de Prado)
- About 3,900 variants were tried in the saved grids, and more ad hoc.
- The **standard DSR** (noise taken from the Sharpe spread across all trials, sd 1.36) is about **0**: the best of 1,000+ tries would reach Sharpe 3–5 by chance.
- That spread overstates the noise, because many variants genuinely differ. Using ORB v1's own sampling noise (±0.34 Sharpe over 9 years) and N ≈ 1,000 independent tries, the luck threshold is about 1.1 and **DSR ≈ 0.79**, below the 0.95 bar.
- **Conclusion:** in-sample evidence alone cannot prove the Edge. A single test on fresh data carries no multiple-testing penalty, so the NAS100 2003–2015 test (ADR 0002) and the Forward Test are what count.

## Where ORB v1's profit comes from (2016–2026, 808 trades)
- 77% of trades are stopped (−1.08R each). 7% hit the 10R target (+9.9R). 16% close at 15:59 (+4.4R).
- **The top 5% of trades make 96% of the profit.** ORB v1 is a trend-day catcher that pays a small fee on most days.
- Longs +0.44R/trade and shorts +0.66R/trade, so it isn't just the bull market.
- **Gap size:** |gap| < 0.1 ATR → +0.05R (n = 185); 0.1–0.25 → +0.68R; 0.25–0.5 → +0.58R; > 0.5 → +0.79R.
- **Stop-outs:** 38% within 5 minutes, 73% within 30 minutes. 23% of stopped trades were first up 2R or more.
- Weekday differences (Wednesday and Friday weaker) are treated as noise and not traded.

### Tested: minimum gap size ≥ 0.1 ATR ❌ not adopted
Walk-forward picks 0.1 every year: $7,000/yr vs $5,562, Sharpe 1.73. But it is a spike (0.15 → $3,959, 0.2 → $3,259), and it is worse on 2025–26 ($2,853 vs $4,693). Spikes are not Edges.

## ❌ Pre-registered NAS100 2003–2016 test: FAIL (ADR 0002)
Frozen ORB v1 on 13 unseen years of Nasdaq-100 data (3,323 Sessions):
- Sharpe **0.34** (the bar was 0.5); 64% of years positive; worst losing streak 31; drawdown 79R.
- Yearly Score: 2003 +3.6k, 2004 +0.8k, 2005 +1.3k, 2006 −2.0k, 2007 −0.6k, 2008 +9.9k, 2009 −0.5k, 2010 +1.8k, 2011 +4.6k, 2012 −1.7k, 2013 −1.3k, 2014 +7.8k, 2015 +0.6k.

**Meaning:** the long-run Edge is weakly positive, and 2016–2026 was either an unusually good regime for Nasdaq opening momentum (leveraged ETFs, 0DTE and retail flows grew over this period) or partly overfit. Most likely both. The Forward Test is now the judge.
