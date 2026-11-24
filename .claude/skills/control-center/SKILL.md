---
name: control-center
description: Run and extend the owner dashboard (FastAPI + static SPA) and the owner-only Telegram bot. Use for dashboard development and Telegram integration.
---
# control-center

Covers: Dashboard Development · Telegram Integration.

## Commands
- API + dashboard: `ATM_OWNER_TOKEN=<token> python3 -m uvicorn --factory atm.api.server:create_app --host 127.0.0.1 --port 8000`
- Telegram: `TELEGRAM_BOT_TOKEN=... TELEGRAM_OWNER_ID=<numeric id> ATM_OWNER_TOKEN=... python3 -m atm.telegram.bot`

## Rules
Every figure comes from the API; label VIRTUAL / HISTORICAL / REPLAY / EXPERIMENTAL_SHADOW; Bengali default with English toggle; Telegram answers only the numeric owner ID and never sends secrets.
