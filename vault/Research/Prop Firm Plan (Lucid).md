---
title: Prop Firm Plan (Lucid)
created: 2026-09-30
tags: [orb, prop-firm, lucid, sizing]
---

# Prop Firm Plan: Lucid Trading

Back to [[ORB]] · Related: [[Edge Hunt Log]]

## Lucid rules used
Source: a third-party summary updated 2026-09-10 (tradetanto.com). Lucid's own site blocks automated reads, so **confirm before buying**.
| | Pro 50K | Flex 50K |
|---|---|---|
| Target / max loss | $3,000 / $2,000, trailing at the close, locks at +$100 | same |
| Daily loss limit | $1,200, soft (pauses the day) | none |
| Evaluation consistency | none | 50% (largest day ≤ half of total profit) |
| Funded consistency | 40% | **none** |
| Funded daily loss limit | $1,200 → LucidScale | **none** |
| Payouts | 3-day cycles, $500 profit goal, buffer | 5 days ≥ $150 per cycle, no buffer |
| Other | automated trading allowed; flat by 16:45 ET; up to 5 funded / 10 evaluations per household | |

## Simulation (`orb/prop.py`): an evaluation started on every NQ Session 2016–2026
Feasible sizes: 1 MNQ ≈ $80 per R at today's ATR. The Ensemble needs 1 MNQ per member ≈ $320/R.
| Account | Setup | Pass | Bust | Median days |
|---|---|---|---|---|
| **Flex 50K** | **ORB v1, 2 MNQ ($160/R)** | **72%** | 24% | 70 |
| Flex 50K | ORB v1, 1 MNQ | 65% | 0% | 162 (35% unresolved after 1 year) |
| Pro 50K | ORB v1, 2 MNQ | 72% | 24% | 66 |
| Pro 50K | Ensemble v3, 1 MNQ per member | 72% | 26% | 65 |
| Pro 150K | ORB v1, 3 MNQ | 65% | 0% | 162 |
| Pro 150K | ORB v1 4 MNQ + Ensemble v3 1/member ($640/R) | 70% | 28% | 70 |

## Recommendation
1. **LucidFlex 50K, ORB v1 at 2 MNQ.** Once funded there's no consistency rule and no daily loss limit, which suits a fat-tail strategy that earns on a few trend days. The 50% evaluation rule only delays a pass slightly.
2. Add Ensemble v3 on a 100K/150K account once the Forward Test confirms it.
3. Expect slow, lumpy payouts (win rate about 22%) and roughly $6k a year per account at 2 MNQ, historically. Multiple accounts multiply both payouts and risk, since the signals are identical.
4. **Gate:** start paying for evaluations only after the Forward Test has run long enough to show behaviour like the backtest. These pass rates come from in-sample rules and ignore live slippage.

## Official Lucid facts (help center, checked 2026-09-30)
- **Fees:** one-time, no subscription or activation fee. Flex 50K about $136 list; ~40% codes are common. Resets about $95 (Flex 50K) and must be requested within 30 days.
- **Flex eval:** exceeding 50% consistency is **not** a fail (keep trading until the largest day ≤ 50%). No time limit; can pass in 2 days. The DLL is an optional add-on.
- **Flex funded payouts:** each needs 5 days of ≥ $150 (50K) in the cycle plus a positive cycle. The payout is ≤ 50% of profit, capped at $2,000; minimum request $500; 90/10 split. The request moves the loss limit to the locked level. Moved to live after 5 payouts.
- **Flex scaling (50K):** 2 minis / 20 micros at the start, 4 / 40 at +$2,000.
- **Pro funded:** the 40% consistency rule **blocks** payouts until diluted (bad for our big-day profile). DLL is 60% of peak EOD.
- **Automation and trade copiers across own accounts are allowed.** Up to 10 accounts per household, max 5 funded. News trading is allowed on Flex / Pro / Direct (not LucidDaily). Auto-flatten at 16:45 ET.
- **Implication:** one-time fees mean patience is free, so the safer 1-MNQ evaluation route (0% bust in the simulation) becomes more attractive.

