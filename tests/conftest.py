import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(scope="session")
def btc():
    from atm.data.loader import load_ohlcv
    return load_ohlcv("BTC_USDT-5m")


def make_df(close, vol=1000.0, spread=0.001):
    close = np.asarray(close, float)
    idx = pd.date_range("2025-01-01", periods=len(close), freq="5min", tz="UTC")
    o = np.r_[close[0], close[:-1]]
    h = np.maximum(o, close) * (1 + spread)
    lo = np.minimum(o, close) * (1 - spread)
    return pd.DataFrame({"open": o, "high": h, "low": lo, "close": close, "volume": vol}, index=idx)


@pytest.fixture
def limits():
    from atm.risk.limits import RiskLimits
    return RiskLimits(min_bar_quote_volume=0.0, max_atr_pct=5.0)
