#!/usr/bin/env bash
# Restore from a backup archive created by backup.sh (verifies checksum, verifies the audit chain).
set -euo pipefail
ARCHIVE="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
sha256sum -c "$ARCHIVE.sha256" --status || { echo "checksum mismatch"; exit 1; }
TMP="$(mktemp -d)"; tar xzf "$ARCHIVE" -C "$TMP"; D="$(ls "$TMP")"
[ -f "$ROOT/data/atm.db" ] && cp "$ROOT/data/atm.db" "$ROOT/data/atm.db.pre-restore"
cp "$TMP/$D/atm.db" "$ROOT/data/atm.db"
cp -a "$TMP/$D/reports/." "$ROOT/reports/" 2>/dev/null || true
cd "$ROOT" && python3 -c "from atm.storage.db import Store; print('audit chain valid/entries:', Store().verify_audit_chain())"
rm -rf "$TMP"
