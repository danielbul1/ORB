# Top TradingView Indicators — how they work, why, and do they work on NQ

2026-09-30. Code: `research/fetch_top_indicators.mjs` (find + download), `orb/jev_indicators.py` (Jev reads the code), `research/indicator_nq_test.py` (NQ test). Data: `research/top_indicators.json`, `research/indicator_profiles.csv`, `research/indicator_nq_test.csv`.

## How the "best" list was built
- 90 category searches on TradingView's public library (trend, momentum, SMC, volume, ICT, ML, …) → **3,147 unique indicators**, ranked by likes (the all-time "agree" count).
- The top 150 open-source ones had their Pine code downloaded (pine-facade). Closed-source (LuxAlgo Signals & Overlays, Price Action Concepts, …) can't be read.
- **Jev** read all 150 codes (cleaned of drawing code) and answered 4 typed questions (family, core math, output, market belief) and 10 yes/no questions (repaints, pivot lag, volume, HTF, alerts, ATR-scaling, crossover, divergence, session time, >10 params). 0 errors.

## What Jev found (top 150 by likes)
| Family | # | likes (sum) |
|---|---|---|
| Market structure / SMC (BOS, CHoCH, order blocks, FVG, liquidity) | 31 | 907k |
| Trend following (SuperTrend, ATR trails, MA ribbons) | 36 | 822k |
| Support / resistance levels (pivots, trendlines, zones, sessions) | 28 | 742k |
| Momentum oscillators (Squeeze, WaveTrend, MACD, ADX) | 21 | 628k |
| Volume (profile, VFI, volume zones) | 16 | 312k |
| Mean-reversion bands (BB, Nadaraya-Watson) | 6 | 164k |
| ML / stats (Lorentzian, SuperTrend AI) | 3 | 80k |

- Core math: **pivot swings in 51 of 150** — the single most common building block. Then moving averages (22), oscillators (19), ATR bands (19).
- What they bet on: **levels hold or break (64)**, trend persistence (47), mean reversion (21).
- **54% can repaint** (Jev p > 0.5) and **35% only know a signal several bars later** (pivots need N right-side bars), yet draw it back at the pivot bar.
- 37% have more than ~10 signal-changing inputs (curve-fit risk). Only 45% define alerts.

**Why the most-liked are popular:** the top SMC/level tools draw swings, order blocks and trendlines *after* the pivot is confirmed, back at the pivot bar. On a historical chart every level looks perfectly placed, so they look like they "work". In real time that information arrives 5–50 bars late. That is the main reason visual popularity ≠ edge.

## Workflow of the top indicators (from their code)
**1. Smart Money Concepts [LuxAlgo] — 170k likes.** Finds swing highs/lows at two sizes (swing = 50 bars, internal = 5). A close through the last swing high/low in the trend direction is a *BOS*, against it a *CHoCH* (trend change). The last opposite candle before the break becomes an *order block*; 3-candle gaps are *fair value gaps*; near-equal highs/lows are *liquidity*. Belief: stop orders cluster at swings; large players leave footprints where the move started. Lag: a swing is known only 5/50 bars later.
**2. Squeeze Momentum [LazyBear] — 117k.** Bollinger Bands inside Keltner Channels = volatility compressed ("squeeze on", black cross). When BB expand out of KC the squeeze "fires"; the histogram (linear-regression of price minus the mid of the 20-bar range and SMA) gives the direction. Belief: quiet → big move. Note: the published code builds the BB with the **KC multiplier 1.5, not its own 2.0 input** (a bug everyone copies), so it flags more squeezes than intended.
**3. SuperTrend [KivancOzbilgic] — 83k.** Line at hl2 ± 3×ATR(10) that only ratchets in the trend's direction; flips when price closes through it. Belief: trends persist; ATR scaling adapts to volatility. No lag, no repaint.
**4. MACD custom (ChrisMoody) — 82k.** MACD 12/26/9 with multi-timeframe option. EMA-difference momentum; cross of signal line / zero line. Belief: trend persistence.
**5. S/R Levels with Breaks [LuxAlgo] — 65k.** Pivots with 15 left / 15 right bars become S/R; a close through them with the volume oscillator (EMA5 vs EMA10 of volume) > 20% is a "Break". Levels are drawn 16 bars back (offset) — lag.
**6. Market Structure Break & Order Block [EmreKb] — 62k.** ZigZag swings → MSB → order blocks. Same idea as #1.
**7. WaveTrend [LazyBear] — 61k.** Channel index of hlc3 vs its EMA(10), smoothed EMA(21) = wt1, SMA(4) = wt2. Buy = wt1 crosses up wt2 below −53/−60 (oversold). Belief: mean reversion. (Also the core of VuManChu Cipher B.)
**8. UT Bot Alerts [QuantNomad] — 59k.** An ATR trailing stop with key value 1 × ATR(10) — a tight SuperTrend; Buy/Sell when price crosses it. Many flips.
**9. ICT Killzones + Pivots [TFO] — 57k.** Draws Asia/London/NY session boxes and their highs/lows. Belief: time of day and session extremes matter. No signal.
**10. Trendlines with Breaks [LuxAlgo] — 53k.** Pivot-anchored trendlines with ATR/stdev slope; break = signal. Jev: 0.83 repaint, 0.84 lag.
**11. Bollinger + RSI Double Strategy [ChartArt] — 49k.** Enter when RSI(6) crosses 50 in the same bar that price re-enters BB(200, 2). Mean reversion, rare.
**12. ADX and DI — 45k.** Wilder DI+/DI− and ADX(14); trend when ADX > 20, direction by DI.
Others worth knowing: Lorentzian Classification (k-nearest neighbours on RSI/WT/CCI/ADX features, "similar past states repeat"), Nadaraya-Watson Envelope (Gaussian kernel smoothing ± 3×MAE; the default drawing **repaints**), Chandelier Exit (highest close − 3×ATR(22) trail), Volume Flow Indicator (volume-weighted money flow over 130 bars).

