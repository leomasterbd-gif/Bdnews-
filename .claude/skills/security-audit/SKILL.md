---
name: security-audit
description: Run security scans and audits (bandit, pip-audit, secret scan, policy checks, audit-chain verification). Use for cybersecurity, API security, supply-chain, code auditing and prompt-injection questions.
---
# security-audit

Covers: Cybersecurity · API Security · Code Auditing · Supply-chain security.

## Commands
- `python3 scripts/security_scan.py` → `reports/security_scan.json`
- Audit chain: `python3 -c "from atm.storage.db import Store; print(Store().verify_audit_chain())"`

## Checklist
Owner bearer token (constant-time compare, login rate-limit) · strict CSP · no secrets in API/Telegram/logs (`redact`) · external text through `atm/security/sanitize.py` · append-only hash-chained audit log · pinned dependencies · third-party repos reviewed before use (only Freqtrade test fixtures are vendored, as data).
