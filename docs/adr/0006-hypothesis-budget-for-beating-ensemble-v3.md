# A fixed budget of pre-registered hypotheses to beat Ensemble v3

Mission (2026-09-30): "create the best ORB strategy." Ensemble v3 is the incumbent. Both holdouts (NQ 2025–26, NAS100 2003–15) are spent, and the Trend-Day Engine showed that more models on the same price bars don't beat v3. Any new "win" is therefore found on seen data and is suspect by default.

Decisions:
- **Best** = highest Prop Score (ADR 0004), and the Rule Set must still have an Edge by Score in both eras of the 23-year base.
- The search builds on v3: new **Filters and Day Types** that add information v3 doesn't use (economic calendar, VIX / cross-asset state at the open; news via Jev once the ADR 0003 pull finishes), and a **second Portfolio Member** from a different family that adds to the Portfolio's Score.
- **Budget:** at most 10 Hypotheses. Each is written into the Edge Hunt Log (rule, parameters, pass bar) *before* it is run. Every variant tried counts toward the deflated Sharpe.
- **Pass bar:** beat v3 (or, for a Portfolio Member, raise the Portfolio's Score and Prop Score) in the Walk-Forward of *both* eras. A pass then runs beside v3 in the Forward Test and replaces or joins it only if the Forward Test agrees.
- If none of the 10 passes, v3 stays the best, and that result counts as a valid outcome.
- Live execution of v3 (NinjaTrader on a VPS) proceeds in parallel and is not blocked by the search.

Considered: an open-ended search (rejected: it guarantees an overfit winner), accepting in-sample gains (rejected for the same reason), and a clean-slate redesign (rejected: repeats work whose result is known).
