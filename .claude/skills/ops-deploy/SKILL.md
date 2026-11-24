---
name: ops-deploy
description: Deploy, operate, back up and recover the system with Docker Compose, Nginx, Prometheus and Grafana on a Linux VPS. Use for Docker/Linux, DevOps, monitoring and incident-recovery tasks.
---
# ops-deploy

Covers: Docker and Linux · DevOps · Incident Recovery.

See `docs/DEPLOYMENT.md` and `docs/BACKUP_RECOVERY.md`.

## Commands
- `docker compose -f docker/docker-compose.yml up -d --build`
- Health: `curl -s localhost:8000/api/health`
- Emergency stop without the UI: `touch data/KILL` (the paper trader refuses to start while it exists) or Telegram `/stop`.

## Incident runbook (short)
1. Stop trading (KILL). 2. Capture logs (`docker compose logs --since 1h`). 3. Verify audit chain. 4. Restore from the latest backup if the DB is corrupt. 5. Re-run tests before resuming.
