#!/usr/bin/env python3
"""Purged walk-forward ML evaluation vs baselines. Usage: python3 scripts/run_ml.py --dataset BTC_USDT-5m --horizon 6"""
import argparse
import json

import _path  # noqa: F401
from atm.ml.models import evaluate_ml
from atm.research.cycle import _clean, load_market
from atm.risk.limits import RiskLimits

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="BTC_USDT-5m")
ap.add_argument("--horizon", type=int, default=6)
a = ap.parse_args()
res = evaluate_ml(*load_market(a.dataset), RiskLimits.load(), horizon=a.horizon)
for k, v in res["models"].items():
    print(f"{k:18s} AUC={v['mean_auc'] or 0:.3f} net={v['backtest']['net_return_pct']:+.3f}% trades={v['backtest']['trades']:3d} {v['verdict']}")
print(json.dumps(_clean({"label_pos_rate": res["label_pos_rate"]})))
