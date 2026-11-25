#!/usr/bin/env python3
"""Download & checksum-verify Binance public spot 5m klines. Usage:
python3 scripts/fetch_binance_archive.py --symbols BTCUSDT ETHUSDT --months 24"""
import argparse
import json

import _path  # noqa: F401
from atm.data.archive import fetch

ap = argparse.ArgumentParser()
ap.add_argument("--symbols", nargs="+", default=["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "BNBUSDT"])
ap.add_argument("--interval", default="5m")
ap.add_argument("--months", type=int, default=24)
ap.add_argument("--last-month", default=None)
a = ap.parse_args()
for s in a.symbols:
    m = fetch(s, a.interval, a.months, a.last_month)
    print(json.dumps({k: m[k] for k in ("dataset", "rows", "start", "end")} | {"missing": len(m["missing"])}), flush=True)
