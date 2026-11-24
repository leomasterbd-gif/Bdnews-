# AI Trading Master

Autonomous quantitative **research & simulation** platform for crypto spot markets.
**Simulation / Binance Spot Testnet only — real-money trading is disabled in code.**
স্বয়ংক্রিয় কোয়ান্ট গবেষণা ও সিমুলেশন প্ল্যাটফর্ম — শুধু ভার্চুয়াল টাকা।

* Real historical Binance candles (12 markets, 5-minute), causal indicators, 11 rule strategies + stat-arb + ensembles
* Event-driven backtester with fees, spread, slippage, latency, partial fills, precision, min-notional, rejects, network failures
* Independent deterministic risk engine with code-level hard ceilings, halts, kill switch
* GA + Optuna optimisation on training data only → walk-forward → holdout → bootstrap → Monte Carlo → 2× cost stress → promotion gates → versioned registry
* ML (logistic, random forest, MLP, LightGBM) and RL (Q-learning) vs simple baselines with purged walk-forward
* "$100 → $200 in 4 hours" challenge with a perfect-foresight upper bound
* Owner-only FastAPI control center + bilingual (বাংলা/English) dashboard, Telegram bot, hash-chained audit log
* 50 Claude Code subagent definitions, 11 skills with working scripts, guard hooks

## Quick start
```bash
pip install -r requirements-dev.txt
python3 -m pytest -q                         # tests
python3 scripts/run_research.py              # full research cycle -> reports/
ATM_OWNER_TOKEN=change-me python3 -m uvicorn --factory atm.api.server:create_app --port 8000
```
Read first: `reports/RESEARCH_REPORT.md` (results), `docs/AUDIT.md` (requirement status), `docs/OWNER_GUIDE_BN.md` (owner guide in Bengali).

Docs: [Architecture](docs/ARCHITECTURE.md) · [Security](docs/SECURITY.md) · [Deployment](docs/DEPLOYMENT.md) · [Backup & recovery](docs/BACKUP_RECOVERY.md) · [Agents](docs/AGENTS.md) · [Skills](docs/SKILLS.md) · [Dependencies & repo evaluation](docs/DEPENDENCIES.md) · [Costs](docs/COSTS.md)

**No guarantee of profit. Simulated results are not real financial performance.**
