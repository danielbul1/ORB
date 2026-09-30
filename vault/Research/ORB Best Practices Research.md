# ORB Best Practices Research (2026-09-30)

This note covers what the research says about making our NQ ORB the best it can be. It picks up after [[ORB Literature Review]], [[arXiv ORB Sweep]], [[Intraday Edges Research]] and [[Edge Hunt Log]], and it does not repeat those sources.

It focuses on the three open problems:
1. **Why did the edge fade in 2025-26?** Ensemble v3's Prop Score went from +$277/mo in 2016-24 to −$16/mo in 2025-26.
2. **How should a fat-tailed ORB be sized and managed** under Lucid's trailing drawdown?
3. **Which non-price signals are left** after ADR 0006 (0/10 price filters passed)?

Tags: **Verified** = we read the primary text or data. **Snippet** = abstract, summary or search snippet only. **Computed** = we calculated it ourselves.

---

## TL;DR: the ranked plan

| # | Action | Why | Data | Evidence |
|---|---|---|---|---|
| 1 | ~~**Dealer-gamma regime gate**~~ **TESTED 2026-09-30: FAIL** (H11, see [[Edge Hunt Log]]; low vs high gamma R/trade +0.214 vs +0.205, t = 0.13) (SqueezeMetrics free daily GEX, prior close) | Long dealer gamma causes *negative* intraday momentum. Negative-GEX days nearly vanished in 2024-26, which likely explains the decay | Free CSV, 2011→today | Strong mechanism + Verified data |
| 2 | **Honest execution costs**: 2-4 ticks entry slippage on MNQ, 8 ticks on high-ATR days, log fill vs trigger live | An independent 5-index replication: NQ ORB gross +0.131R becomes **net +0.002R** under CFD costs. The edge lives in the cost gap | Own data | Verified |
| 3 | **Forward-looking range instead of ATR14**: VIX1D/VXN expected move for the stop and body; VIX1D/VIX ≥ 0.9 day filter | VIX1D beats HAR models for next-day RV (J. Futures Mkts 2025); ORB with range forecasts beats ATR (ACIIDS 2026) | Free (Cboe) | Peer-reviewed + Snippet |
| 4 | **Event and calendar tags**: FOMC, 08:30 macro, OpEx Friday / week after, **mega-cap earnings next session** | Gao: momentum is stronger on news days. Mega-cap earnings drive index vol (Ogneva & Xia). OpEx evidence is mixed, so test rather than assume | Free | Medium |
| 5 | **Prop sizing**: fixed risk at D/r ≈ 10-20R in the eval. Funded: cushion-proportional (Grossman-Zhou), capped at ≤ 0.5 Kelly | Optimal drawdown-constrained sizing; Monte Carlo pass-rate table below | Own sim | Theory + Computed |
| 6 | **Decay-aware expectations**: plan on Sharpe ≈ 0.7, not 1.5. Kill switch = execution parity + drawdown quantiles, **not** live P&L | Post-publication decay is about 50%. A 0.15R edge needs ~850-1,950 trades to confirm or kill statistically | — | Verified abstracts + Computed |
| 7 | **Fade leg for long-gamma days** (failed-breakout reversal) as an ensemble diversifier | NQ mean reversion 2023-26 OOS Sharpe 1.29 (Seeck 2026); high gamma means reversals | Own data | Snippet, small n |

**Do not spend time on:** raw OFI/CVD for direction (effects die within about 1 second); VPIN (debunked on E-minis); ML *direction* models (coin-flip, per Mesfin); LLM-news backtests (look-ahead bias; forward only, as we already do); breakeven stops (they cut the right tail); an extra vol-targeting overlay (a 0.10·ATR stop is already vol-normalised); turn-of-month (gone since 1990).

**Every item above must be pre-registered like ADR 0006**, with 2024-26 kept as the final holdout.

---

## 1. Why the edge faded in 2025-26

