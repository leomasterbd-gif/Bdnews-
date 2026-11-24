# Architecture

```
                 ┌──────────────────────── deterministic, always-on ─────────────────────────┐
 Binance public  │  atm/data (REST klines, WS kline stream, depth)  ──►  quality / stale checks │
 data / Testnet ─┼─►      │                                                                     │
 (when allowed)  │        ▼                                                                     │
 stored history ─┼─► features (causal indicators, regime, ML matrix)                            │
 (real candles)  │        │                                                                     │
                 │        ▼                                                                     │
                 │  strategies ──signals──► RISK ENGINE (independent, immutable limits) ──►     │
                 │                          execution simulator  ──►  portfolio / paper trader  │
                 │                          (or Spot Testnet client, testnet host only)         │
                 │        │                                                                     │
                 │        ▼                                                                     │
                 │  research cycle: GA/Optuna (train only) → walk-forward → holdout → bootstrap │
                 │  → Monte Carlo → 2× cost stress → gates → versioned registry → challenge     │
                 └───────────────┬──────────────────────────────────────────────────────────────┘
                                 │ SQLite (registry, experiments, paper trades, costs, hash-chained audit)
                                 ▼
                 FastAPI (owner token, CSP, rate-limited login)  ──►  dashboard SPA (bn/en)
                         │                                        ──►  Telegram bot (owner ID only)
                         └── /metrics ──► Prometheus ──► Grafana
   On-demand only: Claude Code subagents (.claude/agents) for engineering/research tasks.
```

## Design decisions (and evidence)
| Decision | Why |
|---|---|
| Own event-driven engine instead of Freqtrade/VectorBT at runtime | Needed exact control over timing contract, partial fills, rejects, risk-engine-in-the-loop, and per-session $100 resets. Freqtrade (GPL-3) is a full bot framework — adopting it would duplicate the risk/API layers; VectorBT's vectorised fills can't express the independent risk engine. Freqtrade's **test fixtures** are used as real data. |
| SQLite, not PostgreSQL/Redis | Single node, low write rate, $0. Schema is portable; compose can add Postgres later. Redis adds nothing until there are multiple workers needing a shared cache. |
| Static SPA without JS libraries | Strict CSP (`script-src 'self'`), no supply-chain risk from CDNs, works offline. |
| LightGBM + scikit-learn, no PyTorch | ~3k bars per USDT market cannot support deep sequence models; PyTorch would add ~1 GB and attack surface for no measurable benefit. Re-evaluate with ≥1 year of 1m data. |
| GA + Optuna optimisers, both on training slices only | Optuna TPE is more sample-efficient; GA is dependency-free and robust on integer/discrete spaces. Trial counts are logged to disclose multiple testing. |
| LLM agents on demand, not continuous | Market processing, risk, execution and research are deterministic Python — cheaper, reproducible and auditable. |

## Timing contract
Signal at close of bar *t* → order at open of bar *t+1* (+spread, slippage ∝ range·√participation, latency) → stop/TP evaluated on bar *t+1* range with stop priority. Gaps through stops fill at the open.
