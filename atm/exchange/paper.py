"""Paper / forward-testing trader.

Consumes closed bars from any feed (LIVE_PUBLIC websocket, TESTNET, or REPLAY of stored
history), computes signals causally, routes every entry through the RiskEngine and fills
with the ExecutionSimulator (mode='paper') or sends orders to Binance Spot Testnet
(mode='testnet'). The source label of every bar and trade is preserved end-to-end.
"""
from __future__ import annotations

import threading
import time
import uuid
from collections import deque

import numpy as np
import pandas as pd

from ..backtest.execution import CostModel, ExecutionSimulator, MarketSpec
from ..data.stream import Bar
from ..features import indicators as ind
from ..risk.engine import EntryContext, RiskEngine
from ..risk.limits import RiskLimits
from ..storage.db import Store
from ..strategies.library import StrategySpec


class PaperTrader:
    def __init__(self, spec: StrategySpec, params: dict, market: MarketSpec, limits: RiskLimits, capital_usd: float = 100.0,
                 history: pd.DataFrame | None = None, store: Store | None = None, mode: str = "paper", testnet=None,
                 session_hours: float = 4.0, costs: CostModel = CostModel()):
        if mode not in ("paper", "testnet"):
            raise ValueError("mode must be 'paper' or 'testnet' (live trading is disabled)")
        if mode == "testnet" and (testnet is None or not testnet.has_credentials):
            raise ValueError("testnet mode requires a SpotTestnetClient with credentials")
        self.spec, self.params, self.m, self.limits = spec, params, market, limits
        self.mode, self.testnet, self.store = mode, testnet, store
        self.capital = capital_usd / market.usd_per_quote
        self.cash, self.qty = self.capital, 0.0
        self.entry_px = self.stop_px = self.tp_px = np.nan
        self.entry_fee = 0.0
        self.risk = RiskEngine(limits, self.capital)
        self.risk.start_session(self.capital)
        self.ex = ExecutionSimulator(market, costs, seed=int(time.time()) % 10000)
        self.bars = history.copy() if history is not None else pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        self.session_id = uuid.uuid4().hex[:12]
        self.session_start = None
        self.session_hours = session_hours
        self.equity_curve: deque = deque(maxlen=5000)
        self.trades: list[dict] = []
        self.log: deque = deque(maxlen=300)
        self.source = "NONE"
        self.lock = threading.Lock()
        self.pending: dict | None = None
        self.running = True

    # --------------------------------------------------------------
    def _fill(self, side, qty, ref, bar: Bar, forced=False):
        if self.mode == "testnet":
            cid = f"atm{uuid.uuid4().hex[:16]}"
            r = self.testnet.new_order(self.m.symbol, side, qty, client_id=cid)
            fills = r.get("fills", [])
            q = float(r.get("executedQty", 0))
            px = (sum(float(f["price"]) * float(f["qty"]) for f in fills) / q) if q else ref
            fee = sum(float(f.get("commission", 0)) for f in fills if f.get("commissionAsset") == self.m.quote)
            return q > 0, q, px, fee or q * px * 0.001
        f = self.ex.fill(side, qty, ref, bar.high, bar.low, bar.volume, forced=forced)
        return f.ok, f.qty, f.price, f.fee

    def on_bar(self, bar: Bar) -> None:
        if not bar.closed or not self.running:
            return
        with self.lock:
            self.source = bar.source
            if self.session_start is None:
                self.session_start = bar.ts
            # execute pending order at this bar's open (decided at previous close)
            if self.pending:
                p, self.pending = self.pending, None
                if p["side"] == "sell" and self.qty > 0:
                    self._close(bar.open, bar, p["reason"], forced=p.get("forced", False))
                elif p["side"] == "buy" and self.qty == 0:
                    ok, q, px, fee = self._fill("buy", p["qty"], bar.open, bar)
                    if ok and q * px + fee <= self.cash:
                        self.cash -= q * px + fee
                        self.qty, self.entry_px, self.entry_fee = q, px, fee
                        self.stop_px = px - p["stop_dist"]
                        self.tp_px = px + p["tp_dist"] if np.isfinite(p["tp_dist"]) else np.nan
                        self._record("BUY", q, px, fee, bar)
            # protective orders on this bar
            if self.qty > 0 and bar.low <= self.stop_px:
                self._close(min(self.stop_px, bar.open), bar, "stop_loss", forced=True)
            elif self.qty > 0 and np.isfinite(self.tp_px) and bar.high >= self.tp_px:
                self._close(max(self.tp_px, bar.open), bar, "take_profit", forced=True)
            # append bar, recompute signal on closed history
            self.bars.loc[bar.ts] = [bar.open, bar.high, bar.low, bar.close, bar.volume]
            self.bars = self.bars.iloc[-3000:]
            eq = self.cash + self.qty * bar.close
            self.equity_curve.append((str(bar.ts), eq * self.m.usd_per_quote))
            self.risk.on_bar(bar.ts, eq)
            if self.session_start is not None and bar.ts - self.session_start >= pd.Timedelta(hours=self.session_hours):
                self._log(f"session complete: equity ${eq * self.m.usd_per_quote:.2f}")
                self.running = False
                if self.qty > 0:
                    self.pending = {"side": "sell", "reason": "session_end", "forced": True}
                return
            if len(self.bars) < 120:
                return
            sig = self.spec.signals(self.bars.astype(float), self.params).iloc[-1]
            if self.qty > 0 and (sig["exit"] or self.risk.must_flatten):
                self.pending = {"side": "sell", "reason": "kill/halt" if self.risk.must_flatten else "signal_exit", "forced": self.risk.must_flatten}
            elif self.qty == 0 and sig["entry"] and np.isfinite(sig["stop_dist"]) and sig["stop_dist"] > 0:
                atr_pct = float(100 * ind.atr(self.bars.astype(float), 14).iloc[-1] / bar.close)
                ctx = EntryContext(ts=bar.ts, equity=eq, cash=self.cash, price=bar.close, stop_price=bar.close - sig["stop_dist"],
                                   atr_pct=atr_pct, bar_quote_volume=bar.volume * bar.close * self.m.usd_per_quote,
                                   spread_bps=2 * self.m.half_spread_bps, data_age_s=0.0, min_notional=self.m.min_notional)
                d = self.risk.check_entry(ctx)
                if d.approved:
                    self.pending = {"side": "buy", "qty": d.qty, "stop_dist": float(sig["stop_dist"]), "tp_dist": float(sig.get("tp_dist", np.nan))}
                    self._log(f"entry approved: {d.notional * self.m.usd_per_quote:.2f} USD")
                else:
                    self._log("entry rejected by risk engine: " + "; ".join(d.reasons))

    def _close(self, ref, bar, reason, forced=True):
        ok, q, px, fee = self._fill("sell", self.qty, ref, bar, forced=forced)
        if not ok:
            self._log(f"exit failed ({reason}); will retry")
            self.pending = {"side": "sell", "reason": reason, "forced": True}
            return
        pnl = q * px - fee - q * self.entry_px - self.entry_fee * (q / self.qty)
        self.cash += q * px - fee
        self.qty -= q
        if self.qty < self.m.step_size:
            self.qty = 0.0
        self.risk.on_trade_closed(pnl)
        self._record("SELL", q, px, fee, bar, pnl, reason)

    def _record(self, side, q, px, fee, bar, pnl=None, reason=""):
        t = {"ts": str(bar.ts), "side": side, "qty": q, "price": px, "fee_usd": fee * self.m.usd_per_quote,
             "pnl_usd": None if pnl is None else pnl * self.m.usd_per_quote, "reason": reason, "source": bar.source, "mode": self.mode}
        self.trades.append(t)
        self._log(f"{side} {q:.6f} @ {px:.6f} [{bar.source}/{self.mode}] {reason}")
        if self.store:
            self.store.add_paper_trade(session=self.session_id, symbol=self.m.symbol, side=side, qty=q, price=px, fee=fee,
                                       ts=str(bar.ts), source=f"{bar.source}/{self.mode}", strategy=self.spec.name, pnl=pnl)

    def _log(self, msg):
        self.log.append({"t": time.time(), "msg": msg})

    def emergency_stop(self, reason="owner emergency stop"):
        with self.lock:
            self.risk.emergency_stop(reason)
            if self.qty > 0:
                self.pending = {"side": "sell", "reason": "emergency_stop", "forced": True}
            self._log(f"EMERGENCY STOP: {reason}")

    def snapshot(self) -> dict:
        with self.lock:
            last = float(self.bars.close.iloc[-1]) if len(self.bars) else float("nan")
            eq = self.cash + self.qty * (last if np.isfinite(last) else 0)
            closed = [t for t in self.trades if t["pnl_usd"] is not None]
            return {"session_id": self.session_id, "mode": self.mode, "data_source": self.source, "symbol": self.m.symbol,
                    "strategy": self.spec.name, "params": self.params, "running": self.running,
                    "initial_usd": self.capital * self.m.usd_per_quote, "equity_usd": eq * self.m.usd_per_quote,
                    "cash_usd": self.cash * self.m.usd_per_quote, "position_qty": self.qty, "entry_px": None if not self.qty else self.entry_px,
                    "stop_px": None if not self.qty else self.stop_px, "last_price": last,
                    "net_pnl_usd": (eq - self.capital) * self.m.usd_per_quote,
                    "fees_usd": sum(t["fee_usd"] for t in self.trades), "trades": self.trades[-100:],
                    "closed_trades": len(closed), "wins": sum(1 for t in closed if t["pnl_usd"] > 0),
                    "equity_curve": list(self.equity_curve)[-500:], "risk": self.risk.state(), "log": list(self.log)[-50:]}
