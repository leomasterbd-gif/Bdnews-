#!/usr/bin/env python3
"""Check Binance public data + Spot Testnet connectivity and (if configured) account access.
Credentials are read from BINANCE_TESTNET_API_KEY / BINANCE_TESTNET_API_SECRET env vars only."""
import json

import _path  # noqa: F401
from atm.exchange.binance import PublicMarketData, SpotTestnetClient
from atm.security.secrets import configured

out = {"secrets_configured": configured()}
for name, fn in [("public_ping", lambda: PublicMarketData(timeout=5, retries=0).ping()),
                 ("public_klines", lambda: len(PublicMarketData(timeout=5, retries=0).klines("BTCUSDT", "5m", 5))),
                 ("testnet_time_offset_ms", lambda: SpotTestnetClient(timeout=5, retries=0).sync_time())]:
    try:
        out[name] = {"ok": True, "value": fn()}
    except Exception as e:  # noqa: BLE001
        out[name] = {"ok": False, "error": f"{e.__class__.__name__}: {str(e)[:120]}"}
c = SpotTestnetClient(timeout=5, retries=0)
if c.has_credentials:
    try:
        c.sync_time()
        bal = c.account().get("balances", [])
        out["testnet_account"] = {"ok": True, "assets": len(bal)}
        out["testnet_test_order"] = {"ok": True, "resp": c.new_order("BTCUSDT", "BUY", 0.0002, test=True)}
    except Exception as e:  # noqa: BLE001
        out["testnet_account"] = {"ok": False, "error": e.__class__.__name__}
else:
    out["testnet_account"] = {"ok": False, "error": "BLOCKED: credentials not configured"}
print(json.dumps(out, indent=1, default=str))