## Do they work on NQ? (default rules, no tuning)
Test: each indicator's default signal on a continuous RTH-only chart, signal on bar close → fill next bar, flat at every Session close, costs 0.83 bp round trip (≥ 0.5 pt). 23 years: Era A 2003-15 (NAS100 index), Era B 2016-24 (NQ), 2025-26 shown for information.

Sharpe after costs (gross %/yr in brackets):

| Indicator | TF | A 2003-15 | B 2016-24 | 2025-26 | trades/day |
|---|---|---|---|---|---|
| SuperTrend | 5m | −0.29 (+13%) | **+0.74** (+18%) | +0.35 | 2.6 |
| SuperTrend | 15m | −0.37 | +0.63 (+13%) | −0.96 | 1.5 |
| Chandelier Exit | 15m | −0.14 (+9%) | +0.70 (+14%) | −1.51 | 1.7 |
| UT Bot | 15m | −0.21 (+19%) | +0.55 (+16%) | −1.06 | 3.5 |
| UT Bot | 5m | −4.36 (−7%) | −0.83 | −1.42 | 10.0 |
| MACD 12/26/9 | 15m | −0.79 | +0.44 | −1.29 | 2.6 |
| ADX and DI | 15m | −0.61 | +0.39 | −1.27 | 1.6 |
| SMC structure breaks (5-bar) | 15m | −0.28 | +0.38 | −0.54 | 1.0 |
| Squeeze Momentum | 15m | −0.13 | +0.36 | −1.48 | 0.8 |
| S/R Breaks [LuxAlgo] | 15m | −0.48 | +0.30 | −0.82 | 0.2 |
| Bollinger + RSI | 5m | −0.03 | +0.18 | +0.79 | 0.3 |
| Volume Flow Indicator | 15m | −0.41 | −0.01 | +0.96 | 1.6 |
| WaveTrend | 5m | −1.86 (−3%) | −1.06 (−4%) | −0.08 | 1.7 |
| Nadaraya-Watson (non-repaint) | 5m | −1.03 (−2%) | −1.07 (−7%) | +0.10 | 0.9 |
| CM RSI-2 | 5m | −2.07 | −0.45 | −0.73 | 3.3 |
| *Long every Session* | 5m | −0.33 | +0.19 | +0.38 | 1.0 |
| **Ensemble, 4 OR lengths (ours, orb/long.py)** | — | **+0.89** | **+1.50** | | |

(Full table incl. 5m/15m for all: `research/indicator_nq_test.csv`.)

### What this says
1. **No top indicator is positive after costs in both eras.** None comes close to our OR-length Ensemble (Sharpe 0.89 / 1.50).
2. **Trend-following ones (SuperTrend, Chandelier, UT Bot on 15m) are the only family with a real gross edge** (+9 to +19%/yr before costs in both eras). NQ trends intraday — the same effect ORB trades. Their daily P&L correlates **+0.3** with our Ensemble, so it's partly the same edge, harvested less efficiently (in the market all day, 1.5–3.5 round trips/day → costs eat it; in Era A everything is lost to costs).
3. **Mean-reversion ones (WaveTrend, Nadaraya-Watson, RSI-2) lose even before costs** — fading intraday NQ moves is betting against the effect that exists.
4. Faster = worse: UT Bot on 5m flips 10×/day and its gross edge turns negative.
5. 2025-26: the trend-followers turned negative on 15m, consistent with the known 2025-26 decay of intraday momentum (see Edge Hunt Log).
6. The most-liked SMC / S/R tools are mostly *drawing* tools; their tradeable part (structure breaks) is a weak, slow trend-follower on NQ. Their popularity comes largely from hindsight drawing (lag/repaint), not from forward edge.

### Caveats
- Only default rules were tested, on the Session only (no overnight holding), one market. Many of these tools are meant to be read by a discretionary trader, not traded mechanically.
- Era A volume is index tick volume; volume-based tools are less reliable there.
- Python ports not yet checked bar-for-bar against TradingView (Parity). If any indicator is ever promoted it needs Parity first.
- This is descriptive research, not a Hypothesis: it spends none of the ADR 0006 budget and changes nothing in the live rule sets.

## Takeaway
The "best" TradingView indicators by likes are visual structure tools; by evidence on NQ, the only useful ingredient is **intraday trend persistence** (SuperTrend-style ATR trails), which ORB/Ensemble v3 already captures more efficiently with one trade per Leg per day. If we ever use one, the candidate is a SuperTrend/Chandelier **trailing exit** or trend-state Filter for Ensemble v3 — which would have to be pre-registered as a new Hypothesis (ADR 0006 budget is spent, so a new ADR would be needed).
