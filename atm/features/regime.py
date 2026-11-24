"""Deterministic market-regime classifier (causal).

Regimes: TREND_UP, TREND_DOWN, RANGE, HIGH_VOL. Thresholds use expanding/rolling
percentiles computed only on past data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import indicators as ind

REGIMES = ("TREND_UP", "TREND_DOWN", "RANGE", "HIGH_VOL")


def classify(df: pd.DataFrame, adx_n: int = 14, trend_adx: float = 25.0, vol_window: int = 288) -> pd.Series:
    a = ind.adx(df, adx_n)
    e_fast, e_slow = ind.ema(df.close, 20), ind.ema(df.close, 60)
    rv = ind.realized_vol(df.close, 24)
    # rolling percentile of current vol vs the past vol_window bars (shifted -> past only)
    hist = rv.shift(1).rolling(vol_window, min_periods=50)
    hi_thr = hist.quantile(0.9)
    out = pd.Series("RANGE", index=df.index, dtype=object)
    out[(a >= trend_adx) & (e_fast > e_slow)] = "TREND_UP"
    out[(a >= trend_adx) & (e_fast < e_slow)] = "TREND_DOWN"
    out[rv > hi_thr] = "HIGH_VOL"
    out[a.isna() | e_slow.isna()] = np.nan
    return out


def regime_change_points(reg: pd.Series) -> pd.Series:
    r = reg.ffill()
    return r.ne(r.shift()) & r.shift().notna()
