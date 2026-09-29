"""Vectorized opening-range-breakout backtest over a Days matrix: one trade per day at most.

Fill rules are deliberately pessimistic:
  * stop entries fill at the level or at the bar open if price gapped through it;
  * a stop and a target touched in the same bar count as the stop;
  * the target is not allowed to fill on the entry bar, the stop is;
  * every trade pays `cost` points round trip (slippage + commission).
"""
import numpy as np
import pandas as pd

TICK = 0.25
POINT_USD = 20.0  # NQ; MNQ is 2.0
BIG = 10**6

DEFAULTS = dict(
    or_min=15,          # opening range length in minutes
    entry="stop",       # stop: touch of OR +1 tick | close: 1m close beyond OR, fill next open | candle: OR candle direction at end of OR
    side="both",        # both | long | short
    stop="or",          # or: opposite side | mid: OR midpoint | atr: stop_x * ATR14 from entry
    stop_x=0.1,
    target_r=None,      # take profit in R, None = hold to time exit
    cutoff=120,         # last minute (from 09:30) a new entry may fill
    exit_min=389,       # time exit bar (389 = 15:59 close)
    min_or_atr=0.0,     # skip if OR width / ATR14 below
    max_or_atr=9.0,     # skip if OR width / ATR14 above
    rvol_min=0.0,       # skip if OR volume / mean OR volume of prior 14 days below
    gap_dir=None,       # with | against: only trade breakouts in / against the gap direction
    gap_min=0.0,        # skip if |09:30 open - prior close| / ATR14 is below this
    dows=None,          # iterable of weekdays allowed (0=Mon)
    be_r=None,          # move stop to entry after price reaches be_r R
    body_min=0.0,       # candle entry: skip if |OR close - open| / ATR14 below
    vol_regime=0.0,     # skip unless ATR14 / ATR100 >= this
    nr=None,            # 4 | 7: only trade after an NR4 / NR7 day
    stretch_n=10,       # stretch entry: lookback of mean min(H-O, O-L)
    stretch_m=1.0,      # stretch entry: levels at open +- m * stretch
    # --- ideas harvested from the community scripts (research/orb_script_profiles.csv) ---
    target_or=None,     # target at entry +- k * OR width (range extensions) instead of R
    target_pct=None,    # target at entry +- this fraction of price (fixed-point targets scaled to price)
    trail_x=0.0,        # trailing stop distance in ATR14 (0 = off)
    trail_start=2.0,    # trailing stop arms once the trade has been this many R in profit
    min_risk_cost=0.0,  # skip if the stop distance is below this multiple of the round-trip cost
    dir_override=None,  # research control only: per-Session direction array replacing the signal (after filters)
    vwap_side=False,    # entry bar's prior close must be on the trade side of session VWAP
    ema_n=0,            # prior close must be on the trade side of EMA(n) of 1m closes
    htf_side=False,     # prior day close on the trade side of its 20-day SMA
    rsi_block=0,        # skip longs if RSI(70 x 1m ~ 14 x 5m) > rsi_block, shorts if < 100 - rsi_block
    pdhl_block=0.0,     # skip if prior day high (longs) / low (shorts) lies within x ATR ahead of entry
    cost=1.0,           # points round trip
    cost_bp=None,       # if set, round-trip cost in basis points of the entry price instead of `cost`
    cost_floor=0.0,     # with cost_bp: never charge less than this many points
)


def _first(mask):
    i = mask.argmax(1)
    i[~mask.any(1)] = BIG
    return i


