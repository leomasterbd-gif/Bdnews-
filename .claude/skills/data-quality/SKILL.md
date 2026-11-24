---
name: data-quality
description: Load, resample and verify market data quality (gaps, duplicates, OHLC violations, stale data, abnormal moves). Use for market-data engineering and database tasks.
---
# data-quality

Covers: Market data engineering · Database Management.

## Commands
- `python3 scripts/data_quality.py`
- Datasets and provenance: `data/historical/MANIFEST.json` (real Binance candles from Freqtrade's test fixtures, SHA-256 recorded).
- Resample causally: `atm.data.loader.resample(df, "15m")` (1m,3m,5m,15m,30m,1h,4h).
- Storage: `atm/storage/db.py` (SQLite; schema portable to PostgreSQL). Backups: `scripts/backup.sh`, restore: `scripts/restore.sh <archive>`.
