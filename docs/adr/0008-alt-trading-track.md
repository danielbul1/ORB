# A separate Alt Trading track with its own budget of 5 pre-registered Hypotheses

Mission (2026-10-06): "build the strongest ORB, learning from how alttrading.ai trades." ADR 0006's budget is spent (0 of 10 passed). The rules of their free scripts (ATX ORB Sniper V1–V4, Mike's ORB Signal Pro) are now known from their Pine source; their B1 system is unpublished and none of their claims comes with statistics.

Decisions:
- **Alt Baseline first.** The Sniper modes and Mike's ORB Signal Pro are reproduced as their code runs (quirks included), alongside the existing prose skeleton (`research/alt_skeleton.py`). These are measured for information only: they are never traded and spend no Hypothesis.
- **Budget:** at most 5 Hypotheses, derived from Alt's published ideas (acceptance / retest, OR midpoint, pre-open range 09:15–09:30, Initial Balance breakout with volume, narrow vs wide OR). All five are written into the Edge Hunt Log *before* any Alt Baseline number is seen.
- **Pass bar:** Walk-Forward (ADR 0001) better than the stronger of Ensemble v3 and ORB v1 on Flex 150K, Prop Score above ORB v1 on Flex 150K, then ≥ 60 Sessions of positive Forward Test. A Hypothesis may also pass as a Portfolio Member by raising the Portfolio's Score and Prop Score.
- The Python engine judges; the TradingView indicator and strategy must reach Parity with it.

Considered: folding the Alt ideas into ADR 0006 (rejected: that budget is spent and the bar was v3 alone, which has weakened in 2025–26), a clean slate ignoring past ADRs (rejected: the validation rules are what stop us fooling ourselves), and an open-ended search (rejected: guarantees an overfit winner).
