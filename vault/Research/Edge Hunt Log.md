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

## 23-year research base (NAS100 2003–2016 + NQ 2016–2026)
- **Data fix:** the NQ/ES continuous series were not adjusted for contract rolls. LSE rolls at a low-volume 19:00–20:59 ET bar in the days before expiry week, and since the 2022 rate rises the carry is about +1%. That polluted expiry-week Monday gaps (+0.7 ATR) and ATR. `orb.data.back_adjust` now ratio-adjusts at each roll. Impact on ORB v1 was small (2016–24 Sharpe 1.39, 2025–26 1.30).
- **ES at a realistic 0.5 pt cost:** Sharpe 0.10, i.e. break-even, not −0.46. The Edge is still mostly Nasdaq-specific; ES was partly failing because it was charged too much.
- **Costs in both eras:** 0.83 bp of price, at least 0.5 pt.

### Two-era grid (1,440 variants, ranked by the worse era)
The top 25 are all **opening-candle direction + with the gap + ATR stop on a 30–60-min range**: Sharpe 0.85–1.1 in *both* eras, a broad plateau, and consistent with Gao et al.'s first-half-hour momentum. Walk-forward over 2006–2024: Sharpe 0.84 (2006–15) and 0.83 (2016–24), 16 of 19 years positive. The 30-min version loses in 2025–26 (Sharpe −0.88), though, so the best range length drifts.

### 🧺 OR-length ensemble (ORB v1 rules on 5/15/30/60-min ranges, ¼ risk each, untuned)
| | 2003–15 | 2016–24 | 2025–26 (spent) |
|---|---|---|---|
| ORB v1 (5m) | Sharpe −0.06 | 1.47 | 1.21 |
| **Ensemble** | **0.89** | **1.50** | 0.41 |
- The ensemble is positive in **20 of 22 years** and roughly halves the worst drawdown. Member correlations are 0.23–0.49.
- **Trailing-Sharpe rotation** among members: about 0.9 / 1.35 / 0.75. Mixed against equal weights, so it isn't adopted. The trailing year currently weights **100% on 5m**.

### Mechanism: leveraged ETFs
- **ORB-5's yearly Sharpe vs leveraged-ETF dollar volume** ((TQQQ + SQQQ + QLD) × 3 / QQQ): correlation **+0.60**, Spearman +0.66, over 2006–2026.
- **30m and 60m:** about 0.
- The 5m Edge appeared as leveraged-ETF flows grew, which fits the theory that front-running the rebalancing flow makes the very first move persist.
- **Caveat:** both series trend upward over time, so 0DTE or retail flows could be the true driver. This is supporting evidence, not a rule.

### Status
- **Forward Test** (from 2026-09-30): both **ORB v1** and the **Ensemble** are logged daily by `tools/forward_test.py` (Windows task "ORB Forward Test", weekdays 23:30 local time).
- **Deflated Sharpe** of ORB v1 in-sample is about 0.79, so no real money until the Forward Test agrees.

## ORB Ensemble in TradingView (2026-09-29)
- The new saved script **"ORB Ensemble"** (`pine/orb_ensemble.pine`) runs on MNQ1! 5m next to "ORB v0". It has 4 members (E5 / E15 / E30 / E60) with pyramiding 4 and `close_entries_rule = "ANY"`, so each member's exit closes its own entry. Each member risks $100, with a minimum of 1 MNQ. Every entry and exit carries an alert message.
- **Parity with Python on 2026-09-21 … 09-28:** all 14 TradingView trades match the engine's members, with entries within a tick and exits within about 1 point. One Python trade (09-28, 30m) was skipped in TradingView because price was only 1.2 pt on the VWAP side; TradingView's VWAP comes from MNQ 5m bars, the engine's from NQ 1m. Expect rare borderline differences like this.
- **Bug fixed in both scripts:** the stop and target were placed only after TradingView saw the fill, so the fill bar itself was unprotected (on 09-25 E30 lost 96 pt instead of about 39). Now the bracket goes in with the entry order and is refined from the real fill afterwards.
- `tools/push_pine.mjs` now refuses unless the open script's strategy title equals the file's, so one ORB script can never be pushed over another.

