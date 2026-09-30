"""Do TradingView's most-liked indicators predict anything on Nasdaq-100 intraday? Default rules, no tuning.

Each indicator is computed from its published Pine code defaults (research/top_indicators.json) on a continuous
RTH-only bar series (like a TV chart with extended hours off), signals on bar close, filled at the next bar,
flat at every Session end. Costs as in orb/long.py: 0.83 bp round trip, at least 0.5 pt.

This is a descriptive study of the indicators, not a Hypothesis for beating Ensemble v3 (ADR 0006):
nothing here is tuned or promoted.

Usage: python research/indicator_nq_test.py         -> research/indicator_nq_test.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb.long import COST, eras, load  # noqa: E402

OUT = ROOT / "research" / "indicator_nq_test.csv"


# ---------- Pine built-ins on numpy arrays ----------
def sma(x, n):
    return pd.Series(x).rolling(n).mean().values


def ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False).mean().values


def rma(x, n):
    return pd.Series(x).ewm(alpha=1 / n, adjust=False).mean().values


def stdev(x, n):
    return pd.Series(x).rolling(n).std(ddof=0).values


def highest(x, n):
    return pd.Series(x).rolling(n).max().values


def lowest(x, n):
    return pd.Series(x).rolling(n).min().values


def prev(x, k=1):
    return np.r_[np.full(k, np.nan), x[:-k]]


def true_range(h, l, c):
    pc = prev(c)
    return np.fmax(h - l, np.fmax(np.abs(h - pc), np.abs(l - pc)))


def atr(h, l, c, n):
    return rma(true_range(h, l, c), n)


def linreg(x, n):
    """ta.linreg(x, n, 0): the end point of a least-squares line over the last n values."""
    w = np.arange(n, 0, -1, dtype=float)  # newest bar weighs n
    wma = np.convolve(x, w / w.sum(), mode="full")[: len(x)]
    wma[: n - 1] = np.nan
    return 3 * wma - 2 * sma(x, n)  # identity: least-squares end point = 3 WMA - 2 SMA


def pivots(x, left, right, high=True):
    """ta.pivothigh/pivotlow: value known `right` bars after the pivot, at the confirming bar; else NaN."""
    s = pd.Series(x)
    w = s.rolling(left + right + 1)
    ext = w.max() if high else w.min()
    mid = s.shift(right)
    out = np.where(mid.values == ext.values, mid.values, np.nan)
    return out


def ffill(x):
    return pd.Series(x).ffill().values


def cross_up(a, b):
    return (a > b) & (prev(a) <= prev(b))


def hold(entry_long, entry_short, exit_long=None, exit_short=None, new_day=None):
    """Turn entry/exit events into a position series; flat at each Session start."""
    p = np.zeros(len(entry_long))
    cur = 0
    for i in range(len(p)):
        if new_day[i]:
            cur = 0
        if cur == 1 and exit_long is not None and exit_long[i]:
            cur = 0
        if cur == -1 and exit_short is not None and exit_short[i]:
            cur = 0
        if entry_long[i]:
            cur = 1
        elif entry_short[i]:
            cur = -1
        p[i] = cur
    return p


# ---------- the indicators (defaults from their published code) ----------
def supertrend(o, h, l, c, v, nd):  # KivancOzbilgic SuperTrend: ATR 10, x3, hl2
    a = atr(h, l, c, 10)
    hl2 = (h + l) / 2
    up, dn = hl2 - 3 * a, hl2 + 3 * a
    trend = np.ones(len(c))
    for i in range(1, len(c)):
        if c[i - 1] > up[i - 1]:
            up[i] = max(up[i], up[i - 1]) if np.isfinite(up[i - 1]) else up[i]
        if c[i - 1] < dn[i - 1]:
            dn[i] = min(dn[i], dn[i - 1]) if np.isfinite(dn[i - 1]) else dn[i]
        t = trend[i - 1]
        trend[i] = 1 if t == -1 and c[i] > dn[i - 1] else -1 if t == 1 and c[i] < up[i - 1] else t
    return trend


def ut_bot(o, h, l, c, v, nd):  # QuantNomad UT Bot: key 1, ATR 10
    loss = atr(h, l, c, 10)
    ts = np.zeros(len(c))
    pos = np.zeros(len(c))
    for i in range(1, len(c)):
        p = ts[i - 1]
        if c[i] > p and c[i - 1] > p:
            ts[i] = max(p, c[i] - loss[i])
        elif c[i] < p and c[i - 1] < p:
            ts[i] = min(p, c[i] + loss[i])
        else:
            ts[i] = c[i] - loss[i] if c[i] > p else c[i] + loss[i]
        pos[i] = 1 if c[i - 1] < p < c[i] else -1 if c[i - 1] > p > c[i] else pos[i - 1]
    return np.nan_to_num(pos)


def squeeze(o, h, l, c, v, nd):  # LazyBear: trade the direction of momentum when the squeeze fires
    basis, dev = sma(c, 20), 1.5 * stdev(c, 20)  # sic: the published code uses the KC multiplier for BB
    rng = sma(true_range(h, l, c), 20)
    sqz_on = (basis - dev > basis - rng * 1.5) & (basis + dev < basis + rng * 1.5)
    val = linreg(c - ((highest(h, 20) + lowest(l, 20)) / 2 + sma(c, 20)) / 2, 20)
    fired = prev(sqz_on.astype(float)) == 1
    fired &= ~sqz_on
    return hold(fired & (val > 0), fired & (val < 0), val < prev(val), val > prev(val), nd)


def wavetrend(o, h, l, c, v, nd):  # LazyBear WT: cross in OB/OS 53, exit on opposite cross
    ap = (h + l + c) / 3
    esa = ema(ap, 10)
    d = ema(np.abs(ap - esa), 10)
    wt1 = ema((ap - esa) / (0.015 * d), 21)
    wt2 = sma(wt1, 4)
    up, dn = cross_up(wt1, wt2), cross_up(wt2, wt1)
    return hold(up & (wt1 < -53), dn & (wt1 > 53), dn, up, nd)


def macd(o, h, l, c, v, nd):  # TV built-in MACD 12/26/9: histogram sign
    m = ema(c, 12) - ema(c, 26)
    return np.sign(m - ema(m, 9))


def adx_di(o, h, l, c, v, nd):  # BeikabuOyaji ADX and DI: 14, threshold 20
    up, dn = h - prev(h), prev(l) - l
    pdm = np.where((up > dn) & (up > 0), up, 0)
    mdm = np.where((dn > up) & (dn > 0), dn, 0)
    tr = true_range(h, l, c)
    s = lambda x: pd.Series(np.nan_to_num(x)).ewm(alpha=1 / 14, adjust=False).mean().values  # noqa: E731 (Wilder sum / len)
    dip, dim = s(pdm) / s(tr) * 100, s(mdm) / s(tr) * 100
    adx = sma(np.abs(dip - dim) / (dip + dim) * 100, 14)
    return np.where(adx > 20, np.sign(dip - dim), 0)


def chandelier(o, h, l, c, v, nd):  # everget Chandelier Exit: 22, x3, close extremes
    a = 3 * atr(h, l, c, 22)
    ls, ss = highest(c, 22) - a, lowest(c, 22) + a
    d = np.ones(len(c))
    for i in range(1, len(c)):
        if np.isfinite(ls[i - 1]) and c[i - 1] > ls[i - 1]:
            ls[i] = max(ls[i], ls[i - 1])
        if np.isfinite(ss[i - 1]) and c[i - 1] < ss[i - 1]:
            ss[i] = min(ss[i], ss[i - 1])
        d[i] = 1 if c[i] > ss[i - 1] else -1 if c[i] < ls[i - 1] else d[i - 1]
    return d


def bb_rsi(o, h, l, c, v, nd):  # ChartArt Bollinger + RSI v1.1: RSI 6 crosses 50 as close re-enters BB(200, 2)
    up_, dn_ = np.fmax(c - prev(c), 0), np.fmax(prev(c) - c, 0)
    r = 100 - 100 / (1 + rma(up_, 6) / rma(dn_, 6))
    basis, dev = sma(c, 200), 2 * stdev(c, 200)
    long_ = cross_up(r, np.full(len(c), 50.0)) & cross_up(c, basis - dev)
    short = cross_up(np.full(len(c), 50.0), r) & cross_up(basis + dev, c)
    return hold(long_, short, None, None, nd)  # the strategy has no exit: reverse or Session end


def rsi2(o, h, l, c, v, nd):  # ChrisMoody RSI-2 (Connors): trend by SMA200, dip by RSI(2) < 10, exit above SMA5
    up_, dn_ = np.fmax(c - prev(c), 0), np.fmax(prev(c) - c, 0)
    r = 100 - 100 / (1 + rma(up_, 2) / rma(dn_, 2))
    m5, m200 = sma(c, 5), sma(c, 200)
    return hold((c > m200) & (c < m5) & (r < 10), (c < m200) & (c > m5) & (r > 90), c > m5, c < m5, nd)


def sr_breaks(o, h, l, c, v, nd):  # LuxAlgo S/R with Breaks: pivots 15/15, volume osc > 20
    hi = ffill(prev(pivots(h, 15, 15, True)))
    lo = ffill(prev(pivots(l, 15, 15, False)))
    osc = 100 * (ema(v, 5) - ema(v, 10)) / ema(v, 10)
    return hold(cross_up(c, hi) & (osc > 20), cross_up(lo, c) & (osc > 20), None, None, nd)


def smc_structure(o, h, l, c, v, nd):  # LuxAlgo SMC internal structure (length 5): trade each BOS/CHoCH break
    hi = ffill(pivots(h, 5, 5, True))
    lo = ffill(pivots(l, 5, 5, False))
    return hold(cross_up(c, hi), cross_up(lo, c), None, None, nd)


def vfi(o, h, l, c, v, nd):  # LazyBear Volume Flow Indicator: 130, sign of VFI
    tp = (h + l + c) / 3
    cutoff = 0.2 * stdev(np.log(tp) - np.log(prev(tp)), 30) * c
    vave = prev(sma(v, 130))
    vc = np.fmin(v, vave * 2.5)
    mf = tp - prev(tp)
    vcp = np.where(mf > cutoff, vc, np.where(mf < -cutoff, -vc, 0))
    f = pd.Series(vcp).rolling(130).sum().values / vave
    return np.sign(np.nan_to_num(f))


def nadaraya(o, h, l, c, v, nd):  # LuxAlgo Nadaraya-Watson Envelope, non-repainting endpoint: h=8, mult=3
    w = np.exp(-np.arange(500) ** 2 / (2 * 8 ** 2))
    w = w[w > 1e-8]
    y = np.convolve(c, w / w.sum(), mode="full")[: len(c)]
    y[: len(w)] = np.nan
    mae = sma(np.abs(c - y), 499) * 3
    return hold(cross_up(y - mae, c), cross_up(c, y + mae), c > y, c < y, nd)  # fade the envelope, exit at centre


INDICATORS = {
    "Squeeze Momentum [LazyBear]": squeeze, "SuperTrend [Kivanc]": supertrend, "WaveTrend [LazyBear]": wavetrend,
    "UT Bot Alerts": ut_bot, "S/R Levels with Breaks [LuxAlgo]": sr_breaks, "SMC structure breaks [LuxAlgo]": smc_structure,
    "Bollinger + RSI [ChartArt]": bb_rsi, "ADX and DI": adx_di, "Nadaraya-Watson Env. [LuxAlgo]": nadaraya,
    "Chandelier Exit [everget]": chandelier, "Volume Flow Indicator [LazyBear]": vfi, "CM RSI-2 [ChrisMoody]": rsi2,
    "MACD 12/26/9 (built-in)": macd,
}


def bars(d, k):
    """(D, 390) 1-minute Sessions -> flat arrays of k-minute bars, plus a per-bar Session index."""
    D, n = len(d.dates), 390 // k
    rs = lambda x: x[:, : n * k].reshape(D, n, k)  # noqa: E731
    o, h, l, c, v = rs(d.o)[:, :, 0], rs(d.h).max(2), rs(d.l).min(2), rs(d.c)[:, :, -1], rs(d.v).sum(2)
    ok = np.arange(n)[None, :] * k <= d.last[:, None]  # drop bars after a half-day close
    day = np.repeat(np.arange(D)[:, None], n, 1)
    return [x[ok] for x in (o, h, l, c, v, day)]


def evaluate(d, k):
    o, h, l, c, v, day = bars(d, k)
    nd = np.r_[True, day[1:] != day[:-1]]
    last = np.r_[day[1:] != day[:-1], True]
    ret = np.r_[c[1:] / c[:-1] - 1, 0]
    era = eras(d)
    rows = []
    sigs = dict(INDICATORS, **{"Long every Session (baseline)": lambda *a: np.ones(len(c))})
    for name, fn in sigs.items():
        p = np.nan_to_num(fn(o, h, l, c, v, nd)).astype(float)
        p[last] = 0  # flat into the Session close
        turn = np.abs(np.diff(np.r_[0, p]))
        side_cost = np.maximum(COST["cost_bp"] / 2e4, COST["cost_floor"] / 2 / c)
        gross = p * ret
        net = gross - turn * side_cost
        g_day = np.bincount(day, gross, len(d.dates))
        n_day = np.bincount(day, net, len(d.dates))
        t_day = np.bincount(day, turn, len(d.dates)) / 2
        row = {"indicator": name, "tf": f"{k}m"}
        for en, m in era.items():
            yrs = d.dates[m].astype("datetime64[Y]").astype(int) + 1970
            yearly = pd.Series(n_day[m]).groupby(yrs).sum()
            sd = n_day[m].std()
            row[f"{en} net %/yr"] = round(n_day[m].mean() * 252 * 100, 1)
            row[f"{en} gross %/yr"] = round(g_day[m].mean() * 252 * 100, 1)
            row[f"{en} Sharpe"] = round(n_day[m].mean() / sd * np.sqrt(252), 2) if sd else 0
            row[f"{en} yrs+"] = f"{(yearly > 0).sum()}/{len(yearly)}"
        row["trades/day"] = round(t_day.mean(), 1)
        row["time in mkt"] = round(np.mean(p != 0), 2)
        rows.append(row)
        print(f"{k}m {name:36s} " + "  ".join(f"{e}: {row[f'{e} Sharpe']:+.2f} ({row[f'{e} gross %/yr']:+.0f}% gross)" for e in era))
    return rows


if __name__ == "__main__":
    d = load()
    rows = evaluate(d, 5) + evaluate(d, 15)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("->", OUT)
