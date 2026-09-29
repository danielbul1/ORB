"""Rule Set families as daily P&L functions for the judge (orb/judge.py).

Units: ORB families return R; time-based families return points / ATR14 (a constant-volatility
position), both linear in size, so the judge's Score is comparable across families.
"""
import numpy as np

from orb.backtest import daily as context
from orb.backtest import run

ORB_V1 = dict(or_min=5, entry="candle", stop="atr", stop_x=0.1, target_r=10, body_min=0.05,
              gap_dir="with", vwap_side=True)


def orb(d, **p):
    res = run(d, **{**ORB_V1, **p})
    return np.where(res["ok"], res["r"], 0.0)


def late_day(d, signal="prev_close", start=360, exit_bar=389, thresh=0.0, cost=1.0, side="both",
             agree_orb=False):
    """Intraday momentum into the close (Gao et al. 2018; Baltussen et al. 2021).

    signal: prev_close -> return from yesterday's close to the entry bar ('rest of day', Baltussen)
            open       -> return from today's 09:30 open to the entry bar
            first30    -> return from yesterday's close to 10:00 (Gao et al.)
    Enter at the close of bar `start - 1` (start=360 is 15:30), exit at the close of `exit_bar`.
    thresh: minimum |signal| in ATR14 units to trade.
    """
    rows = np.arange(len(d.dates))
    t0 = np.minimum(start - 1, d.last - 1)
    px_in = d.c[rows, t0]
    ref = {"prev_close": d.prev_close, "open": d.o[:, 0]}.get(signal)
    if signal == "first30":
        sig = d.c[:, 29] - d.prev_close
    else:
        sig = px_in - ref
    atr = d.atr14
    direction = np.sign(sig)
    if side == "long":
        direction = np.where(direction > 0, 1, 0)
    elif side == "short":
        direction = np.where(direction < 0, -1, 0)
    ok = np.isfinite(atr) & np.isfinite(sig) & (np.abs(sig) / atr >= thresh) & (d.last >= start)
    x = np.minimum(exit_bar, d.last)
    px_out = d.c[rows, x]
    pnl = (direction * (px_out - px_in) - cost) / atr
    return np.where(ok & (direction != 0), pnl, 0.0)


def fade(d, or_min=15, cutoff=120, back_bars=0, stop="extreme", stop_x=0.1, target="mid", target_r=2.0,
         exit_min=389, cost=1.0, gap_filter=None):
    """Failed-breakout fade: price breaks one side of the OR, then closes back inside it; trade the other way.

    Entry at the next bar's open after the first close back inside the range (within `cutoff`).
    stop:   extreme -> beyond the breakout's extreme (+1 tick) | atr -> stop_x * ATR14 from entry
    target: mid -> OR midpoint | opposite -> the other side of the OR | r -> target_r * risk | none -> time exit
    """
    D, B = d.o.shape
    rows = np.arange(D)
    idx = np.arange(B)[None, :]
    orh, orl = d.h[:, :or_min].max(1), d.l[:, :or_min].min(1)
    lim = np.minimum(cutoff, d.last - 2)[:, None]
    win = (idx >= or_min) & (idx <= lim)

    def first(m):
        i = m.argmax(1)
        i[~m.any(1)] = 10**6
        return i

    up_break = first(win & (d.h > orh[:, None]))
    dn_break = first(win & (d.l < orl[:, None]))
    broke_up = up_break < dn_break  # the first side taken
    jb = np.minimum(up_break, dn_break)
    back = win & (idx > jb[:, None]) & np.where(broke_up[:, None], d.c < orh[:, None], d.c > orl[:, None])
    jr = first(back)
    e = jr + 1
    ok = (jr < 10**6) & (e < d.last) & np.isfinite(d.atr14)
    ec = np.minimum(e, B - 1)
    direction = np.where(broke_up, -1, 1)
    entry = d.o[rows, ec]
    seg = (idx >= jb[:, None]) & (idx <= np.minimum(jr, B - 1)[:, None])
    ext = np.where(broke_up, np.where(seg, d.h, -np.inf).max(1), np.where(seg, d.l, np.inf).min(1))
    if stop == "extreme":
        stp = np.where(broke_up, ext + 0.25, ext - 0.25)
    else:
        stp = entry - direction * stop_x * d.atr14
    risk = (entry - stp) * direction
    ok &= risk > 0
    if gap_filter == "against":   # fade only breakouts that went with... the gap (trap in gap direction)
        gap = np.sign(d.o[:, 0] - d.prev_close)
        ok &= direction == -gap
    elif gap_filter == "with":
        gap = np.sign(d.o[:, 0] - d.prev_close)
        ok &= direction == gap
    mid = (orh + orl) / 2
    tgt = {"mid": mid, "opposite": np.where(direction > 0, orh, orl),
           "r": entry + direction * target_r * risk, "none": None}[target]
    if tgt is not None:
        ok &= (tgt - entry) * direction > 0
    live = (idx >= ec[:, None]) & (idx <= np.minimum(exit_min, d.last)[:, None])
    dcol = direction[:, None]
    js = first(live & np.where(dcol > 0, d.l <= stp[:, None], d.h >= stp[:, None]))
    jt = first(live & (idx > ec[:, None]) & np.where(dcol > 0, d.h >= tgt[:, None], d.l <= tgt[:, None])) \
        if tgt is not None else np.full(D, 10**6)
    jx = np.minimum(exit_min, d.last)
    f = np.minimum(np.minimum(js, jt), jx)
    fc = np.minimum(f, B - 1)
    o_at = d.o[rows, fc]
    stop_fill = np.where(direction > 0, np.minimum(stp, o_at), np.maximum(stp, o_at))
    out = np.where(f == js, stop_fill, np.where(f == jt, tgt if tgt is not None else 0, d.c[rows, fc]))
    r = (direction * (out - entry) - cost) / np.where(risk > 0, risk, np.nan)
    return np.where(ok, np.nan_to_num(r), 0.0)


def orb_regime(d, ctx, gex_max=1.0, skip_fomc=False, skip_pre_open_event=False, **p):
    """ORB v1 switched off in some regimes. gex_max: skip Sessions whose prior GEX rank (trailing year) is above it."""
    x = orb(d, **p)
    off = np.zeros(len(x), bool)
    if gex_max < 1.0:
        off |= ~(ctx["gex_rank"] <= gex_max)  # unknown GEX (before 2012) counts as off only if a threshold is set
    if skip_fomc:
        off |= ctx["event_afternoon"] & ctx["event_fed"]
    if skip_pre_open_event:
        off |= ctx["event_pre_open"]
    return np.where(off, 0.0, x)
