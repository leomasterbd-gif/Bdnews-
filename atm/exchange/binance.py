"""Binance clients.

* PublicMarketData — unauthenticated public REST market data (klines, depth, ticker).
* SpotTestnetClient — HMAC-SHA256 signed REST client that can ONLY talk to the Spot
  Testnet (https://testnet.binance.vision). The base URL is fixed; any attempt to point it
  at a production host raises. There is no withdrawal method anywhere in this codebase.

Both use a token-bucket rate limiter, honour Retry-After / 418 bans, and back off on errors.
Endpoints and signing follow https://github.com/binance/binance-spot-api-docs.
"""
from __future__ import annotations

import hashlib
import hmac
import threading
import time
import urllib.parse
from dataclasses import dataclass

import requests

from ..security.secrets import get_secret, redact

TESTNET_BASE = "https://testnet.binance.vision"
PUBLIC_BASES = ("https://data-api.binance.vision", "https://api.binance.com")
FORBIDDEN_HOSTS = ("api.binance.com", "api1.binance.com", "api2.binance.com", "api3.binance.com", "api4.binance.com", "api-gcp.binance.com")


class ExchangeError(RuntimeError):
    pass


def hmac_signature(secret: str, query_string: str) -> str:
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()


class RateLimiter:
    """Token bucket on request weight (Binance spot: 6000 weight/min; we use a conservative budget)."""

    def __init__(self, capacity: float = 1200, per_seconds: float = 60.0):
        self.capacity, self.rate = capacity, capacity / per_seconds
        self.tokens, self.t = capacity, time.monotonic()
        self.lock = threading.Lock()
        self.banned_until = 0.0

    def acquire(self, weight: float = 1.0) -> float:
        with self.lock:
            now = time.monotonic()
            if now < self.banned_until:
                raise ExchangeError(f"rate-limit ban active for {self.banned_until - now:.0f}s")
            self.tokens = min(self.capacity, self.tokens + (now - self.t) * self.rate)
            self.t = now
            wait = 0.0 if self.tokens >= weight else (weight - self.tokens) / self.rate
            self.tokens -= weight
        if wait:
            time.sleep(wait)
        return wait

    def ban(self, seconds: float) -> None:
        with self.lock:
            self.banned_until = time.monotonic() + seconds


@dataclass
class Health:
    ok: bool = False
    last_ok: float = 0.0
    last_error: str = ""
    latency_ms: float = 0.0
    consecutive_failures: int = 0
    server_time_offset_ms: float = 0.0


class _Base:
    def __init__(self, base: str, session: requests.Session | None = None, limiter: RateLimiter | None = None,
                 timeout: float = 10.0, retries: int = 3):
        self.base = base.rstrip("/")
        self.s = session or requests.Session()
        self.lim = limiter or RateLimiter()
        self.timeout, self.retries = timeout, retries
        self.health = Health()

    def _request(self, method: str, path: str, params: dict | None = None, weight: float = 1, headers: dict | None = None, signed_qs: str | None = None):
        url = f"{self.base}{path}"
        last = None
        for attempt in range(self.retries + 1):
            self.lim.acquire(weight)
            t = time.monotonic()
            try:
                if signed_qs is not None:
                    r = self.s.request(method, f"{url}?{signed_qs}", headers=headers, timeout=self.timeout)
                else:
                    r = self.s.request(method, url, params=params, headers=headers, timeout=self.timeout)
            except requests.RequestException as e:
                last = f"network: {e.__class__.__name__}"
                self._fail(last)
                time.sleep(min(8, 0.5 * 2 ** attempt))
                continue
            self.health.latency_ms = 1000 * (time.monotonic() - t)
            if r.status_code in (418, 429):
                ra = float(r.headers.get("Retry-After", 60))
                self.lim.ban(ra)
                self._fail(f"HTTP {r.status_code} rate limited, retry after {ra}s")
                raise ExchangeError(f"rate limited ({r.status_code}); backing off {ra}s")
            if r.status_code >= 500:
                last = f"HTTP {r.status_code}"
                self._fail(last)
                time.sleep(min(8, 0.5 * 2 ** attempt))
                continue
            if r.status_code >= 400:
                self._fail(f"HTTP {r.status_code}")
                raise ExchangeError(redact(f"HTTP {r.status_code}: {r.text[:300]}"))
            self.health.ok, self.health.last_ok, self.health.consecutive_failures = True, time.time(), 0
            return r.json()
        raise ExchangeError(redact(f"request failed after retries: {last}"))

    def _fail(self, msg: str) -> None:
        self.health.ok = False
        self.health.last_error = redact(msg)
        self.health.consecutive_failures += 1


