---
title: Intraday Edges Research
created: 2026-09-29
tags: [research, intraday, nq, late-day-momentum, gamma, fomc, mean-reversion, methodology, backtest-candidates]
instrument: NQ / MNQ (1-min bars, RTH 09:30-15:59 ET, flat by the close)
---

# Intraday Edges Research: non-ORB edges for NQ

This note looks for intraday edges on US index futures that are **not** the morning ORB and that may be uncorrelated with it. Back to [[ORB]]. It builds on [[ORB Literature Review]] and [[ORB Backtest Results]]; the ORB, Noise-Area, Crabel and Holmberg/Lundström papers are not repeated here.

> [!info] Evidence labels
> - **Verified (full text)**: I read the PDF text. The numbers are quoted from it.
> - **Abstract / secondary**: I only saw the abstract, a third-party write-up, or a vendor statistics page. Treat the details as less certain.
> - All results are **in-sample and gross of costs** unless stated otherwise.

> [!abstract] TL;DR
> 1. **Late-day momentum is the best-documented non-ORB edge, and it includes NQ.** The return from the previous close to 15:30 predicts the 15:30-16:00 return (Baltussen et al. 2021: NQ slope 6.36, t = 7.97, out-of-sample R² 3.76%, 1996-2020). The **unconditional effect has been flat in 2022-2026** in an SPX retest, but it **survives on short-gamma days** (t = 3.1). So test it **conditioned on regime** (low GEX, high volatility, large move so far).
> 2. **The mechanism works in reverse, too.** When dealers are *long* gamma, intraday moves tend to **reverse** (Dim-Eraker-Vilkov 2024; Barbon et al.). That gives an **anti-trend, midday VWAP fade on high-GEX days**, which should be structurally uncorrelated with the ORB.
> 3. **Event days:** the pre-FOMC drift has **disappeared since 2015** (Kurov et al. 2021). The **FOMC post-announcement reversal** (fade the pre-announcement move from 14:00 to the close; Baglioni & Ribeiro 2022) is newer and less arbitraged, but it only fires about 8 times a year, so use it as an overlay.
> 4. **Failed-breakout fades** (Turtle Soup, 80-20, Oops, liquidity grabs) have mostly **anecdotal or decayed** evidence on US index futures, and the one rigorous MNQ test failed after costs. Test them, but with low priors.
> 5. **Free regime data is available:** SqueezeMetrics daily GEX/DIX from 2011 (`https://squeezemetrics.com/monitor/static/DIX.csv`) and CBOE VIX/VIX3M/VIX9D/VXN CSVs. That makes the gamma hypotheses testable now.

---

## 1. Late-day / intraday momentum (priority 1)

### 1.1 Gao, Han, Li & Zhou (2018), *Market Intraday Momentum*, JFE 129. Partially verified (full-text grep)
- Link: <https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301351> · PDF: <https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/ee7dac49-530b-4950-b5d0-e0b5eee08f2e.pdf>
- **Rules:** r1 = previous close (16:00) → 10:00, which includes the gap. r12 = 15:00-15:30. Trade 15:30 → 16:00 in the direction of sign(r1), or of r1 and r12 when they agree.
- **Results:** SPY 1993-2013, Sharpe 1.08 (details in [[ORB Literature Review]] §2.5).
- **Conditioning (verified):**
  - Predictability **rises with first-half-hour volatility**: R² is 0.6% in the low tercile and 3.3% in the high tercile.
  - It is also higher on **high-volume, recession and macro-news days**.
  - r12 matters more after the 2008 crisis.
- **Decay:** the paper already shows a weaker slope outside the crisis. For later evidence see 1.4.

### 1.2 Baltussen, Da, Lammers & Martens (2021), *Hedging Demand and Market Intraday Momentum*, JFE 142. **Verified (full text)**
- PDF: <https://academicweb.nd.edu/~zda/intramom.pdf>
- **Windows:**
  - ON = previous close → open; FH = first 30 min; M = FH end → close − 60; SLH = close − 60 → close − 30; LH = the last 30 min.
  - **r_ROD = ON + FH + M + SLH**, i.e. the previous close to 15:30.
- **Trade:** hold LH in the direction of sign(r_ROD). There is no threshold in the paper.
- **NQ-specific result, 1996-04 to 2020-05, 6,017 days (Table B1):**
  - ROD slope **6.36** (t = 7.97), R² 4.10%, **R²_OOS 3.76%**.
  - For comparison, ES has slope 6.18 (t = 4.97) and R²_OOS 2.29%.
  - **NQ is the strongest US equity contract in the sample.**
- **Economic size (my arithmetic):** the slope is ×100 in the table, so the effect is about 0.064 × r_ROD.
  - A move of r_ROD = 1% predicts about **+6.4 bp** in the last half hour. At NQ ≈ 20,000 that is about **13 NQ points**, against our 1.0 pt round-trip cost.
  - A move of 0.3% predicts about 4 points.
  - **So the edge is only cost-viable on big-move days, which argues for a threshold.**
