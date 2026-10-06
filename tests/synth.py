"""Synthetic 1m Sessions (random walk with volume and pre-open bars) for engine tests without market data."""
import numpy as np

from orb.data import PRE_BARS, RTH_BARS, Days


def make(n_days=400, seed=0):
    rng = np.random.default_rng(seed)
    B = PRE_BARS + RTH_BARS
    steps = rng.standard_t(4, size=(n_days, B)) * 2.0 + rng.normal(0, 0.3, (n_days, 1))
    start = 15000 + np.cumsum(rng.normal(0, 60, n_days))
    c = start[:, None] + np.cumsum(steps, 1)
    o = np.concatenate([start[:, None], c[:, :-1]], 1)
    wick = np.abs(rng.normal(0, 1.5, (n_days, B)))
    h = np.maximum(o, c) + wick
    l = np.minimum(o, c) - np.abs(rng.normal(0, 1.5, (n_days, B)))
    q = lambda x: np.round(x * 4) / 4
    o, h, l, c = q(o), q(h), q(l), q(c)
    v = rng.gamma(2.0, 500, (n_days, B)) * np.r_[np.full(PRE_BARS, 0.3), np.linspace(3, 1, RTH_BARS)]
    P = PRE_BARS
    last = np.full(n_days, RTH_BARS - 1)
    last[rng.choice(n_days, 5, replace=False)] = 209  # a few half days
    dh, dl = h[:, P:].max(1), l[:, P:].min(1)
    dc = c[np.arange(n_days), P + last]
    prev = np.r_[np.nan, dc[:-1]]
    tr = np.maximum(dh - dl, np.maximum(abs(dh - prev), abs(dl - prev)))
    tr[0] = dh[0] - dl[0]
    atr = np.r_[np.full(14, np.nan), np.convolve(tr, np.ones(14) / 14, "valid")[:-1]]
    dates = np.arange(np.datetime64("2016-01-04"), np.datetime64("2016-01-04") + n_days * 7 // 5 + 7)
    dates = dates[(dates.view("int64") - 4) % 7 < 5][:n_days]
    return Days(dates=dates, o=o[:, P:], h=h[:, P:], l=l[:, P:], c=c[:, P:], v=v[:, P:], last=last,
                prev_close=prev, atr14=atr, dow=(dates.view("int64") - 4) % 7, pre_h=h[:, :P], pre_l=l[:, :P])
