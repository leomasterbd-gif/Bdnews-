# Skill inventory

Project skills in `.claude/skills/*/SKILL.md`. Each points to **working scripts** in `scripts/` and to tested modules — they are
procedures, not just descriptions.

| skill | requested topics covered | description |
|---|---|---|
| `binance-integration` | Binance API Integration · WebSocket Engineering. | Work with Binance public market data, WebSocket streams and the Spot Testnet signed REST client. Use for Binance API integration and WebSock… |
| `control-center` | Dashboard Development · Telegram Integration. | Run and extend the owner dashboard (FastAPI + static SPA) and the owner-only Telegram bot. Use for dashboard development and Telegram integr… |
| `data-quality` | Market data engineering · Database Management. | Load, resample and verify market data quality (gaps, duplicates, OHLC violations, stale data, abnormal moves). Use for market-data engineeri… |
| `four-hour-challenge` | — | Run and interpret the $100 to $200 four-hour quantitative research challenge, including the perfect-foresight upper bound. Use whenever the … |
| `ml-research` | Machine Learning · Deep Learning · Reinforcement Learning · Feature Engineering · Financial Data Science · Hyperparameter Optimization. | Machine-learning research with purged walk-forward evaluation against simple baselines (logistic regression, random forest, MLP, LightGBM, t… |
| `ops-deploy` | Docker and Linux · DevOps · Incident Recovery. | Deploy, operate, back up and recover the system with Docker Compose, Nginx, Prometheus and Grafana on a Linux VPS. Use for Docker/Linux, Dev… |
| `quant-backtesting` | Backtesting · Forward Testing · Walk-Forward Optimization · Monte Carlo Simulation · Strategy Validation · Probability and Statistics · Financial Mathematics. | Run realistic backtests, walk-forward validation, bootstrap and Monte Carlo analysis for AI Trading Master strategies. Use for backtesting, … |
| `risk-management` | Risk Management · Portfolio Management · Capital Preservation · Financial Regulatory Compliance. | Inspect and explain the deterministic risk engine, limits, hard ceilings, halts and kill switch. Use for risk management, portfolio/exposure… |
| `security-audit` | Cybersecurity · API Security · Code Auditing · Supply-chain security. | Run security scans and audits (bandit, pip-audit, secret scan, policy checks, audit-chain verification). Use for cybersecurity, API security… |
| `strategy-research` | Quantitative Finance · Cryptocurrency Market Research · Algorithmic Trading · Technical Analysis · Market Microstructure · Time Series Analysis. | Design, add and evaluate trading strategies (momentum, trend, mean reversion, breakout, pullback, volatility, VWAP, Ichimoku, regime-adaptiv… |
| `testing-qa` | Automated Testing · Performance Engineering · Python Development. | Run and extend the automated test-suite and performance checks. Use for automated testing, QA and performance-engineering tasks.… |

Topics without a dedicated skill: *Python Development* (CLAUDE.md + testing-qa), *Financial Regulatory Compliance*
(risk-management + docs/SECURITY.md real-money policy), *Incident Recovery* (ops-deploy + docs/BACKUP_RECOVERY.md).

Scripts: `run_research.py`, `backtest_one.py`, `run_challenge.py`, `run_ml.py`, `risk_check.py`, `testnet_check.py`,
`data_quality.py`, `security_scan.py`, `run_tests.py`, `backup.sh`, `restore.sh`.
