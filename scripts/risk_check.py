#!/usr/bin/env python3
"""Validate config/risk_limits.yaml against the hard ceilings and print the effective limits."""
import json
import sys

import _path  # noqa: F401
from atm.risk.limits import HARD_CEILINGS, RiskConfigError, RiskLimits

try:
    L = RiskLimits.load(sys.argv[1]) if len(sys.argv) > 1 else RiskLimits.load()
except RiskConfigError as e:
    print("REJECTED:", e)
    sys.exit(1)
print(json.dumps({"effective": L.as_dict(), "hard_ceilings": HARD_CEILINGS}, indent=1))
