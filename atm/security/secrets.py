"""Secret handling: secrets only come from environment variables (or a 0600 env file
loaded by the process supervisor). They are never logged, returned by the API, sent to
Telegram, or passed to research/LLM components."""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import re
import secrets as _secrets

SECRET_ENV = ("BINANCE_TESTNET_API_KEY", "BINANCE_TESTNET_API_SECRET", "TELEGRAM_BOT_TOKEN", "ATM_OWNER_TOKEN")

_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|signature|password)(\"?\s*[:=]\s*\"?)([A-Za-z0-9_\-:.]{6,})"),
    re.compile(r"\b[A-Za-z0-9]{64}\b"),             # Binance-style 64-char keys
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b"),  # Telegram bot tokens
]


def get_secret(name: str) -> str | None:
    if name not in SECRET_ENV:
        raise KeyError(f"{name} is not a registered secret")
    v = os.environ.get(name)
    return v.strip() if v else None


def configured() -> dict[str, bool]:
    """Which secrets are present — booleans only, never values."""
    return {k: bool(os.environ.get(k)) for k in SECRET_ENV}


def redact(text: str) -> str:
    s = str(text)
    for k in SECRET_ENV:
        v = os.environ.get(k)
        if v and len(v) >= 6:
            s = s.replace(v, "***REDACTED***")
    s = _PATTERNS[0].sub(lambda m: m.group(1) + m.group(2) + "***REDACTED***", s)
    s = _PATTERNS[1].sub("***REDACTED***", s)
    s = _PATTERNS[2].sub("***REDACTED***", s)
    return s


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage())
        record.args = ()
        return True


def install_log_redaction() -> None:
    root = logging.getLogger()
    if not any(isinstance(f, RedactingFilter) for f in root.filters):
        root.addFilter(RedactingFilter())
    for h in root.handlers:
        h.addFilter(RedactingFilter())


def token_matches(candidate: str | None, expected: str | None) -> bool:
    if not candidate or not expected:
        return False
    return hmac.compare_digest(hashlib.sha256(candidate.encode()).digest(), hashlib.sha256(expected.encode()).digest())


def new_token() -> str:
    return _secrets.token_urlsafe(32)