## Lessons from the community applied → Ensemble v2 (2026-09-29)
Every candidate had to improve **both** eras on the 23-year base (Sharpe A 2003–15 / B 2016–24 / 2025–26 spent):
| Change | ORB v1 | Ensemble |
|---|---|---|
| Base | −0.06 / 1.47 / 1.21 | 0.89 / 1.50 / 0.41 |
| No target, hold to the close | −0.09 / 1.40 / 0.55 | 0.89 / 1.34 / 0.01 |
| 10R target + trail 0.3 ATR once 2R up | 0.16 / 1.66 / 1.50 | 0.72 / 1.59 / 0.50 |
| EMA200 (1m) trend side | 0.12 / 1.44 / 1.10 | 0.98 / 1.55 / 0.40 |
| 20-day trend side | 0.17 / 1.28 / 0.88 | 0.51 / 1.11 / 0.68 |
| Skip if stop < 4× cost | −0.01 / 1.47 / 1.21 | 0.98 / 1.50 / 0.41 |
| Stress: cost +1 pt | −1.01 / 1.34 / 1.21 | −0.50 / 1.26 / 0.41 |
| **EMA200 + stop floor + trail** | 0.34 / 1.64 / 1.40 (Score $4,038 vs $4,573: drawdown ↑) | **0.92 / 1.64 / 0.49**, Score $2,803 vs $1,998, drawdown 20R vs 30R ✅ |

- **Adopted: Ensemble v2** (`orb.families.ENSEMBLE_V2`). It improves every era, the Score, the drawdown and the losing streak. It is in the Forward Test and in TradingView ("ORB Ensemble", with parity including trailing exits).
- **ORB v1 kept frozen.** Its variant has a better Sharpe but a worse Score because of a larger drawdown.

### Random-direction control (ORB v1, same days and exits, 2016–24)
- Real signal Sharpe **1.39**. Coin-flip direction: mean **0.57** (95th percentile 0.93, best of 300 trials 1.28), so p < 1/300. Opposite direction: **−0.50**.
- **Meaning:** the direction signal is real, and about a third of the Edge comes from *which days* we trade (a gap plus a decisive opening) and the tight-stop / far-target bracket. That bracket works like a cheap option on a trend day, and it is exactly what the community's 1–2R targets throw away.

## ES test of the final rule sets (2026-09-29): not tradable ❌
ES is back-adjusted, with a 0.5 pt (2-tick) round trip, over 2016–2026:
| Rule Set | ES Sharpe 16–24 | ES Sharpe 25–26 | ES years + | NQ Sharpe 16–24 | NQ years + |
|---|---|---|---|---|---|
| ORB v1 | 0.10 | 0.18 | 5/11 | 1.39 | 11/11 |
| Ensemble v1 | 0.23 | −0.13 | 6/11 | 1.44 | 10/11 |
| Ensemble v2 | 0.23 | 0.04 | 5/11 | 1.59 | 11/11 |
- Ensemble v2 yearly Sharpe on ES ranges from −2.1 to +2.6: unstable. Its daily correlation with NQ is 0.52, so ES adds no diversification.
- At a 1 pt cost, v2 shows a *higher* ES Sharpe (0.41), because the stop-size floor then skips ES's small-stop days, and those were the losing days in quiet years.
- **Conclusion:** the Edge is Nasdaq-specific, which is consistent with the tech-momentum and leveraged-ETF mechanism (ORB-5 Sharpe vs leveraged-ETF share: +0.6). Trade NQ/MNQ only; ES stays a control, not a market.

## arXiv ideas tested → Ensemble v3 (2026-09-29)
Source: [[arXiv ORB Sweep]]. Scored on the 23-year base, Sharpe A 2003–15 / B 2016–24 / 2025–26:
| Idea | Ensemble v2 → | ORB v1 → | Verdict |
|---|---|---|---|
| Base | 0.92 / 1.64 / 0.49 | −0.06 / 1.47 / 1.21 | |
| **N1 trend-strength gate** τ ≥ 1.0 (5-min σ, 20 days) | **0.98 / 1.65 / 0.72**; Score $2,803 → **$3,576**; drawdown 20.2 → 14.6R; streak 21 → 18 | mixed | ✅ **adopted = Ensemble v3**. It's a plateau: τ 0.75–1.5 and a 20- or 60-day window all improve |
| N2 earlier exit on VVG days (big gap + big first 30m + high volume) | ±0.02 | ±0.03 | ❌ no effect |
| N4 leveraged-ETF pressure gate (κ·\|gap\|) | B 1.64 → 1.44–1.51 | B 1.47 → 0.75–1.08 | ❌ hurts. The yearly link to leveraged-ETF volume is real, but it doesn't pick days |
| N3 same-slot persistence | On NQ it **reverses** (opposite to stocks): t −2.2 to −3.3 at k = 10–20 days in both eras. As a filter, A 0.76 and 25–26 −0.01 | | ❌ real effect, not tradable |

