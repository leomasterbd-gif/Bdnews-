#!/usr/bin/env bash
# Online, consistent backup of the SQLite DB + reports + settings. Keeps the newest 14.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${ATM_BACKUP_DIR:-$ROOT/backups}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$DEST/$TS"
python3 - "$ROOT/data/atm.db" "$DEST/$TS/atm.db" <<'PY'
import sqlite3, sys
src = sqlite3.connect(sys.argv[1]); dst = sqlite3.connect(sys.argv[2])
src.backup(dst); dst.close(); src.close()
PY
cp -a "$ROOT/reports" "$DEST/$TS/" 2>/dev/null || true
cp -a "$ROOT/data/settings.json" "$DEST/$TS/" 2>/dev/null || true
cp -a "$ROOT/config" "$DEST/$TS/"
(cd "$DEST" && tar czf "$TS.tar.gz" "$TS" && rm -rf "$TS" && sha256sum "$TS.tar.gz" > "$TS.tar.gz.sha256")
ls -1t "$DEST"/*.tar.gz | tail -n +15 | xargs -r rm -f
echo "backup: $DEST/$TS.tar.gz"
