# Deployment (Linux VPS)

Requirements: 2 vCPU / 4 GB RAM / 20 GB disk is enough (research cycle uses ~4 cores for ~20 min; set `--workers 2` on small VPSs). No GPU needed. **Nothing is purchased without owner approval.**

```bash
git clone <your private repo> atm && cd atm
cp docker/env.example docker/.env && chmod 600 docker/.env && nano docker/.env   # fill on the server only
# TLS certs into docker/certs/ (e.g. certbot) — or put the API behind an SSH tunnel and skip nginx
docker compose -f docker/docker-compose.yml up -d --build                     # api + research + nginx
docker compose -f docker/docker-compose.yml --profile telegram up -d          # optional Telegram bot
docker compose -f docker/docker-compose.yml --profile monitoring up -d        # optional Prometheus/Grafana
curl -s http://127.0.0.1:8000/api/health
```

Without Docker:
```bash
pip install -r requirements.txt
export ATM_OWNER_TOKEN=$(python3 -c "import secrets;print(secrets.token_urlsafe(32))")
python3 scripts/run_research.py
python3 -m uvicorn --factory atm.api.server:create_app --host 127.0.0.1 --port 8000
```

## Network allow-list the server needs
`data-api.binance.vision`, `testnet.binance.vision`, `stream.binance.com` (WS), `stream.testnet.binance.vision` (WS), `api.telegram.org` (bot), RSS hosts (optional).

## Hardening checklist
UFW allow 22/443 only · SSH keys only, no root login · unattended-upgrades · fail2ban · `docker/.env` 600 · backups via cron (`docs/BACKUP_RECOVERY.md`).

## Updates
`git pull && python3 -m pytest -q && docker compose up -d --build` — never deploy with failing tests.
