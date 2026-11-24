"""Deterministic, independent risk engine.

It never consults AI/strategy confidence to relax limits. Every rejection carries
machine-readable reasons. A risk rejection always overrides any strategy signal.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import pandas as pd

from .limits import RiskLimits


@dataclass
class EntryContext:
    ts: pd.Timestamp
    equity: float
    cash: float
    price: float
    stop_price: float
    atr_pct: float = 0.0
    bar_quote_volume: float = float("inf")
    spread_bps: float = 0.0
    data_age_s: float = 0.0
    open_notional: float = 0.0
    open_positions: int = 0
    min_notional: float | None = None
    abnormal_market: bool = False
    network_ok: bool = True


@dataclass
class Decision:
    approved: bool
    qty: float = 0.0
    notional: float = 0.0
    reasons: list[str] = field(default_factory=list)


class RiskEngine:
    def __init__(self, limits: RiskLimits, initial_equity: float):
        self.limits = limits
        self.initial_equity = initial_equity
        self.peak = initial_equity
        self.session_start_equity = initial_equity
        self.day_start_equity = initial_equity
        self.current_day = None
        self.consecutive_losses = 0
        self.pause_remaining = 0
        self.halted_reason: str | None = None   # session/day halts (auto-clear on new session/day)
        self.killed_reason: str | None = None   # emergency / drawdown stop (manual owner reset)
        self.events: list[dict] = []

    # ---- state updates -------------------------------------------------
    def start_session(self, equity: float) -> None:
        self.session_start_equity = equity
        if self.halted_reason and self.halted_reason.startswith("session"):
            self.halted_reason = None

    def on_bar(self, ts: pd.Timestamp, equity: float) -> None:
        day = ts.floor("D")
        if day != self.current_day:
            self.current_day = day
            self.day_start_equity = equity
            if self.halted_reason and self.halted_reason.startswith("daily"):
                self.halted_reason = None
        self.peak = max(self.peak, equity)
        if self.pause_remaining > 0:
            self.pause_remaining -= 1
        L = self.limits
        dd = 100 * (1 - equity / self.peak)
        if dd >= L.max_drawdown_pct and not self.killed_reason:
            self._kill(ts, f"max_drawdown {dd:.2f}% >= {L.max_drawdown_pct}%")
        sl = 100 * (1 - equity / self.session_start_equity)
        if sl >= L.max_session_loss_pct and not self.halted_reason:
            self._halt(ts, f"session_loss {sl:.2f}% >= {L.max_session_loss_pct}%")
        dl = 100 * (1 - equity / self.day_start_equity)
        if dl >= L.max_daily_loss_pct and not (self.halted_reason or "").startswith("daily"):
            self._halt(ts, f"daily_loss {dl:.2f}% >= {L.max_daily_loss_pct}%")

    def on_trade_closed(self, pnl: float) -> None:
        if pnl < 0:
            self.consecutive_losses += 1
            if self.consecutive_losses >= self.limits.max_consecutive_losses:
                self.pause_remaining = self.limits.pause_bars_after_losses
                self.events.append({"type": "pause", "reason": f"{self.consecutive_losses} consecutive losses"})
                self.consecutive_losses = 0
        else:
            self.consecutive_losses = 0

    def emergency_stop(self, reason: str = "owner emergency stop", ts=None) -> None:
        self._kill(ts, reason)

    def owner_reset(self) -> None:
        self.killed_reason = None
        self.halted_reason = None
        self.events.append({"type": "owner_reset"})

    def _kill(self, ts, reason):
        self.killed_reason = reason
        self.events.append({"type": "kill", "ts": str(ts), "reason": reason})

    def _halt(self, ts, reason):
        self.halted_reason = reason
        self.events.append({"type": "halt", "ts": str(ts), "reason": reason})

    @property
    def must_flatten(self) -> bool:
        return self.killed_reason is not None or self.halted_reason is not None

    # ---- pre-trade check -----------------------------------------------
    def check_entry(self, c: EntryContext) -> Decision:
        L = self.limits
        reasons = []
        if self.killed_reason:
            reasons.append(f"killed: {self.killed_reason}")
        if self.halted_reason:
            reasons.append(f"halted: {self.halted_reason}")
        if self.pause_remaining > 0:
            reasons.append(f"consecutive-loss pause ({self.pause_remaining} bars)")
        if not c.network_ok:
            reasons.append("network/exchange health check failed")
        if c.abnormal_market:
            reasons.append("abnormal market behaviour detected")
        if c.data_age_s > L.max_data_staleness_s:
            reasons.append(f"stale data ({c.data_age_s:.0f}s)")
        if c.atr_pct > L.max_atr_pct:
            reasons.append(f"volatility {c.atr_pct:.2f}% > {L.max_atr_pct}%")
        if c.bar_quote_volume < L.min_bar_quote_volume:
            reasons.append(f"liquidity {c.bar_quote_volume:.0f} < {L.min_bar_quote_volume}")
        if c.spread_bps > L.max_spread_bps:
            reasons.append(f"spread {c.spread_bps:.1f}bps > {L.max_spread_bps}")
        if c.open_positions >= L.max_open_positions:
            reasons.append("max open positions")
        if not (c.price > 0 and 0 < c.stop_price < c.price) or not math.isfinite(c.stop_price):
            reasons.append("invalid stop (a protective stop below entry is mandatory)")
        if reasons:
            return Decision(False, reasons=reasons)

        risk_amt = c.equity * L.max_risk_per_trade_pct / 100
        qty_risk = risk_amt / (c.price - c.stop_price)
        cap_pos = c.equity * L.max_position_pct / 100
        cap_exp = c.equity * L.max_exposure_pct / 100 - c.open_notional
        notional = min(qty_risk * c.price, cap_pos, cap_exp, c.cash)  # spot: no borrowing
        min_notional = c.min_notional if c.min_notional is not None else L.min_order_notional
        if notional < min_notional:
            return Decision(False, reasons=[f"size {notional:.4f} below min notional {min_notional}"])
        return Decision(True, qty=notional / c.price, notional=notional)

    def state(self) -> dict:
        return dict(peak=self.peak, session_start_equity=self.session_start_equity, day_start_equity=self.day_start_equity,
                    consecutive_losses=self.consecutive_losses, pause_remaining=self.pause_remaining,
                    halted_reason=self.halted_reason, killed_reason=self.killed_reason, limits=self.limits.as_dict())
