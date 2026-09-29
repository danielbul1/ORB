---
title: ORB Literature Review
created: 2026-09-29
tags: [research, orb, intraday-momentum, nq, mnq, backtest-candidates]
instrument: NQ / MNQ (1-min bars, RTH open 09:30 ET)
---

# ORB Literature Review

Evidence review of Opening Range Breakout (ORB) and closely related intraday-momentum strategies, filtered for what is **testable on NQ/MNQ 1-minute bars with a 09:30 ET open**. Back to [[ORB]].

> [!info] How to read this note
> - **Verified (full text)** = I read the paper's actual PDF text; rules and numbers are quoted from it.
> - **Abstract / secondary** = only the abstract, author page, or a third-party write-up was available; treat the details as less certain.
> - All published results are **in-sample** unless stated otherwise. Almost none of the sources has a clean held-out period.

---

## 1. Summary table

| # | Source | Type | Instrument / period | Core rule | Headline result | Evidence quality |
|---|---|---|---|---|---|---|
| 1 | Zarattini & Aziz (2023), *Can Day Trading Really Be Profitable?* | SSRN working paper (Verified) | QQQ, TQQQ; 2016-01 → 2023-02 | 5-min ORB in the direction of the first candle, stop at the other end of the 5-min range, 10R target or EOD | QQQ: 675% total, 31%/yr, Sharpe 1.12, 24% win rate, +0.13R/trade. TQQQ: Sharpe 1.18, 46%/yr | Medium: simple, few parameters, but only 7 years, **no slippage**, no out-of-sample period |
| 2 | Zarattini, Barbon & Aziz (2024), *A Profitable Day Trading Strategy for the U.S. Equity Market* | SSRN / SFI RP 24-98 (Verified) | ~7,000 US stocks; 2016 → 2023 | 5-min ORB on "Stocks in Play": relative volume ≥ 100%, top 20, stop = 10% ATR14, EOD exit | Unfiltered: Sharpe 0.48. RelVol top 20: 1,637%, Sharpe 2.81. 5m ≫ 15m ≫ 30/60m | Medium-high for the *filter* idea (within-paper comparison, survivorship-aware data); relevance to one index future is indirect |
| 3 | Zarattini, Aziz & Barbon (2024), *Beat the Market: An Effective Intraday Momentum Strategy for SPY* | SSRN 4824172 (Verified) | SPY; 2007 → 2024-02 | Time-of-day "Noise Area" band breakout, checked every 30 min, trailing stop max(band, VWAP), vol-targeted sizing | 1,985% total, 19.6%/yr, Sharpe 1.33, MDD 25%, net of commission + slippage | **Highest** among the practitioner papers: 17 years, costs *and* slippage modelled, independent replications on ES/NQ (see #4) |
| 4 | Independent replications of #3 (codecat-ops GitHub; Quantitativo) | Replication (Secondary) | SPY 2020 → 2026, ES 2024 → 2026; NQ/ES 2010 → present | Same rules as #3 (frozen), futures costs | SPY Sharpe 1.11; ES OOS consistent; **Sharpe ≈ 0 in 2025-26**. NQ (90-day lookback): Sharpe 1.67, CAGR 24%, MDD 24% | Medium: shows the rules transfer to futures, but also shows **recent decay** |
| 5 | Maróy (2025), *Improvements to Intraday Momentum Strategies…* | SSRN 5095349 (Abstract) | QQQ | #3 with every parameter optimized plus VWAP / ladder exits | Sharpe > 3, > 50%/yr | Low: fully optimized on one instrument, so an overfitting red flag |
| 6 | Gao, Han, Li & Zhou (2018), *Market Intraday Momentum*, JFE 129 | Peer-reviewed (Verified) | SPY 1993 → 2013 (+ 10 ETFs, ES futures in appendix) | Return from the previous 16:00 close to 10:00 predicts the 15:30-16:00 return | Timing strategy 6.67%/yr, vol 6.19%, Sharpe 1.08; after costs (post-2005) 6.52% vs 7.96% gross | High (top journal, out-of-sample R², many ETFs), but a small effect per trade |
| 7 | Baltussen, Da, Lammers & Martens (2021), *Hedging Demand and Market Intraday Momentum*, JFE 142 | Peer-reviewed (Verified) | 60+ futures incl. **NQ**, 1974 → 2020 | Rest-of-day return (previous close → 15:30) predicts the last 30 minutes | Sharpe 0.87-1.73 by asset class, gross. Mechanism: gamma hedging and leveraged-ETF rebalancing | **High**: gives a causal mechanism and includes NQ. Gross of costs; the authors note a positive net Sharpe for ES at 1 tick |
| 8 | Holmberg, Lönnbark & Lundström (2013), *Assessing the profitability of intraday ORB strategies*, FRL 10(1) | Peer-reviewed (Verified via thesis reprint) | Crude oil futures 1983 → 2011 | Enter at Open × (1 ± q), exit at the close | Significantly positive, **but only in the 2001-2011 subperiod** | Medium: honest, shows the edge is **not stable over time** |
| 9 | Lundström (2013/2017), *Day trading returns across volatility states* | Working paper (Verified) | CL and S&P 500 futures, long history | "Long Strangle" ORB: Open ± q, stop = opposite threshold, EOD exit | Returns rise with volatility state: high-vs-low gap about 150 bp/day on S&P, about 200 bp on CL. Out-of-sample profitability depends on the range and is **not robust over time** | Medium-high as a *filter* result |
| 10 | Toby Crabel (1990) book, S&C articles, 2020s Substack | Practitioner (Secondary) | Futures (S&P, T-bonds, grains) | Stretch = 10-day average of min(H−O, O−L). Buy stop at Open + stretch, sell stop at Open − stretch. EOD exit. NR4 / ID / NR7 as setup filters. Early entries are best | NR4 on S&P: about 63% win rate. Crabel himself reports a "gradual decline in \$/contract and Sharpe over time" | Medium for the concepts; no modern audited stats |
| 11 | Syu / Wu et al.: TORB (2018/19) and *Evolutionary ORB* (2021, Knowledge-Based Systems) | Peer-reviewed (Abstract) | DJIA, S&P, NASDAQ, HSI, TAIEX futures 2003-2013 (1-min); TAIEX 2007-2018 | Data-chosen "probing time" as the opening range. GA-optimized thresholds plus stop | Above 8%/yr in all 5 markets (p < 3%). The best probing time is **short for US markets**. Profit targets hurt, stops helped | Medium-low: GA optimization raises data-snooping risk |
| 12 | Zarattini & Aziz (2023), *VWAP: The Holy Grail for Day Trading Systems* | SSRN 4631351 (Abstract) | QQQ/TQQQ 2018 → 2023-09 | Long above VWAP, short below (1-min) | QQQ 671%, Sharpe 2.1, MDD 9.4% | Low-medium: a short sample, and turnover-heavy |
| 13 | Mesfin (2026), *Structural Limits of OHLCV-Based Intraday Signals in MNQ* | arXiv 2605.04004 (Verified) | MNQ 5-min, 2021-12 → 2025-08, walk-forward | 30-min OR (09:30-09:55) breakout, fixed 75-min hold, 2.0 pt RT friction | ORB long: +2.82 pt net/trade, **t = 0.88**, fails. No OHLCV signal passed | Low-medium (single independent author), but a useful **negative control** |
| 14 | tradingstats.net ES/NQ ORB statistics (2014-2026) | Practitioner descriptive stats (Secondary) | ES, NQ RTH | Break, double-break and continuation rates by OR length | NQ 30-min OR: 39% double-break, 71.5% continuation on 5-min close confirmation | Descriptive only, not P&L |
| 15 | Unger Academy, TradeThatSwing, Yordanov NQ tick study | Practitioner (Secondary) | NQ | Various 15- and 30-min ORBs | Anecdotal, short samples, often no costs | Low; used for ideas only |

---

## 2. Source-by-source detail

### 2.1 Zarattini & Aziz (2023): 5-min ORB on QQQ / TQQQ
Link: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622> · PDF mirror: <https://www.wealth-lab.com/api/discussion/download/pdf/6590-ORB-Strategy-pdf> · Concretum page: <https://concretumgroup.com/can-day-trading-really-be-profitable/>

**Rules (verified from Table 1):**
- **Opening range:** the first 5-min candle, 09:30-09:35.
- **Direction:** the sign of the first candle. Up (C > O) means long; down means short. **Doji (O ≈ C) means no trade.**
- **Entry:** at the **open of the second 5-min candle** (09:35), a market order. This is *not* a stop order at the range high or low.
- **Stop:** the low of the first candle for a long, the high for a short. Risk is \$R = entry − stop.
- **Target:** 10R, otherwise **exit at EOD** (market close).
- **Sizing:** Shares = int(min(A·0.01 / \$R, 4·A / P)). That is 1% risk per trade with a 4× leverage cap. Starting capital \$25k.
- **Costs:** \$0.0005/share commission and **no slippage**.

**Results (2016-01-01 → 2023-02-17):**
- **QQQ:** 675% total, 31%/yr, **Sharpe 1.12**, alpha 33%/yr (p = 0.0025), beta ≈ 0. 1,795 trades (51% long / 49% short), **win rate 24%, average +0.13R**.
- **QQQ without the leverage cap:** +1,630%. About 60% of trades were sized 40% below target because of the 4× cap.
- **TQQQ:** 1,484%, 46%/yr, **Sharpe 1.18**, average +0.18R.
- **Sensitivity (Fig. 7 heat map):** the best average R came from a **stop = 5% of ATR14** and **no target (EOD)**. The target grid ran from 1R to 10R plus EOD. The resulting TQQQ run gave +9,350%. The authors say this is unrealistic with slippage: the TQQQ stop was only about \$0.08 wide.

**Skepticism:** the sample is short (7 years, mostly bull and high volatility), there is no slippage, and there is no held-out period. The 5%-ATR result comes from a parameter scan (data mining). The +0.13R average is thin against costs. With 1-min NQ bars, the stop-out fill assumptions matter a lot.

**NQ translation:** NQ ATR14 in 2024-26 is about 250-450 pts. A 10% ATR stop is about 25-45 pts; a 5% ATR stop is about 12-22 pts. A 5-min OR on NQ has a median of about 26 pts (tradingstats), so the "first-candle extreme" stop and a 10% ATR stop are similar in size.

### 2.2 Zarattini, Barbon & Aziz (2024): ORB on Stocks in Play
Link: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284> · PDF: <https://www.wealth-lab.com/api/discussion/download/pdf/8007-ssrn-4729284-1-pdf>

**Rules (verified):**
- **Universe:** price > \$5, 14-day average volume ≥ 1M shares, ATR14 > \$0.50.
- **Entry:** a **stop order at the 5-min high** if the first candle was bullish, or at the **5-min low** if bearish. A doji means no order.
- **Stop:** **10% of ATR14** from the fill. **Exit at EOD.** 1% risk per position, 4× leverage cap, \$0.0035/share commission.
- **Relative Volume** = OR volume (09:30-09:35) ÷ the average OR volume over the prior 14 days. The filter requires RelVol ≥ 100% and trades only the **top 20** by RelVol.

**Results (2016 → 2023, net):**
| Variant | Total | IRR | Vol | Sharpe | MDD | Alpha |
|---|---|---|---|---|---|---|
| ORB base (all stocks) | 29% | 3.2% | 6.6% | 0.48 | 13% | 3.3% |
| **5m ORB + RelVol** | **1,637%** | **41.6%** | 14.8% | **2.81** | 12% | 35.8% |
| 15m ORB + RelVol | 272% | 17.4% | 12.2% | 1.43 | 11% | 16.9% |
| 30m ORB + RelVol | 21% | 2.3% | 11.1% | 0.21 | 35% | 2.8% |
| 60m ORB + RelVol | 39% | 4.1% | 10.2% | 0.40 | 21% | 4.4% |
| COMBO (equal weight) | 234% | 15.8% | 7.9% | 1.99 | 7% | 15.0% |
| S&P 500 buy and hold | 198% | 14.2% | 18.3% | 0.78 | 34% | n/a |

- Average PnL by RelVol: < 100% gives −0.02R; > 100% gives +0.08R; > 3,000% gives +0.38R.
- **Key takeaways for NQ:** (a) **shorter ORs dominate**, and 30- and 60-min ORs were nearly worthless; (b) **abnormal opening activity is the filter that matters**. For a single index future, the analogue is the *time-series* RelVol of the first 5 minutes compared with its own 14-day history. That is an untested translation.
- The paper also cites Tsai et al. (2018): "the most significant profits occur when the opening range length is within 5 minutes" on DJIA, S&P and NASDAQ futures. It cites Wu et al. (2020): profit targets hurt, stops help.
- **Skepticism:** the cross-sectional selection of the top 20 names cannot be reproduced on one instrument. Commission was modelled but slippage was not; slippage matters on a stop order with a 10%-ATR stop in small caps. A QuantConnect replication on 2016 data gave Sharpe 2.4 (<https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/>).

### 2.3 Zarattini, Aziz & Barbon (2024): "Beat the Market" Noise-Area intraday momentum
Link: <https://ssrn.com/abstract=4824172> · PDF: <https://alexandria.unisg.ch/bitstreams/a99aba00-f967-49b3-aceb-f544dc386e0b/download>

This is effectively a **generalized ORB**: the "range" is a time-of-day-dependent volatility band instead of a fixed first-N-minute box.

**Rules (verified):**
1. For each of the last 14 days *i* and each minute HH:MM, compute move = |Close(HH:MM) / Open(09:30) − 1|.
2. σ(HH:MM) = the mean of those moves over the 14 days.
3. **Gap-adjusted bands:**
   - UB = max(Open(09:30), PrevClose(16:00)) × (1 + VM·σ)
   - LB = min(Open(09:30), PrevClose(16:00)) × (1 − VM·σ)
   - The base case uses VM = 1.
4. Signals are checked **only at HH:00 and HH:30**, with the first check at 10:00. The strategy goes long if price > UB and short if price < LB.
5. **Trailing stop:** for a long, max(UB, VWAP); for a short, min(LB, VWAP). The stop is evaluated at the same semi-hourly checkpoints, and positions can re-enter. **Everything is flat at 16:00.**
6. **Sizing:** Shares = AUM × min(4, 2% / σ_SPY,14d) / Open, where σ_SPY is the standard deviation of the last 14 daily returns.
7. **Costs:** \$0.0035/share commission plus **\$0.001/share slippage**. The slippage figure was measured in live trading, from 1,000+ trades and about \$50M notional.

**Results (2007 → 2024-02, net):**
| Variant | IRR | Vol | Sharpe | Notes |
|---|---|---|---|---|
| Stop at the opposite band, 100% notional | 6.2% | 10.9% | 0.61 | Worst day −10.3%, negative skew |
| Current band + VWAP stop | 9.7% | 7.7% | 1.24 | Positive skew, hit ratio 43% |
| **+ vol-target sizing** | **19.6%** | 14.3% | **1.33** | 1,985% total, MDD 25%, beta slightly < 0 |

- **VIX regimes:** Sharpe rises with VIX (about 1.5 for VIX > 6 up to about 3.5 for VIX > 40).
- **Patterns:** trading only after an **NR4** day gave +22 bp/day (t = 5.14); after a Triangle, +14 bp (t = 3.19); NR7 also helped.
- **Day of week:** Wednesday, Thursday and Friday were significant. Monday was *not*, whereas Monday was the best day for the 5-min ORB.
- **VM sweep:** best Sharpe at **VM ≈ 1.5**. Total return falls as VM rises.
- **Mean reversion regressor:** higher RSI(daily) means lower next-day strategy return (β = −3.25, p = 0.001).

**Independent evidence:**
- The codecat-ops replication (<https://github.com/codecat-ops/zarattini-2024-momentum-spy>) froze the parameters. It found SPY 2020-26 Sharpe 1.11 (alpha 16.7%/yr, t = 2.85), ES May-2024 → Jul-2026 correlation 0.97 with SPY, and **Sharpe ≈ 0 over 2025-26**. Walk-forward parameter re-selection *hurt* (Sharpe 0.57 vs 0.92 with fixed parameters). The original parameters beat 27 variants.
- Quantitativo (<https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq>) ran **NQ futures** from 2010 with a 90-day lookback, a 3% vol target and an 8× cap. Costs were \$0.85 commission, \$1.40 fees and 0.25 tick per side. Result: **CAGR 24.3%, Sharpe 1.67, MDD 24%, 38% win rate, payoff 2.25**. The strategy was flat from 2010 to 2017 and did its work from 2018 on.

### 2.4 Maróy (2025): optimized noise-area variants
Link: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349> (abstract only; the PDF was blocked)
- The paper optimizes *all* parameters on QQQ and adds VWAP, "ladder" and VWAP-plus-ladder exits. It claims Sharpe > 3 and > 50%/yr.
- **Use:** only as a list of exit ideas to try. It is not evidence, because this is maximum-overfit territory.

### 2.5 Gao, Han, Li & Zhou (2018): Market Intraday Momentum (JFE)
Link: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866> · <https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301351>
- **Signal:** r1 = the return from the previous day's 16:00 close to 10:00 (this includes the overnight gap). r12 = 15:00-15:30.
- **Trade:** in the last half hour (15:30-16:00), go long if r1 > 0 and short if r1 < 0.
- **Results (SPY 1993-2013):** 6.67%/yr, vol 6.19%, **Sharpe 1.08**, versus −1.11%/yr for always-long in the last half hour. Adding r12 improves results slightly. After transaction costs (post-2005): 6.52% net vs 7.96% gross. The effect is stronger on **high-volatility, high-volume, recession and macro-news days** (FOMC days: 20%/yr). It also holds for ES futures and 10 other ETFs, and out-of-sample R² is positive.
- **Relevance:** the first 30 minutes (including the gap) set the day's direction. This supports a **late-day hold or add-on** rule and a **gap-inclusive direction filter**.

### 2.6 Baltussen, Da, Lammers & Martens (2021): Hedging Demand and Market Intraday Momentum (JFE)
Link: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3760365> · PDF: <https://www3.nd.edu/~zda/intramom.pdf>
- **Data:** 60+ futures, including **NASDAQ-100 futures (NQ)**, 1974-2020.
- **Signal:** r_ROD = the return from the previous close to 15:30. It predicts the 15:30-16:00 return better than the first half hour alone.
- **Results:** Sharpe **0.87-1.73** by asset class (gross). The authors say a positive net Sharpe survives at 1-tick cost in ES.
- **Mechanism:** short-gamma hedging (option dealers) and leveraged-ETF rebalancing force trend-following flows into the close. The effect reverses over the following days.
- **Relevance:** this gives the **economic reason ORB-style trend days should be held to the close**, and it names a regime variable (dealer gamma).

### 2.7 Holmberg, Lönnbark & Lundström (2013): FRL
Link: <https://www.sciencedirect.com/science/article/abs/pii/S1544612312000438> (full text reprinted in Lundström's thesis: <https://www.usbe.umu.se/digitalAssets/195/195397_ues948.pdf>)
- **Rule:** long when price crosses Open × (1 + q), short at Open × (1 − q), exit at the close. There is no money management in the base case.
- **Data:** crude oil futures 1983-2011.
- **Result:** average returns and success rates are significantly above a fair game, **but only in the 2001-10 → 2011-01 subperiod**. That makes it **not robust over time**.

### 2.8 Lundström: Day trading returns across volatility states
Link: <https://www.diva-portal.org/smash/get/diva2:732318/FULLTEXT02.pdf>
- **"ORB Long Strangle":** resting buy and sell stop orders at Open ± q. The stop for either position is the **opposite threshold**. After a double crossing, trading stops for the day. Exit at the close.
- **Findings:**
  - The ORB return rises monotonically with the volatility state: about **150 bp/day** between the highest and lowest states for S&P 500 futures, and about 200 bp/day for crude oil.
  - Out-of-sample, profitability depends on q and the asset, and it is **not robust over time**.
- **Relevance:** this is the strongest academic justification for a **volatility-regime filter**, for example trading only when ATR or realized volatility is above its trailing median.

### 2.9 Toby Crabel: ORB, stretch, and contraction/expansion
Links:
- Crabel's Substack: <https://tobycrabel.substack.com/p/the-evolution-of-the-opening-range>
- S&C article series: <https://store.traders.com/-v06-c09-playing-pdf.html>

**Rules:**
- **Stretch** = the 10-day average of min(High − Open, Open − Low), the distance to the extreme closest to the open.
- **Orders:** buy stop at **Open + stretch**, sell stop at **Open − stretch**. The first fill is the trade and the other order becomes the stop.
- **Exit:** at the close.
- Early moves (the first 5-10 minutes) are best. If the trade is not profitable within about an hour, move the stop to break-even.

**Setup filters:**
- **NR4** (the narrowest daily range of 4 days), **NR7**, **ID** (inside day), and **ID/NR4**. These express the contraction-then-expansion principle.
- Reported: NR4 on S&P futures about 63%+ win rate; ID/NR4 on T-bonds with a 2.34:1 win/loss ratio (1978-86).

**Other points:**
- Crabel's own recent note shows a **gradual decline in \$/contract and Sharpe over time** for a 0.8 × 10-day-range breakout.
- He also warns about **gap-down Mondays** for shorts and observes that **late-week momentum** is stronger.

**Skepticism:** the statistics come from the 1970s-80s, and the book is out of print.

### 2.10 Syu, Wu et al.: TORB and Evolutionary ORB
- TORB: <https://www.researchgate.net/publication/331076454_Assessing_the_Profitability_of_Timely_Opening_Range_Breakout_on_Index_Futures_Markets>
- Evolutionary ORB (Knowledge-Based Systems 216, 2021): <https://www.sciencedirect.com/science/article/pii/S0950705121000320>

**Findings:**
- The probing time (OR length) is chosen by per-minute volume and volatility. On 1-min bars from 2003-2013, the strategy returned **> 8%/yr on DJIA, S&P and NASDAQ futures**, and 20% on TAIEX.
- The **best probing time is short for US markets**.
- In the GA-optimized version, **stops raised the Sharpe to 2.5**, while **profit targets reduced profitability**.

**Skepticism:** the GA optimization is itself a data-snooping risk.

### 2.11 Zarattini & Aziz (2023): VWAP trend
Link: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4631351>
- **Rule:** long when price is above session VWAP, short below (QQQ, 2018 → 2023-09).
- **Results:** QQQ 671%, Sharpe 2.1, MDD 9.4%.
- **Relevance:** supports **VWAP as a trailing stop or confirmation filter** in ORB, as used in 2.3.

### 2.12 Mesfin (2026): falsification study on MNQ (arXiv)
Link: <https://arxiv.org/pdf/2605.04004>
- **Test setup:** 5-min MNQ data, Dec 2021 → Aug 2025. Expanding walk-forward with out-of-sample years 2023, 2024 and 2025. Round-trip friction of **2.0 pts**, which is conservative. Signal at the bar close, entry at the next bar's open.
- **ORB tested:** a 30-min OR (09:30-09:55) breakout with **fixed bar+1 or bar+15 (75-min) holds, not EOD**.
- **Result:** the best variant (long, 75-min hold) made +2.82 pts net/trade on 447 out-of-sample trades, **t = 0.88**. It fails. A pullback entry had an 80.7% stop-out rate at a 20-pt stop.
- **Lessons:**
  - A **30-min OR with a short fixed hold is not an edge on MNQ**, consistent with the poor 30-min result in 2.2.
  - Costs of about 1-2 pts per round trip kill small-edge signals.
  - Use EOD or trend-following exits, not fixed short holds.

### 2.13 Descriptive ES/NQ ORB statistics (tradingstats.net, 2014-2026)
Link: <https://tradingstats.net/orb-breakout-strategy-guide/>

| NQ, RTH | 5-min OR | 15-min OR | 30-min OR |
|---|---|---|---|
| Median range | 26.5 pts | 40.25 pts | 51.5 pts |
| OR / ATR14 | 0.18 | 0.29 | 0.37 |
| Double-break rate | 69% | 53% | 39% |
| First-break continuation (5-min close confirmation) | 63% | 67% | 71.5% |
| Reaches a 1.0× OR extension | 58.5% | 37.9% | 25.6% |

- Upside breaks beat downside breaks by 8-10 percentage points. OR width is tiered by OR/ATR: narrow < 0.3, wide > 0.6.
- **Caveat:** these are descriptive statistics, not P&L. A higher "continuation %" for longer ORs does not mean more profit, because the remaining move is smaller.

### 2.14 Other practitioner sources (low weight)
- **Unger Academy:** Crabel-style 30-min ORB on NQ with a \$2k stop, a \$5k target and EOD exit. The average trade was thin. Restricting shorts to Fridays improved it, which is a classic data-mined filter. <https://ungeracademy.com/blog/testing-toby-crabel-s-opening-range-breakout-does-it-really-work-code-backtest-on-nasdaq>
- **TradeThatSwing:** 15-min OR on NQ with a 5-min close confirmation, long-only, OR cap of 0.8% of price, target = 0.5 × OR, stop at the other side. Win rate 75%, PF 2.5 on a single year with no costs. That is regime-fitted and anecdotal. <https://tradethatswing.com/opening-range-breakout-strategy-up-400-this-year/>
- **Yordanov NQ order-flow study:** 159 sessions of MBO data. Continuation is higher when the opening delta agrees with the breakout. It is too short a sample. <https://researchpaperfilteropen.vercel.app/>

---

## 3. Cross-cutting conclusions

1. **Hold to the close; don't cap winners.**
   - Zarattini's heat map favours EOD over targets. Wu et al. found targets hurt. Gao and Baltussen show the last 30 minutes *continue* the day's move, driven by gamma and leveraged-ETF hedging flows.
   - The ORB edge is a *right-tail* edge: win rates of 24-45% with large winners.
2. **Short opening ranges beat long ones.**
   - 5m ≫ 15m ≫ 30/60m on stocks. Tsai reports "within 5 minutes" is best for US index futures, and TORB found US probing times are short.
   - The 30-min MNQ ORB failed a walk-forward test.
3. **Tight, volatility-scaled stops** (5-10% of ATR14) raised average R in-sample, but they are extremely sensitive to slippage and 1-minute bar fill assumptions. On NQ a 10% ATR stop is about 25-45 pts, which is workable. A 5% stop is about 12-22 pts, which is marginal once you add 1-2 ticks of slippage.
4. **Filters with real support:**
   - Volatility regime (Lundström; VIX results in 2.3; Gao's high-volatility days).
   - Abnormal opening volume (the RelVol result in 2.2).
   - Contraction days: NR4/NR7/ID (Crabel; t = 5.1 for NR4 in 2.3).
   - Macro-news and FOMC days (Gao).
   - Day-of-week effects are **inconsistent across papers**: Monday was best for the ORB but not significant for noise-area momentum. Treat them as data-mining risk.
5. **Decay is real.**
   - HLL: profitable only 2001-2011.
   - Crabel: \$/contract declined over decades.
   - Noise area: Sharpe ≈ 0 in 2025-26 (replication); flat on NQ in 2010-2017.
   - Expect regime dependence and plan walk-forward and held-out tests.
6. **Costs:** on MNQ, budget about 1.0-2.0 pts per round trip (commission and fees about \$1.0-1.5 RT ≈ 0.5-0.75 pt, plus 1 tick of slippage per side ≈ 0.5 pt). Stress-test at 2× that.

---

## 4. Candidate rule sets to backtest on NQ

Ranked by **strength of evidence**, strongest first. The common scaffolding is below.

**Data and timing:**
- NQ/MNQ 1-min RTH bars. Open = the 09:30 bar's open. PrevClose = the 16:00 RTH close, not the 17:00 settlement.
- Back-adjusted continuous contract, rolled at volume crossover.

**Execution:**
- Signals on the bar close; fills at the next bar's open plus slippage.
- A stop is filled at max(stop, bar open) when the bar gaps through it.
- Costs: 1.0 pt RT for MNQ base case, stressed at 2.0 pts.
- Forced flat at 15:59 (test a 15:55 variant).

**Sizing:**
- Fixed-fractional risk of 0.5-1% of equity per trade, contracts = floor(risk\$ / (stop_pts × \$2)), capped by margin. Alternatively, vol-target (see A).

**Validation:**
- In-sample 2012-2019, validation 2020-2022, **held-out 2023-2026** (touch it once).
- Report Sharpe, CAGR, MDD, PF, average R, trades, and the percentage of P&L from the top 5% of days.

### A. Noise-Area intraday momentum (Zarattini/Aziz/Barbon 2024), NQ port. **Evidence: strongest**
- σ(t) = the mean over N days of |Close(t)/Open − 1|, per minute-of-day. **N ∈ {14, 30, 60, 90}**, with the baseline at 14.
- UB = max(Open, PrevClose)·(1 + VM·σ) and LB = min(Open, PrevClose)·(1 − VM·σ). **VM ∈ {1.0, 1.25, 1.5, 2.0}**, with the baseline at 1.0.
- Check at **HH:00/HH:30 starting 10:00**. Test check intervals of {15, 30, 60} min.
- Long above UB, short below LB. Trailing stop is max(UB, VWAP) for longs and min(LB, VWAP) for shorts, evaluated at checkpoints. Test also every minute.
- EOD exit.
- Size: equity × min(L_max, target / σ_daily14) / (price × \$20), with **target ∈ {1.5%, 2%, 3%}** and **L_max ∈ {2, 4}**.
- Why first: 17 years net of slippage, replicated on ES/NQ futures, and a known mechanism. Watch for the 2025-26 decay.

### B. Zarattini 5-min directional ORB (QQQ paper), NQ port. **Evidence: strong-medium**
- OR = 09:30-09:35. Direction = sign(C5 − O5). Skip if |C5 − O5| < **d × ATR14, d ∈ {0, 0.01, 0.02}** (doji filter).
- **Entry variants:**
  - (B1) market at 09:35 open, as in the paper.
  - (B2) stop order at the 5-min high or low in the candle's direction, as in the stocks paper, valid until **{10:30, 12:00, 15:00}**.
- **Stop:**
  - (a) the other extreme of the first 5-min candle, or
  - (b) **k × ATR14 from entry, k ∈ {0.05, 0.075, 0.10, 0.15, 0.20, 0.25}**.
- **Target ∈ {none/EOD, 3R, 5R, 10R}**, with EOD as the baseline.
- One trade per day, no re-entry.
- Expected profile: win rate 20-30%, average +0.1-0.2R gross. **Fill modelling of tight stops is the crux.**

### C. B + time-series Relative-Volume and volatility-regime filters. **Evidence: medium**
- **RelVol5** = NQ volume 09:30-09:35 ÷ the mean of the same window over the prior 14 days. Trade only if **RelVol5 ≥ {1.0, 1.25, 1.5, 2.0}**.
- **Volatility regime:** trade only if **ATR14 / ATR100 ≥ {0.9, 1.0, 1.1}**, *or* VIX (or VXN) at the open ≥ its 60-day median.
- Test RelVol and volatility separately and then combined. Keep the filter count at 2 or fewer to limit snooping.
- Basis: 2.2 (RelVol: −0.02R without it vs +0.08R with it), 2.8 (the volatility state gap), and 2.3 (VIX).

### D. Crabel stretch ORB with a contraction filter ("Long Strangle"). **Evidence: medium (academic plus a long practitioner history)**
- Stretch = the 10-day mean of min(H−O, O−L) on RTH daily bars. Test a lookback of {5, 10, 20}.
- Buy stop at **Open + m·stretch**, sell stop at **Open − m·stretch**, with **m ∈ {0.5, 0.75, 1.0, 1.5}**.
- Stop = the opposite threshold (the Lundström strangle). Alternative stop: 0.5 × stretch.
- No new trades after the double-cross day. EOD exit. Orders active until {11:00, 13:00, 15:00}.
- **Setup filter:** trade only when yesterday was **NR4, NR7, or ID** (RTH ranges). Compare with the unconditional version.
- Optional: move the stop to break-even if the trade is not in profit after 60 minutes (Crabel).

### E. First-half-hour / rest-of-day momentum into the close (Gao 2018; Baltussen 2021). **Evidence: strong academically, thin per-trade**
- **Signal:** r_ROD = PrevClose(16:00) → 15:30 return. Alternatively r1 = PrevClose → 10:00 (Gao).
- **Trade 15:30 → 16:00** in the direction of the sign. Threshold |r| > **{0, 0.25, 0.5} × σ_daily**.
- **Use two ways:**
  - (E1) as a standalone strategy, which should be cost-stress-tested hard because the edge per trade is only a few bp;
  - (E2) as an **overlay**: in A–D, only exit early before 15:30 if the position is against r_ROD, otherwise hold to 16:00; or **add ½ unit at 15:30** when aligned.
- Stronger on FOMC, CPI and NFP days and on high-volatility or high-volume days.

### F. 15-min ORB with close confirmation (practitioner standard). **Evidence: medium-low**
- OR = 09:30-09:45 (also test 10 min). Entry = the first **1-min or 5-min close beyond the OR** by a buffer of **{0, 0.05, 0.10} × OR width**, valid until {11:00, 12:00}.
- Stop ∈ {opposite OR side, OR midpoint, 0.10 × ATR14}. Exit ∈ {EOD, 1.0× OR-width target, VWAP-cross trailing stop}.
- **OR width filter:** trade only if OR/ATR14 ∈ **[0.15, 0.45]**. Skip very wide ORs, which are already exhausted.
- Basis: 2.2 (15m Sharpe 1.43 on stocks) and the NQ descriptive statistics. The 15-min ORB is weaker than the 5-min version in every direct comparison.

### G. Gap-direction-aligned ORB (combines Gao's r1 with the ORB). **Evidence: medium-low (a combination, never tested as a unit)**
- As in B, but trade only when the first-candle direction **agrees with the overnight gap sign** (Open vs PrevClose), with |gap| ≥ **{0, 0.1, 0.25} × ATR14**.
- Also test the inverse: skip large gaps > **{0.5, 0.75} × ATR14**, which may be exhausted.
- Basis: Gao's r1 is measured from the *previous close*, so the gap is part of the momentum signal. The noise-area bands in A are gap-anchored.

### Not recommended as primary
- A **30- or 60-min OR with a fixed short hold** (failed in 2.2 and 2.12).
- **Fully optimized** exits (Maróy style).
- **Day-of-week filters.** Evidence conflicts across papers (Monday is best for the ORB but not for noise-area momentum; Unger's Friday-only shorts). Report the day-of-week breakdown as a diagnostic only.

---

## 5. Links
- Zarattini & Aziz 2023 (ORB QQQ): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622
- Zarattini, Barbon & Aziz 2024 (Stocks in Play): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284
- Zarattini, Aziz & Barbon 2024 (Beat the Market): https://ssrn.com/abstract=4824172
- Maróy 2025: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349
- VWAP paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4631351
- Gao et al. 2018: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866
- Baltussen et al. 2021: https://www3.nd.edu/~zda/intramom.pdf
- Holmberg et al. 2013: https://www.sciencedirect.com/science/article/abs/pii/S1544612312000438
- Lundström volatility states: https://www.diva-portal.org/smash/get/diva2:732318/FULLTEXT02.pdf
- Crabel: https://tobycrabel.substack.com/p/the-evolution-of-the-opening-range
- TORB (Syu et al.): https://www.researchgate.net/publication/331076454
- Evolutionary ORB (Wu et al. 2021): https://www.sciencedirect.com/science/article/pii/S0950705121000320
- Mesfin 2026 (MNQ falsification): https://arxiv.org/pdf/2605.04004
- Replication (SPY/ES): https://github.com/codecat-ops/zarattini-2024-momentum-spy
- Quantitativo ES/NQ: https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq
- ES/NQ ORB statistics: https://tradingstats.net/orb-breakout-strategy-guide/
