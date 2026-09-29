---
title: arXiv ORB Sweep
created: 2026-09-29
tags: [research, orb, arxiv, intraday-momentum, leveraged-etf, 0dte, nq]
---

# arXiv ORB Sweep

A systematic sweep of arXiv for opening-range, first-period momentum, gap and intraday index-futures papers, done on 2026-09-29. Back to [[ORB]] · See also [[Edge Hunt Log]], [[ORB Literature Review]], [[Intraday Edges Research]].

> [!info] How the sweep was done
> - **arXiv API** (`export.arxiv.org/api/query`): 74 queries (phrase and AND queries, `all:`, `abs:` and `ti:` fields), up to 200 hits each. Terms: opening range (breakout), intraday momentum, intraday time-series momentum, first half hour / first 30 minutes, overnight gap / return / drift, leveraged ETF (rebalancing), 0DTE / zero-day / zero days to expiration, intraday return predictability, market open, opening auction / hour, gap trading, breakout strategy, day trading, last half hour, end of day, gamma hedging, E-mini, Nasdaq, QQQ, SPY, TAIEX, Hang Seng, Nikkei, DAX, crude oil, VWAP, noise area, stocks in play, relative volume, volatility breakout. That gave 691 unique papers, 376 of them in q-fin / stat / econ / cs.LG / cs.CE.
> - **arxiv.org/search** (the web search, abstracts shown): 38 more queries, up to 200 hits each. That gave 1,692 papers, 360 of them in finance or statistics categories.
> - **Web search restricted to arxiv.org** to catch versions of known papers. **Semantic Scholar** rate-limited us after one query; the one that ran found nothing new.
> - Every finance-category title was screened. About 60 abstracts were read in full. **Full PDF text was read for 12 papers** (marked ✅ below).
>
> **Bottom line:** arXiv holds very little ORB or first-period-momentum work. The classic papers (Gao, Baltussen, Zarattini, Holmberg, TORB, Lou–Polk–Skouras, Dim–Eraker–Vilkov) are on SSRN or in journals, not arXiv. The arXiv hits worth our time are: (a) three recent MNQ papers by one independent author, (b) new mechanism papers on leveraged-ETF rebalancing (Korea 2026) and on why fast trend-following died, and (c) a few older physics-style papers on intraday scaling and periodicity.

---

## 1. Every relevant arXiv paper found

Relevance: 5 = directly testable on NQ with our data; 1 = background only. ✅ = full text read; A = abstract only.

