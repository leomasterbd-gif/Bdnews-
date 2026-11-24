"""Strictly causal technical indicators (value at t uses data up to and including bar t)."""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = up / dn.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.where(dn != 0, 100.0).where(up.notna())


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    m = ema(close, fast) - ema(close, slow)
    s = m.ewm(span=signal, adjust=False, min_periods=signal).mean()
    return pd.DataFrame({"macd": m, "signal": s, "hist": m - s})


def true_range(df: pd.DataFrame) -> pd.Series:
    pc = df.close.shift()
    return pd.concat([df.high - df.low, (df.high - pc).abs(), (df.low - pc).abs()], axis=1).max(axis=1)


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    return true_range(df).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def bollinger(close: pd.Series, n: int = 20, k: float = 2.0) -> pd.DataFrame:
    m = sma(close, n)
    sd = close.rolling(n, min_periods=n).std(ddof=0)
    return pd.DataFrame({"mid": m, "upper": m + k * sd, "lower": m - k * sd, "pctb": (close - (m - k * sd)) / (2 * k * sd)})


def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    up = df.high.diff()
    dn = -df.low.diff()
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = true_range(df).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    pdi = 100 * pd.Series(plus_dm, df.index).ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / tr
    mdi = 100 * pd.Series(minus_dm, df.index).ewm(alpha=1 / n, adjust=False, min_periods=n).mean() / tr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def obv(df: pd.DataFrame) -> pd.Series:
    return (np.sign(df.close.diff()).fillna(0) * df.volume).cumsum()


def vwap(df: pd.DataFrame, n: int = 48) -> pd.Series:
    """Rolling VWAP over n bars (session VWAP is ill-defined for 24/7 crypto)."""
    tp = (df.high + df.low + df.close) / 3
    return (tp * df.volume).rolling(n, min_periods=n).sum() / df.volume.rolling(n, min_periods=n).sum()


def stoch_rsi(close: pd.Series, n: int = 14, k: int = 3) -> pd.Series:
    r = rsi(close, n)
    lo, hi = r.rolling(n, min_periods=n).min(), r.rolling(n, min_periods=n).max()
    return ((r - lo) / (hi - lo).replace(0, np.nan)).rolling(k, min_periods=k).mean()


def roc(close: pd.Series, n: int = 12) -> pd.Series:
    return close.pct_change(n)


def donchian(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Channel of the *previous* n bars (shifted) so a breakout compares against the past only."""
    return pd.DataFrame({"high": df.high.rolling(n).max().shift(), "low": df.low.rolling(n).min().shift()})


def ichimoku(df: pd.DataFrame, t: int = 9, k: int = 26, s: int = 52) -> pd.DataFrame:
    """Causal Ichimoku: spans are reported at the bar they become known (no forward displacement)."""
    tenkan = (df.high.rolling(t).max() + df.low.rolling(t).min()) / 2
    kijun = (df.high.rolling(k).max() + df.low.rolling(k).min()) / 2
    span_a = ((tenkan + kijun) / 2).shift(k)
    span_b = ((df.high.rolling(s).max() + df.low.rolling(s).min()) / 2).shift(k)
    return pd.DataFrame({"tenkan": tenkan, "kijun": kijun, "span_a": span_a, "span_b": span_b})


def zscore(s: pd.Series, n: int = 50) -> pd.Series:
    return (s - s.rolling(n, min_periods=n).mean()) / s.rolling(n, min_periods=n).std(ddof=0)


def realized_vol(close: pd.Series, n: int = 48) -> pd.Series:
    return np.log(close).diff().rolling(n, min_periods=n).std(ddof=0)
