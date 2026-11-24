"""Conservative execution simulator: fees, spread, slippage, latency, partial fills,
exchange precision, min notional, random rejects and network failures."""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MarketSpec:
    symbol: str
    quote: str = "USDT"
    usd_per_quote: float = 1.0      # to express $-denominated limits/capital in quote units
    tick_size: float = 0.01
    step_size: float = 0.00001
    min_notional: float = 5.0       # in quote units
    half_spread_bps: float = 1.0    # assumed (no historical order book available)


# Approximate reference conversions for datasets quoted in BTC/ETH (only used to size
# the $100 notional capital and USD liquidity thresholds; PnL is reported in %).
MARKETS = {
    "BTCUSDT": MarketSpec("BTCUSDT", "USDT", 1.0, 0.01, 0.00001, 5.0, 0.5),
    "XRPUSDT": MarketSpec("XRPUSDT", "USDT", 1.0, 0.0001, 0.1, 5.0, 1.0),
}
_BTC_2018 = 11500.0


def market_for(symbol: str, quote: str, last_price: float) -> MarketSpec:
    if symbol in MARKETS:
        return MARKETS[symbol]
    if quote == "BTC":
        usd = 7000.0 if symbol.startswith("UNKNOWN") else _BTC_2018
        tick = 10 ** math.floor(math.log10(last_price) - 3)
        return MarketSpec(symbol, "BTC", usd, tick, 1e-8 if last_price > 1e-3 else 1.0, 0.0001, 5.0)
    if quote == "ETH":
        return MarketSpec(symbol, "ETH", 180.0, 1e-8, 1.0, 0.001, 5.0)
    return MarketSpec(symbol, quote)


@dataclass(frozen=True)
class CostModel:
    taker_fee: float = 0.001          # Binance spot standard 0.10 %
    slippage_bps: float = 1.0         # base adverse slippage
    range_slip_frac: float = 0.05     # extra slippage as fraction of bar range * sqrt(participation)
    latency_bps: float = 0.5          # adverse drift during order latency
    max_participation: float = 0.05   # max share of bar volume we can take (partial fills beyond)
    reject_prob: float = 0.002        # random exchange rejects
    network_fail_prob: float = 0.001  # order lost / timeout
    stress_mult: float = 1.0          # multiply all frictions (stress tests)


@dataclass
class Fill:
    ok: bool
    qty: float = 0.0
    price: float = 0.0
    fee: float = 0.0
    slippage_cost: float = 0.0
    reason: str = ""
    partial: bool = False


def round_step(x: float, step: float) -> float:
    return math.floor(x / step + 1e-9) * step


def round_tick(p: float, tick: float, up: bool) -> float:
    if up:
        return math.ceil(p / tick - 1e-9) * tick
    return math.floor(p / tick + 1e-9) * tick


class ExecutionSimulator:
    def __init__(self, market: MarketSpec, costs: CostModel = CostModel(), seed: int = 7):
        self.m, self.c = market, costs
        self.rng = np.random.default_rng(seed)

    def fill(self, side: str, qty: float, ref_price: float, bar_high: float, bar_low: float,
             bar_volume: float, forced: bool = False, ignore_liquidity: bool = False) -> Fill:
        """Market order at ref_price (next bar open). `forced` exits (stops/kill) are never randomly rejected
        but may be delayed by the caller on network failure."""
        m, c = self.m, self.c
        s = c.stress_mult
        if not forced:
            if self.rng.random() < c.network_fail_prob * s:
                return Fill(False, reason="network_failure")
            if self.rng.random() < c.reject_prob * s:
                return Fill(False, reason="exchange_reject")
        max_qty = c.max_participation * bar_volume if bar_volume > 0 else 0.0
        partial = False
        if qty > max_qty and not ignore_liquidity:
            qty, partial = max_qty, True
        qty = round_step(qty, m.step_size)
        if qty <= 0:
            return Fill(False, reason="zero_qty_after_liquidity/precision")
        participation = qty / bar_volume if bar_volume > 0 else 1.0
        rng_frac = (bar_high - bar_low) / ref_price if ref_price > 0 else 0.0
        adverse = (m.half_spread_bps + c.slippage_bps + c.latency_bps) / 1e4 * s + c.range_slip_frac * rng_frac * math.sqrt(participation) * s
        if side == "buy":
            px = round_tick(ref_price * (1 + adverse), m.tick_size, up=True)
        else:
            px = round_tick(ref_price * (1 - adverse), m.tick_size, up=False)
        notional = qty * px
        if notional < m.min_notional and not forced:
            return Fill(False, reason="below_min_notional")
        fee = notional * c.taker_fee
        return Fill(True, qty, px, fee, abs(px - ref_price) * qty, partial=partial)
