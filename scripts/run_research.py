#!/usr/bin/env python3
"""Run one full autonomous research cycle and write reports/ (JSON + Markdown)."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from atm.research.cycle import run_cycle  # noqa: E402
from atm.research.report import write_markdown  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-optimise", action="store_true")
    a = ap.parse_args()
    s = run_cycle(workers=a.workers, optimise=not a.no_optimise)
    write_markdown()
    print(json.dumps(s, indent=1, default=str))
