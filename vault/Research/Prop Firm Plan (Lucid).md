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