def daily(d):
    """Per-day RTH high/low/close/TR and derived context, cached on the Days object."""
    if getattr(d, "_daily", None) is None:
        rows = np.arange(len(d.dates))
        dh, dl = d.h.max(1), d.l.min(1)
        dc = d.c[rows, d.last]
        rng = dh - dl
        tr = np.maximum(rng, np.maximum(abs(dh - d.prev_close), abs(dl - d.prev_close)))
        tr = np.where(np.isfinite(tr), tr, rng)
        def prior_mean(x, n):
            m = np.convolve(x, np.ones(n) / n, "full")[:len(x)]
            m[:n - 1] = np.nan
            return np.r_[np.nan, m[:-1]]
        def prior_nr(n):  # yesterday's range is the smallest of the last n
            out = np.zeros(len(rng), bool)
            for i in range(n, len(rng)):
                out[i] = rng[i - 1] <= rng[i - n:i].min()
            return out
        stretch_src = np.minimum(dh - d.o[:, 0], d.o[:, 0] - dl)
        flat_c = pd.Series(d.c.ravel())
        ema = {n: flat_c.ewm(span=n, adjust=False).mean().values.reshape(d.c.shape) for n in (50, 100, 200)}
        delta = flat_c.diff()
        up = delta.clip(lower=0).ewm(alpha=1 / 70, adjust=False).mean()
        dn = (-delta.clip(upper=0)).ewm(alpha=1 / 70, adjust=False).mean()
        rsi = (100 - 100 / (1 + up / dn.replace(0, np.nan))).values.reshape(d.c.shape)
        tp = (d.h + d.l + d.c) / 3
        vwap = np.cumsum(tp * d.v, 1) / np.maximum(np.cumsum(d.v, 1), 1e-9)
        sma20 = pd.Series(dc).rolling(20).mean().values
        htf = np.sign(np.r_[np.nan, (dc - sma20)[:-1]])  # sign of yesterday's close vs its 20d SMA
        d._daily = dict(atr100=prior_mean(tr, 100), nr4=prior_nr(4), nr7=prior_nr(7),
                        ema=ema, rsi=rsi, vwap=vwap, htf=htf,
                        pdh=np.r_[np.nan, dh[:-1]], pdl=np.r_[np.nan, dl[:-1]],
                        stretch={n: prior_mean(stretch_src, n) for n in (5, 10, 20)})
    return d._daily


