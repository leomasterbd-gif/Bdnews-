---
name: four-hour-challenge
description: Run and interpret the $100 to $200 four-hour quantitative research challenge, including the perfect-foresight upper bound. Use whenever the owner asks about the profit target, doubling money, or session-level outcomes.
---
# four-hour-challenge

## Commands
- Quick run (default params, all datasets): `python3 scripts/run_challenge.py`
- Full (incl. validated params & doubling analysis): part of `python3 scripts/run_research.py` → `reports/challenge.json`

## Method
Every non-overlapping 4h window of every dataset = an independent session with a fresh $100 and fresh risk session. No window is skipped or reset. `oracle_long_only` gives the best possible result with perfect knowledge of future prices (fees included, 100% capital, no risk limits) — the absolute ceiling for spot trading without leverage.

## Reporting rules
State hit-rate, P(loss), median, worst case, max drawdown and fees. If the oracle itself rarely reaches +100%, say plainly that the target is infeasible and present realistic alternatives (e.g. median/percentile session returns). Never raise risk or add leverage to chase the target.
