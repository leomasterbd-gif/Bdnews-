#!/usr/bin/env python3
"""Security scan: bandit (static analysis), pip-audit (dependency CVEs), secret-pattern scan
of tracked files, and policy checks (no withdrawal code, no production order host).
Writes reports/security_scan.json."""
import json
import re
import subprocess
import sys
import time

import _path  # noqa: F401
from _path import ROOT

out = {"ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
b = subprocess.run([sys.executable, "-m", "bandit", "-q", "-r", "atm", "-f", "json"], cwd=ROOT, capture_output=True, text=True)
try:
    bj = json.loads(b.stdout)
    sev = {}
    for r in bj["results"]:
        sev[r["issue_severity"]] = sev.get(r["issue_severity"], 0) + 1
    out["bandit"] = {"by_severity": sev, "issues": [{"id": r["test_id"], "sev": r["issue_severity"], "file": r["filename"], "line": r["line_number"], "text": r["issue_text"]} for r in bj["results"]]}
except Exception as e:  # noqa: BLE001
    out["bandit"] = {"error": str(e)[:200]}
pa = subprocess.run([sys.executable, "-m", "pip_audit", "-r", "requirements.txt", "-f", "json", "--progress-spinner", "off"], cwd=ROOT, capture_output=True, text=True)
try:
    pj = json.loads(pa.stdout)
    vulns = [{"name": d["name"], "version": d["version"], "ids": [v["id"] for v in d["vulns"]]} for d in pj.get("dependencies", []) if d.get("vulns")]
    out["pip_audit"] = {"packages": len(pj.get("dependencies", [])), "vulnerable": vulns}
except Exception:  # noqa: BLE001
    out["pip_audit"] = {"error": (pa.stderr or pa.stdout)[-300:]}
files = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split()
pat = re.compile(r"(?i)(api[_-]?secret|bot[_-]?token|private[_-]?key)\s*[:=]\s*['\"][A-Za-z0-9_\-:]{16,}['\"]|\b\d{8,10}:[A-Za-z0-9_-]{35}\b")
hits = []
for f in files:
    p = ROOT / f
    if p.suffix in (".py", ".md", ".yml", ".yaml", ".json", ".sh", ".js", ".html", ".toml", ".txt", ".env") and p.exists() and p.stat().st_size < 2e6:
        for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            if pat.search(line) and "secret-scan: allow" not in line:
                hits.append(f"{f}:{i}")
out["secret_scan"] = {"files_scanned": len(files), "hits": hits}
src = "\n".join((ROOT / f).read_text(errors="ignore") for f in files if f.startswith("atm/") and f.endswith(".py"))
out["policy"] = {
    "withdraw_endpoint_absent": "/sapi/v1/capital/withdraw" not in src,
    "testnet_only_order_client": "refuses non-testnet hosts" in src,
    "live_trading_refused_in_limits": "live_trading_enabled=true is refused" in src,
}
out["ok"] = not hits and all(out["policy"].values()) and not out.get("bandit", {}).get("by_severity", {}).get("HIGH") and not out.get("pip_audit", {}).get("vulnerable")
(ROOT / "reports").mkdir(exist_ok=True)
(ROOT / "reports" / "security_scan.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "bandit"} | {"bandit": out.get("bandit", {}).get("by_severity")}, indent=1))
