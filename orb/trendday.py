"""Trend-Day Engine: learn *when* the opening move has become a tradable trend, instead of fixed OR times.

At checkpoints k = 5, 15, 30, 45, 60, 75, 90 minutes after 09:30, for each Session:
  direction = sign(close_k - open); a trade enters at the next bar's open with the Ensemble v3 bracket
  (stop 0.1 ATR, 10R target, trail 0.3 ATR from 2R, flat 15:59). Label = that trade's R (after costs).
Features (all known at the checkpoint, oriented to the trade direction):
  gap/ATR, move/ATR, tau (move in 5-min sigma units), VWAP distance/ATR, EMA200 side, OR-range/ATR,
  relative volume so far, checkpoint time, prior-day return/ATR, 5-day return/ATR, ATR14/ATR100,
  major-event-today flags (Jev-labelled calendar).
Model: L2-regularised logistic regression P(R > 0) + linear model for E[R], re-fit each year on all earlier
years (walk-forward). Policy: per Session, take the first checkpoint whose predicted E[R] >= threshold
(one trade per Session, or up to `max_trades`).
"""
import numpy as np
import pandas as pd

from orb.backtest import daily, run
from orb.families import ENSEMBLE_V3

CHECKPOINTS = (5, 15, 30, 45, 60, 75, 90)


def dataset(d, cost, ctx_ext=None):
    """One row per (Session, checkpoint) with features and the realised R of the bracket trade."""
    ctx = daily(d)
    rows = np.arange(len(d.dates))
    atr = d.atr14
    gap = (d.o[:, 0] - d.prev_close) / atr
    dc = d.c[rows, d.last]
    # Yesterday's close-to-close return: dc[i-1] - dc[i-2]. (A first version used dc[i] - dc[i-1], i.e. *today's*
    # return, a look-ahead that produced a fake Sharpe of 4-5.)
    prev_ret = np.r_[np.nan, np.nan, (dc[1:-1] - dc[:-2])] / atr
    ret5 = (d.prev_close - np.r_[np.full(5, np.nan), dc[:-5]]) / atr
    vol_reg = atr / ctx["atr100"]
    v_cum = np.cumsum(d.v, 1)
    v_mean = {k: pd.Series(v_cum[:, k - 1]).rolling(20).mean().shift(1).values for k in CHECKPOINTS}
    out = []
    base = {**ENSEMBLE_V3, "body_min": 0.0, "gap_dir": None, "vwap_side": False, "ema_n": 0, "tau_min": 0.0,
            "min_risk_cost": 4, **cost}
    for k in CHECKPOINTS:
        r = run(d, **{**base, "or_min": k})
        dirn = np.sign(d.c[:, k - 1] - d.o[:, 0])
        move = (d.c[:, k - 1] - d.o[:, 0]) / atr
        tau = np.log(d.c[:, k - 1] / d.o[:, 0]) / (ctx["sig5"][20] * np.sqrt(k / 5))
        vw = (d.c[:, k - 1] - ctx["vwap"][:, k - 1]) / atr
        ema = np.sign(d.c[:, k - 1] - ctx["ema"][200][:, k - 1])
        rng = (d.h[:, :k].max(1) - d.l[:, :k].min(1)) / atr
        f = pd.DataFrame({
            "day": np.arange(len(d.dates)), "k": k, "ok": r["ok"] & (dirn != 0), "R": np.where(r["ok"], r["r"], np.nan),
            "gap_with": gap * dirn, "gap_abs": np.abs(gap), "move": np.abs(move), "tau": tau * dirn,
            "vwap": vw * dirn, "ema": ema * dirn, "or_rng": rng, "rvol": v_cum[:, k - 1] / v_mean[k],
            "t": k / 90, "prev_with": prev_ret * dirn, "ret5_with": ret5 * dirn, "vol_reg": vol_reg,
        })
        if ctx_ext is not None:
            f["event_am"] = (ctx_ext["event_pre_open"] | ctx_ext["event_morning"]).astype(float)
            f["event_pm"] = ctx_ext["event_afternoon"].astype(float)
        out.append(f)
    df = pd.concat(out, ignore_index=True)
    return df[df.ok].replace([np.inf, -np.inf], np.nan).dropna()


FEATURES = ["gap_with", "gap_abs", "move", "tau", "vwap", "ema", "or_rng", "rvol", "t", "prev_with",
            "ret5_with", "vol_reg"]


def walk_forward(df, years, start, end, feats, thresh=0.1, max_trades=1, C=0.3):
    """Fit on years < Y, predict Y; per Session take up to max_trades earliest checkpoints with E[R] >= thresh."""
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    y_of = years[df.day.values]
    picked = []
    for Y in range(start, end + 1):
        tr, te = y_of < Y, y_of == Y
        if te.sum() == 0:
            continue
        Xtr = df.loc[tr, feats].values
        ytr = np.clip(df.loc[tr, "R"].values, -2, 10)
        m = make_pipeline(StandardScaler(), Ridge(alpha=1.0 / C)).fit(Xtr, ytr)
        t = df.loc[te].copy()
        t["pred"] = m.predict(t[feats].values)
        t = t[t.pred >= thresh].sort_values(["day", "k"])
        picked.append(t.groupby("day").head(max_trades))
    return pd.concat(picked) if picked else df.iloc[:0]


def daily_series(picks, n_days, max_trades=1):
    x = np.zeros(n_days)
    np.add.at(x, picks.day.values, picks.R.values / max_trades)
    return x
