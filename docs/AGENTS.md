# Agent inventory

50 Claude Code subagent definitions live in `.claude/agents/`. They are **on-demand** engineering/research specialists, not
always-running processes: continuous work (market data, risk, execution, research cycle, paper trading) is deterministic
Python, which is cheaper, reproducible and auditable. Every agent inherits the same non-negotiable rules (no live trading,
no edits to risk/security files — enforced by a hook — untrusted external content, no fabricated results).

Model choice: `inherit` (strongest) for architecture, risk, security, ML and audit roles; `sonnet` for most specialists;
`haiku` for cheap text tasks (news/sentiment/economic tagging). Read-only agents cannot edit files.

Used in this build: a **Dashboard Engineer** subagent built `dashboard/`, and an **Independent Code Auditor** subagent reviewed the code
(see docs/AUDIT.md).

| agent | role | model | access | owns |
|---|---|---|---|---|
| anomaly-detection | Anomaly Detection Agent | sonnet | read-only | abnormal-move filter in engine |
| arbitrage-simulation | Arbitrage Simulation Agent | sonnet | read-only | simulation only |
| backend | Backend Engineer | sonnet | read/write | atm/api/server.py |
| backtesting | Historical Backtesting Agent | sonnet | read/write | atm/backtest/engine.py |
| binance-integration | Binance API Integration Engineer | inherit | read/write | atm/exchange/binance.py |
| breakout-research | Breakout Research Agent | sonnet | read/write | breakout, vol_expansion |
| capital-preservation | Capital Preservation Agent | sonnet | read-only | drawdown/session limits |
| chief-trading-director | Chief AI Trading Director | inherit | read/write | overall roadmap; docs/AUDIT.md |
| code-auditor | Independent Code Auditor | inherit | read-only | whole repo (read-only) |
| cybersecurity | Cybersecurity Engineer | inherit | read-only | atm/security/, docs/SECURITY.md |
| dashboard | Dashboard Engineer | sonnet | read/write | dashboard/ |
| database | Database Engineer | sonnet | read/write | atm/storage/db.py |
| deep-learning | Deep Learning Research Agent | inherit | read-only | (not trained) |
| devops | DevOps Engineer | sonnet | read/write | docker/, .github/workflows/ |
| economic-intelligence | Economic Intelligence Agent | haiku | read-only | event calendar (planned) |
| execution-sim | Execution Simulation Engineer | sonnet | read/write | atm/backtest/execution.py |
| feature-engineering | Feature Engineering Agent | sonnet | read/write | atm/features/engineering.py |
| forecasting | Time Series Forecasting Agent | sonnet | read-only | forward labels, horizons |
| forward-testing | Forward Testing Agent | sonnet | read-only | atm/exchange/paper.py |
| fundamental-analysis | Fundamental Analysis Agent | sonnet | read-only | docs/research notes |
| genetic-algorithm | Genetic Algorithm Research Agent | sonnet | read-only | genetic_optimizer |
| liquidity-analysis | Liquidity Analysis Agent | sonnet | read-only | risk liquidity limits, execution participation |
| market-data | Market Data Engineer | sonnet | read/write | atm/data/ |
| market-intelligence | Market Intelligence Agent | sonnet | read-only | atm/api/server.py /api/market |
| market-making-sim | Market Making Simulation Agent | sonnet | read-only | simulation only |
| mean-reversion | Mean Reversion Agent | sonnet | read/write | mean_reversion, vwap_reversion |
| microstructure | Market Microstructure Agent | inherit | read-only | atm/backtest/execution.py |
| ml-engineer | Machine Learning Engineer | inherit | read/write | atm/ml/models.py |
| momentum-research | Momentum Research Agent | sonnet | read/write | momentum, macd_stochrsi |
| monte-carlo | Monte Carlo Simulation Agent | sonnet | read-only | monte_carlo_trades, bootstrap |
| news-intelligence | News Intelligence Agent | haiku | read-only | atm/news/sentiment.py |
| order-book | Order Book Intelligence Agent | sonnet | read/write | atm/data/stream.py orderbook_features |
| performance | Performance Optimization Agent | sonnet | read/write | hot loops in engine/optimizer |
| portfolio-optimization | Portfolio Optimization Agent | sonnet | read-only | exposure limits |
| price-action | Price Action Analysis Agent | sonnet | read-only | atm/strategies/library.py (breakout, pullback) |
| qa | Quality Assurance Agent | sonnet | read/write | tests/ |
| quant-research | Quantitative Research Agent | inherit | read/write | atm/strategies, atm/backtest/validation.py |
| regime-detection | Market Regime Detection Agent | sonnet | read/write | atm/features/regime.py |
| research-supervisor | Autonomous Research Supervisor | inherit | read-only | atm/research/cycle.py |
| risk-manager | Independent Risk Management Agent | inherit | read-only | atm/risk/ |
| rl-research | Reinforcement Learning Research Agent | sonnet | read/write | atm/ml/rl.py |
| scalping-research | Scalping Research Agent | sonnet | read-only | 1m/5m simulations |
| sentiment-analysis | Sentiment Analysis Agent | haiku | read-only | lexicon sentiment |
| stat-arb | Statistical Arbitrage Research Agent | sonnet | read/write | pair_relative |
| strategy-discovery | Strategy Discovery Agent | inherit | read/write | atm/strategies/library.py |
| strategy-optimization | Strategy Optimization Agent | sonnet | read/write | atm/research/optimizer.py |
| technical-analysis | Technical Analysis Agent | sonnet | read/write | atm/features/indicators.py |
| trend-following | Trend Following Agent | sonnet | read/write | ema_trend, ichimoku_trend |
| volatility-analysis | Volatility Analysis Agent | sonnet | read-only | ATR, realized vol, vol_expansion |
| volume-analysis | Volume Analysis Agent | sonnet | read-only | OBV, VWAP, volume filters |
