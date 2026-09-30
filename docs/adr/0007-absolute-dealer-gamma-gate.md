# Absolute dealer-gamma sizing gate on Ensemble v3 (H11)

Registered 2026-09-30, **before** any run. Source: [[ORB Best Practices Research]] §1.1 (Adams et al. 2026; Barbon & Buraschi; Zarattini/Aziz/Barbon 2024 §4.5): long dealer gamma produces intraday reversal, short gamma produces momentum. SqueezeMetrics GEX was negative on 41% of days in 2022 but only 0.4 / 3.6 / 4.8% in 2024 / 2025 / 2026. That could explain v3's flat 2025-26.

Why this is not a repeat of the Round 1 GEX switch (rejected): Round 1 used the **trailing-year rank** of GEX on ORB v1 and skipped days. A trailing rank rescales every year to 0-1. So it cannot express "gamma was high all year", which is exactly the decay story. H11 uses the **absolute level** (sign, and GEX/price against its whole history), and it **sizes** instead of skipping.

Decisions (fixed before the run):
- **Rule H11:**
  - Variable: g = GEX(t−1) / SPX price(t−1) from `data/ext/DIX.csv`, using the prior trading day only.
  - Cut: c = the 1/3 quantile of all g values from 2011-05-02 up to t−1 (expanding window; defined once ≥ 252 values exist).
  - Size = **1.0** if GEX(t−1) ≤ 0 or g ≤ c, otherwise **0.25**. Every Leg of Ensemble v3 is unchanged.
- **Judged Sessions:** only those where the gate is defined, i.e. era A is restricted to ~2012-05 → 2015. The same Sessions are used for v3.
- **Pass bar (as ADR 0006):** beat v3 on Score, Sharpe (≥) **and** Prop Score in **both** eras (A restricted, B 2016-24).
  - For the Prop Score only, H11's daily R is rescaled so that its era-B max drawdown equals v3's. Otherwise lower size would lose on dollars by construction.
  - 2025-26 is reported as information only (it is spent, and this idea was motivated by looking at it).
- **Information only (cannot rescue a fail):**
  - plateau checks with the cut at the 1/4 and 1/2 quantiles and off-size 0 / 0.5;
  - v3 R per year and per GEX regime.
- Budget: this ADR opens a new budget of **at most 8 Hypotheses (H11-H18)** under the ADR 0006 rules. H11 is the first. Every variant counts toward the deflated Sharpe, including ADR 0006's 10.
- If H11 passes, it joins the Forward Test beside v3. It replaces v3 only if the Forward Test agrees (ADR 0001).

Considered: a pure skip at GEX ≤ 0 (rejected: GEX ≤ 0 was 0.4% of 2024 days, so it would barely trade in the regime we care about, and n is too small); a VIX proxy (kept for later as a separate Hypothesis, H12).
