# Backup & disaster recovery

* **Backup:** `scripts/backup.sh` — online SQLite backup API (consistent while running), plus reports, settings and config; tar.gz + SHA-256; keeps 14. Cron: `17 */6 * * * /opt/atm/scripts/backup.sh` and copy `backups/` off-site (e.g. `rclone`, owner's choice).
* **Restore:** `scripts/restore.sh backups/<ts>.tar.gz` — verifies checksum, keeps `data/atm.db.pre-restore`, verifies the audit hash chain.
* **Reports are reproducible:** everything in `reports/` can be regenerated with `python3 scripts/run_research.py` from the versioned code + `data/historical` (fixed seeds).
* **Automatic restart:** compose `restart: unless-stopped` + healthchecks; WebSocket feeds reconnect with exponential back-off; REST client retries 5xx/network errors and backs off on 418/429.
* **Emergency shutdown:** dashboard EMERGENCY STOP, Telegram `/stop`, or `touch data/KILL`. Positions are flattened (forced exits) and new sessions refuse to start until the owner types RESUME.

## Incident runbook
1. Stop (KILL). 2. `docker compose logs --since 2h > incident.log`. 3. `python3 -c "from atm.storage.db import Store; print(Store().verify_audit_chain())"`. 4. Restore the DB if corrupt. 5. `python3 -m pytest -q`. 6. Write up the cause in `docs/incidents/` before resuming.
