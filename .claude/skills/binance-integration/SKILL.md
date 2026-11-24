---
name: binance-integration
description: Work with Binance public market data, WebSocket streams and the Spot Testnet signed REST client. Use for Binance API integration and WebSocket engineering tasks.
---
# binance-integration

Covers: Binance API Integration · WebSocket Engineering.

## Commands
- `python3 scripts/testnet_check.py` — connectivity, clock offset, account & test order (only if credentials are configured).

## Facts
- Client: `atm/exchange/binance.py`. `SpotTestnetClient` is hard-wired to `https://testnet.binance.vision` and raises for any other host. No withdrawal code exists.
- Signing: HMAC-SHA256 of the exact query string (verified against the official docs example in `tests/test_security_exchange.py`).
- Rate limits: token bucket + Retry-After handling; HTTP 418/429 trigger a ban/back-off.
- Streams: `atm/data/stream.py::BinanceKlineStream` reconnects with exponential back-off and flags stale data.
- Credentials: only `BINANCE_TESTNET_API_KEY` / `BINANCE_TESTNET_API_SECRET` environment variables on the server. Never ask for them in chat; never print them.
