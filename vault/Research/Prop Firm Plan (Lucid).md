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
