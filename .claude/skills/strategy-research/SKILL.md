---
name: strategy-research
description: Design, add and evaluate trading strategies (momentum, trend, mean reversion, breakout, pullback, volatility, VWAP, Ichimoku, regime-adaptive, stat-arb, ensembles). Use for algorithmic trading, technical analysis, quantitative finance, crypto market research, market microstructure and time-series questions.
---
# strategy-research

Covers: Quantitative Finance · Cryptocurrency Market Research · Algorithmic Trading · Technical Analysis · Market Microstructure · Time Series Analysis.

## Adding a strategy
1. Write `fn(df, params) -> DataFrame[entry, exit, stop_dist, tp_dist]` in `atm/strategies/library.py` using only causal indicators from `atm/features/indicators.py`.
2. Register a `StrategySpec` with defaults and a parameter `space` (for the GA / Optuna optimiser).
3. `python3 -m pytest tests/test_no_lookahead.py -q` — the strategy is automatically included in the causality test.
4. `python3 scripts/backtest_one.py --strategy <name> --wf` on several datasets. Register only what passes the gates.

## Cost reality
Binance spot taker fee 0.10%/side ⇒ ≥0.2% round trip + spread + slippage. On 5m BTC bars the median move is far smaller, so high-frequency rules need a demonstrated edge larger than costs.