| arXiv id | Title | Year | Market | Method | Key result | Rel. |
|---|---|---|---|---|---|---|
| [2605.04004](https://arxiv.org/abs/2605.04004) ✅ | Structural Limits of OHLCV-Based Intraday Momentum Signals in MNQ Futures (Mesfin) | 2026 | MNQ 5m, 2021–25 | 14 signal families, expanding walk-forward, 2 pt round-trip friction | ORB 30-min long bar+15: +2.82 pt, T = 0.88 (fail). Gap-continuation short: +14.5 pt net, T = 1.46, only 35 trades. **Positive controls:** London Signal B T = 4.30, RTH Confluence T = 3.11 | 5 |
| [2605.11423](https://arxiv.org/abs/2605.11423) ✅ | A Validated Volatility-Volume-Gap (VVG) Classifier for Regime Identification in MNQ (Mesfin) | 2026 | MNQ 5m, 2021–25 | Day classifier: \|gap\|, \|first-30m return\| and first-bar relative volume all in the top tercile | 4.4% of days. 77.6% reverse from their intraday peak by the close; mean giveback 11.7 pt; next-day spread +25.6 bp. No directional rule passed (best T = 1.46) | 5 |
| [2605.17724](https://arxiv.org/abs/2605.17724) A | Sequential Structure in Intraday Futures Data: LSTM vs Gradient Boosting on MNQ (Mesfin) | 2026 | MNQ 5m, 2021–25 | GBM and LSTM predicting close > 10:30 open + 10 pt | OOS accuracy 50.0–50.9% vs a 51.8% base rate; permutation p ≥ 0.135. No edge | 3 |
| [2501.16772](https://arxiv.org/abs/2501.16772) ✅ | Trends and Reversion in Financial Markets on Time Scales from Minutes to Decades (Safari & Schmidhuber) | 2025 | 24 futures incl. S&P, DAX, Nikkei, Eurostoxx; 14 yrs of minute data | Next-minute return regressed on the trend t-stat (linear, cubic and quintic terms) | Below about 1 hour, **weak trends mean-revert** (b = −0.91%, t = −13.6) and strong trends revert less (cubic +0.26%, t = +4.6). From a few hours to a few years, markets trend | 4 |
| [1202.2447](https://arxiv.org/abs/1202.2447) ✅ | Ensemble properties of HF data and intraday trading rules (Bassi, Baldovin, Stella et al.) | 2012 | S&P 500 index, 10-min bars, 1985–2010 | Morning returns scale as t^D with D ≈ 0.35 (not 0.5). Time-of-day quantile band from 10:00; trade the band break, exit when price re-crosses the band | +2.7 to +4.9 bp per trade. Out of sample (rolling 15-yr calibration) 2000–10 beats the GARCH benchmark. Index, no costs | 4 |
| [1005.3535](https://arxiv.org/abs/1005.3535) ✅ | Intraday Patterns in the Cross-section of Stock Returns (Heston, Korajczyk & Sadka) | 2010 | US stocks, half-hour bars, 2001–05 | Return at lags of 13, 26, … half-hours (the same time on earlier days) | Same-half-hour continuation persists for 40+ days. It is strongest in the **first and last half-hours** (decile spread > 11 bp in the opening half-hour). Short-term reversal lasts < 1 h | 4 |
| [2608.03703](https://arxiv.org/abs/2608.03703) ✅ | Preying on Leveraged ETFs (Zhao) | 2026 | Korea single-stock LETFs; US controls (QQQ, SMH, SPY) | Model plus DiD. Rebalance = A·(L²−L)·r, executed at the close | Speculators **pre-position from the open** on overnight news, then unload into the close. About 75% of the day's news move reverses by the next close. US effects are small (Ivanov–Lenkey etc.) | 4 |
| [2608.22768](https://arxiv.org/abs/2608.22768) ✅ | The Loop-Gain Matrix: Coupled Rebalancing Feedback… | 2026 | Korea LETF complex; US MSTR/COIN | Reduced-form estimator of the loop gain from cross-asset overnight reversals | Samsung imports about 41% of its closing displacement from the SK Hynix LETF complex. **US estimate is null** because US closing venues are deep | 3 |
| [2607.01550](https://arxiv.org/abs/2607.01550) ✅ | Is Trend Still Your Friend? The Demise of Short-Term Trend-Following | 2026 | About 100 futures, 1995–2025, daily | EWM trend signals, CTA proxy, split by tick size | Fast trend Sharpe 0.84 → 0.12 after 2009. Equity indices and FX died. The survivors are **large-tick** contracts, where HFT still leaves depth; loop: trend trades → impact → trend | 4 |
| [2504.20116](https://arxiv.org/abs/2504.20116) ✅ | Compounding Effects in Leveraged ETFs: Beyond the Volatility Drag Paradigm | 2025 | SPY, QQQ and their LETFs, about 20 yrs | AR(1)-GARCH, regime switching | LETF payoff depends on return autocorrelation: daily-rebalanced LETFs win in momentum regimes. QQQ has a larger compounding effect than SPY | 2 |
| [2512.17923](https://arxiv.org/abs/2512.17923) ✅ | Inferring Latent Market Forces: LLM Detection of Gamma Exposure Patterns | 2025 | SPY options, 242 days of 2024 | GEX computed from open interest; LLM obfuscation test | By their GEX calculation, every day in 2024 had negative gamma (threshold −$2B). 0DTE hedging pattern "detected". Weak for trading | 2 |
| [2607.09426](https://arxiv.org/abs/2607.09426) ✅ (skimmed) | The Quarter-Hour Effect: Periodic Algorithmic Trading and Return Predictability in Crypto Futures | 2026 | Binance perpetuals | Clock-phase autocorrelation map | Quarter-hour **opening returns are predictable out of sample** from same-phase lags (average R²_OOS 2.46%). Opening order imbalance predicts 4–12 h returns | 3 |
| [2201.00223](https://arxiv.org/abs/2201.00223) ✅ / [2010.01727](https://arxiv.org/abs/2010.01727) / [2107.12516](https://arxiv.org/abs/2107.12516) / [1811.04994](https://arxiv.org/abs/1811.04994) | Knuteson: Strikingly Suspicious Overnight and Intraday Returns (series) | 2018–22 | Global indices incl. Nasdaq, Nikkei, DAX, HSI, TAIEX | Split into overnight and intraday returns | Overnight returns are hugely positive and intraday returns negative for decades. His hypothesis: a large quant firm expands its book in the morning. Implies a **short bias intraday** | 3 |
| [2507.04481](https://arxiv.org/abs/2507.04481) A | Does Overnight News Explain Overnight Returns? | 2025 | US stocks | Supervised topic model on 2.4M articles | News topics explain much of the overnight-minus-intraday gap and the continuation and reversal patterns between the two sessions | 2 |
| [0903.0993](https://arxiv.org/abs/0903.0993) A | Statistical analysis of the overnight and daytime return | 2009 | 2,215 NYSE stocks, 1988–2007 | Distributions and cross-correlations | Overnight and daytime returns are **anti-correlated** (gap-fade tendency at the stock level) | 2 |
| [1509.08079](https://arxiv.org/abs/1509.08079) A | Asymmetry of cross correlations between intra-day and overnight volatilities | 2015 | US stocks | Correlation of \|returns\| | \|Overnight\| predicts the **following** day's intraday volatility much better than the preceding one. Supports a gap-size filter as a volatility proxy | 3 |
| [1309.5806](https://arxiv.org/abs/1309.5806) A | Fine structure of volatility feedback II: overnight and intra-day effects (Blanc, Chicheportiche, Bouchaud) | 2013 | US stocks | ARCH split by session | Overnight volatility is almost entirely feedback. Intraday and overnight returns behave very differently | 1 |
| [2607.03669](https://arxiv.org/abs/2607.03669) A | Split-Session Cluster GARCH for Overnight and Intraday Returns | 2026 | US stocks | Multivariate GARCH | Tails differ sharply between the overnight and intraday sessions | 1 |
| [2511.06177](https://arxiv.org/abs/2511.06177) A | Push-response anomalies in high-frequency S&P 500 price series | 2025 | SPY NBBO, about 1,500 days | Conditional response to a standardized "push" | Efficient below about 5,000 ticks. Beyond that, large pushes get non-zero responses, and **large down-pushes rebound more** than up-pushes | 2 |
| [2508.06788](https://arxiv.org/abs/2508.06788) A | Returns and Order Flow Imbalances: Intraday Dynamics and Macro News Effects | 2025 | ES, 1-sec | SVAR per 15-min slot | On macro news, price impact rises and flow impact falls; shocks die within 1 s | 1 |
| [2006.08307](https://arxiv.org/abs/2006.08307) A | HMMs Applied to Intraday Momentum Trading with Side Information | 2020 | Futures (unspecified) | 2–3 state HMM; realized-vol ratio and intraday seasonality as inputs | Side information via splines predicts returns; no P&L after costs | 2 |
| [2602.18912](https://arxiv.org/abs/2602.18912) A | Overreaction as an indicator for momentum: AAPL | 2026 | AAPL 1–15 min | ML plus Twitter emotion | Behavioral momentum dominates at about the **10-min** frequency | 1 |
| [2604.26063](https://arxiv.org/abs/2604.26063) A | Volume-Price-Adjusted MACD for US Equity Indices | 2026 | SPX, NDX, DJIA daily | Calibrated 2018–22, OOS 2023–26 | Beats plain MACD OOS; daily, not intraday | 1 |
| [2607.06117](https://arxiv.org/abs/2607.06117) A | Relief-Gated Relative Rotation for QQQ-DIA | 2026 | QQQ / DIA daily | Walk-forward | Sharpe gains only; daily | 1 |
| [2501.03171](https://arxiv.org/abs/2501.03171) A / [2505.17388](https://arxiv.org/abs/2505.17388) A | CSI 300 index futures lead-lag and order-flow-imbalance papers | 2025 | CSI 300 IF | Microstructure | Futures lead spot; OFI dynamics. No opening-range content | 1 |
| [1702.07374](https://arxiv.org/abs/1702.07374) A | Time series momentum and contrarian effects in the Chinese stock market | 2017 | China indices | TSMOM, daily and longer | Short-run TSMOM, long-run contrarian | 1 |
| [2106.08420](https://arxiv.org/abs/2106.08420) A | Trend-Following Strategies via Dynamic Momentum Learning | 2021 | 56 futures, daily | Dynamic classifier choosing among look-backs | Beats naive TSMOM. Idea: learn member weights (analogous to our OR-length ensemble) | 2 |
| [2603.05862](https://arxiv.org/abs/2603.05862) A / [2010.13036](https://arxiv.org/abs/2010.13036) A | LETF–futures arbitrage and LETF rebalancing in artificial markets (Nikkei LETFs) | 2020, 2026 | Simulated Nikkei futures | Agent-based simulation | Rebalancing moves futures prices; splitting orders reduces impact; arbitrage transfers liquidity between the two markets | 2 |
| [2603.07600](https://arxiv.org/abs/2603.07600), [2603.29430](https://arxiv.org/abs/2603.29430), [2605.22792](https://arxiv.org/abs/2605.22792) A | 0DTE and ultra-short option pricing (differential ML, Edgeworth++, density extraction) | 2026 | SPX 0DTE | Pricing | No return or momentum evidence; pricing only | 1 |
| [2511.22766](https://arxiv.org/abs/2511.22766) A | Beta-Dependent Gamma Feedback and Endogenous Volatility Amplification | 2025 | Theory | Dealer delta-hedging loop | Stability condition for gamma squeezes | 1 |
| [2201.09319](https://arxiv.org/abs/2201.09319) A | Option Volume Imbalance as a predictor for equity market returns | 2022 | Index options | Volume split by participant class | Market-maker put/call imbalance predicts **overnight** returns | 2 |
| [2307.11012](https://arxiv.org/abs/2307.11012) A | Fast and Furious: Robinhood users' intraday behavior | 2023 | US stocks | Hourly reactions | Retail buys big losers within an hour; more attention to overnight moves | 1 |
| [2112.15108](https://arxiv.org/abs/2112.15108) A | Modeling and Forecasting Intraday Market Returns: ML | 2021 | S&P, 1-min | LSTM / RF rolling | VIX is the strongest intraday predictor; RF adds nothing | 1 |
| [1802.01921](https://arxiv.org/abs/1802.01921) A | Dynamical regularities of US equities opening and closing auctions | 2018 | US stocks | Auction microstructure | Indicative opening price mean-reverts with imbalance | 1 |
| [2609.14859](https://arxiv.org/abs/2609.14859) A | Gate Design in Retail Prop-Trading Evaluations | 2026 | Prop-firm futures accounts | Contract geometry | Break-even is a 40.5–41.5% win rate at 1:1.5 net; passing is not evidence of skill. Relevant to the Account Profile | 2 |

**Searched, no relevant arXiv paper exists:** "opening range breakout" beyond Mesfin; Gao/Baltussen-style market intraday momentum; TORB; Zarattini/Concretum; SPY/QQQ noise area; TAIEX, HSI or crude-oil intraday ORB; empirical 0DTE-and-momentum studies (all on SSRN; see [[Intraday Edges Research]]).

---

## 2. Detail on the most relevant papers

### 2.1 Mesfin (2026a), arXiv 2605.04004: the negative control, and its two *positive* controls ✅
Already known as a negative control. **What we had not used:** the two signals the author says *do* survive walk-forward on MNQ 2022–25 (2 pt round-trip friction, idealized stop fills).
- **London Session Signal B:** 15-min bars 03:00–08:30 ET. A 3-state GMM with 5 features (ATR ratio, volume z-score, close position in bar, 15-min return, directional consistency), each rolling-z-scored and then StandardScaled, refit each walk-forward fold. **Go long at the next 15-min open** after a clean transition from Regime 0 (bearish chop) to Regime 2 (bullish drift), with no Regime 1 (extreme volatility) in the prior 2 bars. **Exit at +60 min or 08:30. Stop 20 pt fixed.**
  - Walk-forward OOS: N = 247, **+4.09 pt net, T = 4.30**, win rate 61.5%. Unconditional long over the same window: −0.47 pt.
  - **A one-bar (15-min) delay flips the sign** (T = −2.78). That points to either a bar-boundary artifact or a move that is over within one bar. Treat with suspicion.
- **RTH Confluence:** 5-min bars. GMM regime = "Active Flow", rolling-200-bar Markov P(R1→R2) > 0.15, and 50-bar volume z > 0.5. Enter on a pullback of 25×ATR_ratio pt within 6 bars, exit at bar 13, stop 80×ATR_ratio pt.
  - OOS T = 3.11, +11.8 pt, N = 196.
  - The author ran 53+ combinations first, and the ATR baseline carries a global look-ahead.
- **Gap continuation short (near miss):** a gap-down day where the standardized Kalman velocity on 1-min bars in 09:30–10:00 is above 2.5 (top 0.62%): short.
  - Gross +16.5 pt, net +14.5, T = 1.46. Only 35 OOS trades; 2024 was −11.9.
  - Motivated by the first-half-hour predictability in crude oil documented by Wen et al. (2021).
- **ORB 30-min (09:30–09:55), fixed 75-min hold:** fails. This is consistent with our view that a *fixed hold* throws away the fat right tail that pays ORB v1 (top 5% of trades = 96% of profit).

### 2.2 Mesfin (2026b), arXiv 2605.11423: VVG days reverse late ✅
- **Rule:** all three of these are in the **top tercile of their expanding-window distributions** (minimum 60 days of history):
  - \|overnight gap\|
  - \|09:30–10:00 return\|
  - first 5-min bar volume ÷ its 20-day mean
- **Result (MNQ 2021–25):** fires on 4.4% of days (about 10 a year).
  - The path drifts through the morning, peaks between 14:00 and 15:30, then reverses. 77.6% of VVG days give back from the peak, by 11.7 pt on average, about 1 baseline ATR.
  - Peak timing is bimodal: a 10:30 cluster and a 15:30–16:00 cluster.
  - Mean at 15:30 was +11.2 pt vs −0.5 at the close.
- Directional rules all failed year stability. A 2024 continuation year sits against 2022, 2023 and 2025 reversal years.
- **Our angle:** VVG days are exactly the days ORB v1 trades (with the gap, big first move). The question is not "fade them" but **"exit ORB earlier on VVG days"** (see §3).

### 2.3 Safari & Schmidhuber (2025), arXiv 2501.16772: weak intraday trends revert, strong ones don't ✅
- **Trend strength τ_T** = the t-statistic of the trend over horizon T = 2^k minutes: a weighted sum of past 1-min log returns normalized by volatility, capped at ±2.5. **The first minute of the day is dropped** and the first T minutes are ramp-up.
- **Regression:** R(t+1) = a + b·τ + c·τ³ + d·τ⁵ + e·sign(τ).
  - For T ≤ 16 min: b = −0.91% (t = −13.6), c = +0.26% (t = +4.6), d = −0.04%, e = −0.28% (the tick-bounce step).
  - So **small minute-scale trends revert, and the reversion weakens as |τ| grows**. From a few hours to years the sign flips and trends persist.
- **Meaning for ORB:** a breakout that starts from a *weak* opening move (low |τ|) is fighting minute-scale reversion. A strong one (|τ| ≳ 2) is not. Our "opening-candle direction" is a crude |τ| proxy with no strength threshold.

### 2.4 Bassi / Baldovin / Stella (2012), arXiv 1202.2447: a sub-diffusive morning band ✅
- On the S&P 500 (1985–2010, 10-min bars from 10:00), morning returns scale as **t^0.35**, not t^0.5, so volatility decays through the morning.
- **Rule:** build conditional quantile bands (Q = 5%, 10% or 25%) of the index path from the 10:00 price, conditioned on the first 0, 3, 6 or 9 ten-minute returns.
  - Buy when price crosses above the upper band; sell when it crosses below the lower band.
  - **Close the long when price falls back inside the upper band**, and vice versa. Flat at 16:00.
  - Multiple trades are possible on volatile days, one on trend days, none on quiet days.
- **Result:** +2.7 to +4.9 bp per trade in-sample. Out of sample 2000–10 (rolling 15-yr calibration) it beats the GARCH benchmark every year. No costs; the cash index is not tradable.
- **What's new vs Zarattini's Noise Area:** (1) the band width grows as t^D with D ≈ 0.35 instead of the empirical mean |move| per minute; (2) the **exit is a band re-entry**, not a VWAP or trailing stop. It was profitable in **1985–2010**, which covers the era where ORB-5 fails for us.

### 2.5 Heston, Korajczyk & Sadka (2010), arXiv 1005.3535: same-time-of-day continuation ✅
- A stock's return in half-hour slot h predicts its return in the **same slot on later days** (lags of 13, 26, … half-hours) for 40+ days. It is **strongest in the first and last half-hours**: the daily-lag decile spread earns more than 11 bp in the opening half-hour.
- Explained by institutional order-splitting at fixed times of day, not by volume or spreads.
- The crypto analogue (2607.09426) finds quarter-hour **opening returns** forecastable out of sample from same-phase lags.
- **Meaning for NQ:** if the 09:30–10:00 direction has same-slot persistence (for example from recurring fund or LETF hedging flow), yesterday's and last week's opening direction is a free prior for today's ORB side.

### 2.6 Zhao (2026), arXiv 2608.03703, and the Loop-Gain Matrix (2608.22768): the LETF mechanism ✅
- **Mandated rebalance** = Σ_f A_f·(L_f² − L_f)·r, with r the return up to the close. The coefficient is +2 for a 2× fund, 6 for 3× and −2×, and 12 for −3×. The rebalance is known in sign from the moment r is known.
- **Model:** speculators **pre-position at the open on the overnight news**, which "foreloads the price impact since market opens", then liquidate into the closing auction. This is the story behind "gap + first-candle momentum".
- **Evidence:**
  - In Korea (2026 single-stock LETFs) about 75% of a news day's move reverses by the next close.
  - For the US, the paper and its literature review (Ivanov–Lenkey 2018, Barbon et al. 2022, Murray–Sammon 2026) say index-LETF price effects are **small and absorbed**, because US closing auctions are deep. The loop-gain estimator also returns **nulls** for the US MSTR/COIN complex.
- **Meaning for us:** the mechanism is real, but at US index scale it should show up as a *modest* conditional effect that grows with LETF capital relative to depth. Our +0.60 correlation fits that. It predicts the effect is strongest on **news-gap days** and should rise with Σ A·(L²−L) / (NQ + QQQ dollar depth).

### 2.7 "Is Trend Still Your Friend?" (2026), arXiv 2607.01550 ✅
- **Result:** fast daily trend-following (EWM τ = 5 days) had Sharpe 0.84 before 2009 and 0.12 after. It died in equity indices and FX and survived in rates and commodities.
- **What separates the two groups:** volatility-normalized tick size. Small-tick books (thin depth per tick) let HFTs withdraw liquidity in front of predictable directional flow, which breaks the loop "trend trade → impact → more trend".
- **Tension with our data:** NQ is a *small-tick* contract (0.25 pt on about 20,000) and ES a larger-tick one, yet our ORB works on NQ and not ES. So whatever drives NQ opening momentum is **not** a generic CTA trend loop. It needs a **predictable, price-insensitive flow** (LETF rebalancing, dealer short gamma, retail 0DTE) that is large relative to NQ's depth. That supports the LETF/0DTE story over a behavioral-underreaction story.

---

## 3. New to us: ideas not yet tested, with parameter grids

Ranked by (prior evidence × fit with our data × low overfit risk). All should go through the standard judge: **Walk-Forward 2016–24, two-era check (NAS100 2003–15), then the Forward Test**. Test each as a **filter or exit on the existing ORB v1 / Ensemble** first, and as a standalone only where stated. Keep grids small: the DSR penalty is already heavy.

### N1. Trend-strength gate on the opening move (Safari & Schmidhuber)
- **Rule:** at each ensemble member's entry time (09:35 / 09:45 / 10:00 / 10:30), compute τ = the t-stat of the 1-min log-return path since 09:31, excluding the first minute: τ = Σ r_i / (σ_1m · √n), where σ_1m is the trailing 20-day 1-min standard deviation at the same time of day, capped at ±2.5.
  - Take the member's trade only if sign(τ) = trade side and **|τ| ≥ τ*.**
- **Grid:** τ* ∈ {0, 1.0, 1.5, 2.0} (0 = current rule) × σ window {20, 60} days. That is 8 cells, applied identically to all 4 members.
- **Why it could fix 2003–15:** the paper's minute-scale reversion is strongest in exactly the weak-open cases that ORB-5 trades.
- **Expected:** fewer trades and a higher win rate. Kill it if the Ensemble's Sharpe in the worse era drops.

### N2. Late exit on VVG days (Mesfin 2605.11423)
- **Rule:** VVG = \|gap\|, \|09:30–10:00 return\| and 09:30–09:35 volume ÷ its 20-day mean all ≥ the expanding-window percentile p (minimum 250 days of history).
  - On VVG days, override the 15:59 time exit with an exit at time X, or a trailing stop of k × ATR14(5m) from the intraday peak active after 14:00.
- **Grid:** p ∈ {67, 75} × X ∈ {14:00, 15:00, 15:30, 15:59 (control)}, and separately k ∈ {1, 2} (10 cells).
- **Why:** 16% of our trades close at 15:59 for +4.4R. If 78% of VVG days give back about 1 ATR from the peak, that tail is partly left on the table. It needs the 23-year base: about 10 VVG days a year.

### N3. Same-slot persistence prior (Heston–Korajczyk–Sadka)
- **Signal:** S_k = the mean sign (or mean return) of the 09:30–10:00 NQ return over the last k sessions, and separately the same slot exactly 5 sessions ago (weekly lag).
- **Filter:** take ORB members only when sign(S_k) = trade side. Or size ×1.5 when they agree and ×0.5 when they disagree (a size change avoids halving trade count).
- **Grid:** k ∈ {1, 5, 10, 20} × {filter, size-tilt} (8 cells).
- **Diagnostic first:** the regression of r(09:30–10:00, t) on r(09:30–10:00, t−j) for j = 1…20, split by era. Only proceed if the lag-1 or lag-5 t-stat > 2 in both eras.

### N4. LETF rebalancing capital × gap as the regime variable (Zhao 2026)
- **K_t** = Σ_f A_f,t−1·(L_f² − L_f) over the Nasdaq-100 LETFs: TQQQ (6), SQQQ (12), QLD (2), QID (6); optionally add SOXL/SOXS and the NVDA/TSLA single-stock LETFs from 2022, which hedge through the same names.
  - A = AUM, or shares outstanding × price. Use the prior day's value.
- **Normalize:** κ_t = K_t / (20-day mean NQ + QQQ dollar volume).
- **Pre-positioning intensity:** P_t = κ_t × \|gap_t\| / ATR14.
- **Filter:** trade ORB-5 only when P_t ≥ its trailing-252-day percentile q. Also test it as a **selector between members:** weight ORB-5 by the κ percentile and the 30/60-min members by 1 − that percentile.
- **Grid:** q ∈ {0 (control), 30, 50} × {filter, member-weighting} (6 cells).
- **Difference from what we did:** we correlated *yearly* Sharpe with *volume share*. This is a *daily*, gap-conditioned, AUM-based version that follows the paper's mechanism. It needs ETF AUM history (shares outstanding) from 2010 onward.

### N5. Sub-diffusive band with band re-entry exit (Bassi et al. 2012)
- **Standalone Rule Set, from 10:00:**
  - Upper/lower band = O_10:00 × (1 ± z_Q · σ_d · (m/m₀)^D), where m = minutes since 10:00, σ_d = the 14-day mean \|move\| at m₀ = 30 min, and z_Q is the normal quantile.
  - Enter on a 10-min close outside the band. **Exit on a 10-min close back inside the band**, or at 15:59. No target.
- **Grid:** D ∈ {0.35, 0.5} × Q ∈ {10%, 25%} × bar {5, 10 min} (8 cells).
- **Why:** the published evidence covers 1985–2010, the era where our ORB-5 is flat, and the exit logic differs from both ORB v1 and the Noise Area. A candidate 5th ensemble member; check its correlation with ORB-5.

### N6. Pre-market London long (Mesfin Signal B), simplified
- **Rule:** replace the GMM with a transparent proxy on 15-min bars 03:00–08:30 ET:
  - The prior 2 bars had a return < 0 and a range below the 20-day median (chop).
  - The current bar has return > +0.5 × its 20-day σ and a close in the top 30% of its range.
  - Go long at the next bar open. Stop 20 pt NQ-equivalent (scale by ATR). Exit at +60 min or 08:30.
- **Grid:** threshold {0.5, 1.0}σ × stop {fixed 20 pt, 0.1 × ATR14 daily} (4 cells).
- **Why:** it would be uncorrelated with RTH ORB. But it is a single author, reports a sign flip under a 1-bar delay, and uses idealized stop fills. **Also test with a 1-minute delay.** If the edge dies, drop it.

### N7. Gap-down continuation short with a velocity threshold (Mesfin near-miss)
- **Rule:** gap < −g × ATR14, and the 09:30–10:00 1-min velocity (Kalman or EWM slope, standardized over the prior 250 days) < −z. Then short at 10:00 with ORB v1 stop/target logic.
- **Grid:** g ∈ {0.25, 0.5} × z ∈ {1.5, 2.0, 2.5} (6 cells).
- **Why last:** mostly overlaps the ORB-30 member on gap-down days. It fits the asymmetry that our shorts earn more (+0.66R vs +0.44R) and Knuteson's negative intraday drift. Test it as "short-side weight ×1.5 on gap-down + strong velocity" rather than as a new Rule Set.

> [!warning] Budget
> N1–N7 add about 50 cells. At our current trial count that barely moves the DSR threshold, but **pre-register** the cell to promote (for example the median-performing cell of a plateau, not the best), and judge only on the worse era.

---

## 4. Evidence on our mechanism

### Leveraged ETFs
- **For:**
  - Zhao 2608.03703 gives the causal chain we hypothesized: overnight news → a known close rebalance of A·(L²−L)·r → speculators trade in the gap direction **from the open** → the price impact is "foreloaded" into the session.
  - It predicts the effect scales with LETF capital relative to venue depth, which matches our ORB-5 Sharpe vs LETF-share correlation (+0.60). It also matches our finding that 30/60-min members don't correlate: pre-positioning happens *at the open*.
  - 2504.20116 shows daily-rebalanced QQQ LETFs benefit from positive autocorrelation. This is the same feedback seen from the fund side.
- **Against / caveats:**
  - Both 2608.03703 and 2608.22768 say US index LETF effects are **small**, and the loop-gain estimator finds US **nulls** because US closing auctions are deep.
  - The effect on NQ is therefore likely a *conditional tilt*, not a standalone edge. The Korean 75% next-day reversal should *not* be expected at US index scale.
  - The ES failure fits (SPY LETF capital relative to ES depth is far smaller than QQQ LETFs relative to NQ depth).
- **Next test:** N4 (a daily, gap-conditioned κ).

### 0DTE
- arXiv has **no empirical paper linking 0DTE to intraday momentum**. The arXiv 0DTE papers are about pricing (2603.07600, 2603.29430, 2605.22792).
- 2512.17923 reports that by open-interest GEX **every 2024 day was net negative gamma** (below −$2B), attributed to 0DTE. If true, "low-gamma regime" was always on in 2024, which weakens GEX as a day-level switch. That matches our failed GEX switches.
- The empirical 0DTE literature (Dim–Eraker–Vilkov; Adams et al. 2025: 0DTEs *dampen* volatility) is on SSRN and already in [[Intraday Edges Research]].
- **Verdict:** 0DTE remains an untested rival explanation to LETFs. Separate them by testing ORB-5 before and after 2022-05 (daily SPX/XSP expiries), controlling for κ.

### Gap continuation
- **For continuation in NQ:** Mesfin's gap-down continuation near-miss (+14.5 pt, T = 1.46), and VVG days drifting in the gap direction through midday (+11 pt at 15:30).
- **Against, or pointing to reversal:**
  - Stock-level overnight and daytime returns are anti-correlated (0903.0993).
  - Gap-fill fades fail on MNQ at 09:30, 09:45 and 10:00 (T ≈ −0.3 to −0.4), so neither naive fading nor naive continuation works.
  - Knuteson (2010.01727 etc.) finds intraday index returns negative for decades. That argues for a short tilt, which our longs/shorts split (+0.44R / +0.66R) already shows.
- **Gap size as a volatility proxy:** \|overnight return\| predicts *the next session's* volatility (1509.08079). This is a clean reason why our \|gap\| ≥ 0.1 ATR bucket holds most of the profit (the +0.05R vs +0.6–0.8R split): trend days need volatility.
- **Late reversal:** VVG days (big gap, big first move, big volume) usually give back about 1 ATR from a 14:00–15:30 peak. That is a reason to consider an earlier exit (N2), not a fade.

### First-period momentum
- **Minute scale reverts, hour scale trends** (2501.16772, 24 futures). Opening moves that persist must be *strong*, and the persistence shows up over hours, which matches our 10R / EOD payoff structure.
- **Fast trend died post-2009 on small-tick contracts** (2607.01550). A generic trend loop cannot explain NQ ORB; a specific flow is needed (LETF / 0DTE / fund order-splitting).
- **Same-time-of-day persistence is strongest at the open** (1005.3535, 2607.09426), consistent with scheduled institutional or algorithmic flow at 09:30 (see N3).
- **Negative controls on MNQ 2021–25:** fixed-hold 30-min ORB fails (T = 0.88); ML on 5-min OHLCV sequences fails (50.6% vs 51.8% base). Our edge comes from *trade management* (tight 0.1 ATR stop plus a runner) and conditioning (gap, VWAP), not from bar-pattern prediction.
- **Sub-diffusive morning volatility** (D ≈ 0.35, 1202.2447): a fixed-width opening range becomes "wider" relative to remaining volatility as the morning goes on. This may be why 30/60-min ORs behave differently from 5-min ones.

---

## Sources
All arXiv links are in the table in §1. Full texts read: 2605.04004, 2605.11423, 2501.16772, 1202.2447, 1005.3535, 2608.03703, 2608.22768, 2607.01550, 2504.20116, 2512.17923, 2607.09426 (skimmed), 2201.00223.
