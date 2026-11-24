"""Look-ahead / leakage tests: every indicator, strategy signal and ML feature computed on a
truncated history must equal the value computed on the full history at the same bar."""
import numpy as np
import pandas as pd
import pytest

from atm.features import indicators as ind
from atm.features.engineering import build_features, forward_label
from atm.features.regime import classify
from atm.strategies.library import STRATEGIES

CUTS = [700, 1500, 2600]


def _eq(a, b):
    a, b = np.asarray(a, dtype=object), np.asarray(b, dtype=object)
    for x, y in zip(a, b):
        if isinstance(x, float) and isinstance(y, float):
            if np.isnan(x) and np.isnan(y):
                continue
            assert abs(x - y) <= 1e-7 * max(1, abs(x)), (x, y)
        else:
            assert x == y or (pd.isna(x) and pd.isna(y)), (x, y)


@pytest.mark.parametrize("fn", [
    lambda d: ind.rsi(d.close), lambda d: ind.macd(d.close)["hist"], lambda d: ind.atr(d), lambda d: ind.adx(d),
    lambda d: ind.bollinger(d.close)["lower"], lambda d: ind.obv(d), lambda d: ind.vwap(d), lambda d: ind.stoch_rsi(d.close),
    lambda d: ind.roc(d.close), lambda d: ind.donchian(d)["high"], lambda d: ind.ichimoku(d)["span_b"],
    lambda d: ind.zscore(d.close), lambda d: ind.realized_vol(d.close), lambda d: classify(d),
])
def test_indicators_causal(btc, fn):
    full = fn(btc)
    for k in CUTS:
        part = fn(btc.iloc[:k])
        _eq(part.iloc[-50:].values, full.iloc[k - 50:k].values)


@pytest.mark.parametrize("name", list(STRATEGIES))
def test_strategy_signals_causal(btc, name):
    spec = STRATEGIES[name]
    full = spec.signals(btc)
    for k in CUTS:
        part = spec.signals(btc.iloc[:k])
        for col in ("entry", "exit"):
            if name == "buy_hold":
                continue
            assert (part[col].iloc[-30:].values == full[col].iloc[k - 30:k].values).all(), (name, col, k)
        _eq(part["stop_dist"].iloc[-30:].values, full["stop_dist"].iloc[k - 30:k].values)


def test_ml_features_causal(btc):
    full = build_features(btc)
    for k in CUTS:
        part = build_features(btc.iloc[:k])
        _eq(part.iloc[-20:].values.ravel(), full.iloc[k - 20:k].values.ravel())


def test_label_uses_only_future_and_is_nan_at_end(btc):
    y = forward_label(btc, 6, 0.002)
    assert y.iloc[-7:].isna().all()
    assert y.iloc[:-7].notna().all()