- **Mechanism (verified, Table 7):**
  - The effect comes from **dealer short-gamma hedging** plus leveraged-ETF rebalancing.
  - On **negative-NGE days** (NGE = net gamma exposure, from SqueezeMetrics / OptionMetrics) the slope is large and significant.
  - On **positive-NGE days** the slope is 0.82 (t = 1.03), which is **not significant**.
  - Yesterday's LH return enters with a *negative* sign, so there is no same-slot seasonality.
- **Costs:** gross results only. The authors say the effect is net-positive in ES at 1 tick.
- **Subsamples:** 1974-99 and 2000-20 are similar.

### 1.3 Leveraged-ETF rebalancing and option imbalances
- **Cheng & Madhavan (2010):**
  - The rebalancing demand is **AUM × L(L−1) × r_day**, where L is the leverage.
  - The factor L(L−1) is 6 for 3x, 12 for −3x, 2 for 2x and 6 for −2x.
  - The trade is **always in the direction of the day's move** and executes at or near the close.
  - In 2009 it was 16.8% of market-on-close volume on 1% days and 50.2% on 5% days (secondary source).
  - For NQ the relevant funds are TQQQ, SQQQ, QLD and QID, plus single-stock levered ETFs on mega-caps.
- **Barbon, Beckmeyer, Buraschi & Moerke**, *Leveraged ETFs, Option Market Imbalances, and End-of-Day Price Dynamics* (abstract verified) <https://portal.northernfinanceassociation.org/viewp.php?n=2240036708>
  - Large **negative** aggregate gamma relative to dollar volume gives **end-of-day momentum**. Large **positive** gamma gives **end-of-day reversal**.
  - The **LETF effect is larger** than the option-gamma effect.
  - It **reverts at the next open**, which fits a pure price-pressure effect.
- **Current size:** leveraged-ETF rebalancing reached about $50 bn per day in mid-2026 (Benzinga, secondary). JPM estimated about $15 bn of rebalancing sales on 2024-09-03, when the Nasdaq-100 fell 3%, and ES fell 34 points in 17 minutes into the close. So the flow is **larger than ever** and concentrated in 15:45-16:00.
- **Cross-section (for context only): Baltussen, Da & Soebhag, *End-of-Day Reversal* (2023)** <http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/EndofDayReversal_withnames.pdf>
  - *Individual stocks* reverse in the last 30 minutes: 3.45-4.45 bp/day long-short, driven by short-sellers' end-of-day risk management.
  - This is **independent of market intraday momentum**. It is not directly tradable on NQ, but it explains why single names and the index can disagree into the close.
- **Bogousslavsky (2021, JF)**, *The Cross-Section of Intraday and Overnight Returns*: mispricing factors earn returns up to the last half hour and then reverse, as arbitrageurs de-risk before the close. Also cross-sectional.

### 1.4 Decay evidence, 2020-2026
| Source | Sample | Finding |
|---|---|---|
| FirmTape retest (dev.to) <https://dev.to/firmtape/intraday-momentum-is-dead-in-the-0dte-era-we-measured-it-on-1085-spx-sessions-43g0> (Secondary) | SPX, 1,085 sessions, 2022-04 → 2026-08. Predictor = open → close − 30, target = last 30 min | Unconditional slope +0.006 ± 0.009 (t = 0.6); **flat in every year** with alternating signs. **On dealer-short-gamma days at 15:30 (≈15% of sessions): slope +0.055, t = 3.1.** |
| Dim, Eraker & Vilkov (2024), *0DTEs: Trading, Gamma Risk and Volatility Propagation* <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4692190> (Abstract) | SPX 0DTE era | Market-maker 0DTE gamma is **on average positive**. Positive gamma **strengthens intraday reversal** and negative gamma strengthens momentum. |
| Adams, Dim, Eraker, Fontaine, Ornthanalai & Vilkov (2025) <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5641974> (Abstract) | SPX | 0DTEs **dampen** volatility. Changes in hedging needs predict stronger order-flow reversals and **lower momentum returns**. |
| Wu & Zhu (2023, EFMA), *HFT and Intraday Momentum* <https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2023-UK/papers/EFMA%202023_stage-4455_question-Full%20Paper_id-31.pdf> (Verified intro) | 120 US stocks, 2008-09 | More HFT means weaker intraday momentum. Momentum is stronger on **macro-news days, positive-return days, and low-liquidity / high-volatility days**. The LH return reverses the next day. |
| Li, Sakkas & Urquhart (2022), JFM <https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf> (Abstract) | 16 developed markets | Intraday TS-momentum holds in and out of sample. It is stronger with **low liquidity, high volatility and discrete news**. |
| Concretum, *Breaking the Rules of Intraday Trading* (2026) <https://concretumgroup.com/breaking-the-rules-of-intraday-trading/> (Secondary) | SPY 2006-2026 | The Noise-Area intraday momentum baseline, **flat at the close, has Sharpe 0.88** (versus 1.33 in the 2007-24 paper). That is decay, consistent with our NQ holdout of 0.32. |

