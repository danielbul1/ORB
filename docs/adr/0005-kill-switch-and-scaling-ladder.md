# Kill switch and scaling ladder are fixed in advance

Good strategies usually fail at the last mile: rules changed mid-drawdown, or silent automation bugs. From 2026-09-30 these rules are fixed and are not edited on a bad day.

**Kill switch: stop live trading and investigate if**
- live fills average > 2 ticks worse than the engine over any 10 trades, or
- a live trade differs from `results/forward_log.csv` on the same Session (missing, extra, wrong side or wrong size), or
- live drawdown exceeds 1.5× the historical worst for the Rule Set (Ensemble v3: 1.5 × 14.6R ≈ 22R).

**Not a reason to change anything:** a losing streak shorter than 25 trades, or a drawdown below 1.5× the historical worst. Both are normal. Monthly review only; never retune on live results.

**Scaling ladder** (each step only after the previous one is met):
1. One Lucid Flex 150K, Ensemble v3 at 1 MNQ per member, until 20 live trading days with fills matching the engine.
2. Full sizes: evaluation 3 MNQ per member ($960/R), funded 2 per member ($640/R).
3. After the first payout, add a second account with a start date ≥ 2 weeks later.
4. Add accounts one at a time, each after the previous one passes, up to 5 funded (Lucid limit).

**The first 3–5 live days are watched by the trader** (entries 16:35–17:30 local, UTC+3), with a manual flatten ready.