### 1.1 Dealer gamma is the best-supported explanation in the literature (❌ but NOT on our data: H11 failed, see [[Edge Hunt Log]])
- **Adams et al. (2026), "Do S&P500 Options Increase Market Volatility? Evidence from 0DTEs", SSRN 5641974** (Snippet, via [QuantPedia](https://quantpedia.com/do-sp500-0dtes-options-increase-market-volatility/)).
  - Natural experiment: Tue/Thu 0DTE availability before May 2022.
  - SPX RV is 60 bp (annualized) lower on 0DTE days, and the hedging-to-vol multiplier is ≈ −4.
  - **Higher dealer net gamma predicts order-flow reversals in E-minis and negative high-frequency momentum.**
  - Carried-over positions matter far more (24 bp) than fresh 0DTE positions (3 bp).
- **Dim, Eraker & Vilkov (2024), SSRN 4692190** (Snippet): 0DTE gamma is inversely related to intraday RV and does not amplify moves.
- **Barbon & Buraschi, "Gamma Fragility" / SFI 22-40** (Snippet, [SSRN 3925725](https://papers.ssrn.com/abstract=3925725)): intraday **momentum** needs negative gamma **plus** illiquidity; positive gamma produces **reversal**.
- **Zarattini/Aziz/Barbon 2024 §4.5** (Verified PDF): momentum P&L on prior-close RSI(5), a gamma proxy, gives β = −3.25 bp per RSI point (p = 0.001). After selloffs dealers are short gamma and trends continue.
- **Cboe "0DTEs Decoded" (2025)** (Verified, [link](https://www.cboe.com/insights/posts/0-dt-es-decoded-positioning-trends-and-market-impact)): market-maker 0DTE hedging is "at most 0.2% of SPX daily liquidity". So look at **total** gamma, not only 0DTE.
- **Counterpoint, Elms (2026), SSRN 6564078** (Snippet): no pinning at expiry, and high near-expiry ATM OI goes with ~16% wider ranges. This measures range, not persistence. Do not blanket-skip OpEx.

**Free data, SqueezeMetrics DIX/GEX** (Verified: https://squeezemetrics.com/monitor/static/DIX.csv, 3,876 days, 2011-05 → 2026-09-29). Share of negative-GEX days per year:

| 2015 | 2016 | 2018 | 2020 | **2022** | 2023 | **2024** | **2025** | **2026 YTD** |
|---|---|---|---|---|---|---|---|---|
| 9.1% | 8.7% | 15.5% | 12.3% | **41.4%** | 9.2% | **0.4%** | **3.6%** | **4.8%** |

Caveat: GEX/price in 2024-26 (0.73-0.93) is mid-range historically, so this is "almost never negative", not "record long gamma".

**FlashAlpha 8-year SPY GEX study** (Verified, [link](https://flashalpha.com/articles/gex-dex-vex-chex-8-year-backtest-spy-vix-control)):
- GEX vs next-day RV: ρ = −0.36.
- After a VIX control: ρ = −0.14.
- After VIX + ATM IV: ρ = −0.03 (not significant).

So GEX is largely a vol-regime proxy. Test whether it adds anything over VIX/VIX1D for **persistence** (the chance of a 10R day), not just range.

**Hypothesis H-GEX (pre-register):**
- Full risk when GEX(t−1) < 0 or in the bottom tercile of GEX/price (expanding-window cut-offs); ¼ risk otherwise.
- Report Sharpe per regime in 2016-24 and 2025-26.
- Also check whether v3's 2016-24 P&L is concentrated in 2018/2020/2022. If it is, the 2025-26 flatness means "no short-gamma days", not "dead edge".

**Free fallback proxy:** skip when VIX is below its 20-day median **and** VIX(09:30) − VIX(prior close) ≤ 0.

### 1.2 Leveraged ETFs: re-specify our +0.6 correlation
- US leveraged AUM is ~$156-192B, but **single-stock LETFs (~$56B) are about half of leveraged equity volume**. Their rebalancing hits NVDA/TSLA, not NQ (Snippet: etf.com, Ultumus).
- Fed FEDS paper, Ivanov & Lenkey (Snippet): investor flows substantially offset LETF rebalancing on big-move days.
- Barbon et al.: LETF effects are short-lived because liquidity providers pre-position against them.

**To do:** recompute the driver as **index-LETF rebalancing notional** (TQQQ/SQQQ/QLD/QID: AUM × L × (L−1) × day return) ÷ NQ volume, instead of total LETF volume share.

### 1.3 Crowding and publication decay
- No direct evidence of ORB crowding was found.
- **Falck, Rej & Thesmar (CFM 2021), [arXiv 2105.01380](https://arxiv.org/abs/2105.01380)** (Verified abstract): the publication year explains 30% of Sharpe decay, about 5 pp more decay per year since publication. Complexity/overfitting proxies explain another ~15%.
- McLean & Pontiff: about −58% of the return after publication (cross-sectional equities).
- **Use:** plan on a live Sharpe of ~0.7, not 1.5, and keep filters minimal, since each gate adds decay risk.

### 1.4 New 2025-26 replications
- **Krueger (25 Sep 2026), "ORB paper replicated on five indices: gross reproduced, net zero"** (Verified, [mql5](https://www.mql5.com/en/blogs/post/776235)): exact Zarattini rules on CFDs, 2015 → Jun 2026.
  - **NQ gross +0.131R, 23.2% hit rate, net +0.002R** with 2.5 pt costs. SPX net −0.081R.
  - 2015-17 was negative in every market (low-vol, long-gamma years, which fits §1.1). NQ 2021-26 was at best +0.06R.
  - Rule of thumb: initial risk ≥ 2× round-trip cost.
- **"Backtests, Not Signals" (Mar 2026)** (Verified, [link](https://backtestsnotsignals.substack.com/p/opening-range-breakout-real-edge)): MNQ **60-min OR** + 200-SMA trend filter, 1.4-4.4R target, **exit next open**.
  - IS 2020-22 Sharpe 1.37; **OOS 2023 → Feb 2026 Sharpe 1.10**, PF 1.32, 24.9% WR, 474 trades. The grid was optimized.
  - Idea: overnight hold on our 60-min Leg.
- **Seeck (2026), SSRN 7364204** (Snippet): NQ band-breach **mean reversion**, walk-forward OOS 2023-26 Sharpe 1.29, strongest at VXN extremes. This supports a fade Leg in long-gamma regimes.
- **ACIIDS 2026, "Enhancing ORB with LSTM True-Range Prediction"** (ES, Snippet): an oracle true range sharply improves ORB, and the LSTM forecast gives ~+70% cumulative vs the ATR baseline.
- **Brown (2026), SSRN 6847024** (Snippet): ES microstructure across 4 vol regimes, 2024-26. Descriptive only.

### 1.5 When to worry about a drawdown
- **Rej, Seager & Bouchaud (2017), [arXiv 1707.01457](https://arxiv.org/abs/1707.01457)** (Verified abstract): exact drawdown length and depth distributions for a given Sharpe. People underestimate both.
- **Use:** simulate at Sharpe 0.7 and halve risk only beyond the 95th-percentile drawdown length or depth. At that Sharpe, a flat 2025-26 may still be normal.
- **Equity-curve throttle** (full size only when equity > its 40-trade MA): anecdotal, but testable because ORB P&L clusters by regime.

---

## 2. Regime filters available at or before the open

| Filter | Rule to test | Source | Data |
|---|---|---|---|
| VIX1D expected move | stop = 0.10 × (VIX1D(09:25)/√252 × price); body ≥ 0.05 × same. Use VXN-scaled for NQ | Albers 2025, *J. Futures Mkts* 45(11), [link](https://ideas.repec.org/a/wly/jfutmk/v45y2025i11p2092-2108.html) (Verified abstract): adjusted VIX1D beats HAR; raw VIX1D **overestimates** and drifts up intraday, so read it at a fixed time | Free (Cboe, from 2023 only) |
| VIX1D/VIX ratio | trade only if ≥ 0.9 (practitioners: ≥ 1.0 elevated, ≤ 0.75 quiet) | Snippet | Free |
| VIX term structure | VIX/VIX3M > 1 or VIX9D > VIX → **size up**, not a direction signal | FlashAlpha inversion study (Snippet): no directional edge, forward dispersion +60% | Free |
| GEX | see §1.1 | | Free |
| ATR ratio | skip or halve when ATR14/ATR100 < 0.8 | Sizing report | Own data |

---

## 3. Non-price signals

### 3.1 Order flow at the open: mostly a dead end for direction
- **Cont, Kukanov & Stoikov (2014), [arXiv 1011.6402](https://arxiv.org/abs/1011.6402)** (Verified abstract): OFI explains price changes **in the same interval** only.
- **Takahashi (2025), [arXiv 2508.06788](https://arxiv.org/abs/2508.06788)** (ES, 1-second data, Verified abstract): shocks "dissipate almost entirely within a second".
- **Andersen & Bondarenko (2014/15), *Review of Finance*** (Snippet): VPIN has no incremental power on E-minis. Drop it.
- **Kang, Kang & Lee (2022), *J. Futures Mkts* 42(3)** (Verified abstract): **option** order imbalance in the first 10 minutes predicts rest-of-day index returns, net of costs. This is KOSPI 200, and US signed option data is paid (OPRA). Park it.
- **Quantpedia (2026), morning SPY OFI** (Verified): 09:30-10:00 is the most informative window, but the signal is a multi-day **reversal**, not same-day continuation.
- CVD: practitioner-only, with no statistics.

### 3.2 Relative volume at the open (free, our own bars)
- There is no futures-specific paper.
- Indirect support: Gao (momentum is stronger on high-volume days); first-hour vol explains up to 68% of daily vol (Snippet).
- **Test:** `RVOL_k` = NQ volume 09:30→09:30+k ÷ the 20-day median of the same window, with k = each Leg's OR length. Test terciles and require them to be monotonic; candidate rule: trade only if ≥ 1.2.

### 3.3 Cross-asset
- **Mega-cap earnings (Ogneva & Xia 2021, Snippet):** a large-firm earnings release produces ~21% of the abnormal index vol and ~47% of the abnormal volume of an average macro release. The earnings share of index vol has been stable while the macro share has fallen.
  - NQ is concentrated in NVDA/MSFT/AAPL/AMZN/META/GOOGL/AVGO/TSLA, so this matters more for NQ than for ES.
  - **Test EarnDay** (the first RTH session after any of the 8 report), gap-aligned subset separately. Dates are free (yfinance / Nasdaq calendar).
- **Breadth ($ADD):** practitioner-only. The open value correlates 0.56 with the 10:00 value. Test same sign with |ADD| ≥ 500 at the end of the OR (TV `USI:ADD`).
- **ZN overnight:** skip longs if the 10-yr yield is up > 5 bp from 16:00 to 09:30 (Snippet, Saxo). Low priority.
- **NQ vs ES relative strength, semis lead:** no rigorous evidence; lead-lag works on a scale of minutes.

### 3.4 Meta-labeling (only after ≥ 2 features show univariate signal)
- **Hudson & Thames** (Verified): on ES, meta-labeling a trend model raised precision from 0.48 to 0.54 out of sample. Price-only features, one split.
- **Joubert (2022), JFDS** (Snippet): calibrated probabilities improve sizing; ensembles help only when regimes exist.
- **Ferreira & Medeiros (2021), [arXiv 2112.15108](https://arxiv.org/abs/2112.15108)** (Verified abstract): VIX is the strongest intraday predictor, and random forests add nothing.
- **Recipe:**
  - Label = hit +1R before the stop by 16:00.
  - Features: non-price only (RVOL, VIX level/Δ, GEX, EarnDay, FOMC/CPI/NFP, OpEx, ADD).
  - Model: LightGBM with depth ≤ 3 and ≤ 100 trees, purged walk-forward, 1-day embargo.
  - Size 0.5× if p < 0.4.
  - Needs ≥ 5 years of trades.

### 3.5 News and LLMs
- **Lopez-Lira & Tang (v6, Oct 2025), [arXiv 2304.07619](https://arxiv.org/abs/2304.07619)** (Verified abstract): predictability sits in small caps and bad news, and **returns fall as LLM adoption rises**.
- **Chen/Tang/Zhou/Zhu (2025), arXiv 2502.10008** (Snippet): GPT-scored WSJ headlines predict S&P at daily and monthly horizons, not intraday.
- **Sun, Najand & Shen (2016), JBF** (Snippet): half-hour news sentiment predicts intraday S&P returns until the close. Proprietary data.
- **Conclusion:** our current design (the GDELT test pre-registered in ADR 0003, plus a forward-only arm) is the right one. Don't backtest with a post-cutoff LLM.

### 3.6 Calendar
- **FOMC:** pre-FOMC drift is now ~40 bp, only at press-conference meetings (NY Fed, Snippet). The 14:00 announcement falls inside our hold. **Test: exit at 13:55 on FOMC days vs hold.**
- **08:30 macro days (CPI/NFP/PPI/retail):** Gao reports stronger momentum on news days. Test that R on these days is ≥ R on other days; also test skipping the 5-min Leg on these days.
- **OpEx:** test OpEx Friday vs the Mon-Wed after vs other days. Evidence is mixed (§1.1).
- **Day of week:** noise unless explained by FOMC or OpEx.
- **Turn of month:** gone since ~1990 (Maberly & Waggoner). Skip.

Use Bonferroni α = 0.0125 across the 4 calendar tags.

---

## 4. Sizing under Lucid's trailing drawdown

⚠️ **Lucid rules to re-verify on Lucid's own site.** A third-party summary (proptradingvibes) says the **150K** needs payout days ≥ **$250** (not $150) and caps payouts at **$3k** (not $2k). It lists the MLL as $2,000 on the 50K and $4,500 on the 150K, EOD trailing, locking at start + $100. The eval has a 50% consistency rule: one 10R day at $200/R = $2k, which is > 50% of a $3k target. `orb/prop.py` must model it; per our earlier notes, this means "keep trading", not "fail".

### 4.1 Theory → formulas
- **Grossman & Zhou (1993), *Math. Finance* 3(3)** (Snippet): with a floor, optimal exposure ∝ cushion.
  - Rule: `risk$ = m · (Equity − MLL)`, with m ≈ 0.05-0.08.
  - With a 75% loss rate, the expected longest losing streak in 250 trades is ≈ ln(62.5)/ln(4/3) ≈ 14-15. At m = 0.07, about 35% of the cushion is left after 15 straight losses.
  - Discrete-time caveat: not always growth-optimal.
- **Fractional Kelly (Thorp 2006):**
  - P(ever falling to fraction x of start) = x^(2/c − 1).
  - For our R distribution (Computed: μ = 0.148R, σ = 2.66R, skew 2.8), **f\* ≈ μ/σ² ≈ 2.1% per R**.
  - Half-Kelly gives P(cushion halves) = 12.5%. **Funded: ≤ 0.25-0.5 Kelly of the cushion.**
- **Busseti, Ryu & Boyd (2016), [arXiv 1603.06183](https://arxiv.org/pdf/1603.06183)** (Snippet): P(W_min < α) < β if E[(1+f·R)^(−λ)] ≤ 1, with λ = log β / log α.
  - A one-scalar search on bootstrapped R. Example: α = 0.5, β = 0.1 → λ = 3.32.
- **Trailing-barrier pass probability (Taylor 1975 / Lehoczky 1977):**
  - P(pass) = exp(−γT), with γ = θ/(e^{θD} − 1) and θ = 2μ/σ² (in R units).
  - At zero edge this is e^(−T/D), i.e. 13.5% for a 2:1 target:drawdown.

### 4.2 Monte Carlo (Computed; trailing floor locking at +$100; no consistency rule, no fees)

| Account | Risk $/trade | Analytic P(pass) | MC P(pass) | Median trades to pass |
|---|---|---|---|---|
| 50K | 100 | 0.38 | 0.48 | 64 |
| 50K | 200 | 0.30 | 0.39 | 18 |
| 50K | 450 | 0.26 | 0.37 | 4 |
| 150K | 100 | 0.51 | 0.70 | 394 |
| 150K | 200 | 0.30 | 0.47 | 116 |
| 150K | 300 | 0.24 | 0.39 | 56 |

The Monte Carlo beats the Brownian formula because 10R days overshoot the target.

**Rule:**
- Eval risk at **D/r ≈ 10-20R**: 50K $100-200 (1-2 MNQ at ~$75-80 risk each), 150K $225-450 (3-6 MNQ).
- Optimise **expected payouts per dollar of fees per month**, not pass probability. `orb/propscore.py` already does roughly this.
- Eval: fixed risk until the MLL locks, then step up.
- Funded: payouts are capped, so it is a harvesting problem. Use cushion-proportional sizing with a small m.

### 4.3 Vol targeting: don't add an overlay
- Zarattini 2024 (Verified): vol sizing raised Sharpe only from 1.24 to 1.33 but **doubled max DD from 12% to 25%**.
- Harvey et al. 2018 (Snippet): Sharpe gains only in equities; it does cut left tails.
- **Cederburg et al. 2020, JFE** (Snippet): vol-managed versions **underperformed out of sample in 72 of 103** strategies.
- Our stop (0.10·ATR) plus fixed $ risk is already vol-normalised. Test a regime *filter* instead (§2).

---

## 5. Exits and trade management
- **Keep 10R/EOD.** The Gao/Baltussen mechanism is end-of-day hedging, and our earlier tests found partial TP hurts.
- **Kaminski & Lo (2014), *J. Fin. Markets*** (Snippet): stops add value only when returns have momentum. Breakeven or tight trails cut the right tail that pays for 75% losers. **No breakeven stops.** If tested at all, use "BE only after +3R and after 12:00", and accept only if p90/p95 R are preserved.
- **The one trailing stop with evidence:** Zarattini's max(band, VWAP) trail raised Sharpe from 0.61 to 1.24 (Verified). **Test a VWAP trail activated only after +2R** vs 10R/EOD.
- **Time stop (hypothesis):** exit if not at +0.5R by 11:00.
- **FOMC 13:55 exit** (§3.6).

## 6. Execution at the open (MNQ via NinjaTrader/Tradovate)
- MNQ tick = 0.25 pt = $0.50, usually a 1-tick spread (CME).
- Open slippage is only anecdotal: ~2 ticks average on stop-market orders at 09:30, with NQ fast moves 8+ ticks (NexusFi/NT forums, Snippet). **Model 2-4 ticks entry, 1 tick exit, ~$1.5 RT commission; stress test at 8 ticks on top-decile ATR days.**
- Our 0.10·ATR stop (~37 pt at ATR ≈ 370) makes costs ≈ 3-4% of R. That is far better than the CFD replication, but only if we measure it honestly.
- **Orders:** submit the entry as a stop-**limit** with 4-8 ticks of protection, and measure the missed-trade rate in sim. Put entry + bracket in one OCO with a fixed stop price. Tradovate brackets are priced at submission and held server-side, so they survive a disconnect. NT8 strategies do **not** auto-reconnect. Run the EOD flatten server-side where possible. Log trigger vs fill for every trade → `tools/nt_parity.py`.

## 7. Validation additions
- **Deflated Sharpe** (Bailey & López de Prado 2014, SSRN 2460551). We already use DSR. Keep N = every config ever tried.
- **PBO/CSCV** (Bailey, Borwein, López de Prado & Zhu 2017): S = 16 blocks, C(16,8) splits, target **PBO < 0.2**. Not yet done → add it.
- **White's Reality Check / Hansen SPA** with a **stationary block bootstrap** (Politis-Romano, 5-10-day blocks). Not yet done → add it.
- **Live trade count needed** (Computed, μ = 0.15R, σ = 2.66R):
  - n ≈ (1.645·2.66/0.15)² ≈ **852 trades** to show μ > 0 at 95%.
  - **1,946** with 80% power.
  - SPRT: ~850 to kill, ~1,200 to confirm.
  - At ~250 trades/yr, **live P&L cannot judge the edge within a year**. The 99% lower band after 250 trades is ≈ −60R.
- **→ Live kill switch should be parity-based** (ADR 0005 update candidate):
  - mean slippage > 2× the model, or
  - signal mismatch > 5%, or
  - cumulative R below −2.33·σ·√n.

---

## 8. Proposed next hypotheses (to pre-register as ADR 0007, H11-H18)
1. **H11 GEX gate** (§1.1): full risk when GEX(t−1) < 0 or in the bottom tercile, else ¼.
2. **H12 VIX fallback gate**: skip if VIX < its 20-day median and overnight ΔVIX ≤ 0.
3. **H13 VIX1D/VXN expected move** replacing ATR14 in the stop and body (2023+ only, so it is a short test).
4. **H14 EarnDay**: mega-cap earnings next session, tested alone and gap-aligned.
5. **H15 Event tags**: FOMC 13:55 exit; 08:30 macro; OpEx Fri; the week after OpEx (Bonferroni).
6. **H16 RVOL_k** terciles.
7. **H17 VWAP trail after +2R** and the **11:00 no-progress time stop**.
8. **H18 Fade Leg**: failed-breakout reversal (closes back inside the OR within 30 min), only in the top GEX tercile.

Also: redo the LETF correlation with index-LETF rebalancing notional (§1.2); add PBO + SPA to `research/`; update `orb/prop.py` with the consistency rule, 2-4 tick slippage and the Lucid 150K payout rules once verified.

## Sources (quick list)
- Adams et al. 2026, SSRN 5641974 · Dim/Eraker/Vilkov 2024, SSRN 4692190 · Barbon & Buraschi, SSRN 3925725 · Elms 2026, SSRN 6564078 · Cboe 0DTEs Decoded 2025
- SqueezeMetrics DIX.csv · FlashAlpha GEX 8-yr study · Albers 2025, J. Futures Mkts 45(11) · ACIIDS 2026 LSTM-TR ORB
- Krueger 2026, mql5 blog 776235 · Backtests Not Signals 2026 · Seeck 2026, SSRN 7364204 · Brown 2026, SSRN 6847024
- Falck/Rej/Thesmar 2021, arXiv 2105.01380 · Rej/Seager/Bouchaud 2017, arXiv 1707.01457 · Ivanov & Lenkey, Fed FEDS
- Cont/Kukanov/Stoikov 2014 · Takahashi 2025, arXiv 2508.06788 · Andersen & Bondarenko 2015 · Kang/Kang/Lee 2022 · Quantpedia OFI 2026
- Ogneva & Xia 2021 · Hudson & Thames meta-labeling · Joubert 2022 · Ferreira & Medeiros 2021 · Lopez-Lira & Tang 2025 · Chen et al. 2025 · Sun/Najand/Shen 2016 · Lucca & Moench (NY Fed)
- Grossman & Zhou 1993 · Thorp 2006 · Busseti/Ryu/Boyd 2016 · Taylor 1975 / Lehoczky 1977 · Zarattini/Aziz/Barbon 2024 · Harvey et al. 2018 · Cederburg et al. 2020 · Kaminski & Lo 2014
- Bailey & López de Prado 2014 (DSR) · Bailey et al. 2017 (PBO) · White 2000 · Hansen 2005 · Politis & Romano 1994
