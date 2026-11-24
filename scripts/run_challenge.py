#!/usr/bin/env python3
"""Run only the $100 -> $200 four-hour challenge (default params) and print the summary table."""
import argparse
import json

import _path  # noqa: F401
from atm.research.challenge import run_challenge
from atm.research.cycle import PRIMARY, SECONDARY, load_market, write_json
from atm.risk.limits import RiskLimits
from atm.strategies.library import STRATEGIES

ap = argparse.ArgumentParser()
ap.add_argument("--datasets", nargs="*", default=PRIMARY + SECONDARY)
ap.add_argument("--save", action="store_true")
a = ap.parse_args()
ch = run_challenge({d: load_market(d) for d in a.datasets}, {n: (s, dict(s.defaults)) for n, s in STRATEGIES.items()}, RiskLimits.load())
ch.pop("sessions_detail")
if a.save:
    write_json("challenge_quick.json", ch)
print(f"{'strategy':18s} {'sessions':>8s} {'hits':>5s} {'P(loss)%':>9s} {'median%':>9s} {'worst%':>8s}")
for n, s in ch["summary"].items():
    print(f"{n:18s} {s['sessions']:8d} {s['target_hits']:5d} {s['prob_loss_pct']:9.1f} {s['median_return_pct']:9.4f} {s['worst_return_pct']:8.3f}")
print("oracle (perfect foresight, 100% capital):", json.dumps(ch["oracle"]))
