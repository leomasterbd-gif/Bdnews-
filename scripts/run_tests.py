#!/usr/bin/env python3
"""Run the pytest suite and store a machine-readable summary in reports/test_results.json."""
import json
import re
import subprocess
import sys
import time

from _path import ROOT

t = time.time()
p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", "-rA"], cwd=ROOT, capture_output=True, text=True)
tail = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", tail)}
tests = re.findall(r"^(PASSED|FAILED|ERROR) (\S+)", p.stdout, re.M)
out = {"ok": p.returncode == 0, "summary": tail, "counts": counts, "seconds": round(time.time() - t, 1),
       "tests": [{"status": s, "id": i} for s, i in tests], "ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
(ROOT / "reports").mkdir(exist_ok=True)
(ROOT / "reports" / "test_results.json").write_text(json.dumps(out, indent=1))
print(tail)
sys.exit(p.returncode)
