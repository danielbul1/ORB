"""Test the arXiv-sweep ideas on the 23-year base (vault/Research/arXiv ORB Sweep.md).

N1 trend-strength gate (arXiv 2501.16772): trade a member only if the move from the 09:30 open to its entry,
   in units of 1-minute volatility, tau = ln(C_k/O)/(sigma_1m*sqrt(k)), has the trade's sign and |tau| >= tau*.
N2 earlier exit on VVG days (2605.11423): |gap|, |09:30-10:00 return| (both /ATR) and first-5-min volume /
   its 20-day mean all >= their trailing-year percentile p -> exit at t_exit instead of 15:59.
N3 same-slot persistence (1005.3535): does the sign of the last k days' 09:30-10:00 return predict today's?
N4 leveraged-ETF pressure (2608.03703): kappa = sum(L^2-L) x 20-day dollar volume (TQQQ, SQQQ, QLD) / QQQ's;
   trade ORB-5 only when kappa x |gap|/ATR (prior-day kappa) is above its trailing-year percentile q.
Every change must improve both eras (A 2003-15, B 2016-24); 2025-26 is information only.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from orb import long as L  # noqa: E402
from orb.backtest import run  # noqa: E402
from orb.families import ENSEMBLE_MEMBERS, ENSEMBLE_V2, ORB_V1  # noqa: E402
from orb.judge import stats  # noqa: E402


def trailing_pct(x, win=252, minp=60):
    return pd.Series(x).rolling(win, min_periods=minp).rank(pct=True).shift(1).values


def features(d):
    D, B = d.c.shape
    lr = np.diff(np.log(d.c), axis=1)
    sig_day = np.nanstd(lr, axis=1)
    f = {}
    for n in (20, 60):
        f[f"sig{n}"] = pd.Series(sig_day).rolling(n).mean().shift(1).values
    f["gap_atr"] = np.abs(d.o[:, 0] - d.prev_close) / d.atr14
    f["r30_atr"] = np.abs(d.c[:, 29] - d.o[:, 0]) / d.atr14
    v5 = d.v[:, :5].sum(1)
    f["rvol5"] = v5 / pd.Series(v5).rolling(20).mean().shift(1).values
    return f


def lev_pressure(d):
    def dv(sym):
        j = json.load(open(ROOT / "data" / "ext" / f"{sym}.json"))["chart"]["result"][0]
        q = j["indicators"]["quote"][0]
        s = pd.Series(np.array(q["close"], float) * np.array(q["volume"], float),
                      index=pd.to_datetime(j["timestamp"], unit="s").normalize())
        return s.rolling(20, min_periods=5).mean()
    k = (6 * dv("TQQQ")).add(12 * dv("SQQQ"), fill_value=0).add(2 * dv("QLD"), fill_value=0) / dv("QQQ")
    k = k.dropna()
    idx = np.searchsorted(k.index.values.astype("datetime64[D]"), d.dates, side="left") - 1  # prior day only
    out = np.full(len(d.dates), np.nan)
    ok = idx >= 0
    out[ok] = k.values[idx[ok]]
    return out


def member(d, p, om, gate=None, exit_arr=None):
    q = {**p, "or_min": om, **L.COST}
    if exit_arr is not None:
        q["exit_min"] = exit_arr
    r = run(d, **q)
    ok = r["ok"] if gate is None else r["ok"] & gate(om, r)
    return np.where(ok, r["r"], 0.0)


def rule_set(d, p, members, **kw):
    return sum(member(d, p, om, **kw) for om in members) / len(members)


def show(tag, x, E):
    s = [stats(x[m]) for m in E.values()]
    print(f"{tag:52} A {s[0]['sharpe']:>5} B {s[1]['sharpe']:>5} 25-26 {s[2]['sharpe']:>5} | trades A/B {s[0]['trades']}/{s[1]['trades']}")


def main():
    d = L.load()
    E = L.eras(d)
    f = features(d)
    base = {"Ensemble v2": (ENSEMBLE_V2, ENSEMBLE_MEMBERS), "ORB v1": (ORB_V1, (5,))}
    for name, (p, mem) in base.items():
        print(f"\n===== {name}")
        show("BASE", rule_set(d, p, mem), E)
        print("-- N1 trend-strength gate")
        for win in (20, 60):
            for tmin in (1.0, 1.5, 2.0, 3.0):
                def gate(om, r, win=win, tmin=tmin):
                    tau = np.log(d.c[:, om - 1] / d.o[:, 0]) / (f[f"sig{win}"] * np.sqrt(om))
                    return r["dir"] * tau >= tmin
                show(f"tau >= {tmin} (sigma {win}d)", rule_set(d, p, mem, gate=gate), E)
        print("-- N2 earlier exit on VVG days")
        for pc in (0.67, 0.75):
            vvg = ((trailing_pct(f["gap_atr"]) >= pc) & (trailing_pct(f["r30_atr"]) >= pc)
                   & (trailing_pct(f["rvol5"]) >= pc))
            for t_exit, lab in ((270, "14:00"), (330, "15:00"), (360, "15:30")):
                ex = np.where(vvg, t_exit, 389)
                show(f"VVG p{int(pc*100)} ({vvg.mean():.1%} of days) exit {lab}", rule_set(d, p, mem, exit_arr=ex), E)
    print("\n===== N4 leveraged-ETF pressure gate on ORB-5 (and on the 5m member of Ensemble v2)")
    kap = lev_pressure(d)
    press = kap * f["gap_atr"]
    pr = trailing_pct(press)
    for q in (0.3, 0.5):
        g5 = lambda om, r, q=q: (om != 5) | (np.nan_to_num(pr) >= q)
        show(f"ORB v1, pressure pct >= {q}", rule_set(d, ORB_V1, (5,), gate=g5), E)
        show(f"Ensemble v2, 5m member gated pct >= {q}", rule_set(d, ENSEMBLE_V2, ENSEMBLE_MEMBERS, gate=g5), E)
    print("   kappa coverage from", d.dates[np.isfinite(kap)][0])
    print("\n===== N3 same-slot persistence: sign(09:30-10:00 today) vs mean of last k days")
    r30 = np.log(d.c[:, 29] / d.o[:, 0])
    for k in (1, 5, 10, 20):
        past = pd.Series(r30).rolling(k).mean().shift(1).values
        for era, m in E.items():
            ok = m & np.isfinite(past)
            x, y = np.sign(past[ok]), r30[ok]
            b = np.polyfit(x, y, 1)[0]
            resid = y - np.polyval(np.polyfit(x, y, 1), x)
            t = b / (resid.std() / np.sqrt(ok.sum()) / x.std())
            print(f"  k={k:>2} {era:12} slope {b*1e4:+.2f} bp  t {t:+.2f}")


if __name__ == "__main__":
    main()