class PublicMarketData(_Base):
    def __init__(self, base: str = PUBLIC_BASES[0], **kw):
        super().__init__(base, **kw)

    def ping(self) -> bool:
        self._request("GET", "/api/v3/ping")
        return True

    def server_time(self) -> int:
        return int(self._request("GET", "/api/v3/time")["serverTime"])

    def klines(self, symbol: str, interval: str, limit: int = 500, start_ms: int | None = None, end_ms: int | None = None) -> list:
        p = {"symbol": symbol, "interval": interval, "limit": min(limit, 1000)}
        if start_ms:
            p["startTime"] = start_ms
        if end_ms:
            p["endTime"] = end_ms
        return self._request("GET", "/api/v3/klines", p, weight=2)

    def depth(self, symbol: str, limit: int = 100) -> dict:
        return self._request("GET", "/api/v3/depth", {"symbol": symbol, "limit": limit}, weight=5)

    def book_ticker(self, symbol: str) -> dict:
        return self._request("GET", "/api/v3/ticker/bookTicker", {"symbol": symbol}, weight=2)

    def exchange_info(self, symbol: str) -> dict:
        return self._request("GET", "/api/v3/exchangeInfo", {"symbol": symbol}, weight=20)


class SpotTestnetClient(_Base):
    """Signed Spot Testnet client. Production hosts are refused unconditionally."""

    def __init__(self, api_key: str | None = None, api_secret: str | None = None, base: str = TESTNET_BASE, recv_window: int = 5000, **kw):
        u = urllib.parse.urlparse(base)
        host = u.hostname or ""
        if u.scheme != "https" or host != "testnet.binance.vision" or u.username or u.password or host in FORBIDDEN_HOSTS:
            raise ExchangeError("SpotTestnetClient refuses non-testnet hosts; real-money trading is disabled")
        super().__init__(base, **kw)
        self._key = api_key if api_key is not None else get_secret("BINANCE_TESTNET_API_KEY")
        self._secret = api_secret if api_secret is not None else get_secret("BINANCE_TESTNET_API_SECRET")
        self.recv_window = recv_window
        self.time_offset = 0

    def __setattr__(self, name, value):
        if name == "base" and "base" in self.__dict__:
            raise ExchangeError("base URL is immutable")
        super().__setattr__(name, value)

    def __repr__(self) -> str:  # never print credentials
        return f"SpotTestnetClient(base={self.base!r}, credentials={'set' if self._key else 'missing'})"

    @property
    def has_credentials(self) -> bool:
        return bool(self._key and self._secret)

    def sync_time(self) -> int:
        st = int(self._request("GET", "/api/v3/time")["serverTime"])
        self.time_offset = st - int(time.time() * 1000)
        self.health.server_time_offset_ms = self.time_offset
        return self.time_offset

    def sign(self, params: dict) -> str:
        if not self.has_credentials:
            raise ExchangeError("Testnet credentials not configured (set BINANCE_TESTNET_API_KEY / _SECRET in the server env)")
        p = {**params, "timestamp": int(time.time() * 1000) + self.time_offset, "recvWindow": self.recv_window}
        qs = urllib.parse.urlencode(p)
        return f"{qs}&signature={hmac_signature(self._secret, qs)}"

    def _signed(self, method: str, path: str, params: dict, weight: float = 1):
        return self._request(method, path, headers={"X-MBX-APIKEY": self._key}, weight=weight, signed_qs=self.sign(params))

    def account(self) -> dict:
        return self._signed("GET", "/api/v3/account", {"omitZeroBalances": "true"}, weight=20)

    def new_order(self, symbol: str, side: str, qty: float, order_type: str = "MARKET", price: float | None = None,
                  client_id: str | None = None, test: bool = False) -> dict:
        side = side.upper()
        if side not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")
        p = {"symbol": symbol, "side": side, "type": order_type, "quantity": f"{qty:.8f}".rstrip("0").rstrip("."), "newOrderRespType": "FULL"}
        if order_type == "LIMIT":
            p.update(price=f"{price:.8f}".rstrip("0").rstrip("."), timeInForce="GTC")
        if client_id:
            p["newClientOrderId"] = client_id
        return self._signed("POST", "/api/v3/order/test" if test else "/api/v3/order", p)

    def get_order(self, symbol: str, client_id: str) -> dict:
        return self._signed("GET", "/api/v3/order", {"symbol": symbol, "origClientOrderId": client_id}, weight=4)

    def open_orders(self, symbol: str) -> list:
        return self._signed("GET", "/api/v3/openOrders", {"symbol": symbol}, weight=6)

    def cancel_all(self, symbol: str) -> list:
        return self._signed("DELETE", "/api/v3/openOrders", {"symbol": symbol})

    def reconcile(self, symbol: str, local_orders: dict[str, dict]) -> dict:
        """Compare locally tracked orders with exchange state; return mismatches."""
        mismatches = {}
        for cid, local in local_orders.items():
            try:
                remote = self.get_order(symbol, cid)
            except ExchangeError as e:
                mismatches[cid] = {"error": str(e)}
                continue
            if remote.get("status") != local.get("status") or float(remote.get("executedQty", 0)) != float(local.get("executedQty", 0)):
                mismatches[cid] = {"local": local, "remote": {k: remote.get(k) for k in ("status", "executedQty", "cummulativeQuoteQty")}}
        return mismatches
