# Monthly cost report

| item | cost now | notes |
|---|---|---|
| Software (all components) | **$0** | open-source, pinned |
| Market data | **$0** | Binance public data + Spot Testnet are free |
| Telegram | **$0** | |
| GPU | **$0** | not needed (no deep models justified by data size) |
| VPS | **$0 until approved** | 2 vCPU / 4 GB is sufficient; typical market price ≈ $5–12/month — **owner decision** |
| Claude API / agents | **$0 continuous** | No LLM runs in the always-on loop. Subagents are used on demand during development only. |
| **Total committed** | **$0 / month** | Nothing has been purchased. |

Live tracking: `/api/costs` and the "Infrastructure Cost" screen show measured resources (`atm/cost.py`) and the owner's
declared assumptions (`ATM_VPS_MONTHLY_USD`, `ATM_CLAUDE_BUDGET_USD`). Any entry in the `costs` ledger table is recorded with a
category and note; the system has no code path that can spend money.
