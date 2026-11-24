# Security

## Controls implemented
| Area | Control | Where |
|---|---|---|
| Real money | `live_trading_enabled: true` is rejected at load; order client refuses non-testnet hosts; no withdrawal code exists | `atm/risk/limits.py`, `atm/exchange/binance.py`, tests |
| Secrets | Env vars only (`docker/.env`, chmod 600, git-ignored); never returned by API, never sent to Telegram, redacted in logs; research code never receives them | `atm/security/secrets.py` |
| Auth | Owner bearer token, constant-time comparison, login limited to 5/min/IP, WebSocket auth on first message | `atm/api/server.py` |
| Telegram | Only the approved numeric owner ID is answered; others are ignored and audited | `atm/telegram/bot.py` |
| Web | CSP `default-src 'self'`, no inline scripts, X-Frame-Options DENY, nosniff, no-referrer, no-store on API; nginx TLS + HSTS + rate-limit; OpenAPI docs disabled | server, `docker/nginx.conf` |
| Audit | Append-only (SQL triggers) SHA-256 hash-chained log of logins, settings, stops, registrations | `atm/storage/db.py` |
| Prompt injection | External text cleaned, length-limited, flagged; never used as instructions or config | `atm/security/sanitize.py` |
| Agent guardrails | PreToolUse hook blocks edits to risk/security files and "enable live trading" commands; permission denies for secret files | `.claude/` |
| Containers | non-root user, read-only FS, `cap_drop: ALL`, `no-new-privileges`, healthchecks | `docker/` |
| Supply chain | Pinned requirements; `pip-audit` + `bandit` in CI and `scripts/security_scan.py`; vendored third-party content limited to data files with SHA-256 provenance | |

## Third-party repository review
Freqtrade was cloned read-only (shallow, sparse: `tests/testdata` only). No code from it is executed or imported; only `.feather` candle files were converted to CSV with hashes recorded in `data/historical/MANIFEST.json`. `backtesting.py` was downloaded as a wheel for inspection only, not installed.

## Real-money enablement policy
Not possible by configuration. It would require a code change reviewed by the owner plus: legal eligibility in the owner's jurisdiction, exchange KYC, a strategy validated on ≥6 months of out-of-sample and ≥3 months of forward testing, and explicit written authorisation. Geographic restrictions must never be bypassed.