> [!warning] Implication
> Unconditional "trade the last 30 minutes in the direction of the day" is **probably dead in 2022+**. The surviving version is **regime-conditional**: short gamma, high volatility, a big day move, and possibly news days. The 0DTE era has pushed dealers net long gamma on most days, which argues for **reversal** most of the time and **momentum** only in stress.

---

## 2. Failed-breakout / reversal (fade) strategies (priority 2)

### 2.1 Connors & Raschke, *Street Smarts* (1995): Turtle Soup, Turtle Soup +1, 80-20. Rules from the book as formalized by MQL5 (Secondary)
- **Turtle Soup (long):**
  - Setup: today makes a new **20-day low**, and the previous 20-day low was **at least 4 sessions earlier**.
  - Entry: buy stop **5-10 ticks above the previous 20-day low**, after price has traded below it that day.
  - Stop: 1 tick below today's low. Trail it; the hold is intended to last from hours to a few days.
- **Turtle Soup +1:** the new-20-day-low day **closes** at or below the prior 20-day low. Next day, buy stop at the prior 20-day low.
- **80-20:**
  - Setup: yesterday **opened in the top 20% and closed in the bottom 20%** of its range, and that range was larger than average.
  - Trigger: today trades **≥ 5-15 ticks below yesterday's low**.
  - Entry: buy stop at yesterday's low. Stop: today's low. Then trail.
  - Short = the mirror image. The book's own numbers came from Moore Research on 1980s-90s futures.
