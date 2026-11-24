#!/usr/bin/env python3
"""Data-quality report for every stored dataset (gaps, duplicates, OHLC violations, abnormal moves)."""
import json

import _path  # noqa: F401
from atm.research.cycle import _clean, data_quality

print(json.dumps(_clean(data_quality()), indent=1))
