---
name: quant-backtesting
description: Run realistic backtests, walk-forward validation, bootstrap and Monte Carlo analysis for AI Trading Master strategies. Use for backtesting, forward testing, walk-forward optimisation, Monte Carlo, strategy validation, probability/statistics and financial-math questions.
---
# quant-backtesting

Covers: Backtesting · Forward Testing · Walk-Forward Optimization · Monte Carlo Simulation · Strategy Validation · Probability and Statistics · Financial Mathematics.

## Commands
- One strategy: `python3 scripts/backtest_one.py --dataset BTC_USDT-5m --strategy momentum [--interval 15m]`
- With promotion gates: `python3 scripts/backtest_one.py --dataset XRP_USDT-5m --strategy breakout --wf`
- Full research cycle (all strategies × 12 real datasets, GA-optimised walk-forward, ML, RL, challenge): `python3 scripts/run_research.py`

## Timing contract (never break)
Signals at close of bar t → fill at open of bar t+1 via `ExecutionSimulator`; stops/TPs checked on bar t+1 high/low, stop first if both touch.

## Promotion gates (`atm/backtest/validation.py::Gates`)
≥30 OOS trades · OOS compound return >0 · profit factor ≥1.15 · ≥60% positive folds · bootstrap P(mean trade>0) ≥0.90 · holdout >0 · 2× cost stress ≥0. Anything else is REJECTED and stays out of paper trading.

## Interpreting results
Report trial counts (multiple-testing). A positive in-sample result without OOS confirmation is not evidence.