- **Modern tests:**
  - 80-20 on FX 2011-16 (MQL5 <https://www.mql5.com/en/articles/2785>): barely profitable; it only works in trending phases.
  - Turtle Soup on daily data 2000-2020: profit factor 1.86, DD 11.5% (vendor claim, unverified; <https://www.mql5.com/en/articles/2717>).
  - **No rigorous 1-min NQ test found.**

### 2.2 Larry Williams "Oops" (failed gap beyond the prior day's range)
- **Rules:** open **below the prior day's low**; buy stop at the prior low; exit at the close or at the first profitable open. The short is the mirror.
- **Evidence:**
  - Williams reported 86% winners and PF 3.02 on S&P 1982-98, with "no Thursday" (a data-mined day filter).
  - **Unger Academy on DAX 2010-2026:** about €163k profit, but **losses in 2023-25**. They attribute this to 24-hour trading shrinking the gaps. <https://ungeracademy.com/blog/we-tested-larry-williams-oops-pattern-the-results-might-surprise-you>
- **Decay: yes.** ES/NQ trade nearly 24 hours, so an RTH gap beyond PDH/PDL is only a "session gap".

### 2.3 Quantitative NQ descriptive statistics on fade setups (tradingstats.net, 2015-2025, RTH; Secondary, no P&L)
- **Initial Balance (09:30-10:30):**
  - Breakout rates: single-up 40.6%, single-down 33.0%, double 22.6%, none 3.8%.
  - After a failed first break, price goes on to break the *other* side only **27.1% (up-fail) / 22.6% (down-fail)** of the time. So "failed breakout → full reversal" is **not** the common case on NQ. <https://tradingstats.net/initial-balance-breakout-statistics/>
- **IB retests:** after a breakout and a retest of the IB level, continuation beats reversal up to about 1.4× IB extension. **Beyond 1.4× reversals dominate** (1.5×: 18% continue vs 27% reverse).
  - Time of day matters: at the 1.2× extension, continuation is 58% at 10:30-12:00 but only **23% at 14:00-16:00**.
  - Speed matters: fast moves continue 62% of the time and slow grinds 42%. <https://tradingstats.net/initial-balance-retest-statistics/>
- **Gap fill, 2,791 NQ days:**
  - 60.3% of gaps fill by the close.
  - Fill rate by gap size: tiny gap (< 0.3 ATR) **77.8%**, 0.3-0.7 ATR 42%, 0.7-1.2 ATR 25.6%, > 1.2 ATR 8.2%.
  - Tiny gap + first 15-min candle toward the fill: **93.1%** fill.
  - Median MAE for tiny-gap fades is 27.8 pts; P90 is 130 pts. <https://tradingstats.net/gap-fill-strategy/>

### 2.4 Rigorous negative evidence
- **Mesfin (2026), arXiv 2605.04004:** 14 signal families on MNQ, 5-min, 2021-2025, walk-forward, 2-pt round-trip friction. The families include **liquidity grabs, gap strategies** and cross-session momentum. **None passed**; the best gross edge was 0.07-1.5 pts/trade. See [[ORB Literature Review]] §2.12.
- **Our own backtest:** "trade the ORB against the gap" had Sharpe ≈ 0 across the whole grid ([[ORB Backtest Results]]). That is *not* the same as a gap-*fill* trade with a gap-sized target, but it lowers the prior.

> [!note] Takeaway
> Fade setups have a real **mechanism** only when dealers are long gamma, which pushes prices back toward the mean, or at **extension exhaustion** late in the day. Without a regime filter, the evidence says they are cost-dominated on NQ.

---

## 3. Event-day and calendar effects (priority 3)

### 3.1 FOMC
- **Lucca & Moench (2015, JF)**, *The Pre-FOMC Announcement Drift* <https://onlinelibrary.wiley.com/doi/10.1111/jofi.12196> · <https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr512.pdf>
  - SPX rises about **49 bp in the 24 hours before scheduled announcements** (14:00 the day before → announcement), 1994-2011. That was about 80% of the annual equity premium.
  - Most of it accrues in the **morning of the FOMC day**.
- **Decay:** Kurov, Wolfe & Gilbert (2021, FRL), *The Disappearing Pre-FOMC Announcement Drift* <https://pmc.ncbi.nlm.nih.gov/articles/PMC7525326/>. The drift **essentially disappeared after 2015**, both with and without press conferences.
- **Baglioni & Ribeiro (2022)**, *The FOMC Announcement Reversal* <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4182628> (Abstract)
  - The pre-announcement return strongly and **negatively** predicts the post-announcement return.
  - Strategy: at the announcement, **buy ES if the pre-return < 0, sell if > 0, and exit at the close.**
  - 1997-2020, 180 meetings: Sharpe **more than 2.5× the pre-FOMC drift's**.
  - PapersWithBacktest shows it as a tiny sleeve: 0.43% a year at 1.55% volatility, SR 0.29 on total capital. That is because it trades only 8 days a year.
  - The exact pre-window was not accessible to me (SSRN returned 403). **Test both "previous close → 13:59" and "09:30 → 13:59".**
- **Practitioner claim:** "about 65% of FOMC days see the first 5-min post-release candle reversed by the close" (FOMC fake-out; secondary, unverified).
- **Gao et al. (2018):** last-half-hour momentum on FOMC days earned **20%/yr**. It is an overlay for §1.

### 3.2 CPI / NFP (08:30 ET, before the RTH open)
- The effect shows up in the **overnight gap and the opening range** rather than in RTH drift.
- Mesfin (2026): no persistent post-news drift on MNQ once the spike bars are excluded.
- Gao, Wu & Zhu, and Li et al.: intraday momentum is **stronger on macro-news days**. Treat news days as a **regime flag** for §1 and for the ORB, not as a standalone strategy.

### 3.3 Overnight vs intraday decomposition
- **Kelly & Clark (2011, J. Asset Mgmt)**, *Returns in Trading versus Non-Trading Hours: The Difference is Day and Night* <https://www.researchgate.net/publication/233589349>
  - Essentially **all** index-ETF returns 1999-2006 came overnight. Intraday returns were flat or negative.
  - Proposed cause: day traders are averse to overnight risk.
- **Boyarchenko, Larsen & Whelan (2023, RFS)**, *The Overnight Drift* <https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf> (Verified abstract and intro)
  - ES returns are concentrated at **02:00-03:00 ET**, the European open: 3.7% a year, 1.48 bp/day.
  - The drift is driven by **end-of-US-day order imbalances**. **Sell-offs produce strong overnight reversals**; rallies produce weak ones.
  - Long 02:00-03:00 nets Sharpe about 0.3 after costs. **Out of scope** (not flat by close), but relevant because the RTH session has **no structural long drift**, so an intraday rule should not rely on a long bias.
- **Lou, Polk & Skouras (2019, JFE)**, *A Tug of War*: overnight and intraday returns are **negatively related** in the cross-section, with different clienteles. At the index level this weakly supports **gap fade** over gap follow. Our ORB result (gap-aligned wins) says the *first-5-min confirmation* matters more.
- **Decay:** the overnight-vs-intraday gap has **waned since about 2012**, and it reversed briefly in early 2020 (Elm Wealth summary). <https://elmwealth.com/night-moves-overnight-drift/>

### 3.4 Day-of-week, turn-of-month, OpEx
- **Turn of the month:** McConnell & Xu (2008), and Quantpedia's claim that it is "the only persistent calendar effect in S&P futures" (<https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes>). It is a daily effect and it is **not known whether it lives in RTH or overnight**. Cheap to check as a diagnostic, but it adds long-bias correlation with ORB longs.
- **OpEx / quad witching:** strike pinning on individual stocks (Ni, Pearson & Poteshman 2005, JFE). The Quantpedia OpEx-week effect is daily. A practitioner statistic says quad witching days since 2021 average −0.52% with only about 25% green (secondary, 14 observations). With **daily 0DTE**, monthly OpEx is less special. **Diagnostic only.**
- **Day-of-week:** the evidence conflicts. Do not filter on it (same conclusion as [[ORB Literature Review]]).

---

## 4. Cross-market, lead-lag and regime variables (priority 4)

| Idea | Evidence | Verdict for NQ 1-min |
|---|---|---|
| **ES ↔ NQ lead-lag** | Classic lead-lag results (futures lead cash by 5-45 min in the 1990s; Kawaller-Koch-Koch; Chan 1992) are **arbitraged down to milliseconds** today. The most liquid contract (ES) leads at the HF level. "SMT divergence" (ES makes a new high, NQ doesn't) is a practitioner claim with **no published P&L** found. | Low priority. At most a *filter* ("only take the ORB if ES's 5-min candle agrees"). It is cheap to test if we have ES 1-min. |
| **Bonds → equities intraday** | The literature (e.g., *The lead-lag relation between the stock and bond markets*, EJF 2018 <https://www.tandfonline.com/doi/full/10.1080/1351847X.2017.1340320>) finds weak, regime-dependent lead-lag. The stock-bond correlation flipped positive in 2022. | Low priority. Minute-level predictability is not robust. |
| **Mega-cap (NVDA/AAPL/MSFT) → NQ** | No credible intraday lead-lag evidence found. Futures and ETFs lead constituents in price discovery, not the reverse. Earnings moves happen overnight. | Skip as an entry signal. Maybe use a "mega-cap earnings day" as a volatility regime flag. |
| **Dealer gamma (GEX)** | Baltussen et al. (verified): momentum only when NGE < 0. Dim-Eraker-Vilkov: positive gamma → reversal. Barbon et al.: sign-dependent momentum vs reversal. FirmTape 2022-26: t = 3.1 on short-gamma closes. | **High priority.** The free SqueezeMetrics series (SPX-based, published after the close, **use t−1**) has **negative GEX on only about 10% of days** (2016: 22, 2017: 2, 2018: 39, 2019: 18, 2020: 31, 2021: 16, **2022: 104**, 2023: 23, 2024: 1). Use **rolling 252-day percentiles**, not the sign. |
| **VIX term structure** | VIX/VIX3M > 1 (backwardation) is a stress regime, about 16% of days (2013-24). That is when volatility is high and intraday momentum is stronger (Gao; Li et al.). The VIX9D/VIX ratio is the short-dated version. | **Medium-high** as a regime filter. It is a proxy for negative gamma if GEX data is doubted. CBOE CSVs: `https://cdn.cboe.com/api/global/us_indices/daily_prices/{VIX,VIX3M,VIX9D,VXN}_History.csv` |

---

## 5. Methodology used by the best (priority 5)

### 5.1 Multiple-testing control
- **Deflated Sharpe Ratio**, Bailey & López de Prado (2014) <https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf> (Verified)
  - DSR = Φ( (SR̂ − SR₀)·√(T−1) / √(1 − γ₃·SR̂ + (γ₄−1)/4·SR̂²) ).
  - The benchmark is SR₀ = √V[SR_n] · ((1−γ)·Φ⁻¹(1 − 1/N) + γ·Φ⁻¹(1 − 1/(N·e))), where γ ≈ 0.5772 is the Euler-Mascheroni constant.
  - N is the number of *effectively independent* trials. Use the number of grid cells after clustering correlated variants.
  - SR is per-period (daily). T is the number of days. γ₃ and γ₄ are the skew and kurtosis of daily returns. **The ORB's positive skew helps; fades with high win rates are negatively skewed, which is penalized.**
  - **Accept only DSR > 0.95.**
- **Probability of Backtest Overfitting (PBO / CSCV)**, Bailey, Borwein, López de Prado & Zhu (2016) <https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf>
  - Split the daily P&L matrix (days × variants) into S = 16 blocks.
  - For every combination of 8 in-sample blocks, pick the best in-sample variant and record its out-of-sample rank.
  - PBO = the fraction of combinations where that out-of-sample rank falls below the median. **Target PBO < 0.2.**
- **White's Reality Check (2000)** and **Hansen's SPA (2005):** bootstrap (stationary, mean block about 10 days) the maximum over variants of the mean excess return, to test whether the best rule beats zero after the search. Romano-Wolf StepM identifies *which* variants survive.
- **Harvey, Liu & Zhu (2016, RFS):** require **t > 3** (not 2) for a new factor or anomaly found after search.
- **Combinatorial Purged CV** (López de Prado, *AFML* ch. 7 and 12):
  - Purge training days whose labels overlap test days, and embargo about 1% of days after each test block.
  - For flat-by-close strategies the labels do not overlap, but any **rolling parameter** (ATR14, GEX percentile, noise band) leaks within about 14-252 days. Embargo that length.
- **Walk-forward, Kevin Davey style:** optimize once on in-sample data, test once on out-of-sample data, and **never re-optimize after seeing out-of-sample**. Prefer parameter **plateaus**: train-vs-validate Sharpe correlation across the grid, which we already used (0.95 for the ORB).

### 5.2 Sizing and combination
- **Volatility targeting:**
  - Moreira & Muir (2017, JF) and Harvey et al. (2018, *The Impact of Volatility Targeting*): scaling by inverse recent volatility improves the Sharpe of **equity** exposures, through the leverage effect.
  - Zarattini et al. size intraday trades to a daily-volatility target (for example 2% target / σ_14d).
  - For us, an ATR-based stop already normalizes risk per trade. For time-exit strategies with no stop (§1), **size = target daily risk / σ(last-30-min returns, 60d)**.
- **Portfolio of small edges:**
  - Carver (*Systematic Trading*): equal-risk sleeves, a correlation-aware diversification multiplier IDM = 1 / √(wᵀρw), and a cap on it (about 2.5).
  - Concretum (2026, *Fast Alphas*, SSRN 6391638) makes an important point: a signal that fails *standalone after costs* can still add value as a **timing overlay**. Their 5-min one-bar reversal lifted a trend model's Sharpe from 0.87 to 0.99. Keep "informational alpha" candidates as **entry/exit modifiers** for the ORB, not as their own trades.
- **Always report:**
  - daily-P&L **correlation with ORB v1**;
  - the P&L **conditional on the ORB outcome** (ORB no-trade / stopped out / still open at 15:30);
  - the combined portfolio Sharpe at equal risk.

---

## 6. Ranked: next rule sets to test on NQ 1-min data

**Common protocol** (same as [[ORB Backtest Results]]):
- **Split:** Train 2016-06 → 2021, Validate 2022 → 2024, Holdout 2025-26 (look once).
- **Fills:** pessimistic, **1.0 pt round-trip cost**, and a stress test at **2.0 pts**.
- **Timestamps:** "prev close" = the prior 15:59 bar close. σ_d = 20-day stdev of close-to-close RTH returns, known at t−1. ATR14 as in the ORB engine. GEX_pct = the rolling 252-day percentile of SqueezeMetrics GEX at **t−1**. TS = VIX/VIX3M at t−1.
- **Scoring:** DSR (N = grid size), PBO (CSCV, S = 16), yearly sign consistency (≥ 6 of 9 years positive), and correlation with ORB v1.

| Rank | Rule set | Why (evidence) | Expected corr. with ORB |
|---|---|---|---|
| **1** | **LDM: regime-conditioned late-day momentum** | Strongest academic evidence, NQ-specific, with a mechanism. Unconditionally decayed; conditionally alive (t = 3.1). | Low-moderate. It is time-disjoint except when an ORB winner is still open. Check the conditional table. |
| **2** | **GFADE: high-GEX midday VWAP fade** | Mechanism (positive dealer gamma → reversal), 0DTE-era papers. Profits on range days, where the ORB loses. | **Negative to low**. This is the diversifier. |
| **3** | **FOMC-REV: post-announcement reversal** | Published after the pre-FOMC drift died. Short holding period. About 72 events in 2016-24. | ≈ 0 (8 days a year) |
| **4** | **GAPFILL: tiny-gap fill on days the ORB skips** | Descriptive fill rates of 78-93%. By construction it trades only on days the ORB filters out. | ≈ 0 (disjoint days) |
| **5** | **EXH: IB-extension exhaustion fade, afternoon** | Descriptive statistics: reversals dominate beyond 1.4× IB, and afternoon continuation is only 23%. | Negative (it fades trend days). Size small. |
| **6** | **SOUP: intraday prior-day-extreme failed break (Turtle Soup / 80-20 / Oops)** | Classic, but decayed and failed Mesfin's MNQ test. Low prior. | Low |
| **7** | **Regime filters on ORB v1 itself** (GEX percentile, VIX/VIX3M, news day) | Same mechanism as #1 and #2. A cheap test. | Not a new sleeve |

### 6.1 LDM: late-day momentum (rank 1)
- **Signal (evaluated at the close of the 15:29 bar):**
  - r_ROD = close(15:29) / prevClose − 1.
  - Variants: r1 = open(09:30) … close(09:59) measured from prevClose (Gao), and r_ROD with r12 agreement.
- **Entry:** market at the open of **{15:30, 15:40, 15:45, 15:50}**, in the direction of sign(r_ROD). The later entries target the LETF and market-on-close window; the MOC imbalance is published at 15:50.
- **Threshold:** |r_ROD| ≥ **k·σ_d**, k ∈ **{0, 0.25, 0.5, 0.75, 1.0, 1.5}**.
- **Regime (one axis at a time, then the best pair):**
  - GEX_pct ≤ **{100 (none), 50, 33, 20}**;
  - or TS ≥ **{none, 0.95, 1.00}**;
  - or VXN ≥ its **{none, 60th, 80th}** 252-day percentile;
  - or first-30-min realized-volatility tercile = **{all, high}** (Gao).
- **Exit:** market at **15:59** close. Optional catastrophic stop at **{none, 0.10, 0.20} × ATR14**.
- **Size:** inverse σ of the last-30-min return (60-day).
- **Grid:** 4 × 6 × about 10 regime cells × 3 stops ≈ 720 (N for DSR ≈ 100 after clustering).
- **Report:** results split by ORB state at 15:30: **no ORB trade / ORB stopped / ORB open and aligned / ORB open and opposed**.

### 6.2 GFADE: high-gamma midday VWAP fade (rank 2)
- **Regime gate:** GEX_pct ≥ **{50, 67, 80}** *and* TS < **{1.00, 0.95}**, i.e. contango.
- **Window:** signals from **{10:30, 11:00}** to **{13:30, 14:30}**.
- **Signal:** 1-min close deviates from the session VWAP by **≥ d × ATR14**, d ∈ **{0.20, 0.30, 0.40, 0.50}**. Also require the deviation to have been reached within the last **{30, 60, ∞}** minutes, so it is an impulse and not a grind.
- **Entry:** fade at the next 1-min open (short above VWAP, long below). Maximum 1 trade per day per side.
- **Stop:** **{0.10, 0.15, 0.25} × ATR14** beyond the entry, or beyond the session extreme + 0.02 × ATR.
- **Target:** **{VWAP touch, 50% of the deviation, 1R, 2R}**.
- **Time exit:** **15:30**, which keeps the book flat before the LDM window.
- **Grid:** 3 × 2 × 2 × 2 × 4 × 3 × 3 × 4 ≈ 3.5k. Collapse it by fixing the window at 11:00-14:30 first.
- **Control:** run the same rule on **low-GEX days** and expect it to lose. That sign flip is the mechanism check.

### 6.3 FOMC-REV: FOMC post-announcement reversal (rank 3)
- **Days:** scheduled FOMC statement days only, from the federalreserve.gov calendar. There are about 72 in 2016-2024.
- **Pre-return:** r_pre = close(13:59) / **{prevClose, open 09:30}** − 1.
- **Entry:** fade sign(r_pre) at **{14:00 open, 14:05, 14:30 (after the press-conference start), 14:45}**. Threshold |r_pre| ≥ **{0, 0.25, 0.5} × σ_d**.
- **Exit:** 15:59. Stop **{none, 0.25, 0.5} × ATR14**.
- **Also log** the dead Lucca-Moench leg as a control: long 09:35 → 13:55 on FOMC days. Expect ≈ 0 after 2015.
- **Caveat:** with 72 events, report the t-stat and bootstrap CI. Do not optimize more than about 12 cells.

### 6.4 GAPFILL: tiny-gap fill on ORB-skip days (rank 4)
- **Gap:** g = open(09:30) / prevClose − 1, with |g| ≤ **{0.15, 0.20, 0.30} × ATR14%**.
- **Trigger:** first 5-min candle **against** the gap, i.e. exactly the days where ORB v1's gap filter blocks a trade. Body ≥ **{0, 0.03, 0.05} × ATR14**. Entry at the **09:35 open** or on the **{first 1-min close beyond the 09:30-09:35 range in the fill direction}**.
- **Target:** prevClose (100% fill) or **{75%, 100%, 100% + 0.05 ATR}**.
- **Stop:** the opposite end of the 5-min range, or **{0.05, 0.10} × ATR14**. Time exit **{11:00, 12:00, 15:59}**.
- **Watch:** win rate will be high and R small. Costs and negative skew are the killers. Require the average trade to be ≥ 3 pts net.

### 6.5 EXH: IB-extension exhaustion fade (rank 5)
- **IB** = 09:30-10:29.
- **Signal after {12:00, 13:00}:** price reaches **≥ x × IB range** beyond the IB edge, x ∈ **{1.4, 1.5, 1.75, 2.0}** (measured from the opposite IB edge, as in the tradingstats definition). Also a slow approach: time since the last new extreme ≥ **{15, 30}** min (stall), or a 1-min close back inside the extreme by **{0.02, 0.05} × ATR**.
- **Entry:** fade. Stop at the extreme + **{0.05, 0.10} × ATR14**. Target **{VWAP, IB edge, 2R}**. Time exit **15:29**, before LDM.
- **Gate:** GEX_pct ≥ 50 (optional). **Size at half risk**, because it opposes ORB winners.

### 6.6 SOUP: failed break of the prior-day high/low (rank 6)
- **Setup:** during **09:35 → {11:00, 12:00}**, price trades **≥ b × ATR14** beyond PDH or PDL (RTH), b ∈ **{0.03, 0.05, 0.10, 0.20}**.
  - Turtle-Soup flavour: also require that the PDH/PDL was a **{5, 10, 20}-day** extreme set at least 4 days ago.
  - 80-20 flavour: require yesterday opened in the top or bottom 20% and closed in the opposite 20%.
- **Trigger:** a 1-min close back inside PDH/PDL within **{5, 15, 30}** min. Enter at the next open.
- **Stop:** session extreme + **{0.02, 0.05} × ATR14**.
- **Target:** **{VWAP, prevClose, 2R, 3R, 15:59}**.
- **Low prior** (Mesfin: liquidity grabs failed on MNQ; Oops decayed after 2022). Keep the grid small and require DSR > 0.95.

### 6.7 Regime filters on ORB v1 (rank 7; cheap, run first)
Add one filter at a time to the frozen ORB v1:
- skip if GEX_pct ≥ **{80, 67}**;
- or trade only if GEX_pct ≤ **{50, 67}**;
- TS ≥ **{0.90, 0.95}**;
- a **news-day** flag (CPI, NFP, FOMC): **{include, exclude, only}**.

The hypothesis (Baltussen/Dim) is that the ORB earns most on **low-GEX or stress days**. Our earlier ATR-ratio volatility filter hurt, so require the improvement in **both** Train and Validate before believing it.

> [!tip] Suggested order of work
> 7 (1 hour, data join only) → 1 → 2 → 3 → 4 → 5 → 6. Needed data joins: SqueezeMetrics DIX.csv, CBOE VIX/VIX3M/VIX9D/VXN, FOMC dates (federalreserve.gov), and CPI/NFP dates (BLS). Assemble the portfolio only from sleeves with DSR > 0.95, PBO < 0.2 and a positive Validate Sharpe. Weight by equal risk, capped by correlation.

---

## 7. Links
- Gao, Han, Li & Zhou (2018) JFE: <https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301351>
- Baltussen, Da, Lammers & Martens (2021) JFE: <https://academicweb.nd.edu/~zda/intramom.pdf>
- Barbon, Beckmeyer, Buraschi & Moerke, LETFs and end-of-day dynamics: <https://portal.northernfinanceassociation.org/viewp.php?n=2240036708>
- Baltussen, Da & Soebhag (2023), End-of-Day Reversal: <http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/EndofDayReversal_withnames.pdf>
- Dim, Eraker & Vilkov (2024), 0DTEs: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4692190>
- Adams et al. (2025), 0DTEs and volatility: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5641974>
- FirmTape 2022-26 SPX retest: <https://dev.to/firmtape/intraday-momentum-is-dead-in-the-0dte-era-we-measured-it-on-1085-spx-sessions-43g0>
- Wu & Zhu (2023), HFT and intraday momentum: <https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2023-UK/papers/EFMA%202023_stage-4455_question-Full%20Paper_id-31.pdf>
- Li, Sakkas & Urquhart (2022): <https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf>
- Lucca & Moench (2015): <https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr512.pdf>
- Kurov, Wolfe & Gilbert (2021): <https://pmc.ncbi.nlm.nih.gov/articles/PMC7525326/>
- Baglioni & Ribeiro (2022): <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4182628>
- Boyarchenko, Larsen & Whelan, Overnight Drift: <https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf>
- Kelly & Clark (2011): <https://www.researchgate.net/publication/233589349_Returns_in_Trading_versus_Non-Trading_Hours_The_Difference_is_Day_and_Night>
- Street Smarts formalizations (MQL5): <https://www.mql5.com/en/articles/2717> · <https://www.mql5.com/en/articles/2785>
- Oops on DAX (Unger): <https://ungeracademy.com/blog/we-tested-larry-williams-oops-pattern-the-results-might-surprise-you>
- tradingstats.net NQ statistics: <https://tradingstats.net/initial-balance-breakout-statistics/> · <https://tradingstats.net/initial-balance-retest-statistics/> · <https://tradingstats.net/gap-fill-strategy/>
- Mesfin (2026) MNQ falsification: <https://arxiv.org/abs/2605.04004>
- Concretum, Fast Alphas: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6391638> · Breaking the Rules: <https://concretumgroup.com/breaking-the-rules-of-intraday-trading/>
- Deflated Sharpe Ratio: <https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf> · PBO: <https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf>
- Data: SqueezeMetrics GEX/DIX <https://squeezemetrics.com/monitor/static/DIX.csv> · CBOE <https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv>
