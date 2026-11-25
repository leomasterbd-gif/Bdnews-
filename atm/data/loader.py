"""Historical OHLCV loading, resampling and data-quality verification."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HIST_DIR = ROOT / "data" / "historical"

INTERVALS = {"1m": "1min", "3m": "3min", "5m": "5min", "15m": "15min", "30m": "30min", "1h": "1h", "4h": "4h"}

# Datasets and what they are. "quote" tells the engine which currency PnL is in.
DATASETS = {
    "BTC_USDT-5m": dict(symbol="BTCUSDT", quote="USDT", era="2025-11"),
    "XRP_USDT-5m": dict(symbol="XRPUSDT", quote="USDT", era="2025-11"),
    "ETH_BTC-5m": dict(symbol="ETHBTC", quote="BTC", era="2018-01"),
    "LTC_BTC-5m": dict(symbol="LTCBTC", quote="BTC", era="2018-01"),
    "ADA_BTC-5m": dict(symbol="ADABTC", quote="BTC", era="2018-01"),
    "DASH_BTC-5m": dict(symbol="DASHBTC", quote="BTC", era="2018-01"),
    "ETC_BTC-5m": dict(symbol="ETCBTC", quote="BTC", era="2018-01"),
    "TRX_BTC-5m": dict(symbol="TRXBTC", quote="BTC", era="2018-01"),
    "XLM_BTC-5m": dict(symbol="XLMBTC", quote="BTC", era="2018-01"),
    "XMR_BTC-5m": dict(symbol="XMRBTC", quote="BTC", era="2018-01"),
    "ZEC_BTC-5m": dict(symbol="ZECBTC", quote="BTC", era="2018-01"),
    "NXT_BTC-5m": dict(symbol="NXTBTC", quote="BTC", era="2018-01"),
    "UNITTEST_BTC-1m": dict(symbol="UNKNOWN-BTC", quote="BTC", era="2017-11"),
    "XRP_ETH-1m": dict(symbol="XRPETH", quote="ETH", era="2019-10"),
}
# Two years of official Binance archives (scripts/fetch_binance_archive.py, checksums in binance/MANIFEST.json)
BINANCE_ARCHIVE = {f"binance/{s}-5m": dict(symbol=s, quote="USDT", era="2024-11..2026-10")
                   for s in ("BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "BNBUSDT")}
DATASETS.update({k: v for k, v in BINANCE_ARCHIVE.items() if (HIST_DIR / f"{k}.csv.gz").exists()})


@dataclass
class QualityReport:
    rows: int
    duplicates: int
    gaps: int
    missing_bars: int
    bad_ohlc: int
    zero_volume_bars: int
    nonpositive_prices: int
    max_abs_return: float
    ok: bool
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def load_ohlcv(name: str, directory: Path = HIST_DIR) -> pd.DataFrame:
    path = directory / f"{name}.csv.gz"
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.drop_duplicates("date").sort_values("date").set_index("date")
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    df.attrs.update(DATASETS.get(name, {}), name=name)
    return df


def manifest() -> dict:
    return json.loads((HIST_DIR / "MANIFEST.json").read_text())


def infer_freq(df: pd.DataFrame) -> pd.Timedelta:
    return pd.Series(df.index).diff().mode().iloc[0]


def resample(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    """Causal OHLCV resample (label/closed=left: a bar is only complete at its end)."""
    rule = INTERVALS[interval]
    out = df.resample(rule, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    ).dropna()
    out.attrs.update(df.attrs)
    return out


def quality_check(df: pd.DataFrame, max_abs_ret: float = 0.25) -> QualityReport:
    issues = []
    idx = pd.Series(df.index)
    dup = int(idx.duplicated().sum())
    step = infer_freq(df)
    d = idx.diff().dropna()
    gaps = int((d > step).sum())
    missing = int(((d[d > step] / step) - 1).sum()) if gaps else 0
    bad = int(((df.high < df[["open", "close"]].max(axis=1)) | (df.low > df[["open", "close"]].min(axis=1)) | (df.high < df.low)).sum())
    zero_vol = int((df.volume <= 0).sum())
    nonpos = int((df[["open", "high", "low", "close"]] <= 0).any(axis=1).sum())
    r = np.log(df.close).diff().abs().max()
    if dup:
        issues.append(f"{dup} duplicate timestamps")
    if gaps:
        issues.append(f"{gaps} gaps ({missing} missing bars)")
    if bad:
        issues.append(f"{bad} bars violate OHLC ordering")
    if nonpos:
        issues.append(f"{nonpos} non-positive prices")
    if r > max_abs_ret:
        issues.append(f"abnormal single-bar move {r:.3f} log-return")
    ok = not (dup or bad or nonpos) and missing <= 0.02 * len(df)
    return QualityReport(len(df), dup, gaps, missing, bad, zero_vol, nonpos, float(r), ok, issues)


def is_stale(last_bar_close_ts: pd.Timestamp, now: pd.Timestamp, max_staleness_s: float) -> bool:
    return (now - last_bar_close_ts).total_seconds() > max_staleness_s
