#!/usr/bin/env python3
"""Backtest one strategy on one dataset (optionally walk-forward validate it).
Usage: python3 scripts/backtest_one.py --dataset BTC_USDT-5m --strategy momentum [--interval 15m] [--wf] [--params '{"n":24}']"""
import argparse
import json

import _path  # noqa: F401
from atm.backtest.engine import run_backtest
from atm.backtest.validation import walk_forward
from atm.data.loader import resample
from atm.research.cycle import _clean, load_market
from atm.risk.limits import RiskLimits
from atm.strategies.library import STRATEGIES

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default="BTC_USDT-5m")
ap.add_argument("--strategy", default="momentum", choices=list(STRATEGIES))
ap.add_argument("--interval", default="5m")
ap.add_argument("--params", default="{}")
ap.add_argument("--wf", action="store_true", help="run walk-forward validation with promotion gates")
a = ap.parse_args()
df, m = load_market(a.dataset)
if a.interval != "5m":
    df = resample(df, a.interval)
spec, L = STRATEGIES[a.strategy], RiskLimits.load()
if a.wf:
    out = walk_forward(df, spec, m, L)
    out.pop("folds")
else:
    r = run_backtest(df, spec.signals(df, json.loads(a.params)), m, L, start=300 if len(df) > 600 else 50)
    out = {"metrics": r.metrics, "rejections": r.rejections, "trades": r.trades.tail(10).to_dict("records")}
print(json.dumps(_clean(out), indent=1, default=str))
