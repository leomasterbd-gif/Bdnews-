#!/usr/bin/env python3
"""One autonomous paper-trading step on LIVE public Binance prices (virtual money only).

Run hourly. State persists in reports/live_paper/state.json (committed to git) so each run
continues where the last one stopped. For every symbol:
  * fetch the latest closed 5m candles from the public API (no keys),
  * catch up bar-by-bar since the last processed bar through the PaperTrader
    (risk engine + execution simulator; source label LIVE_PUBLIC),
  * only strategies that passed every validation gate may trade; otherwise the account stays
    flat and the step records a monitoring snapshot (price, regime, what each strategy signals).
Never places real orders. Writes reports/live_paper/{state.json,log.jsonl,status.md}."""
import json
import sys
import time
from pathlib import Path

import _path  # noqa: F401
import numpy as np
import pandas as pd
from atm.backtest.execution import market_for
from atm.data.stream import Bar
from atm.exchange.binance import PublicMarketData
from atm.exchange.paper import PaperTrader
from atm.features.regime import classify
from atm.risk.limits import RiskLimits
from atm.strategies.library import STRATEGIES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "live_paper"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "BNBUSDT"]
CAPITAL = 100.0


def validated_strategy(symbol: str):
    """Latest walk-forward evidence for this symbol; returns (spec, params) only if VALIDATED."""
    best = None
    for f in ("big_walk_forward.json", "walk_forward.json"):
        p = ROOT / "reports" / f
        if not p.exists():
            continue
        for r in json.loads(p.read_text()):
            if symbol in r.get("dataset", "").replace("_", "") and r["verdict"] == "VALIDATED" and r["strategy"] in STRATEGIES:
                if best is None or r["oos_compound_return_pct"] > best["oos_compound_return_pct"]:
                    best = r
        if best:
            break
    return (STRATEGIES[best["strategy"]], best["final_params"]) if best else (None, None)


def klines_df(rows) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=["t", "open", "high", "low", "close", "volume", "ct", "qv", "n", "tb", "tq", "i"])
    df["date"] = pd.to_datetime(df.t, unit="ms", utc=True)
    df = df.set_index("date")[["open", "high", "low", "close", "volume"]].astype(float)
    now_ms = time.time() * 1000
    closed = pd.Series([r[6] for r in rows], index=df.index) < now_ms  # drop the still-forming candle
    return df[closed.values]


