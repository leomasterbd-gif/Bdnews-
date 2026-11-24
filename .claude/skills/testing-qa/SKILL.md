---
name: testing-qa
description: Run and extend the automated test-suite and performance checks. Use for automated testing, QA and performance-engineering tasks.
---
# testing-qa

Covers: Automated Testing · Performance Engineering · Python Development.

## Commands
- `python3 -m pytest -q` (or `python3 scripts/run_tests.py` to also write `reports/test_results.json`)
- Lint: `ruff check atm tests scripts`

## Required tests for any change
Look-ahead (`tests/test_no_lookahead.py`), risk invariants (`tests/test_risk.py`), execution realism (`tests/test_backtest.py`), security (`tests/test_security_exchange.py`), API/Telegram (`tests/test_app.py`).