**Ensemble v3** = `orb.families.ENSEMBLE_V3`. It is in the Forward Test (column `ensemble_v3_r`) and in TradingView "ORB Ensemble", with parity on 09-28. The earlier days are TradingView warm-up, since σ needs 20 days of 5-minute history.

## Trend-Day Engine (learned entries) vs Ensemble v3 (2026-09-30)
**Idea:** instead of 4 fixed OR times, score checkpoints at 5 / 15 / 30 / 45 / 60 / 75 / 90 min with a ridge model on 12 pre-entry features (gap, move, τ, VWAP, EMA, OR range, rel. volume, time, prior-day and 5-day returns, vol regime). Walk-forward yearly on the 23-year base; enter at the first checkpoint whose predicted E[R] ≥ threshold; same bracket as v3. Code: `orb/trendday.py`.
- ⚠️ **The first run showed Sharpe 4–5: a look-ahead bug.** "Previous-day return" was actually *today's* close − yesterday's close (correlation with R 0.32, against ≤ 0.04 for every other feature). It is fixed and documented in the code.
- **After the fix:** best is 1.14 / 1.51 / 0.72 vs **Ensemble v3 1.14 / 1.65 / 0.72**. Other settings range 0.44–1.19 / 1.30–1.74 / 0.02–0.69. The shuffled-label control gives −0.2 / −0.2 / −1.3, so no leak remains.
- **Verdict ❌ not adopted.** The learned model rediscovers the hand-built rules (opening move + gap + trend strength) and doesn't beat them.
- **Meaning:** v3 already captures most of what price-derived features know. Further gains need **new information** (news via Jev, payout-aware design, live execution data), not more models on the same bars.

## Beat Ensemble v3: 10 pre-registered Hypotheses (ADR 0006, registered 2026-09-30, none run yet)
**Common rules.** Base = the 23-year research base, Walk-Forward in both eras (A = NAS100 2003–15, B = NQ 2016–24); 2025–26 is reported but is spent. Costs, ATR and trail are exactly as in v3. Free data only (Yahoo daily ^VIX; BLS release dates). Every variant run counts toward the deflated Sharpe (N = all variants across H1–H10). Parameters below are fixed; a "plateau check" (±50% on the one number) is reported but cannot rescue a fail.
- **Filter / Day Type pass bar:** v3 + Filter beats v3 on Score **and** Prop Score in **both** eras, with Sharpe no lower in either.
- **Portfolio Member pass bar:** daily-R correlation with v3 ≤ 0.3; Score > 0 on its own in both eras; v3 + Member raises the Portfolio Score **and** Prop Score in both eras.
- A pass joins the Forward Test beside v3. It is not traded live until the Forward Test agrees.

| # | Kind | Hypothesis (fixed rule) | Result |
|---|---|---|---|
| H1 | Filter | **VIX calm skip:** no trade when VIX prior close < 20th percentile of its last 252 closes | – |
| H2 | Filter | **VIX shock:** trade only when \|VIX open / prior close − 1\| ≥ 3% (either direction). Only years where the VIX open is a real print (open ≠ prior close on > 90% of days) are used | – |
| H3 | Day Type | **CPI / NFP days:** on 08:30 CPI or NFP release days, trade only the 30- and 60-minute Legs | – |
| H4 | Filter (size) | **Overnight compression:** Globex range (18:00–09:29) < 0.5 × ATR14 → full size, otherwise half size | – |
| H5 | Filter | **NQ leads ES:** take a Leg only if NQ's OR move ÷ its ATR14 exceeds ES's, with the same sign (era B only; A has no ES; the pass bar applies to B + 2025–26) | – |
| H6 | Filter | **Compression yesterday:** trade only after an NR7 or inside day | – |
| H7 | Member | **Against-gap:** on days where the OR candle closes against the gap (days v3 skips), trade in the OR-candle direction with v3's Leg rules | – |
| H8 | Member | **Low-τ VWAP reversion:** on days v3's τ gate blocks (τ < 1), after 10:00 fade the first touch of the 30-min OR high/low; target session VWAP, stop 0.25 × ATR14 beyond the extreme, flat 15:59, one trade per day | – |
| H9 | Member | **Globex extreme breakout:** after 09:35, first break of the overnight high/low, entry in the break direction; stop 0.10 × ATR14, v3 trail, flat 15:59, one trade per day | – |
| H10 | Member | **Prior-day extreme breakout:** as H9 with the prior Session's high/low as the level | – |

Run order: H7, H8, then H1–H6, then H9, H10. If none pass, Ensemble v3 stays the best Rule Set.