## Open decisions (grilling round 1, 2026-09-30); continue next session
- **Q1 Score:** Prop Score = expected net $/month across accounts (payouts − fees − resets), simulated under Lucid rules for the eval *and* the funded phase. Recommended.
- **Q2:** the monthly budget for evaluations and resets (the user's call).
- **Q3:** a staggered account portfolio (mixed rule sets, sizes and start dates) vs identical accounts. Recommended: staggered.
- **Q4:** separate sizes for eval and funded. Recommended.
- **Q5:** allow payout-aware variants (partial take-profit at about +1R to create more ≥ $150 days), judged by Prop Score and required to stay positive in both eras. Recommended.
- **Q6:** start with one Flex 50K eval at 1 MNQ now as a real-money execution test; scale after the Forward Test agrees. Recommended.
- **Also open:** the user saw a "$44k profit" on a strategy or indicator in TradingView on 2026-09-29. It wasn't found on the current chart (ORB Ensemble on NQ1! 5m shows +$8,045: 4 trades, 1 NQ per member). Ask the user for the script name or a Strategy Tester screenshot, then reproduce it on the 23-year base.

## Decisions (2026-09-30): the user accepted all recommendations Q1–Q6 → ADR 0004
Q1 Prop Score is the objective · Q2 start with a single evaluation (budget set later) · Q3 staggered portfolio · Q4 separate eval / funded sizes · Q5 payout-aware variants allowed but must earn their place · Q6 one evaluation first, as a live execution test.

## Prop Score results (`orb/propscore.py`: full Lucid Flex lifecycle, NQ 2016–2024, 2-year rolling windows)
| Account | Setup (eval → funded $/R) | Net $/month/slot | p10 | Losing windows | Payouts/yr |
|---|---|---|---|---|---|
| Flex 50K | Ensemble v3 640 → 480 | 267 | +36 | 0% | 4.5 |
| Flex 100K | Ensemble v3 960 → 640 | 325 | +32 | 1% | 4.5 |
| **Flex 150K** | **Ensemble v3 960 → 640** | **378** | **+83** | **0%** | **4.5** |
| Flex 150K | ORB v1 + Ens v3 960 → 960 | 399 | −32 | 16% | 4.1 |
| Flex 50K | ORB v1 alone 160 → 160 (1-year windows) | 70 | −20 | 41% | 0.8 |
- **Q5 answered by data:** partial take-profit at 1R (33–50%) lowers Prop Score in every case. Rejected.
- **Best slot: Flex 150K with Ensemble v3,** 3 MNQ per member in the eval ($960/R) and 2 per member funded ($640/R).
- **5 funded slots ≈ $1,500–1,900/month historically.** Slots are correlated (identical signals), so outcomes cluster.
- **Caveats:** in-sample rules, no slippage, fees estimated with a 40% code, live stage not credited.

## Next steps
1. Buy **one Flex 150K** evaluation. Trade Ensemble v3 at **1 MNQ/member** ($320/R) as a live execution test.
2. Connect TradingView alerts → Lucid's platform (Tradovate / TradingView via CQG, or Rithmic). Automation is allowed.
3. Scale to 3/2 MNQ per member and add accounts (up to 5 funded) once the Forward Test and the live fills match the backtest.

## Execution decisions (2026-09-30, ADR 0005)
- **Platform:** Tradovate / TradingView-CQG route recommended; confirming once the automation-bridge research returns.
- **Kill switch:** stop and investigate if fills average > 2 ticks worse than the engine over 10 trades, if a live trade differs from the forward log, or if the drawdown exceeds 1.5× the historical worst (Ensemble v3 ≈ 22R). Losing streaks under 25 trades are normal: no rule changes.
- **Scaling Ladder:** 1 Flex 150K at 1 MNQ per member for 20 clean live days → full sizes → a 2nd staggered account after the first payout → one more at a time, up to 5 funded.
- **The trader watches the first 3–5 live days** (16:35–17:30 local), with a manual flatten ready.
- **Monthly review:** `tools/monthly_review.py` (Windows task "ORB Monthly Review", every 4 weeks, Saturdays) writes `results/monthly_review.txt`.
- **Research continues:** Jev news test (GDELT pull, slow) and monthly re-validation; SOX / NVDA cross-market check when convenient.

## Execution route (decided 2026-09-30)
- **Q6:** a VPS is acceptable. Preferred route is **NinjaTrader 8 on a VPS (CQG feed)**, running Ensemble v3 as a native NinjaScript strategy with every entry's stop and target held at the broker. Pending confirmation that NinjaScript handles 4 per-entry brackets plus activation trailing.
- **Q7:** if exact execution isn't possible, a simplified "execution version" (brackets at entry, broker-native trailing) is allowed **only** after its own 23-year both-era backtest scores close to Ensemble v3.
- **Q8:** the user's TradingView plan is unknown. Only needed for the TradingView→bridge fallback (Essential+ with 2FA).
- **Fallback:** TradingView → PickMyTrade ($50/mo, unlimited accounts) or TradersPost (~$42/mo) on the Tradovate/CQG feed; send the explicit contract (e.g. MNQZ2026), not MNQ1!.
- **Buy the Lucid account on the CQG feed** (works for NinjaTrader, Tradovate and TradingView).

## Execution route confirmed (2026-09-30): NinjaTrader 8 on a Chicago VPS, Lucid CQG / Tradovate credentials
- NinjaScript supports unique entry names + `StopTargetHandling.PerEntryExecution` + `SetStopLoss` / `SetProfitTarget(fromEntrySignal)`, so each member has its own resting broker stop and target. The trail is custom code moving each stop; a disconnect freezes the trail, but the resting stops still protect.
- **No NT license needed** for Tradovate-credential prop accounts. VPS about $15–80/mo.
- **Rejected:** direct Tradovate API (closed to prop / eval accounts); PickMyTrade (`update_sl` changes all legs at once); TradersPost (no trail activation offset).
- **Code:** `ninja/ORBEnsembleV3.cs`. Not compiled yet; needs an NT compile plus a Strategy Analyzer parity check against the Python engine. Reviewed 2026-09-30: fixed the half-day carry-over (exit-on-session-close backstop) and the RTH-chart next-day exit (the flatten is now at the 15:55 open).

## Go-live checklist
1. Buy **Lucid Flex 150K** on the **CQG** feed (use a discount code).
2. Rent a **Windows VPS in Chicago**; install **NinjaTrader 8**; connect with Lucid's Tradovate / CQG credentials.
3. Import `ninja/ORBEnsembleV3.cs` (NinjaScript Editor → compile). Fix any compile errors with Claude.
4. **Strategy Analyzer** on MNQ 5-min, last ~6 months → Trades tab → right-click → Export CSV → `python tools/nt_parity.py <file> --tz <NT time zone>`. Pass = same Sessions, Legs and direction, and entry within 1 tick. Exits may differ slightly (NT flattens at 15:55 on 5-min bars; the engine at 15:59 on 1-min bars).
   - **Size for 2025–26, not the in-sample result:** v3's Prop Score on Flex 150K in 2025–26 was about −$16/month (Edge Hunt Log, ADR 0006 run). Keep the live test at 1 MNQ per Leg (RiskUsd ≈ 80).
5. Run on **Sim101 / Playback** for 3–5 days, then enable on the evaluation at **RiskUsd = $80 (1 MNQ per member)**. The trader watches the first 3–5 live days (ADR 0005).
6. Record live fills in `results/live_fills.csv` for the monthly review's fill check.

## Best-setup search (2026-09-30, `research/prop_search.py`, output `results/prop_search.txt` / `.csv`)
- **Search:** 282 setups = 4 Flex accounts (25K/50K/100K/150K) × 3 Rule Sets (ORB v1, Ensemble v3, v1 + v3) × eval size × funded size (1-6 MNQ per Leg, within Lucid's micro caps).
- **Ranking:** by the **worse** of 2016-24 and 2025-26 net $/month per slot. Both eras use 1-year rolling windows so they're comparable. That makes these numbers lower than the 2-year-window table above.
- **Account rules:** review sites (tradetanto, tradingfunder): targets $1.25k/$3k/$6k/$9k, max loss $1k/$2k/$3k/$4.5k, payout days $100/$150/$200/$250, caps $1k/$2k/$2.5k/$3k. The 150K rules in the code were already right.
- **Fees:** only the 50K ($136 list) is known. The others are assumed at $100/$200/$245 list, all with a 40% code, reset = eval fee. The Flex price page is JS-only; **check at checkout.**

| Account | Rule Set | Eval MNQ | Funded MNQ | $/mo 2016-24 | Losing yrs 2016-24 | $/mo 2025-26 | p10 2025-26 | Losing yrs 2025-26 |
|---|---|---|---|---|---|---|---|---|
| **Flex 150K** | **ORB v1** | **6** | **3** | **128** | **14%** | **244** | **+94** | **0%** |
| Flex 150K | ORB v1 | 6 | 4 | 133 | 29% | 379 | +189 | 0% |
| Flex 100K | ORB v1 | 6 | 3 | 101 | 33% | 289 | +58 | 0% |
| Flex 50K | ORB v1 | 3 | 2 | 77 | 33% | 103 | +32 | 10% |
| Flex 150K | v1 + v3 (1 MNQ each) | 3 | 2 | 278 | 23% | 44 | — | 20% |
| Flex 150K | Ensemble v3 (best 2016-24) | 6/Leg | 3/Leg | **315** | 23% | **−39** | — | **100%** |
| Flex 150K | Ensemble v3 (**current plan**) | 3/Leg | 2/Leg | 267 | 27% | **−27** | — | **100%** |

**Findings**
- **Ensemble v3 loses money under Lucid rules in every 2025-26 window, at every size and on every account.** It's the best 2016-24 setup, but it's broken for prop trading now. v3's extra parts (the 15/30/60 Legs, EMA-200, trail, trend gate) are exactly what stopped paying in 2025-26.
- **ORB v1 is the only Rule Set positive in both eras.** ORB v1 was frozen *before* 2025-26 (that period was its holdout, Sharpe 1.12), so its 2025-26 result is the most honest number we have.
- **Recommended: Flex 150K, ORB v1, 6 MNQ in the evaluation ($480/R ≈ 9R of max loss), 3 MNQ funded.**
  - 6→4 earns more in 2025-26 but has twice as many losing years in 2016-24.
- **Caveats:**
  - 2025-26 is only about 21 months (roughly 10 overlapping 1-year windows, about 2 independent years).
  - Choosing ORB v1 over v3 *using* 2025-26 is itself a selection on seen data.
  - Fees for 25K/100K/150K are assumptions.
- **Action:**
  - `ninja/ORBEnsembleV3.cs` trades v3. ORB v1 is simpler: one 5-min Leg, gap + VWAP filters, 10R/EOD, no trail. It needs either its own NinjaScript port or a v3 strategy mode with only the 5-min Leg and the v2/v3 extras off.
  - Keep v3 in the Forward Test to see whether it recovers.