def run(d, **p):
    p = {**DEFAULTS, **p}
    ctx = daily(d)
    D, B = d.o.shape
    rows = np.arange(D)
    idx = np.arange(B)[None, :]
    k = p["or_min"]
    orh = d.h[:, :k].max(1)
    orl = d.l[:, :k].min(1)
    width = orh - orl
    atr = d.atr14
    cutoff = np.minimum(p["cutoff"], d.last - 1)[:, None]
    window = (idx >= k) & (idx <= cutoff)

    # --- entry -------------------------------------------------------------
    if p["entry"] == "stop":
        up, dn = orh + TICK, orl - TICK
        jl = _first(window & (d.h >= up[:, None]))
        js = _first(window & (d.l <= dn[:, None]))
        direction = np.where(jl < js, 1, np.where(js < jl, -1, 0))  # same bar = ambiguous, skip
        e = np.minimum(jl, js)
        ec = np.minimum(e, B - 1)
        px_l = np.maximum(up, d.o[rows, ec])
        px_s = np.minimum(dn, d.o[rows, ec])
        entry = np.where(direction > 0, px_l, px_s)
    elif p["entry"] == "close":
        jl = _first(window & (d.c > orh[:, None]))
        js = _first(window & (d.c < orl[:, None]))
        direction = np.where(jl < js, 1, np.where(js < jl, -1, 0))
        e = np.minimum(jl, js) + 1
        e = np.where(e <= cutoff[:, 0] + 1, e, BIG)
        entry = d.o[rows, np.minimum(e, B - 1)]
    elif p["entry"] == "retest":
        jl = _first(window & (d.c > orh[:, None]))
        js = _first(window & (d.c < orl[:, None]))
        direction = np.where(jl < js, 1, np.where(js < jl, -1, 0))
        jb = np.minimum(jl, js)
        edge = np.where(direction > 0, orh, orl)
        back = window & (idx > jb[:, None]) & np.where(direction[:, None] > 0, d.l <= edge[:, None], d.h >= edge[:, None])
        e = _first(back)
        ec = np.minimum(e, B - 1)
        o_e = d.o[rows, ec]
        entry = np.where(direction > 0, np.minimum(edge, o_e), np.maximum(edge, o_e))  # limit order at the edge
    elif p["entry"] == "stretch":
        st = ctx["stretch"][p["stretch_n"]]
        up = np.round((d.o[:, 0] + p["stretch_m"] * st) / TICK) * TICK
        dn = np.round((d.o[:, 0] - p["stretch_m"] * st) / TICK) * TICK
        orh, orl = up - TICK, dn + TICK  # the opposite level is the stop ("or")
        w = (idx >= 0) & (idx <= cutoff)
        jl = _first(w & (d.h >= up[:, None]))
        js = _first(w & (d.l <= dn[:, None]))
        direction = np.where(jl < js, 1, np.where(js < jl, -1, 0))
        e = np.minimum(jl, js)
        ec = np.minimum(e, B - 1)
        entry = np.where(direction > 0, np.maximum(up, d.o[rows, ec]), np.minimum(dn, d.o[rows, ec]))
        width = up - dn
    elif p["entry"] == "candle":
        body = d.c[:, k - 1] - d.o[:, 0]
        direction = np.sign(body).astype(int)
        e = np.full(D, k)
        entry = d.o[:, k]
    else:
        raise ValueError(p["entry"])

    ok = (e < BIG) & (direction != 0) & np.isfinite(atr) & (e < d.last)
    if p["side"] == "long":
        ok &= direction > 0
    elif p["side"] == "short":
        ok &= direction < 0

    # --- filters (all known at entry time) -----------------------------------
    if p["body_min"] > 0:
        ok &= np.abs(d.c[:, k - 1] - d.o[:, 0]) / atr >= p["body_min"]
    if p["vol_regime"] > 0:
        ok &= atr / ctx["atr100"] >= p["vol_regime"]
    if p["nr"]:
        ok &= ctx[f"nr{p['nr']}"]
    pe = np.clip(np.minimum(e, B) - 1, 0, B - 1)  # last bar closed before the entry fills
    px_known = d.c[rows, pe]
    if p["vwap_side"]:
        ok &= direction * (px_known - ctx["vwap"][rows, pe]) > 0
    if p["ema_n"]:
        ok &= direction * (px_known - ctx["ema"][p["ema_n"]][rows, pe]) > 0
    if p["htf_side"]:
        ok &= direction == ctx["htf"]
    if p["rsi_block"]:
        rv = ctx["rsi"][rows, pe]
        ok &= ~(((direction > 0) & (rv > p["rsi_block"])) | ((direction < 0) & (rv < 100 - p["rsi_block"])))
    if p["pdhl_block"]:
        room = np.where(direction > 0, ctx["pdh"] - entry, entry - ctx["pdl"])
        ok &= ~((room > 0) & (room < p["pdhl_block"] * atr))
    ratio = width / atr
    ok &= (ratio >= p["min_or_atr"]) & (ratio <= p["max_or_atr"])
    if p["rvol_min"] > 0:
        orv = d.v[:, :k].sum(1)
        mean = np.convolve(orv, np.ones(14) / 14, "full")[:D]
        prior = np.r_[np.nan, mean[:-1]]
        prior[:14] = np.nan
        ok &= orv / prior >= p["rvol_min"]
    if p["gap_dir"]:
        gap = np.sign(d.o[:, 0] - d.prev_close)
        ok &= (direction == gap) if p["gap_dir"] == "with" else (direction == -gap)
    if p["gap_min"] > 0:
        ok &= np.abs(d.o[:, 0] - d.prev_close) / atr >= p["gap_min"]
    if p["dows"] is not None:
        ok &= np.isin(d.dow, list(p["dows"]))

    if p["dir_override"] is not None:
        direction = np.where(ok, np.asarray(p["dir_override"]), direction)

    # --- stop / target -------------------------------------------------------
    if p["stop"] == "or":
        stop = np.where(direction > 0, orl - TICK, orh + TICK)
    elif p["stop"] == "mid":
        stop = np.where(direction > 0, (orh + orl) / 2 - TICK, (orh + orl) / 2 + TICK)
    elif p["stop"] == "atr":
        stop = entry - direction * p["stop_x"] * atr
    elif p["stop"] == "pct":  # fixed-point stops, expressed as a fraction of price
        stop = entry - direction * p["stop_x"] * entry
    else:
        raise ValueError(p["stop"])
    risk = (entry - stop) * direction
    ok &= risk > 0
    if p["min_risk_cost"]:
        rt = p["cost"] if p["cost_bp"] is None else np.maximum(p["cost_bp"] * 1e-4 * entry, p["cost_floor"])
        ok &= risk >= p["min_risk_cost"] * rt
    tgt = entry + direction * p["target_r"] * risk if p["target_r"] else None
    if p["target_or"]:
        tgt = entry + direction * p["target_or"] * width
    if p["target_pct"]:
        tgt = entry + direction * p["target_pct"] * entry

    ec = np.where(ok, e, 0)[:, None]
    after = idx >= ec
    x_end = np.minimum(p["exit_min"], d.last)
    live = after & (idx <= x_end[:, None])
    dcol = direction[:, None]
    hit_stop = live & np.where(dcol > 0, d.l <= stop[:, None], d.h >= stop[:, None])

    if p["be_r"]:
        trig = entry + direction * p["be_r"] * risk
        jb = _first(live & (idx > ec) & np.where(dcol > 0, d.h >= trig[:, None], d.l <= trig[:, None]))
        be_stop = live & (idx > jb[:, None]) & np.where(dcol > 0, d.l <= entry[:, None], d.h >= entry[:, None])
        j_orig = _first(hit_stop)
        j_be = _first(be_stop)
        use_be = j_be < j_orig
        js_ = np.where(use_be, j_be, j_orig)
        stop_px = np.where(use_be, entry, stop)
    else:
        js_ = _first(hit_stop)
        stop_px = stop

    if p["trail_x"]:
        # Trailing stop: once the best price since entry is >= trail_start R in profit, the stop follows it at
        # trail_x * ATR14. The level used in bar j comes only from bars before j (no look-ahead).
        fav = np.where(live, np.where(dcol > 0, d.h, -d.l), -np.inf)
        best = np.maximum.accumulate(fav, axis=1)
        prev_best = np.concatenate([np.full((D, 1), -np.inf), best[:, :-1]], axis=1)  # signed: long high / -short low
        lvl = prev_best - p["trail_x"] * atr[:, None]            # signed level
        armed = prev_best >= (direction * entry + p["trail_start"] * risk)[:, None]
        signed_low = np.where(dcol > 0, d.l, -d.h)
        hit_tr = live & (idx > ec) & armed & (signed_low <= lvl)
        jtr = _first(hit_tr)
        tr_px = direction * lvl[rows, np.minimum(jtr, B - 1)]
        use_tr = jtr < js_
        js_ = np.where(use_tr, jtr, js_)
        stop_px = np.where(use_tr, tr_px, stop_px)

    if tgt is not None:
        hit_t = live & (idx > ec) & np.where(dcol > 0, d.h >= tgt[:, None], d.l <= tgt[:, None])
        jt = _first(hit_t)
    else:
        jt = np.full(D, BIG)

    jx = x_end
    first = np.minimum(np.minimum(js_, jt), jx)
    fc = np.minimum(first, B - 1)
    o_at = d.o[rows, fc]
    stop_fill = np.where(direction > 0, np.minimum(stop_px, o_at), np.maximum(stop_px, o_at))
    exit_px = np.where(first == js_, stop_fill,
                       np.where(first == jt, tgt if tgt is not None else 0.0, d.c[rows, fc]))
    cost = p["cost"] if p["cost_bp"] is None else np.maximum(p["cost_bp"] * 1e-4 * entry, p["cost_floor"])
    pnl = direction * (exit_px - entry) - cost
    r = pnl / np.where(risk > 0, risk, np.nan)

    return dict(ok=ok, dir=direction, entry=entry, stop=stop, risk=risk, e=e, x=first,
                exit=exit_px, pnl=np.where(ok, pnl, 0.0), r=np.where(ok, r, 0.0),
                reason=np.where(first == js_, "stop", np.where(first == jt, "target", "time")))


