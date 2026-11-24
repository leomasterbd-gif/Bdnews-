"""Causal feature matrix + forward-return labels for ML research."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import indicators as ind
from . import regime as rg


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    c = df.close
    lr = np.log(c).diff()
    at = ind.atr(df, 14)
    f = pd.DataFrame(index=df.index)
    for k in (1, 3, 6, 12, 24, 48):
        f[f"ret_{k}"] = np.log(c / c.shift(k))
    f["rsi14"] = ind.rsi(c, 14) / 100
    f["rsi6"] = ind.rsi(c, 6) / 100
    m = ind.macd(c)
    f["macd_hist_n"] = m["hist"] / at
    f["bb_pctb"] = ind.bollinger(c).pctb
    f["atr_pct"] = at / c
    f["adx"] = ind.adx(df) / 100
    f["rv24"] = ind.realized_vol(c, 24)
    f["rv_ratio"] = ind.realized_vol(c, 12) / ind.realized_vol(c, 96)
    f["vol_z"] = ind.zscore(np.log1p(df.volume), 96)
    f["obv_slope"] = ind.obv(df).diff(12) / df.volume.rolling(96).sum()
    f["vwap_dev"] = (c - ind.vwap(df, 48)) / at
    f["stoch_rsi"] = ind.stoch_rsi(c)
    f["ema_gap"] = (ind.ema(c, 20) - ind.ema(c, 100)) / c
    f["range_pos"] = (c - df.low.rolling(48).min()) / (df.high.rolling(48).max() - df.low.rolling(48).min())
    f["skew48"] = lr.rolling(48).skew()
    hr = df.index.hour + df.index.minute / 60
    f["hour_sin"], f["hour_cos"] = np.sin(2 * np.pi * hr / 24), np.cos(2 * np.pi * hr / 24)
    reg = rg.classify(df)
    for r in rg.REGIMES:
        f[f"reg_{r}"] = (reg == r).astype(float)
    return f.replace([np.inf, -np.inf], np.nan)


def forward_label(df: pd.DataFrame, horizon: int, cost: float) -> pd.Series:
    """1 if the log return from next-bar open to the open `horizon` bars later exceeds `cost`.
    The label at t uses prices strictly after t (it is the target, never a feature)."""
    o = df.open
    fwd = np.log(o.shift(-(horizon + 1)) / o.shift(-1))
    y = (fwd > cost).astype(float)
    return y.where(fwd.notna())
