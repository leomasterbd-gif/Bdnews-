"""Strategy library. Long-only spot. All signals are computed at bar close t from data <= t
and are executed by the engine at bar t+1 (no look-ahead).

Each strategy returns a DataFrame with columns:
  entry (bool), exit (bool), stop_dist (price distance of protective stop, >0),
  tp_dist (optional take-profit distance, NaN = none).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from ..features import indicators as ind
from ..features import regime as rg


@dataclass
class StrategySpec:
    name: str
    family: str
    fn: Callable[[pd.DataFrame, dict], pd.DataFrame]
    defaults: dict
    space: dict = field(default_factory=dict)  # param -> (low, high, type)
    description: str = ""

    def signals(self, df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
        p = {**self.defaults, **(params or {})}
        out = self.fn(df, p)
        out = out.reindex(df.index)
        out["entry"] = out["entry"].fillna(False).astype(bool)
        out["exit"] = out["exit"].fillna(False).astype(bool)
        if "tp_dist" not in out:
            out["tp_dist"] = np.nan
        return out


def _frame(entry, exit_, stop_dist, tp_dist=None):
    d = {"entry": entry, "exit": exit_, "stop_dist": stop_dist}
    if tp_dist is not None:
        d["tp_dist"] = tp_dist
    return pd.DataFrame(d)


def buy_hold(df, p):
    e = pd.Series(False, df.index)
    e.iloc[0] = True
    return _frame(e, pd.Series(False, df.index), df.close * p["stop_pct"] / 100)


def ema_trend(df, p):
    f, s = ind.ema(df.close, int(p["fast"])), ind.ema(df.close, int(p["slow"]))
    a = ind.adx(df, 14)
    at = ind.atr(df, 14)
    entry = (f > s) & (f.shift() <= s.shift()) & (a > p["adx_min"])
    exit_ = (f < s)
    return _frame(entry, exit_, at * p["atr_stop"])


def momentum(df, p):
    r = ind.roc(df.close, int(p["n"]))
    e = ind.ema(df.close, int(p["trend"]))
    at = ind.atr(df, 14)
    entry = (r > p["th"] / 100) & (df.close > e) & (r.shift() <= p["th"] / 100)
    exit_ = r < 0
    return _frame(entry, exit_, at * p["atr_stop"], at * p["atr_tp"])


def mean_reversion(df, p):
    bb = ind.bollinger(df.close, int(p["n"]), p["k"])
    r = ind.rsi(df.close, 14)
    a = ind.adx(df, 14)
    at = ind.atr(df, 14)
    entry = (df.close < bb.lower) & (r < p["rsi_lo"]) & (a < p["adx_max"])
    exit_ = df.close > bb.mid
    return _frame(entry, exit_, at * p["atr_stop"])


def breakout(df, p):
    dc = ind.donchian(df, int(p["n"]))
    dc_exit = ind.donchian(df, int(p["exit_n"]))
    vol_ok = df.volume > ind.sma(df.volume, 20) * p["vol_mult"]
    at = ind.atr(df, 14)
    entry = (df.close > dc.high) & vol_ok
    exit_ = df.close < dc_exit.low
    return _frame(entry, exit_, at * p["atr_stop"])


def pullback(df, p):
    e_f, e_s = ind.ema(df.close, 50), ind.ema(df.close, 200)
    r = ind.rsi(df.close, int(p["rsi_n"]))
    at = ind.atr(df, 14)
    entry = (e_f > e_s) & (r > p["rsi_dip"]) & (r.shift() <= p["rsi_dip"])
    exit_ = (r > p["rsi_exit"]) | (e_f < e_s)
    return _frame(entry, exit_, at * p["atr_stop"])


def vol_expansion(df, p):
    bb = ind.bollinger(df.close, 20, 2.0)
    width = (bb.upper - bb.lower) / bb.mid
    squeeze = width.shift() < width.shift().rolling(int(p["look"]), min_periods=50).quantile(p["q"])
    at = ind.atr(df, 14)
    entry = squeeze & (df.close > bb.upper)
    exit_ = df.close < bb.mid
    return _frame(entry, exit_, at * p["atr_stop"], at * p["atr_tp"])


def vwap_reversion(df, p):
    vw = ind.vwap(df, int(p["n"]))
    dev = (df.close - vw) / ind.atr(df, 14)
    at = ind.atr(df, 14)
    entry = (dev < -p["z"]) & (dev.shift() >= -p["z"])
    exit_ = df.close >= vw
    return _frame(entry, exit_, at * p["atr_stop"])


def macd_stochrsi(df, p):
    m = ind.macd(df.close)
    sr = ind.stoch_rsi(df.close)
    at = ind.atr(df, 14)
    entry = (m["hist"] > 0) & (m["hist"].shift() <= 0) & (sr < p["sr_max"])
    exit_ = m["hist"] < 0
    return _frame(entry, exit_, at * p["atr_stop"])


def ichimoku_trend(df, p):
    ic = ind.ichimoku(df)
    cloud_top = ic[["span_a", "span_b"]].max(axis=1)
    at = ind.atr(df, 14)
    entry = (df.close > cloud_top) & (ic.tenkan > ic.kijun) & (ic.tenkan.shift() <= ic.kijun.shift())
    exit_ = (ic.tenkan < ic.kijun) | (df.close < cloud_top)
    return _frame(entry, exit_, at * p["atr_stop"])


def regime_adaptive(df, p):
    reg = rg.classify(df)
    tr = momentum(df, {**MOMENTUM_DEFAULTS})
    mr = mean_reversion(df, {**MR_DEFAULTS, "adx_max": 100})
    entry = (tr.entry & (reg == "TREND_UP")) | (mr.entry & (reg == "RANGE"))
    exit_ = (tr.exit & (reg != "RANGE")) | (mr.exit & (reg == "RANGE")) | (reg == "TREND_DOWN") | (reg == "HIGH_VOL")
    stop = tr.stop_dist.where(reg == "TREND_UP", mr.stop_dist) * p["stop_scale"]
    return _frame(entry, exit_, stop)


def pair_relative(df, p):
    """Statistical-arbitrage style (long-only): buy the asset when its log-price spread
    vs a reference series is unusually low; exit on mean reversion. Requires df['ref_close']."""
    if "ref_close" not in df:
        raise ValueError("pair_relative requires a 'ref_close' column")
    n = int(p["n"])
    lr = np.log(df.close) - np.log(df.ref_close)
    z = ind.zscore(lr, n)
    at = ind.atr(df, 14)
    entry = (z < -p["z_in"]) & (z.shift() >= -p["z_in"])
    exit_ = z > -p["z_out"]
    return _frame(entry, exit_, at * p["atr_stop"])


MOMENTUM_DEFAULTS = dict(n=12, th=0.6, trend=100, atr_stop=2.0, atr_tp=4.0)
MR_DEFAULTS = dict(n=20, k=2.0, rsi_lo=30, adx_max=22, atr_stop=2.0)

STRATEGIES: dict[str, StrategySpec] = {
    s.name: s
    for s in [
        StrategySpec("buy_hold", "baseline", buy_hold, dict(stop_pct=3.0), {}, "Risk-managed buy & hold baseline (3% stop, sized by the risk engine)."),
        StrategySpec("ema_trend", "trend_following", ema_trend, dict(fast=12, slow=48, adx_min=20, atr_stop=2.5),
                     dict(fast=(5, 30, int), slow=(30, 150, int), adx_min=(10, 35, float), atr_stop=(1.0, 4.0, float)),
                     "EMA crossover filtered by ADX."),
        StrategySpec("momentum", "momentum", momentum, MOMENTUM_DEFAULTS,
                     dict(n=(4, 48, int), th=(0.2, 2.0, float), trend=(30, 200, int), atr_stop=(1.0, 4.0, float), atr_tp=(1.5, 8.0, float)),
                     "Rate-of-change impulse above trend EMA."),
        StrategySpec("mean_reversion", "mean_reversion", mean_reversion, MR_DEFAULTS,
                     dict(n=(10, 60, int), k=(1.5, 3.0, float), rsi_lo=(15, 40, float), adx_max=(15, 35, float), atr_stop=(1.0, 4.0, float)),
                     "Bollinger lower-band + RSI oversold in low-ADX (range) markets."),
        StrategySpec("breakout", "breakout", breakout, dict(n=48, exit_n=24, vol_mult=1.5, atr_stop=2.0),
                     dict(n=(12, 144, int), exit_n=(6, 72, int), vol_mult=(1.0, 3.0, float), atr_stop=(1.0, 4.0, float)),
                     "Donchian channel breakout with volume confirmation."),
        StrategySpec("pullback", "pullback", pullback, dict(rsi_n=14, rsi_dip=40, rsi_exit=65, atr_stop=2.0),
                     dict(rsi_n=(7, 28, int), rsi_dip=(25, 50, float), rsi_exit=(55, 80, float), atr_stop=(1.0, 4.0, float)),
                     "Buy RSI dips in an EMA50>EMA200 uptrend."),
        StrategySpec("vol_expansion", "volatility", vol_expansion, dict(look=288, q=0.2, atr_stop=1.5, atr_tp=3.0),
                     dict(look=(96, 576, int), q=(0.05, 0.4, float), atr_stop=(1.0, 3.0, float), atr_tp=(1.5, 6.0, float)),
                     "Bollinger squeeze followed by upside expansion."),
        StrategySpec("vwap_reversion", "mean_reversion", vwap_reversion, dict(n=48, z=2.0, atr_stop=2.0),
                     dict(n=(12, 144, int), z=(1.0, 4.0, float), atr_stop=(1.0, 4.0, float)),
                     "Revert to rolling VWAP after ATR-normalised deviation."),
        StrategySpec("macd_stochrsi", "momentum", macd_stochrsi, dict(sr_max=0.8, atr_stop=2.0),
                     dict(sr_max=(0.3, 1.0, float), atr_stop=(1.0, 4.0, float)),
                     "MACD histogram turn confirmed by Stochastic RSI."),
        StrategySpec("ichimoku_trend", "trend_following", ichimoku_trend, dict(atr_stop=2.5),
                     dict(atr_stop=(1.0, 4.0, float)), "Causal Ichimoku TK-cross above the cloud."),
        StrategySpec("regime_adaptive", "adaptive", regime_adaptive, dict(stop_scale=1.0),
                     dict(stop_scale=(0.5, 2.0, float)), "Switches momentum / mean-reversion by detected regime."),
    ]
}
PAIR_STRATEGY = StrategySpec("pair_relative", "stat_arb", pair_relative, dict(n=96, z_in=2.0, z_out=0.0, atr_stop=3.0),
                             dict(n=(24, 288, int), z_in=(1.0, 3.5, float), z_out=(-1.0, 1.0, float), atr_stop=(1.0, 5.0, float)),
                             "Long-only relative-value vs a reference asset.")


def ensemble(df: pd.DataFrame, members: list[tuple[StrategySpec, dict]], min_votes: int = 2) -> pd.DataFrame:
    sigs = [m.signals(df, p) for m, p in members]
    votes = sum(s.entry.astype(int) for s in sigs)
    exits = sum(s.exit.astype(int) for s in sigs)
    stop = pd.concat([s.stop_dist for s in sigs], axis=1).median(axis=1)
    return pd.DataFrame({"entry": votes >= min_votes, "exit": exits >= max(1, len(sigs) - min_votes + 1),
                         "stop_dist": stop, "tp_dist": np.nan})
