#!/usr/bin/env python3
"""PostToolUse hook: lint edited Python files with ruff and surface problems to the agent."""
import json
import shutil
import subprocess
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
path = str((data.get("tool_input") or {}).get("file_path", ""))
if not path.endswith(".py") or not shutil.which("ruff"):
    sys.exit(0)
r = subprocess.run(["ruff", "check", "--quiet", path], capture_output=True, text=True)
if r.returncode:
    print(r.stdout[-2000:], file=sys.stderr)
    sys.exit(2)
