#!/usr/bin/env python3
"""PROPOSED replacement for .claude/hooks/protect_risk_files.py (audit finding #12).
Owner installs it (outside Claude):  cp docs/owner_patches/0002-protect_risk_files.py .claude/hooks/protect_risk_files.py

Improvements: realpath normalisation (defeats '//', '..', symlinks); protects the whole risk
package, validation gates, exchange host lock and paper-trader mode checks; catches more write
forms (python write_text/open(...,'w'), dd, install, ln, git checkout/apply/restore, chmod);
no false positive on '2>&1' in read-only commands."""
import json
import os
import re
import sys

PROTECTED = ("config/risk_limits.yaml", "atm/risk/", "atm/security/", "atm/backtest/validation.py",
             "atm/exchange/binance.py", "atm/exchange/paper.py", ".claude/hooks/", ".claude/settings.json")
ROOT = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
WRITE = re.compile(r"(?<![0-9&])>(?!&)|\btee\b|\bsed\s+-i|\bperl\s+-p?i|\bmv\b|\bcp\b|\brm\b|\btruncate\b|\bdd\b|\binstall\b|\bln\b|"
                   r"\bgit\s+(checkout|apply|restore|reset|am|stash)|write_text|write_bytes|open\([^)]*['\"][wa]|\bchmod\b")


def protected(path: str) -> bool:
    rel = os.path.relpath(os.path.realpath(os.path.join(ROOT, path)), ROOT).replace(os.sep, "/")
    return any(rel == p.rstrip("/") or rel.startswith(p) for p in PROTECTED)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}
    target = str(inp.get("file_path") or inp.get("notebook_path") or "")
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit") and target and protected(target):
        print(f"BLOCKED: {target} is owner-controlled (risk/security). Propose the change to the owner instead.", file=sys.stderr)
        return 2
    if tool == "Bash":
        cmd = re.sub(r"/+", "/", str(inp.get("command", "")))
        mentions = any(p.rstrip("/") in cmd for p in PROTECTED) or re.search(r"risk_limits|atm/risk|atm/security|\.claude/hooks", cmd)
        if mentions and WRITE.search(cmd):
            print("BLOCKED: shell command would modify owner-controlled risk/security files.", file=sys.stderr)
            return 2
        if re.search(r"live_trading_enabled\s*[:=]\s*true", cmd, re.I):
            print("BLOCKED: enabling live trading is not permitted.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
