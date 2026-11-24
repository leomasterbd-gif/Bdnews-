"""News intelligence: RSS fetch (when network policy allows) + deterministic lexicon
sentiment. All text is untrusted; it can only produce a bounded numeric score and flags,
never instructions. Sentiment is a *research feature*, not a trading trigger by itself."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET  # nosec B405 - see parse_rss guard

import requests

from ..security.sanitize import as_untrusted

DEFAULT_FEEDS = ("https://www.coindesk.com/arc/outboundfeeds/rss/", "https://cointelegraph.com/rss")
POS = {"surge", "rally", "gain", "gains", "bullish", "record", "approval", "approved", "adoption", "inflow", "inflows",
       "upgrade", "partnership", "soar", "soars", "rebound", "breakout", "beat", "growth", "launch"}
NEG = {"hack", "hacked", "exploit", "crash", "plunge", "bearish", "ban", "lawsuit", "sec", "outflow", "outflows",
       "liquidation", "liquidations", "fraud", "selloff", "sell-off", "drop", "drops", "fall", "falls", "fear", "delist", "probe"}
NEGATORS = {"not", "no", "never", "without"}


def score(text: str) -> float:
    toks = re.findall(r"[a-z\-]+", text.lower())
    s = 0
    for i, t in enumerate(toks):
        v = 1 if t in POS else -1 if t in NEG else 0
        if v and i > 0 and toks[i - 1] in NEGATORS:
            v = -v
        s += v
    return max(-1.0, min(1.0, s / max(3, len(toks) ** 0.5)))


def parse_rss(xml_text: str, source: str) -> list[dict]:
    items = []
    # Refuse DTDs/entities outright (XXE / entity-expansion); RSS never needs them.
    head = xml_text[:4096].upper()
    if "<!DOCTYPE" in head or "<!ENTITY" in xml_text.upper():
        return items
    try:
        root = ET.fromstring(xml_text)  # nosec B314 - DTD/entities rejected above
    except ET.ParseError:
        return items
    for it in root.iter("item"):
        title = (it.findtext("title") or "")
        desc = (it.findtext("description") or "")
        u = as_untrusted(f"{title}. {desc}", source)
        u["title"] = as_untrusted(title, source)["text"][:200]
        u["sentiment"] = score(u["text"])
        u["published"] = it.findtext("pubDate")
        items.append(u)
    return items


def fetch_news(feeds=DEFAULT_FEEDS, timeout=8) -> dict:
    out, errors = [], []
    for f in feeds:
        try:
            r = requests.get(f, timeout=timeout, headers={"User-Agent": "atm-research/1.0"})
            r.raise_for_status()
            out += parse_rss(r.text[:2_000_000], f)
        except Exception as e:  # noqa: BLE001
            errors.append({"feed": f, "error": e.__class__.__name__})
    agg = sum(i["sentiment"] for i in out) / len(out) if out else None
    return {"items": out[:100], "aggregate_sentiment": agg, "errors": errors, "status": "OK" if out else "UNAVAILABLE"}
