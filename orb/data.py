"""Load 1-minute bars into a (days x 390) matrix of NY regular-session bars.

Row d holds the 09:30..15:59 ET minutes of one trading day; missing minutes are NaN.
Daily context (prior close, ATR, gap, opening-range volume history) is computed from
earlier rows only, so every feature is known at 09:30 of that day.
"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RTH_BARS = 390  # 09:30..15:59


@dataclass
class Days:
    dates: np.ndarray   # datetime64[D], one per trading day
    o: np.ndarray       # (D, 390) float
    h: np.ndarray
    l: np.ndarray
    c: np.ndarray
    v: np.ndarray
    last: np.ndarray    # index of the last valid bar per day (half days end early)
    prev_close: np.ndarray  # prior session 15:59 close
    atr14: np.ndarray       # 14-day ATR of RTH daily bars, prior days only
    dow: np.ndarray         # 0=Mon

    def slice(self, mask):
        return Days(**{k: getattr(self, k)[mask] for k in self.__dataclass_fields__})


def build(csv_path, cache_path=None):
    cache = Path(cache_path) if cache_path else None
    if cache and cache.exists():
        z = np.load(cache)
        return Days(**{k: z[k] for k in z.files})

    df = pd.read_csv(csv_path)
    ts = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert("America/New_York")
    minute = ts.dt.hour * 60 + ts.dt.minute - (9 * 60 + 30)
    keep = (minute >= 0) & (minute < RTH_BARS) & (ts.dt.dayofweek < 5)
    df, ts, minute = df[keep], ts[keep], minute[keep]
    day = ts.dt.tz_localize(None).dt.normalize()

    dates = np.array(sorted(day.unique()), dtype="datetime64[D]")
    row = np.searchsorted(dates, day.values.astype("datetime64[D]"))
    col = minute.values
    D = len(dates)
    mats = {}
    for k in "ohlcv":
        m = np.full((D, RTH_BARS), np.nan)
        m[row, col] = df[{"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}[k]].values
        mats[k] = m

    # Drop thin days (holidays / data gaps): need the open bar and most of the session.
    count = np.isfinite(mats["c"]).sum(1)
    good = np.isfinite(mats["o"][:, 0]) & (count >= 200)
    dates = dates[good]
    mats = {k: m[good] for k, m in mats.items()}
    # Last real bar of the session (half days close at 13:00).
    last = RTH_BARS - 1 - np.argmax(np.isfinite(mats["c"])[:, ::-1], axis=1)
    # Forward-fill missing minutes with a flat bar at the prior close.
    c = pd.DataFrame(mats["c"]).ffill(axis=1).values
    for k in "ohl":
        mats[k] = np.where(np.isfinite(mats[k]), mats[k], c)
    mats["c"] = c
    mats["v"] = np.nan_to_num(mats["v"])

    dh = np.nanmax(mats["h"], 1)
    dl = np.nanmin(mats["l"], 1)
    dc = mats["c"][np.arange(len(dates)), last]
    prev_close = np.r_[np.nan, dc[:-1]]
    tr = np.maximum(dh - dl, np.maximum(abs(dh - prev_close), abs(dl - prev_close)))
    tr[0] = dh[0] - dl[0]
    atr = pd.Series(tr).rolling(14).mean().shift(1).values  # prior days only

    out = Days(dates=dates, o=mats["o"], h=mats["h"], l=mats["l"], c=mats["c"], v=mats["v"],
               last=last, prev_close=prev_close, atr14=atr,
               dow=((dates.astype("datetime64[D]").view("int64") - 4) % 7))
    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache, **{k: getattr(out, k) for k in out.__dataclass_fields__})
    return out
