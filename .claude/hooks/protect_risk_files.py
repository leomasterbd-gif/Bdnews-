#!/usr/bin/env python3
"""PreToolUse hook: agents may not modify risk limits, risk-limit code or security code,
and may not flip live trading on. The owner edits these files by hand."""
import json
import re
import sys

PROTECTED = ("config/risk_limits.yaml", "atm/risk/limits.py", "atm/security/", ".claude/hooks/", ".claude/settings.json")
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
tool = data.get("tool_name", "")
inp = data.get("tool_input", {}) or {}
target = str(inp.get("file_path") or inp.get("notebook_path") or "")
if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit") and any(p in target for p in PROTECTED):
    print(f"BLOCKED: {target} is owner-controlled (risk/security). Propose the change to the owner instead.", file=sys.stderr)
    sys.exit(2)
if tool == "Bash":
    cmd = str(inp.get("command", ""))
    writes = re.search(r"(>|\btee\b|\bsed\s+-i|\bperl\s+-pi|\bmv\b|\bcp\b|\brm\b|\btruncate\b|open\([^)]*['\"]w)", cmd)
    if writes and any(p in cmd for p in PROTECTED):
        print("BLOCKED: shell command would modify owner-controlled risk/security files.", file=sys.stderr)
        sys.exit(2)
    if re.search(r"live_trading_enabled\s*[:=]\s*true", cmd, re.I):
        print("BLOCKED: enabling live trading is not permitted.", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