def metrics(d, res, mask=None):
    ok = res["ok"] if mask is None else res["ok"] & mask
    dates = d.dates if mask is None else d.dates
    n = int(ok.sum())
    if n == 0:
        return dict(n=0)
    r = res["r"][ok]
    pts = res["pnl"][ok]
    days_r = np.where(ok, res["r"], 0.0)[mask if mask is not None else slice(None)]
    eq = np.cumsum(days_r)
    dd = (np.maximum.accumulate(eq) - eq).max()
    wins, losses = r[r > 0].sum(), -r[r < 0].sum()
    years = (dates[mask][-1] - dates[mask][0]).astype(int) / 365.25 if mask is not None else \
        (dates[-1] - dates[0]).astype(int) / 365.25
    return dict(
        n=n,
        win=round(float((r > 0).mean()), 3),
        avgR=round(float(r.mean()), 3),
        pf=round(float(wins / losses), 2) if losses else float("inf"),
        totR=round(float(r.sum()), 1),
        sharpe=round(float(days_r.mean() / days_r.std() * np.sqrt(252)), 2) if days_r.std() else 0.0,
        ddR=round(float(dd), 1),
        pts=round(float(pts.sum()), 0),
        rPerYr=round(float(r.sum() / max(years, 1e-9)), 1),
    )
