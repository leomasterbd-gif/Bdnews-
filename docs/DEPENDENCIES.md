# Dependency inventory & repository evaluation

## Runtime dependencies (pinned in `requirements.txt`)
| package | version | license | purpose |
|---|---|---|---|
| numpy | 2.5.3 | BSD-3 | numerics |
| pandas | 3.0.5 | BSD-3 | time series |
| scipy | 1.18.1 | BSD-3 | statistics (via sklearn) |
| scikit-learn | 1.9.1 | BSD-3 | logistic regression, random forest, MLP, metrics |
| lightgbm | 4.7.0 | MIT | gradient boosting |
| optuna | 5.1.0 | MIT | TPE hyperparameter search |
| fastapi / starlette | 0.165.0 / 1.7.0 | MIT / BSD-3 | API |
| uvicorn | 0.54.0 | BSD-3 | ASGI server |
| pydantic | 2.13.5 | MIT | (FastAPI) |
| PyYAML | 6.0.3 | MIT | risk config (`safe_load` only) |
| requests | 2.34.2 | Apache-2.0 | REST clients |
| websockets | 17.4 | BSD-3 | kline streams |

Dev: pytest 9.1.1, ruff 0.17.6, bandit 1.9.4, pip-audit 2.10.1. Vulnerability status: see `reports/security_scan.json`.

## Requested repositories — evaluation
| repository | decision | reason |
|---|---|---|
| anthropics/skills | **Pattern adopted** | SKILL.md format/frontmatter used for 11 project skills. No code needed. |
| freqtrade/freqtrade (GPL-3) | **Data only** | Shallow sparse read-only clone of `tests/testdata`; real Binance candles converted with SHA-256 provenance. The bot framework itself overlaps with our engine/risk/API and its GPL-3 license would apply to derivative code — not imported. FreqAI ideas (purged training windows, outlier filters) are reflected in `atm/ml`. |
| ccxt/ccxt | Not adopted (yet) | Only Binance is in scope; the official REST API is small and signing is verified against the docs. CCXT becomes worthwhile for multi-venue arbitrage research. |
| binance/binance-spot-api-docs | **Followed** | Endpoints, weights, HMAC signing example (unit-tested), error codes 418/429. |
| binance/binance-connector-python | Not adopted | A 150-line client with explicit testnet-host lock is easier to audit than a general SDK that can reach production. |
| polakowo/vectorbt | Not adopted | Vectorised fills can't model the independent risk engine in the loop; evaluated conceptually only. Our engine runs a 3k-bar backtest in ~0.1 s, which is fast enough. |
| microsoft/qlib | Not adopted | Equity-research oriented, heavy data pipeline; our dataset is too small to benefit. |
| microsoft/RD-Agent | Not adopted | LLM-driven research loop; our cycle is deterministic by design (cost, reproducibility). Could later propose hypotheses for the registry. |
| optuna/optuna | **Adopted** | `optuna_optimizer` (TPE, seeded). |
| pytorch/pytorch | Not installed | No deep model is justified with ~3k bars/market; avoids ~1 GB dependency. |
| scikit-learn | **Adopted** | baselines and models. |
| dmlc/xgboost | Not adopted | LightGBM covers gradient boosting; two GBM libraries would be redundant. |
| microsoft/LightGBM | **Adopted** | |
| DLR-RM/stable-baselines3 | Not adopted | Needs PyTorch and far more data; tabular Q-learning baseline implemented instead (`atm/ml/rl.py`). |
| kernc/backtesting.py | Inspected only | Wheel downloaded to inspect bundled data (daily BTC/USD); not used. |

Every adopted package came from PyPI with pinned versions; no install scripts from repositories were executed.
