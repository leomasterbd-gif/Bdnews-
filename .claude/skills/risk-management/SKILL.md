---
name: risk-management
description: Inspect and explain the deterministic risk engine, limits, hard ceilings, halts and kill switch. Use for risk management, portfolio/exposure limits, capital preservation and financial regulatory-compliance questions.
---
# risk-management

Covers: Risk Management · Portfolio Management · Capital Preservation · Financial Regulatory Compliance.

## Commands
- `python3 scripts/risk_check.py [path.yaml]` — validates limits against the code-level ceilings.
- `python3 -m pytest tests/test_risk.py -q`

## Rules
- Limits live in `config/risk_limits.yaml` (owner-only; a hook blocks agent edits). `atm/risk/limits.py` rejects values above the hard ceilings, leverage, shorting and `live_trading_enabled: true`.
- A risk rejection always overrides strategy signals. No martingale, averaging down or loss-recovery sizing exists or may be added.
- Compliance: simulation/testnet only. Real-money trading needs legal eligibility in the owner's jurisdiction, exchange KYC, independent validation and explicit owner authorisation — never bypass geo-restrictions.
