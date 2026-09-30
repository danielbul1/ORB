"""ADR 0006: the 10 pre-registered Hypotheses to beat Ensemble v3 (vault/Research/Edge Hunt Log.md).

Every rule and number here is fixed by the pre-registration; the only extra runs are the +-50% plateau checks,
which are reported but cannot rescue a fail. Every variant run is counted for the deflated Sharpe.
Usage: python research/beat_v3.py [H7 H8 ...]   (default: all, in the registered run order)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb import long as L  # noqa: E402
from orb.backtest import TICK, daily, run  # noqa: E402
from orb.data import build  # noqa: E402
from orb.families import ENSEMBLE_MEMBERS, ENSEMBLE_V3  # noqa: E402
from orb.judge import deflated_sharpe, stats  # noqa: E402
from orb.propscore import Flex, prop_score  # noqa: E402

FLEX150 = Flex(target=9000, mll=4500, day_min=250, payout_cap=3000)
USD_EVAL, USD_FUNDED, HORIZON = 960, 640, 504
TRIALS = []  # (name, daily) of every variant run, for the deflated Sharpe
BIG = 10**6


# ---------------------------------------------------------------- Ensemble v3 with hooks
def legs(d, **p):
    """Per-Leg run results of Ensemble v3 (p overrides the rules)."""
    return {om: run(d, **{**ENSEMBLE_V3, "or_min": om, **L.COST, **p}) for om in ENSEMBLE_MEMBERS}


def combine(res, day_on=None, size=None, leg_on=None):
    """Ensemble daily R: each Leg 1/4. day_on: Sessions allowed; size: per-Session multiplier;
    leg_on: {om: bool array} Leg-specific switch."""
    D = len(next(iter(res.values()))["r"])
    x = np.zeros(D)
    for om, r in res.items():
        ok = r["ok"].copy()
        if day_on is not None:
            ok &= day_on
        if leg_on is not None and om in leg_on:
            ok &= leg_on[om]
        x += np.where(ok, r["r"], 0.0)
    x /= len(res)
    return x if size is None else x * size


# ---------------------------------------------------------------- judging
def era_line(x, E):
    out = {}
    for k, m in E.items():
        s = stats(x[m])
        out[k] = s
    return out


def prop(x, m, scale=1.0):
    h = HORIZON if m.sum() > HORIZON + 21 else 252  # 2025-26 is shorter than two years
    return prop_score(x[m] * scale, USD_EVAL, USD_FUNDED, FLEX150, horizon=h)


def judge_filter(name, x, v3, E, eras=("A 2003-15", "B 2016-24"), a_mask=None):
    TRIALS.append((name, x))
    print(f"\n=== {name}")
    ok_all = True
    for k in ("A 2003-15", "B 2016-24", "spent 25-26"):
        m = E[k] if not (k.startswith("A") and a_mask is not None) else E[k] & a_mask
        s, b = stats(x[m]), stats(v3[m])
        p, pb = prop(x, m)["net_per_month"], prop(v3, m)["net_per_month"]
        win = s["score"] > b["score"] and p > pb and s["sharpe"] >= b["sharpe"]
        judged = k in eras
        if judged:
            ok_all &= win
        tag = ("PASS" if win else "fail") if judged else "info"
        print(f"  {k:12} Score {s['score']:>7,.0f} vs {b['score']:>7,.0f} | Sharpe {s['sharpe']:>5} vs {b['sharpe']:>5} | "
              f"Prop ${p:>5,.0f} vs ${pb:>5,.0f} | trades {s['trades']:>5} vs {b['trades']:>5} | DD {s['maxdd']:.1f}R  [{tag}]")
    if "B 2016-24" in eras and eras == ("B 2016-24",):
        ok_all &= stats(x[E["spent 25-26"]])["yearly"] >= 0
    print(f"  VERDICT: {'PASS' if ok_all else 'FAIL'}")
    return ok_all


def judge_member(name, y, v3, E, eras=("A 2003-15", "B 2016-24")):
    TRIALS.append((name, y))
    combo = v3 + y
    scale = stats(v3[E["B 2016-24"]])["maxdd"] / stats(combo[E["B 2016-24"]])["maxdd"]
    print(f"\n=== {name}  (Prop scale {scale:.2f})")
    ok_all = True
    for k in ("A 2003-15", "B 2016-24", "spent 25-26"):
        m = E[k]
        sy, sc, sb = stats(y[m]), stats(combo[m]), stats(v3[m])
        traded = (y[m] != 0) & (v3[m] != 0)
        corr = float(np.corrcoef(y[m], v3[m])[0, 1]) if y[m].std() else 0.0
        pc, pb = prop(combo, m, scale)["net_per_month"], prop(v3, m)["net_per_month"]
        win = corr <= 0.3 and sy["score"] > 0 and sc["score"] > sb["score"] and pc > pb
        judged = k in eras
        if judged:
            ok_all &= win
        tag = ("PASS" if win else "fail") if judged else "info"
        print(f"  {k:12} alone Score {sy['score']:>7,.0f} Sharpe {sy['sharpe']:>5} trades {sy['trades']:>5} win {sy.get('win')} | "
              f"corr {corr:+.2f} | v3+M Score {sc['score']:>7,.0f} vs {sb['score']:>7,.0f} Sharpe {sc['sharpe']} | "
              f"Prop ${pc:>5,.0f} vs ${pb:>5,.0f} | same-day {int(traded.sum())}  [{tag}]")
    print(f"  VERDICT: {'PASS' if ok_all else 'FAIL'}")
    return ok_all


# ---------------------------------------------------------------- generic level trade
def level_trade(d, direction, entry, e, stop, tgt=None, trail=True, exit_min=389):
    """One trade per Session from bar e at `entry`, v3-style exits: stop, optional target, v3 trail
    (0.3 ATR once 2R up), flat 15:59. Pessimistic fills as in orb.backtest.run. Returns R per Session."""
    D, B = d.o.shape
    rows = np.arange(D)
    idx = np.arange(B)[None, :]
    atr = d.atr14
    cost = np.maximum(L.COST["cost_bp"] * 1e-4 * entry, L.COST["cost_floor"])
    risk = (entry - stop) * direction
    ok = (e < BIG) & (direction != 0) & np.isfinite(atr) & (e < d.last) & (risk > 0) & (risk >= 4 * cost)
    ec = np.where(ok, np.minimum(e, B - 1), 0)[:, None]
    x_end = np.minimum(exit_min, d.last)
    live = (idx >= ec) & (idx <= x_end[:, None])
    dc = direction[:, None]

    def first(m):
        i = m.argmax(1)
        i[~m.any(1)] = BIG
        return i
    js = first(live & np.where(dc > 0, d.l <= stop[:, None], d.h >= stop[:, None]))
    stop_px = stop.copy()
    if trail:
        fav = np.where(live, np.where(dc > 0, d.h, -d.l), -np.inf)
        best = np.maximum.accumulate(fav, axis=1)
        prev = np.concatenate([np.full((D, 1), -np.inf), best[:, :-1]], axis=1)
        lvl = prev - 0.3 * atr[:, None]
        armed = prev >= (direction * entry + 2.0 * risk)[:, None]
        jtr = first(live & (idx > ec) & armed & (np.where(dc > 0, d.l, -d.h) <= lvl))
        use = jtr < js
        stop_px = np.where(use, direction * lvl[rows, np.minimum(jtr, B - 1)], stop_px)
        js = np.where(use, jtr, js)
    jt = first(live & (idx > ec) & np.where(dc > 0, d.h >= tgt[:, None], d.l <= tgt[:, None])) \
        if tgt is not None else np.full(D, BIG)
    f = np.minimum(np.minimum(js, jt), x_end)
    fc = np.minimum(f, B - 1)
    o_at = d.o[rows, fc]
    stop_fill = np.where(direction > 0, np.minimum(stop_px, o_at), np.maximum(stop_px, o_at))
    out = np.where(f == js, stop_fill, np.where(f == jt, tgt if tgt is not None else 0.0, d.c[rows, fc]))
    r = (direction * (out - entry) - cost) / np.where(risk > 0, risk, np.nan)
    return np.where(ok, np.nan_to_num(r), 0.0)


def breakout(d, hi, lo, start=5, cutoff=120, stop_x=0.10):
    """First stop-entry break of hi/lo from bar `start`; a side whose level already traded before `start` is void."""
    D, B = d.o.shape
    rows = np.arange(D)
    idx = np.arange(B)[None, :]
    pre_h, pre_l = d.h[:, :start].max(1), d.l[:, :start].min(1)
    up, dn = hi + TICK, lo - TICK
    win = (idx >= start) & (idx <= np.minimum(cutoff, d.last - 1)[:, None])

    def first(m):
        i = m.argmax(1)
        i[~m.any(1)] = BIG
        return i
    jl = np.where((pre_h < up) & np.isfinite(hi), first(win & (d.h >= up[:, None])), BIG)
    js = np.where((pre_l > dn) & np.isfinite(lo), first(win & (d.l <= dn[:, None])), BIG)
    direction = np.where(jl < js, 1, np.where(js < jl, -1, 0))
    e = np.minimum(jl, js)
    ec = np.minimum(e, B - 1)
    entry = np.where(direction > 0, np.maximum(up, d.o[rows, ec]), np.minimum(dn, d.o[rows, ec]))
    stop = entry - direction * stop_x * d.atr14
    return level_trade(d, direction, entry, e, stop)


# ---------------------------------------------------------------- external context
def prior_series(d, s, lag=1):
    """Value of a date-indexed series on the last date strictly before each Session (lag=1) or on it (lag=0)."""
    idx = np.searchsorted(s.index.values.astype("datetime64[D]"), d.dates, side="left" if lag else "right") - 1
    out = np.full(len(d.dates), np.nan)
    ok = idx >= 0
    out[ok] = s.values[idx[ok]]
    return out


def vix():
    v = pd.read_csv(ROOT / "data" / "ext" / "VIX_History.csv")
    v.index = pd.to_datetime(v["DATE"], format="%m/%d/%Y")
    return v


def release_days(pattern):
    c = pd.read_csv(ROOT / "data" / "ext" / "forexfactory_calendar.csv", encoding="utf-8-sig")
    c = c[(c.currency == "USD") & c.event.str.contains(pattern, regex=True, na=False)]
    return np.array(pd.to_datetime(c.date, format="%a %b %d %Y").values, dtype="datetime64[D]")


def globex_range(d):
    """18:00 (prior day) .. 09:29 high-low per Session from the raw 1m file (NaN where no overnight bars)."""
    cache = ROOT / "data" / "globex_hl.npz"
    if cache.exists():
        z = np.load(cache)
        return z["hi"], z["lo"]
    df = pd.read_csv(ROOT / "data" / "long_1m.csv")
    t = pd.to_datetime(df.time, unit="s", utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    mins = t.dt.hour * 60 + t.dt.minute
    on = (mins >= 18 * 60) | (mins < 9 * 60 + 30)
    sess = (t + pd.to_timedelta(np.where(mins >= 18 * 60, 1, 0), unit="D")).dt.normalize()
    sess = sess.where(sess.dt.dayofweek < 5, sess + pd.to_timedelta((7 - sess.dt.dayofweek) % 7, unit="D"))
    g = df[on.values].groupby(sess[on].values).agg(hi=("high", "max"), lo=("low", "min"), n=("high", "size"))
    g = g[g.n >= 300]  # a real overnight session (>= 5 hours of bars)
    hi = prior_series(d, g.hi, lag=0)
    lo = prior_series(d, g.lo, lag=0)
    same = np.isin(d.dates, g.index.values.astype("datetime64[D]"))
    hi[~same], lo[~same] = np.nan, np.nan
    np.savez_compressed(cache, hi=hi, lo=lo)
    return hi, lo


# ---------------------------------------------------------------- the Hypotheses
def H1(d, E, res, v3, pct=0.20):
    v = vix()
    rank = v.CLOSE.rolling(252, min_periods=200).rank(pct=True)
    r = prior_series(d, rank)
    return judge_filter(f"H1 VIX calm skip (pct < {pct:.2f})", combine(res, day_on=~(r < pct)), v3, E)


def H2(d, E, res, v3, thr=0.03):
    v = vix()
    real = (v.OPEN != v.CLOSE.shift(1)).groupby(v.index.year).mean()
    good_years = real[real > 0.9].index
    chg = prior_series(d, (v.OPEN / v.CLOSE.shift(1) - 1), lag=0)
    same = np.isin(d.dates, v.index.values.astype("datetime64[D]"))
    y = d.dates.astype("datetime64[Y]").astype(int) + 1970
    valid = same & np.isin(y, good_years)
    print(f"  H2: VIX open is a real print in years {list(good_years)[:3]}..{list(good_years)[-1]} "
          f"({len(good_years)} years)")
    x = combine(res, day_on=valid & (np.abs(chg) >= thr))
    base = combine(res, day_on=valid)  # compare on the same years
    return judge_filter(f"H2 VIX shock (|open chg| >= {thr:.0%})", x, base, E)


def H3(d, E, res, v3):
    days = np.union1d(release_days(r"^CPI m/m|^Core CPI m/m"), release_days(r"Non-Farm Employment Change"))
    rel = np.isin(d.dates, days)
    print(f"  H3: {rel.sum()} release Sessions ({rel[E['B 2016-24']].sum()} in B)")
    x = combine(res, leg_on={5: ~rel, 15: ~rel})
    a = d.dates >= np.datetime64("2007-01-01")
    return judge_filter("H3 CPI/NFP: only 30/60 Legs", x, v3, E, a_mask=a)


def H4(d, E, res, v3, k=0.5):
    hi, lo = globex_range(d)
    rng = (hi - lo) / d.atr14
    size = np.where(rng < k, 1.0, 0.5)
    have = np.isfinite(rng)
    print(f"  H4: overnight data on {have.mean():.0%} of Sessions; compressed {np.mean(rng[have] < k):.0%}")
    x = combine(res, size=np.where(have, size, 1.0))
    return judge_filter(f"H4 overnight compression (< {k} ATR full, else half)", x, v3, E, eras=("B 2016-24",))


def H5(d, E, res, v3):
    es = build(None, ROOT / "data" / "es_adj_rth.npz")
    j = np.searchsorted(es.dates, d.dates)
    j = np.clip(j, 0, len(es.dates) - 1)
    have = es.dates[j] == d.dates
    leg_on = {}
    for om in ENSEMBLE_MEMBERS:
        nq = (d.c[:, om - 1] - d.o[:, 0]) / d.atr14
        e = (es.c[j, om - 1] - es.o[j, 0]) / es.atr14[j]
        leg_on[om] = have & (np.sign(nq) == np.sign(e)) & (np.abs(nq) > np.abs(e))
    print(f"  H5: ES on {have.mean():.0%} of Sessions")
    return judge_filter("H5 NQ leads ES", combine(res, leg_on=leg_on), v3, E, eras=("B 2016-24",))


def H6(d, E, res, v3):
    ctx = daily(d)
    dh, dl = d.h.max(1), d.l.min(1)
    inside = np.r_[False, False, (dh[1:-1] <= dh[:-2]) & (dl[1:-1] >= dl[:-2])]
    on = ctx["nr7"] | inside
    print(f"  H6: {on.mean():.0%} of Sessions follow an NR7 / inside day")
    return judge_filter("H6 after NR7 / inside day only", combine(res, day_on=on), v3, E)


def H7(d, E, res, v3):
    y = combine(legs(d, gap_dir="against"))
    return judge_member("H7 against-gap member (v3 Legs, gap_dir=against)", y, v3, E)


def H8(d, E, res, v3, stop_x=0.25):
    D, B = d.o.shape
    rows = np.arange(D)
    idx = np.arange(B)[None, :]
    ctx = daily(d)
    sig5 = ctx["sig5"][20]
    taus = [np.abs(np.log(d.c[:, k - 1] / d.o[:, 0]) / (sig5 * np.sqrt(k / 5))) for k in (5, 15, 30)]
    blocked = np.all([t < 1.0 for t in taus], axis=0) & np.isfinite(sig5)
    orh, orl = d.h[:, :30].max(1), d.l[:, :30].min(1)
    win = (idx >= 30) & (idx <= d.last[:, None] - 1)

    def first(m):
        i = m.argmax(1)
        i[~m.any(1)] = BIG
        return i
    ju, jd = first(win & (d.h >= orh[:, None])), first(win & (d.l <= orl[:, None]))
    direction = np.where(ju < jd, -1, np.where(jd < ju, 1, 0))  # fade the first touch
    e = np.minimum(ju, jd)
    ec = np.minimum(e, B - 1)
    entry = np.where(direction < 0, orh, orl)  # limit at the extreme
    stop = np.where(direction < 0, orh + stop_x * d.atr14, orl - stop_x * d.atr14)
    tgt = ctx["vwap"][rows, np.clip(ec - 1, 0, B - 1)]
    ok = blocked & ((tgt - entry) * direction > 0)
    direction = np.where(ok, direction, 0)
    y = level_trade(d, direction, entry, np.where(ok, e, BIG), stop, tgt=tgt, trail=False)
    print(f"  H8: v3-blocked Sessions {blocked.mean():.0%}")
    return judge_member(f"H8 low-tau VWAP reversion (stop {stop_x} ATR)", y, v3, E)


def H9(d, E, res, v3, stop_x=0.10):
    hi, lo = globex_range(d)
    y = breakout(d, hi, lo, stop_x=stop_x)
    return judge_member(f"H9 Globex extreme breakout (stop {stop_x} ATR)", y, v3, E, eras=("B 2016-24",))


def H10(d, E, res, v3, stop_x=0.10):
    ctx = daily(d)
    y = breakout(d, ctx["pdh"], ctx["pdl"], stop_x=stop_x)
    return judge_member(f"H10 prior-day extreme breakout (stop {stop_x} ATR)", y, v3, E)


PLATEAU = {"H1": ("pct", 0.20), "H2": ("thr", 0.03), "H4": ("k", 0.5), "H8": ("stop_x", 0.25),
           "H9": ("stop_x", 0.10), "H10": ("stop_x", 0.10)}
ORDER = ["H7", "H8", "H1", "H2", "H3", "H4", "H5", "H6", "H9", "H10"]


def main(which):
    d = L.load()
    E = L.eras(d)
    res = legs(d)
    v3 = combine(res)
    verdicts = {}
    for h in which:
        f = globals()[h]
        verdicts[h] = f(d, E, res, v3)
        if h in PLATEAU:
            k, v = PLATEAU[h]
            for m in (0.5, 1.5):
                print(f"  -- plateau check {k} = {v * m:g} (information only)")
                f(d, E, res, v3, **{k: v * m})
    print("\n==== SUMMARY", verdicts)
    n = len(TRIALS)
    sh = [stats(x[E["B 2016-24"]])["sharpe"] for _, x in TRIALS]
    for h, ok in verdicts.items():
        if ok:
            x = next(x for name, x in TRIALS if name.startswith(h + " "))
            print(f"  DSR {h} (N={n}):", deflated_sharpe(x[E["B 2016-24"]], n, sh))


if __name__ == "__main__":
    main(sys.argv[1:] or ORDER)
