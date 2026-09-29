"""The judge: Score, losing streaks and Walk-Forward over 2016-2024 (see docs/adr/0001).

Every Rule Set family is a function `f(d, **params) -> daily` where `daily` is a per-Session P&L array
in any linear unit (R, points, or ATR-normalised points): 0 on days without a trade, NaN never.
Because P&L scales linearly with position size, sizing a Rule Set so its worst drawdown equals the
Account Profile's cap gives Score = cap * yearly P&L / max drawdown.
"""
import itertools

import numpy as np

CAP_USD = 2_000          # Account Profile: max drawdown
WF_START, WF_END = 2019, 2024  # test years; each is tuned on all earlier years (>= 3 years)
RESEARCH_END = np.datetime64("2024-12-31")


def years_of(d):
    return d.dates.astype("datetime64[Y]").astype(int) + 1970


def stats(daily, traded=None):
    """Score and friends for one daily P&L series."""
    x = np.asarray(daily, float)
    if len(x) == 0 or not np.any(x):
        return dict(score=0.0, sharpe=0.0, trades=0, streak=0, yearly=0.0, maxdd=0.0)
    eq = np.cumsum(x)
    dd = float((np.maximum.accumulate(np.r_[0, eq]) - np.r_[0, eq]).max())
    yearly = float(x.mean() * 252)
    t = x[x != 0] if traded is None else x[traded]
    losing = (t < 0).astype(int)
    streak = max((len(list(g)) for k, g in itertools.groupby(losing) if k), default=0)
    return dict(score=round(CAP_USD * yearly / dd, 0) if dd > 0 else float("inf"),
                sharpe=round(float(x.mean() / x.std() * np.sqrt(252)), 2) if x.std() else 0.0,
                trades=int((t != 0).sum()), streak=streak, yearly=round(yearly, 3), maxdd=round(dd, 3),
                win=round(float((t > 0).mean()), 3) if len(t) else 0.0)


def grid(space):
    keys = list(space)
    return [dict(zip(keys, v)) for v in itertools.product(*space.values())]


def walk_forward(d, family, space, key="score", min_trades=60):
    """Tune on years < Y, test on Y, for Y in WF_START..WF_END. Returns stitched OOS daily P&L and choices."""
    yrs = years_of(d)
    params = grid(space)
    cache = {i: family(d, **p) for i, p in enumerate(params)}
    oos = np.zeros(len(d.dates))
    picks = []
    for y in range(WF_START, WF_END + 1):
        tr, te = yrs < y, yrs == y
        best, best_v = None, -np.inf
        for i, p in enumerate(params):
            s = stats(cache[i][tr])
            if s["trades"] >= min_trades and s[key] > best_v:
                best, best_v = i, s[key]
        if best is None:
            continue
        oos[te] = cache[best][te]
        picks.append((y, params[best], round(best_v, 2), stats(cache[best][te])["score"]))
    wf = yrs <= WF_END
    wf &= yrs >= WF_START
    return oos, picks, stats(oos[wf])


def report(name, d, oos, picks, s):
    print(f"\n### {name}\nWalk-forward {WF_START}-{WF_END}: Score ${s['score']:,.0f}/yr at ${CAP_USD} DD cap | "
          f"Sharpe {s['sharpe']} | trades {s['trades']} | win {s.get('win')} | worst losing streak {s['streak']}")
    for y, p, tv, te in picks:
        print(f"  {y}: tuned {tv:>8} -> test Score {te:>8}  {p}")


def deflated_sharpe(daily, n_trials, trial_sharpes_annual):
    """Bailey & Lopez de Prado (2014): probability that the true Sharpe > 0 after selecting the best of
    `n_trials` variants whose annualised Sharpes spread like `trial_sharpes_annual`."""
    from scipy.stats import kurtosis, norm, skew
    x = np.asarray(daily, float)
    T = len(x)
    sr = x.mean() / x.std()                       # per-Session Sharpe
    v = np.var(np.asarray(trial_sharpes_annual) / np.sqrt(252))
    g = 0.5772156649
    sr0 = np.sqrt(v) * ((1 - g) * norm.ppf(1 - 1 / n_trials) + g * norm.ppf(1 - 1 / (n_trials * np.e)))
    denom = np.sqrt(1 - skew(x) * sr + (kurtosis(x, fisher=False) - 1) / 4 * sr**2)
    return dict(sharpe_annual=round(sr * np.sqrt(252), 2), sr0_annual=round(sr0 * np.sqrt(252), 2),
                dsr=round(float(norm.cdf((sr - sr0) * np.sqrt(T - 1) / denom)), 4))
