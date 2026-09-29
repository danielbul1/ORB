"""Noise-area intraday momentum (Zarattini, Aziz & Barbon 2024, "Beat the Market"), ported to NQ.

sigma(t) = mean over the prior `n` days of |close(t) / open - 1| for each minute of the session.
Upper band = max(open, prior close) * (1 + vm * sigma(t)); lower band = min(open, prior close) * (1 - vm * sigma(t)).
Every `step` minutes from 10:00: go long above the upper band, short below the lower band;
the trailing stop is max(upper band, VWAP) for longs and min(lower band, VWAP) for shorts, checked at the
same checkpoints. Flat at the close. Fills at the checkpoint close plus half the round-trip cost per side.
"""
import numpy as np


def run(d, n=14, vm=1.0, step=30, first=30, cost=1.0, side="both", exit_min=389):
    D, B = d.c.shape
    o0 = d.o[:, 0]
    move = np.abs(d.c / o0[:, None] - 1)
    csum = np.cumsum(np.nan_to_num(move), axis=0)
    sigma = np.full_like(move, np.nan)
    sigma[n:] = (csum[n - 1:-1] - np.r_[np.zeros((1, B)), csum[:-n - 1]]) / n  # prior n days only
    ref_hi = np.fmax(o0, d.prev_close)[:, None]
    ref_lo = np.fmin(o0, d.prev_close)[:, None]
    ub = ref_hi * (1 + vm * sigma)
    lb = ref_lo * (1 - vm * sigma)
    tp = (d.h + d.l + d.c) / 3
    vwap = np.cumsum(tp * d.v, 1) / np.maximum(np.cumsum(d.v, 1), 1e-9)

    checks = list(range(first - 1, B, step))
    if checks[-1] != exit_min:
        checks = [c for c in checks if c < exit_min] + [exit_min]
    rows = np.arange(D)
    pos = np.zeros(D)
    pnl = np.zeros(D)
    trades = np.zeros(D)
    prev_px = None
    valid = np.isfinite(sigma[:, 0]) & np.isfinite(d.prev_close)
    for j, t in enumerate(checks):
        t_eff = np.minimum(t, d.last)
        px = d.c[rows, t_eff]
        if prev_px is not None:
            pnl += pos * (px - prev_px)
        final = (j == len(checks) - 1) | (t >= d.last)
        u, l_, vw = ub[rows, t_eff], lb[rows, t_eff], vwap[rows, t_eff]
        new = pos.copy()
        new[(pos > 0) & (px < np.fmax(u, vw))] = 0
        new[(pos < 0) & (px > np.fmin(l_, vw))] = 0
        flat = new == 0
        if side in ("both", "long"):
            new[flat & (px > u)] = 1
        if side in ("both", "short"):
            new[flat & (px < l_)] = -1
        new[final] = 0
        new[~valid] = 0
        trades += np.abs(new - pos)
        pos = np.where(final, 0, new)
        prev_px = px
    pnl -= trades * cost / 2
    return dict(pnl=pnl, ret=pnl / o0, trades=trades, valid=valid)


def metrics(d, res, mask, vol_target=None, cap=4.0):
    """Sharpe of daily returns at 1x notional; with vol_target, sized by prior 14-day realized vol."""
    r = res["ret"].copy()
    if vol_target:
        vol = np.full_like(r, np.nan)
        dr = d.c[np.arange(len(r)), d.last] / d.prev_close - 1
        for i in range(15, len(r)):
            vol[i] = np.nanstd(dr[i - 14:i])
        lev = np.minimum(cap, vol_target / vol)
        r = r * np.nan_to_num(lev)
    m = mask & res["valid"]
    x = r[m]
    active = res["trades"][m] > 0
    eq = np.cumsum(x)
    return dict(days=int(m.sum()), active=round(float(active.mean()), 2),
                annRet=round(float(x.mean() * 252), 3), sharpe=round(float(x.mean() / x.std() * np.sqrt(252)), 2),
                maxDD=round(float((np.maximum.accumulate(eq) - eq).max()), 3),
                ptsPerDay=round(float(res["pnl"][m].mean()), 2))
