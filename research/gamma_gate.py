"""ADR 0007 H11: absolute dealer-gamma sizing gate on Ensemble v3 (rules fixed in docs/adr/0007).

Usage: python research/gamma_gate.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research"))
import beat_v3 as B  # noqa: E402
from orb import long as L  # noqa: E402
from orb.judge import deflated_sharpe, stats  # noqa: E402

N_PRIOR_TRIALS = 10  # ADR 0006's Hypotheses, counted toward the deflated Sharpe


def gamma_state(d, q=1 / 3, min_n=252):
    """Per Session: GEX(t-1) <= 0, g(t-1) = GEX/SPX, and the expanding q-quantile cut of g up to t-1."""
    x = pd.read_csv(ROOT / "data" / "ext" / "DIX.csv", parse_dates=["date"]).dropna(subset=["gex", "price"])
    g = (x.gex / x.price).values
    cut = pd.Series(g).expanding(min_periods=min_n).quantile(q).values  # includes day i itself
    idx = pd.DatetimeIndex(x.date)
    s_g, s_cut, s_neg = (pd.Series(v, index=idx) for v in (g, cut, (x.gex <= 0).astype(float).values))
    # prior_series(lag=1): value on the last DIX date strictly before the Session, so all three are t-1.
    return B.prior_series(d, s_g), B.prior_series(d, s_cut), B.prior_series(d, s_neg)


def gate(d, q=1 / 3, off=0.25):
    g, cut, neg = gamma_state(d, q)
    defined = np.isfinite(g) & np.isfinite(cut)
    full = defined & ((neg > 0) | (g <= cut))
    return np.where(full, 1.0, off), full, defined


def judge(name, x, v3, E, defined, verbose=True):
    B.TRIALS.append((name, x))
    mB = E["B 2016-24"] & defined
    scale = stats(v3[mB])["maxdd"] / stats(x[mB])["maxdd"]
    if verbose:
        print(f"\n=== {name}  (Prop rescale x{scale:.2f} to v3's era-B max DD)")
    ok = True
    for k in ("A 2003-15", "B 2016-24", "spent 25-26"):
        m = E[k] & defined
        s, b = stats(x[m]), stats(v3[m])
        p, pb = B.prop(x, m, scale)["net_per_month"], B.prop(v3, m)["net_per_month"]
        win = s["score"] > b["score"] and s["sharpe"] >= b["sharpe"] and p > pb
        judged = k != "spent 25-26"
        ok &= win or not judged
        tag = ("PASS" if win else "fail") if judged else "info"
        if verbose:
            print(f"  {k:12} Sessions {m.sum():>5} | Score {s['score']:>7,.0f} vs {b['score']:>7,.0f} | "
                  f"Sharpe {s['sharpe']:>5} vs {b['sharpe']:>5} | Prop ${p:>5,.0f} vs ${pb:>5,.0f} | "
                  f"DD {s['maxdd']:.1f}R vs {b['maxdd']:.1f}R  [{tag}]")
    if verbose:
        print(f"  VERDICT: {'PASS' if ok else 'FAIL'}")
    return ok


def describe(d, v3, full, defined):
    """Information only: v3 R per year, split by the H11 regime."""
    y = d.dates.astype("datetime64[Y]").astype(int) + 1970
    print("\n--- v3 by year and gamma regime (info only; R = ensemble daily R summed)")
    print(f"  {'year':>4} {'full-size days':>15} {'R low-gamma':>12} {'R high-gamma':>13} {'R/day low':>10} {'R/day high':>11}")
    for yr in range(2012, y.max() + 1):
        m = (y == yr) & defined
        lo, hi = m & full, m & ~full
        print(f"  {yr:>4} {lo.sum():>6} ({lo.sum() / max(m.sum(), 1):>4.0%})   {v3[lo].sum():>+11.2f} {v3[hi].sum():>+13.2f} "
              f"{v3[lo].mean() if lo.any() else 0:>+10.3f} {v3[hi].mean() if hi.any() else 0:>+11.3f}")
    tot_lo, tot_hi = defined & full, defined & ~full
    print(f"  all  {tot_lo.sum():>6} ({tot_lo.sum() / defined.sum():>4.0%})   {v3[tot_lo].sum():>+11.2f} "
          f"{v3[tot_hi].sum():>+13.2f} {v3[tot_lo].mean():>+10.3f} {v3[tot_hi].mean():>+11.3f}")
    t = v3[tot_lo][v3[tot_lo] != 0], v3[tot_hi][v3[tot_hi] != 0]
    se = np.sqrt(t[0].var() / len(t[0]) + t[1].var() / len(t[1]))
    print(f"  per traded day: low {t[0].mean():+.3f} (n={len(t[0])}) vs high {t[1].mean():+.3f} (n={len(t[1])}), "
          f"diff t = {(t[0].mean() - t[1].mean()) / se:.2f}")


def main():
    d = L.load()
    E = L.eras(d)
    res = B.legs(d)
    v3 = B.combine(res)
    size, full, defined = gate(d)
    print(f"Gate defined from {d.dates[defined][0]} ({defined.sum()} Sessions); full size on {full[defined].mean():.0%}")
    verdict = judge("H11 absolute GEX gate (cut 1/3, off 0.25)", v3 * size, v3, E, defined)
    describe(d, v3, full, defined)
    print("\n--- plateau checks (information only, cannot rescue a fail)")
    for q, off in ((1 / 4, 0.25), (1 / 2, 0.25), (1 / 3, 0.0), (1 / 3, 0.5)):
        s, _, _ = gate(d, q, off)
        judge(f"H11 plateau cut {q:.2f} off {off}", v3 * s, v3, E, defined)
    n = N_PRIOR_TRIALS + len(B.TRIALS)
    mB = E["B 2016-24"] & defined
    sh = [stats(x[mB])["sharpe"] for _, x in B.TRIALS]
    print(f"\nDSR H11 (N={n}):", deflated_sharpe((v3 * size)[mB], n, sh))
    print("\n==== H11 VERDICT:", "PASS" if verdict else "FAIL")


if __name__ == "__main__":
    main()