def step_symbol(sym: str, st: dict, limits: RiskLimits, api: PublicMarketData) -> dict:
    df = klines_df(api.klines(sym, "5m", 1000))
    m = market_for(sym, "USDT", float(df.close.iloc[-1]))
    s = st.setdefault(sym, {"cash": CAPITAL, "qty": 0.0, "entry_px": None, "stop_px": None, "tp_px": None,
                            "entry_fee": 0.0, "last_ts": None, "trades": [], "strategy": None})
    spec, params = validated_strategy(sym)
    snap = {"symbol": sym, "price": float(df.close.iloc[-1]), "as_of": str(df.index[-1]),
            "regime": str(classify(df).iloc[-1]), "source": "LIVE_PUBLIC"}
    snap["signals"] = {}
    for n, sp in STRATEGIES.items():
        x = sp.signals(df).iloc[-1]
        snap["signals"][n] = "ENTRY" if x.entry else ("EXIT" if x.exit else "-")
    if spec is None:
        if s["qty"]:  # strategy lost validation while holding: flatten at market (virtual)
            px = float(df.close.iloc[-1])
            s["cash"] += s["qty"] * px * (1 - 0.001)
            s["trades"].append({"ts": str(df.index[-1]), "side": "SELL", "price": px, "reason": "validation_revoked"})
            s["qty"] = 0.0
        s["strategy"] = None
        s["last_ts"] = str(df.index[-1])
        snap.update(status="FLAT — no validated strategy (by design)", equity_usd=s["cash"])
        return snap
    last = pd.Timestamp(s["last_ts"]) if s["last_ts"] else df.index[-300]
    hist, new = df[df.index <= last], df[df.index > last]
    t = PaperTrader(spec, params, m, limits, CAPITAL, history=hist, session_hours=24 * 3650)
    t.cash, t.qty = s["cash"], s["qty"]
    if s["qty"]:
        t.entry_px, t.stop_px, t.entry_fee = s["entry_px"], s["stop_px"], s["entry_fee"]
        t.tp_px = s["tp_px"] if s["tp_px"] is not None else np.nan
    for ts, r in new.iterrows():
        t.on_bar(Bar(ts, r.open, r.high, r.low, r.close, r.volume, True, "LIVE_PUBLIC"))
    s.update(cash=t.cash, qty=t.qty, entry_px=t.entry_px if t.qty else None, stop_px=t.stop_px if t.qty else None,
             tp_px=(None if not t.qty or not np.isfinite(t.tp_px) else t.tp_px), entry_fee=t.entry_fee,
             last_ts=str(df.index[-1]), strategy=spec.name)
    s["trades"] = (s["trades"] + t.trades)[-200:]
    snap.update(status=f"ACTIVE — {spec.name} (VALIDATED)", equity_usd=t.cash + t.qty * float(df.close.iloc[-1]),
                new_trades=t.trades, risk=t.risk.state()["halted_reason"] or t.risk.state()["killed_reason"])
    return snap


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sp = OUT / "state.json"
    state = json.loads(sp.read_text()) if sp.exists() else {"created": pd.Timestamp.now("UTC").isoformat(), "symbols": {}}
    if (ROOT / "data" / "KILL").exists() or state.get("stopped"):
        print("STOPPED by owner — no action")
        return 0
    limits, api = RiskLimits.load(), PublicMarketData(timeout=15, retries=2)
    snaps, errors = [], []
    for sym in SYMBOLS:
        try:
            snaps.append(step_symbol(sym, state["symbols"], limits, api))
        except Exception as e:  # noqa: BLE001 - one market failing must not stop the others
            errors.append({"symbol": sym, "error": f"{e.__class__.__name__}: {str(e)[:150]}"})
    total = sum(x.get("equity_usd", CAPITAL) for x in snaps) + CAPITAL * len(errors)
    run = {"ts": pd.Timestamp.now("UTC").isoformat(), "total_virtual_equity_usd": total,
           "initial_usd": CAPITAL * len(SYMBOLS), "snapshots": snaps, "errors": errors}
    state["last_run"] = run["ts"]
    state["runs"] = state.get("runs", 0) + 1
    sp.write_text(json.dumps(state, indent=1, default=str))
    with open(OUT / "log.jsonl", "a") as fh:
        fh.write(json.dumps({k: v for k, v in run.items() if k != "snapshots"} |
                            {"prices": {x["symbol"]: x["price"] for x in snaps}, "status": {x["symbol"]: x["status"] for x in snaps}}, default=str) + "\n")
    lines = ["# লাইভ পেপার ট্রেডিং / Live paper trading (VIRTUAL money)\n", f"Last run: {run['ts']} · runs: {state['runs']}\n",
             f"**মোট ভার্চুয়াল ইকুইটি / total virtual equity: ${total:,.2f}** (শুরু ${CAPITAL * len(SYMBOLS):,.0f})\n",
             "| market | price | regime | status | equity $ |", "|---|---|---|---|---|"]
    for x in snaps:
        lines.append(f"| {x['symbol']} | {x['price']:,.4f} | {x['regime']} | {x['status']} | {x.get('equity_usd', CAPITAL):,.2f} |")
    for e in errors:
        lines.append(f"| {e['symbol']} | — | — | ERROR {e['error']} | — |")
    (OUT / "status.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"total_virtual_equity_usd": total, "status": {x["symbol"]: x["status"] for x in snaps},
                      "new_trades": sum(len(x.get("new_trades", [])) for x in snaps), "errors": errors}, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
