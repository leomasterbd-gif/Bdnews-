"""Untrusted-input handling for external text (news, websites, repo content, exchange
messages). External text is data: it is length-limited, stripped of control characters
and markup, and flagged when it contains instruction-like content. It is never
concatenated into system prompts or used to change configuration."""
from __future__ import annotations

import html
import re
import unicodedata

MAX_LEN = 4000
_INJECTION = re.compile(
    r"(?i)(ignore (all|any|previous|prior) (instructions|rules)|disregard (the|your) (rules|instructions)|"
    r"system prompt|you are now|act as|developer mode|jailbreak|reveal (your|the) (secret|key|token|prompt)|"
    r"api[_ ]?key|withdraw|transfer (all|funds)|disable (risk|safety|limits)|set (risk|leverage)|"
    r"<\s*/?\s*(system|assistant|tool)\s*>|BEGIN (SYSTEM|INSTRUCTIONS))"
)
_TAGS = re.compile(r"<[^>]{0,200}>")


def clean_text(s: str, max_len: int = MAX_LEN) -> str:
    s = html.unescape(str(s))
    s = _TAGS.sub(" ", s)
    s = "".join(ch for ch in s if unicodedata.category(ch)[0] != "C" or ch in "\n\t")
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s[:max_len]


def injection_flags(s: str) -> list[str]:
    return sorted({m.group(0).lower() for m in _INJECTION.finditer(s)})


def as_untrusted(s: str, source: str) -> dict:
    t = clean_text(s)
    return {"source": source, "text": t, "trusted": False, "injection_flags": injection_flags(t)}
