---
title: Open-Source Quant Code Review
created: 2026-09-29
tags: [orb, research, code-review, execution, costs, nq, es]
---

# Open-Source Quant Code Review

Back to [[ORB]] · Log: [[Edge Hunt Log]] · Builds on: [[ORB Literature Review]], [[Intraday Edges Research]], [[Community ORB Scripts]]

**Scope.** This note reads the *code* of serious public ORB and intraday-momentum implementations and records what they do that our engine (`orb/backtest.py`, `orb/data.py`) does not. Papers already summarised in the Literature Review are not repeated. Section 5 lists quick diagnostics I ran on our own engine to check the lessons. They are descriptive checks and do not change any Rule Set.

---

## 1. Zarattini / Concretum replications

### 1.1 giovannibrusco/zarattini-2023-orb-qqq: ORB-5 on QQQ, stress-tested
<https://github.com/giovannibrusco/zarattini-2023-orb-qqq> (`src/qqq_opening_bias/backtest.py`, `data.py`, `analysis.py`)
- **Rules:** direction of the 09:30 5-min bar, entry at the 09:35 open, stop at the other side of the bar, 10R target or flat at the close. This is the paper's rule. Our ORB v1 is this rule plus the body, gap and VWAP filters and an ATR stop.
- **Sizing:** `min(risk_fraction*equity/risk_per_share, leverage_cap*equity/entry_price)` with `risk_fraction=0.01, leverage_cap=4.0`. The leverage cap binds on narrow-range days.
- **Costs:** `entry_slippage_per_share` plus an *extra* `additional_stop_slippage_per_share`, charged only when the exit is a stop (`if exit_reason == "stop": per_share_cost += ...`). EOD exits get no slippage.
- **Fills:** the stop fills exactly at `stop_price`, and when stop and target touch in the same bar, the stop counts.
- **DST:** `tz_localize("America/Chicago", ambiguous="NaT", nonexistent="NaT")`. Ambiguous times are dropped, not guessed.
- **Results:** replication without costs gives Sharpe 1.06 (paper-like). **At 2¢/share slippage, Sharpe 0.23 (t = 0.52); break-even is about 2.2¢/share.** An *NQ 09:25 pre-open bar must agree* filter gives Sharpe 0.77 (t = 2.05, n = 844) and beats a QQQ-own-premarket placebo (t = 1.27). But **76% of the filtered PnL is 2022**, and the Sharpe CI [0.05, 1.41] overlaps buy-and-hold.
- **Forward data point (issue #3):** <https://github.com/giovannibrusco/zarattini-2023-orb-qqq/issues/3>. On **ES, Mar–Sep 2026, 129 trades: −0.28R gross**, so the edge was negative before any costs.
- **Lesson for us:** (a) charge stop exits *extra* slippage, separately from the entry; (b) use placebo controls, which test whether a filter's information is specific or just "any momentum proxy"; (c) the NQ pre-open bar is a cheap candidate filter we have never tried.

### 1.2 MQL5 blog: ORB-5 replicated on five indices, "gross reproduced, net zero"
<https://www.mql5.com/en/blogs/post/776235> (no code; method described)
- 2015 → 2026-06, paper rule. Round-trip costs: **NQ 2.5 pt**, SPX 0.8, Dow 4, DAX 2.5, FTSE 1.5. A *minimum risk floor of 2× the round-trip cost* keeps tiny-stop days from exploding the R numbers.
- **Gross avgR:** NQ +0.131 (t = 2.9), SPX +0.119, DAX +0.116, Dow +0.048, FTSE +0.050. **Net:** NQ +0.002, SPX −0.081.
- **Random-direction control:** the same bracket, but long and short every day. The first-candle direction beats it by +0.10 to +0.13R, a real signal, but only about the size of a 2.5-pt round trip.
- **Lesson:** the *raw* first-candle signal exists on both NQ and S&P, so our filters (gap, body, VWAP) must be what separates NQ. The **random-direction control** is the right null for our 10R bracket, and we have never run it.

### 1.3 Concretum's own "Beat the Market" code (SPY, Alpaca/Polygon, Colab)
<https://concretumgroup.com/backtesting-7-years-of-free-data-beat-the-market-an-effective-intraday-momentum-strategy-for-the-sp500-etf-spy/> · <https://concretumgroup.com/coding/>
- Noise area: `move_open` 14-day rolling mean per minute-of-day, `min_periods=13`, then `.shift(1)`. Bands: `max(open, prev_close_adjusted)*(1+band_mult*sigma_open)`, where **`prev_close_adjusted = prev_close - dividend`**, so the gap is corrected for the ex-dividend drop.
- Decisions only at `min_from_open % 30 == 0`.
- **Sizing:** `shares = round(prev_aum/open * min(target_vol/spx_vol, max_leverage))`, with `target_vol=0.02, max_leverage=4`. `spx_vol` is the 14-day std of daily returns.
- **Costs:** `max(0.35, 0.0035*shares)` per order. **No slippage, no DST or half-day code.** The reported 2018–24 Sharpe of 1.95 is therefore commission-only.
- **Lesson:** the gap reference must be corrected for mechanical price jumps (dividends for SPY, **contract rolls for futures**; see 5.1). Their vol-target sizing with a hard leverage cap is the standard.

### 1.4 codecat-ops/zarattini-2024-momentum-spy (SPY and ES, frozen protocols)
<https://github.com/codecat-ops/zarattini-2024-momentum-spy> (`docs/SPEC.md`, `src/sizing.py`, `reports/validation_es.md`, `data/es_1min_rolls.csv`)
- The ES continuous series is built with a **volume-crossover roll plus additive back-adjustment**. The roll log shows ES rolls on the Monday of expiry week with **offsets of +50 to +75 pts** (carry at 4–5% rates). For NQ the same carry is about 4× larger in points.
- Sizing (`sizing.py`): `exposure = min(equity*0.02/sigma_d, 4*equity)`, where `sigma_d` is the 14-day close-to-close std, `.shift(1)`.
- Costs: $0.85 commission + $1.40 fees per side, 0.25 tick of slippage per side, with a mandatory re-run at 0.5 and 1 tick.
- **Half days** are checked explicitly (225 bars, futures close 13:15).
- **Pre-registration:** `PROTOCOL_WALKFORWARD.md` was frozen *before* the run, with one design, a binary success criterion and "no variation will be tried on this sample". The walk-forward re-selection lost to the fixed paper config, the same finding as our Edge Hunt Log (fixed params beat re-tuned).
- **ES 2024-05 → 2026-07:** "final" variant Sharpe −0.07. ES and SPY daily returns correlate at 0.97, so the decay is real and not a data artefact.
- **Lesson:** pre-register every new test in a dated file *before* running it, and use back-adjusted or roll-aware data.

### 1.5 QuantConnect: ORB for Stocks in Play (#18444)
<https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/>
- Entry with `StopMarketOrder` at the OR high/low. Sizing: `(riskSize*TPV/MaxPositions)/(entry-stop)`, capped at `1/MaxPositions` of equity. The 1% stop is ATR-based.
- There is no explicit fee or slippage model in the post; commenters note that costs eat about 25%. The backtest covers only 2016 (Sharpe 2.4). The stop is placed one minute after the entry in the backtest but immediately in live trading.
- **Lesson:** single-year showcase numbers are worthless. The per-position notional cap is the part worth copying.

---

## 2. Open-source index-futures ORB frameworks

### 2.1 s9d9m/backtest ("ORB Lab"): the most rigorous futures ORB code found
<https://github.com/s9d9m/backtest> (branch `claude/adoring-keller-3zp5av`; `RESEARCH_NOTES.md`, `config/instruments.yaml`, `orb_lab/data_sources/futures_roll.py`, `orb_lab/optimization/stress.py`)
- **Costs (`instruments.yaml`):** NQ $0.85 commission + $1.40 fees per side and 1 tick slippage per market or stop fill. **MNQ $0.25 + $0.35 per side, 1 tick.** For MNQ that is 0.6 pt of fees plus 0.5 pt of slippage, about **1.1 pt round trip**.
- **Roll:** `build_front_month` trades, for session *d*, the outright contract with the **highest volume in session d−1** (causal). Rolls only move forward, and prices are raw with no back-adjustment. **Sessions containing two contracts are dropped** (A-06).
- **Sessions:** the XNYS calendar. On early closes the forced exit moves to 5 minutes before the close, and a DST volume-profile check catches misaligned timestamps.
- **A-10 (key finding):** on a *synthetic random walk* that moves several ticks per step, **stop orders showed a +0.045R frictionless "edge"** in 11 of 12 seeds. It vanished with 1-tick steps. Stop fills on bar data are optimistic in fast markets.
- **A-13/A-15:** same-bar ambiguity is resolved on 1-min bars with the stop first. Stops are rounded *away* from entry, and risk is measured from the *actual* fill including slippage. The share of ambiguous exits is reported every run.
- **A-18:** a time exit fills at the exit bar's *open minus slippage*, not at the close.
- **`stress.py` verdict:** ROBUST / FRAGILE / NOT POSITIVE under +0.5…3 ticks of slippage, fixed costs ×1.5/2/3, pessimistic ambiguity, and 1–2 ticks of adverse entry. The combined worst case is +1 tick, 2× costs and pessimistic fills.
- **Lesson:** adopt its stress table as a standard gate. Our engine charges one flat number and has no stop-exit-specific slippage.

### 2.2 Smaller NQ repos (low weight)
- **nessos666/nq-strategy-builder** <https://github.com/nessos666/nq-strategy-builder>: a 60/20/20 IS/OOS/holdout split with grades from PF degradation (example PF 1.61 → 1.38). Costs are not disclosed. The process is fine; the evidence is weak.
- **Dev3mmm/nq-paper-trader** <https://github.com/Dev3mmm/nq-paper-trader>: 15-min ORB with close confirmation on *Dukascopy CFD* data from 2023–26 (PF 1.56–1.74, 1 pt cost), plus a live paper dashboard. It is a single regime on CFD data, so it tells us nothing about futures fills.

---

## 3. Why NQ and not ES? Evidence

| Evidence | Source | What it says |
|---|---|---|
| Intraday momentum is 3× stronger per trade on NQ | Quantitativo <https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq> | Same code and costs from 2010: **NQ +6 bps/trade, Sharpe 1.67; ES +2 bps, Sharpe 1.25**. No explanation given. |
| The first-candle signal exists on both | MQL5 5-index study (1.2) | Gross avgR NQ +0.131, SPX +0.119. The difference is mostly cost relative to the stop. |
| ES first-candle ORB negative recently | brusco issue #3 | ES 2026: −0.28R gross. |
| LETF rebalancing is concentrated late in the day and now large | Benzinga, Jul 2026 <https://www.benzinga.com/etfs/broad-u-s-equity-etfs/26/07/60264868/leveraged-etf-rebalancing-hits-50-billion-as-traders-warn-of-a-powerful-force-now-driving-us-market-vo> | About $50B/day and 1.6% of ES volume. TQQQ/SQQQ rebalance amplifies the *direction of the day* into the close. That fits a 10R hold-to-close ORB, which earns its tail on trend days. |
| SPX 0DTE is mostly dealer long-gamma, which damps trends | Cboe <https://www.cboe.com/insights/posts/the-evolution-of-same-day-options-trading/>; Dim/Eraker/Vilkov (in [[Intraday Edges Research]]) | SPX 0DTE is more than 50% of SPX option volume. QQQ 0DTE doubled in 2024 but is much smaller relative to NQ notional. ES is more gamma-pinned. |
| **Our own diagnostic (5.2)** | `orb/backtest.py` | Part of the "ES fails" result is a **cost-unit artefact**. 1.0 pt on ES = 4 ticks = about 2 bp = **0.22R** at ES's median 4.5-pt stop. |

**Working hypothesis.** Three things make the difference. (1) NQ has more trend-day tail: mega-cap concentration, higher beta, and 3× LETFs whose close-rebalance runs in the day's direction. (2) The cost as a fraction of the stop is lower on NQ, because NQ's tick is 0.125 bp versus 0.5 bp on ES. (3) ES is damped by SPX dealer gamma. Only (2) is proven here; (1) and (3) are plausible but untested.

---

## 4. Execution realism for MNQ at 09:35

- **Fees:** MNQ is about $0.25–0.50 commission plus $0.35 exchange/NFA per side, so **$1.2–1.7 round trip = 0.6–0.85 pt**. This is large next to our 1-pt all-in assumption.
- **Slippage at the open:** practitioner reports on Elite Trader say 0–1 tick in normal conditions and "a few points" on CPI-type events <https://www.elitetrader.com/et/threads/what-is-the-slippage-for-nq-stop-market-orders-during-non-spike-trading-hours.385991/>. ClearEdge's MNQ automation guide uses 1–2 ticks in liquid hours and 1–2 *extra* ticks in volatile periods, because the MNQ book is thinner than NQ's <https://www.clearedge.trading/post/mnq-micro-nasdaq-automation-settings-guide>. Every quant repo reviewed assumes **0.25–1 tick per side**. I found **no public tick-level measurement** of MNQ fills at exactly 09:35:00. We will have to measure it ourselves in the Forward Test.
- **Realistic all-in MNQ round trip:** about 0.7 pt of fees + 1 tick in + 1–2 ticks on stop exits = **1.2–1.5 pt**. In news-open sessions (08:30 CPI/NFP days) it is 2+ pt.
- **Structural points in our favour:** the entry is a *market order at a known time*, not a stop entry, so the A-10 random-walk bias does not apply to entries. The target is a limit (no slippage). Only stop exits (78% of exits) and time exits pay slippage.

---

## 5. Diagnostics run on our engine (descriptive; `orb/backtest.py`, ORB v1 params, all years)

### 5.1 Data bug: unadjusted contract rolls contaminate the gap filter ⚠️
`data/nq_1m_tv.csv` is TradingView NQ1!, which is **not back-adjusted**. The mean gap/ATR on the **Monday of quarterly expiry week** (roll day, offset −4 from the 3rd Friday) is **+0.26 overall, and +0.7 to +1.0 in 2023–25**. In non-quarterly months it is +0.05. That jump is the carry between contracts (about 150–300 NQ pts), not a real overnight gap. On those days (about 4 a year, 15 ORB v1 trades so far) the **gap filter is forced long**. The day's true range (TR) is also inflated, which raises ATR14 and widens the stop for the next 14 days. The effect on P&L is small (those 15 trades happened to be +1.73R average), but it is a correctness bug. It also affects every prev-close feature, including the ES test.

A broader quarterly window, the 10 days up to expiry Friday, gave avgR +0.08 (n = 110) against +0.60 elsewhere. It is noisy across years (5 of 11 positive), so treat it as a watch item, not a filter.

### 5.2 Cost sensitivity and the ES verdict
| | 0 pt | 0.5 pt | 1.0 pt | 0.83 bp | Median stop |
|---|---|---|---|---|---|
| **NQ** avgR / Sharpe (all yrs) | 0.61 / 1.57 | 0.57 / 1.47 | 0.53 / 1.37 | 2016–24: 0.57 / 1.46 | 20 pt (13.9 bp) |
| **ES** avgR / Sharpe (all yrs) | 0.16 / 0.48 | 0.02 / 0.04 | −0.13 / −0.39 | 2016–24: 0.09 / 0.25 | 4.5 pt (10 bp) |

- **ES is weak rather than negative:** gross Sharpe 0.48, 8 of 11 years positive. At a realistic ES round trip (0.5 pt = 2 ticks) it breaks even. NQ is still about 4× stronger per trade, so the edge is mostly Nasdaq-specific, but the Edge Hunt Log's "ES Sharpe −0.46" overstates the failure.
- **NQ early-era fragility:** the median stop was **4.8 pt in 2016–17** and 33–45 pt in 2025–26. At 2 pt round trip, 2016–17 turn flat or negative (−0.02R in 2017), and at 3 pt 2016–17 lose. Today's edge is robust to costs; the early years were not.
- 7.1% of trades are stopped on the entry bar. Exits: 626 stop, 126 time, 56 target.

---

## 6. Actionable changes for our engine and Rule Set (each testable)

1. **Fix the roll handling (bug).** Either build a volume-roll, back-adjusted NQ/ES series, or at minimum compute `gap` and TR on roll Mondays against the *new* contract's prior close (or skip those sessions, as s9d9m A-06 does). Re-run ORB v1 walk-forward and ES. *Pass:* Sharpe within ±0.1 of the current value, with the trade list changing only on roll days.
2. **Scale costs by instrument, not in points.** Use `cost = fees_$/point_value + ticks × 0.25` per side, and charge stop exits an extra 1 tick (Brusco, s9d9m). Defaults: MNQ 0.7 pt fees + 1 tick in + 2 ticks on stop exits; ES 0.09 pt fees + the same ticks. Re-state the ES verdict at equal ticks.
3. **Adopt a stress gate (s9d9m `stress.py`).** Headline results at baseline, +1/+2 ticks per side, 2× fees, and the combined worst case. A Rule Set is **FRAGILE** if moderate stress makes expectancy ≤ 0 in *any* walk-forward year.
4. **Risk floor.** Skip a trade when the stop is < k × round-trip cost (MQL5 uses k = 2; test k = 3–5 on 2016–19 only, then freeze). Evidence: 2016–17 stops of about 5 pt.
5. **Random-direction and placebo controls.** Run the same bracket with a coin-flip direction (100 seeds) and with a shuffled gap sign. ORB v1's edge over the random bracket is the real signal. Report it next to every Score.
6. **Pre-registered NQ-specific filters (one shot each, frozen in a dated file first):** (a) the NQ 09:25–09:30 pre-open 5-min bar agrees with the trade (Brusco, t = 2.05); (b) the *NQ-minus-β·ES* first-5-min return has the trade's sign, meaning a Nasdaq-specific impulse, which tests hypothesis 3.
7. **Notional leverage cap in the Score.** Size = min(risk-based contracts, 4× equity / notional), as in Concretum and Brusco. On tiny-ATR days the DD-capped sizing may assume impossible MNQ counts. Report how often the cap binds.
8. **Time exit at the 15:59 bar open minus 1 tick, and early-close handling.** Exit half days at 5 minutes before the close (s9d9m A-18/A-05). Check that `d.last` on half days is not treated as a normal 15:59 exit.

## Links
- Brusco ORB-QQQ replication: <https://github.com/giovannibrusco/zarattini-2023-orb-qqq> · ES issue: <https://github.com/giovannibrusco/zarattini-2023-orb-qqq/issues/3>
- MQL5 5-index ORB study: <https://www.mql5.com/en/blogs/post/776235>
- Concretum code pages: <https://concretumgroup.com/backtesting-7-years-of-free-data-beat-the-market-an-effective-intraday-momentum-strategy-for-the-sp500-etf-spy/> · <https://concretumgroup.com/coding/> · <https://concretumgroup.substack.com/p/capturing-intraday-edges-a-python>
- codecat-ops SPY/ES replication: <https://github.com/codecat-ops/zarattini-2024-momentum-spy>
- QuantConnect Stocks in Play: <https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/>
- s9d9m ORB Lab: <https://github.com/s9d9m/backtest>
- nq-strategy-builder: <https://github.com/nessos666/nq-strategy-builder> · nq-paper-trader: <https://github.com/Dev3mmm/nq-paper-trader>
- Quantitativo ES vs NQ: <https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq>
- LETF flows (Benzinga 2026): <https://www.benzinga.com/etfs/broad-u-s-equity-etfs/26/07/60264868/leveraged-etf-rebalancing-hits-50-billion-as-traders-warn-of-a-powerful-force-now-driving-us-market-vo>
- Cboe 0DTE evolution: <https://www.cboe.com/insights/posts/the-evolution-of-same-day-options-trading/>
- Slippage anecdotes: <https://www.elitetrader.com/et/threads/what-is-the-slippage-for-nq-stop-market-orders-during-non-spike-trading-hours.385991/> · <https://www.clearedge.trading/post/mnq-micro-nasdaq-automation-settings-guide>
