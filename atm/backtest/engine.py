"""Bar-by-bar event-driven backtest engine (long-only spot).

Timing contract (prevents look-ahead):
  * signals and risk context are taken from bar t-1 (fully closed),
  * orders fill at bar t open through the ExecutionSimulator,
  * protective stops / take-profits are evaluated against bar t high/low; if both
    could have triggered in the same bar the stop is assumed (pessimistic),
  * liquidity caps and slippage use the previous closed bar's volume/range (known at decision time),
  * the risk session (session-loss limit) resets every `session_hours` (4h), matching deployment,
  * partial fills of one position are merged into a single logical trade.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..features import indicators as ind
from ..risk.engine import EntryContext, RiskEngine
from ..risk.limits import RiskLimits
from . import metrics as mt
from .execution import CostModel, ExecutionSimulator, MarketSpec


@dataclass
class BacktestResult:
    equity: pd.Series
    trades: pd.DataFrame
    metrics: dict
    rejections: dict = field(default_factory=dict)
    risk_events: list = field(default_factory=list)


def _bars_per_year(index: pd.DatetimeIndex) -> float:
    step = pd.Series(index).diff().median()
    return pd.Timedelta(days=365) / step


def run_backtest(df: pd.DataFrame, sig: pd.DataFrame, market: MarketSpec, limits: RiskLimits,
                 costs: CostModel = CostModel(), capital_usd: float = 100.0,
                 start: int | None = None, end: int | None = None, seed: int = 7,
                 session_hours: float = 4.0) -> BacktestResult:
    o, h, l, c, v = (df[k].to_numpy(float) for k in ("open", "high", "low", "close", "volume"))
    idx = df.index
    entry, exit_ = sig["entry"].to_numpy(bool), sig["exit"].to_numpy(bool)
    stop_d = sig["stop_dist"].to_numpy(float)
    tp_d = sig["tp_dist"].to_numpy(float)
    atr_pct = (100 * ind.atr(df, 14) / df.close).to_numpy(float)
    lr = np.log(df.close).diff()
    abnormal = (lr.abs() > 6 * lr.rolling(288, min_periods=50).std().shift()).to_numpy(bool)

    start = 1 if start is None else max(1, start)
    end = len(df) if end is None else min(len(df), end)
    capital = capital_usd / market.usd_per_quote
    cash, qty = capital, 0.0
    entry_px = stop_px = tp_px = np.nan
    entry_i = -1
    # remaining (not yet allocated) entry costs + accumulators for the current logical trade
    rem_fee = rem_slip = 0.0
    pos = {"pnl": 0.0, "fees": 0.0, "slip": 0.0, "cost": 0.0, "qty": 0.0, "proceeds_px_qty": 0.0}
    risk = RiskEngine(limits, capital)
    risk.start_session(capital)
    session_bars = max(1, int(pd.Timedelta(hours=session_hours) / pd.Series(idx).diff().median()))
    ex = ExecutionSimulator(market, costs, seed)
    trades, rej = [], {}
    eq = np.empty(end - start)
    usd_liq_scale = market.usd_per_quote

    def close_pos(i, px_ref, reason, forced=True, ignore_liquidity=False):
        """Sell (part of) the position. Liquidity/slippage use the previous closed bar (j=i-1)."""
        nonlocal cash, qty, rem_fee, rem_slip
        j = max(i - 1, 0)
        f = ex.fill("sell", qty, px_ref, h[j], l[j], v[j], forced=forced, ignore_liquidity=ignore_liquidity)
        if not f.ok:
            rej[f.reason] = rej.get(f.reason, 0) + 1
            return False
        frac = f.qty / qty
        fee_alloc, slip_alloc = rem_fee * frac, rem_slip * frac
        rem_fee -= fee_alloc
        rem_slip -= slip_alloc
        proceeds = f.qty * f.price - f.fee
        cost_basis = f.qty * entry_px + fee_alloc
        pos["pnl"] += proceeds - cost_basis
        pos["fees"] += f.fee + fee_alloc
        pos["slip"] += f.slippage_cost + slip_alloc
        pos["cost"] += cost_basis
        pos["qty"] += f.qty
        pos["proceeds_px_qty"] += f.qty * f.price
        cash += proceeds
        qty -= f.qty
        if qty < market.step_size or qty * px_ref < 1e-12:
            cash += qty * px_ref if qty > 0 else 0.0  # dust below step size is valued at the reference price
            qty = 0.0
        if qty == 0.0:  # one logical trade per position, however many fill slices it took
            trades.append(dict(entry_ts=idx[entry_i], exit_ts=idx[i], entry_px=entry_px, exit_px=pos["proceeds_px_qty"] / pos["qty"],
                               qty=pos["qty"], pnl=pos["pnl"], ret_pct=100 * pos["pnl"] / pos["cost"], fees=pos["fees"],
                               slippage=pos["slip"], bars=i - entry_i, reason=reason))
            risk.on_trade_closed(pos["pnl"])
            for key in pos:
                pos[key] = 0.0
        return True

    for k, i in enumerate(range(start, end)):
        j = i - 1
        if k and k % session_bars == 0:   # 4-hour session boundary: new session-loss baseline
            risk.start_session(cash + qty * c[j])
        # 1) orders decided at close of bar j, executed at open of bar i
        if qty > 0 and (exit_[j] or risk.must_flatten):
            close_pos(i, o[i], "kill/halt" if risk.must_flatten else "signal_exit", forced=risk.must_flatten)
        elif qty == 0 and entry[j] and np.isfinite(stop_d[j]) and stop_d[j] > 0:
            ctx = EntryContext(ts=idx[j], equity=cash, cash=cash, price=c[j], stop_price=c[j] - stop_d[j],
                               atr_pct=atr_pct[j] if np.isfinite(atr_pct[j]) else 0.0,
                               bar_quote_volume=v[j] * c[j] * usd_liq_scale, spread_bps=2 * market.half_spread_bps,
                               open_notional=0.0, open_positions=0, min_notional=market.min_notional,
                               abnormal_market=bool(abnormal[j]))
            d = risk.check_entry(ctx)
            if not d.approved:
                for r in d.reasons:
                    key = r.split(" ")[0]
                    rej[key] = rej.get(key, 0) + 1
            else:
                f = ex.fill("buy", d.qty, o[i], h[j], l[j], v[j])
                if not f.ok:
                    rej[f.reason] = rej.get(f.reason, 0) + 1
                elif f.qty * f.price + f.fee <= cash:
                    cash -= f.qty * f.price + f.fee
                    qty, entry_px, entry_i, rem_fee, rem_slip = f.qty, f.price, i, f.fee, f.slippage_cost
                    stop_px = f.price - stop_d[j]
                    tp_px = f.price + tp_d[j] if np.isfinite(tp_d[j]) else np.nan
                else:
                    rej["insufficient_cash"] = rej.get("insufficient_cash", 0) + 1
        # 2) intrabar protective orders (stop has priority)
        if qty > 0:
            if l[i] <= stop_px:
                close_pos(i, min(stop_px, o[i]), "stop_loss")
            elif np.isfinite(tp_px) and h[i] >= tp_px:
                close_pos(i, max(tp_px, o[i]), "take_profit")
        # 3) mark to market, risk bookkeeping
        equity = cash + qty * c[i]
        eq[k] = equity
        risk.on_bar(idx[i], equity)

    if qty > 0:
        # accounting liquidation at the final close (liquidity cap waived so no position is silently dropped)
        close_pos(end - 1, c[end - 1], "end_of_test", ignore_liquidity=True)
        eq[-1] = cash + qty * c[end - 1]
    equity_s = pd.Series(eq, index=idx[start:end])
    tdf = pd.DataFrame(trades, columns=["entry_ts", "exit_ts", "entry_px", "exit_px", "qty", "pnl", "ret_pct",
                                        "fees", "slippage", "bars", "reason"])
    m = mt.compute(equity_s, tdf, _bars_per_year(idx), capital)
    m["capital_usd"] = capital_usd
    m["net_pnl_usd"] = (m["final_equity"] - capital) * market.usd_per_quote
    return BacktestResult(equity_s, tdf, m, rej, risk.events)
