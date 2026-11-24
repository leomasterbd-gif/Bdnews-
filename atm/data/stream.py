"""Real-time feeds.

* BinanceKlineStream — WebSocket kline stream with automatic reconnect, exponential
  backoff, heartbeat/stale detection (wss://stream.binance.com:9443 or testnet stream).
* ReplayFeed — replays stored historical bars at a chosen speed. Every bar it emits is
  tagged source='REPLAY' so dashboards never present it as live.
* orderbook_features — imbalance / spread / depth metrics from a depth snapshot.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import AsyncIterator, Iterator

import pandas as pd

log = logging.getLogger(__name__)

LIVE_WS = "wss://stream.binance.com:9443/ws"
TESTNET_WS = "wss://stream.testnet.binance.vision/ws"


@dataclass
class Bar:
    ts: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float
    closed: bool
    source: str  # LIVE_PUBLIC | TESTNET | REPLAY


def parse_kline_msg(msg: dict, source: str) -> Bar | None:
    k = msg.get("k")
    if not k:
        return None
    return Bar(pd.Timestamp(int(k["t"]), unit="ms", tz="UTC"), float(k["o"]), float(k["h"]), float(k["l"]),
               float(k["c"]), float(k["v"]), bool(k["x"]), source)


class BinanceKlineStream:
    def __init__(self, symbol: str, interval: str = "5m", url: str = LIVE_WS, stale_after_s: float = 90.0, source: str = "LIVE_PUBLIC"):
        self.symbol, self.interval, self.url = symbol.lower(), interval, url
        self.stale_after_s, self.source = stale_after_s, source
        self.last_msg = 0.0
        self.reconnects = 0

    @property
    def stale(self) -> bool:
        return self.last_msg == 0 or time.time() - self.last_msg > self.stale_after_s

    async def bars(self) -> AsyncIterator[Bar]:
        import websockets

        backoff = 1.0
        stream = f"{self.url}/{self.symbol}@kline_{self.interval}"
        while True:
            try:
                async with websockets.connect(stream, ping_interval=20, ping_timeout=20, open_timeout=10) as ws:
                    backoff = 1.0
                    while True:
                        raw = await asyncio.wait_for(ws.recv(), timeout=self.stale_after_s)
                        self.last_msg = time.time()
                        b = parse_kline_msg(json.loads(raw), self.source)
                        if b:
                            yield b
            except (asyncio.TimeoutError, OSError, Exception) as e:  # noqa: BLE001 - reconnect on anything
                self.reconnects += 1
                log.warning("kline stream reconnect #%d after %s", self.reconnects, e.__class__.__name__)
                await asyncio.sleep(backoff)
                backoff = min(60.0, backoff * 2)


class ReplayFeed:
    def __init__(self, df: pd.DataFrame, start: int = 0, speed_s: float = 0.0):
        self.df, self.i, self.speed_s = df, start, speed_s

    def __iter__(self) -> Iterator[Bar]:
        for ts, r in self.df.iloc[self.i:].iterrows():
            if self.speed_s:
                time.sleep(self.speed_s)
            yield Bar(ts, r.open, r.high, r.low, r.close, r.volume, True, "REPLAY")


def orderbook_features(depth: dict, levels: int = 20) -> dict:
    bids = [(float(p), float(q)) for p, q in depth.get("bids", [])[:levels]]
    asks = [(float(p), float(q)) for p, q in depth.get("asks", [])[:levels]]
    if not bids or not asks:
        return {"valid": False}
    bb, ba = bids[0][0], asks[0][0]
    mid = (bb + ba) / 2
    bq, aq = sum(q for _, q in bids), sum(q for _, q in asks)
    bn, an = sum(p * q for p, q in bids), sum(p * q for p, q in asks)
    micro = (ba * bids[0][1] + bb * asks[0][1]) / (bids[0][1] + asks[0][1])
    return {"valid": bb < ba, "mid": mid, "spread_bps": 1e4 * (ba - bb) / mid, "imbalance": (bq - aq) / (bq + aq),
            "bid_notional": bn, "ask_notional": an, "microprice_offset_bps": 1e4 * (micro - mid) / mid,
            "top_imbalance": (bids[0][1] - asks[0][1]) / (bids[0][1] + asks[0][1])}
