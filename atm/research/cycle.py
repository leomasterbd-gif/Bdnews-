"""Autonomous research cycle:
Market Data -> Quality -> Strategy generation/optimisation -> Backtest -> Independent validation
-> Registry (versioned) -> Challenge experiment -> Reports.

Deterministic Python does all the work; no LLM is in the loop. Results (good and bad) are
written to reports/ and to the registry; failed experiments are archived, never deleted."""
from __future__ import annotations

import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from ..backtest.engine import run_backtest
from ..backtest.execution import market_for
from ..backtest.validation import Gates, walk_forward
from ..data.loader import DATASETS, load_ohlcv, quality_check, resample
from ..ml.models import evaluate_ml
from ..ml.rl import q_signals, train_q
from ..risk.limits import RiskLimits
from ..storage.db import Store
from ..strategies.library import PAIR_STRATEGY, STRATEGIES
from . import optimizer as optm
from .challenge import run_challenge, sessions_to_double

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"

PRIMARY = ["BTC_USDT-5m", "XRP_USDT-5m"]
SECONDARY = ["ETH_BTC-5m", "LTC_BTC-5m", "ADA_BTC-5m", "DASH_BTC-5m", "ETC_BTC-5m", "TRX_BTC-5m",
             "XLM_BTC-5m", "XMR_BTC-5m", "ZEC_BTC-5m", "NXT_BTC-5m"]


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        f = float(o)
        return None if math.isnan(f) else (1e9 if math.isinf(f) and f > 0 else (-1e9 if math.isinf(f) else f))
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (pd.Timestamp,)):
        return str(o)
    return o


def write_json(name: str, obj) -> Path:
    REPORTS.mkdir(exist_ok=True)
    p = REPORTS / name
    p.write_text(json.dumps(_clean(obj), indent=1, default=str))
    return p


FORWARD_FRAC = 0.10  # final 10% of every dataset is never used by research; reserved for forward (replay) tests


def research_slice(df):
    """Data available to research (walk-forward + holdout). The last FORWARD_FRAC is untouched."""
    return df.iloc[: int(len(df) * (1 - FORWARD_FRAC))]


def load_market(name: str):
    df = load_ohlcv(name)
    meta = DATASETS[name]
    return df, market_for(meta["symbol"], meta["quote"], float(df.close.iloc[-1]))


def _wf_job(args):
    name, sname, optimise, n_candidates = args
    df, market = load_market(name)
    df = research_slice(df)
    limits = RiskLimits.load()
    spec = STRATEGIES[sname] if sname in STRATEGIES else PAIR_STRATEGY
    if sname == "pair_relative":
        ref = research_slice(load_ohlcv("ETH_BTC-5m" if name != "ETH_BTC-5m" else "LTC_BTC-5m"))
        df = df.join(ref.close.rename("ref_close"), how="inner")
    opt = optm.genetic_optimizer(market, limits) if optimise and spec.space else None
    t = time.time()
    n_before = len(optm.TRIALS_LOG)  # worker processes are reused: count only this job's trials
    res = walk_forward(df, spec, market, limits, optimizer=opt, gates=Gates(n_candidates=n_candidates))
    res["dataset"] = name
    res["optimised"] = bool(opt)
    res["seconds"] = round(time.time() - t, 1)
    res["trials"] = sum(x["trials"] for x in optm.TRIALS_LOG[n_before:])
    res["optimizer_errors"] = optm.ERRORS["count"]
    return res


def data_quality() -> dict:
    out = {}
    for name in DATASETS:
        df = load_ohlcv(name)
        q = quality_check(df).to_dict()
        q.update(start=str(df.index[0]), end=str(df.index[-1]), symbol=DATASETS[name]["symbol"], quote=DATASETS[name]["quote"])
        out[name] = q
    return out


def timeframe_study(limits: RiskLimits) -> dict:
    out = {}
    for name in PRIMARY:
        df5, market = load_market(name)
        for tf in ("5m", "15m", "30m", "1h"):
            df = df5 if tf == "5m" else resample(df5, tf)
            for sname, spec in STRATEGIES.items():
                r = run_backtest(df, spec.signals(df), market, limits, start=min(300, len(df) // 3))
                out.setdefault(name, {}).setdefault(tf, {})[sname] = {k: r.metrics[k] for k in ("net_return_pct", "trades", "profit_factor", "max_drawdown_pct", "total_fees")}
    return out


def rl_experiment(limits: RiskLimits) -> dict:
    out = {}
    for name in PRIMARY + ["ETH_BTC-5m"]:
        df, market = load_market(name)
        df = research_slice(df)
        split = int(len(df) * 0.6)
        Q = train_q(df, split)
        r = run_backtest(df, q_signals(df, Q, split), market, limits, start=split)
        out[name] = {"train_bars": split, "oos": r.metrics, "verdict": "CANDIDATE" if r.metrics["net_return_pct"] > 0 and r.metrics["trades"] >= 10 else "REJECTED"}
    return out


def run_cycle(workers: int = 4, optimise: bool = True, store: Store | None = None) -> dict:
    t0 = time.time()
    store = store or Store()
    limits = RiskLimits.load()
    store.audit("research_supervisor", "cycle_start", {"optimise": optimise})
    summary: dict = {"started": pd.Timestamp.utcnow().isoformat(), "risk_limits": limits.as_dict()}

    dq = data_quality()
    write_json("data_quality.json", dq)

    pairs = ["LTC_BTC-5m", "DASH_BTC-5m", "XMR_BTC-5m"]
    n_cand = len(PRIMARY + SECONDARY) * len(STRATEGIES) + len(pairs)
    jobs = [(d, s, optimise, n_cand) for d in PRIMARY + SECONDARY for s in STRATEGIES]
    jobs += [(d, "pair_relative", optimise, n_cand) for d in pairs]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        wf = list(ex.map(_wf_job, jobs))
    for r in wf:
        status = "VALIDATED" if r["verdict"] == "VALIDATED" else "REJECTED"
        store.register(r["strategy"], r["family"], r["final_params"], status,
                       {"oos_return_pct": r["oos_compound_return_pct"], "oos_trades": r["oos_trades"], "pf": r["oos_profit_factor"],
                        "holdout_return_pct": r["holdout"]["net_return_pct"], "gates": r["gates"]}, r["dataset"])
        store.experiment("walk_forward", f"{r['strategy']} is profitable OOS on {r['dataset']} after costs", {"optimised": r["optimised"]},
                         {"oos": r["oos_compound_return_pct"], "holdout": r["holdout"]["net_return_pct"]}, r["verdict"])
    write_json("walk_forward.json", wf)
    total_trials = sum(r.get("trials", 0) for r in wf) + len(wf)

    ml = {}
    for name in PRIMARY + ["ETH_BTC-5m"]:
        df, m = load_market(name)
        ml[name] = evaluate_ml(research_slice(df), m, limits)
    for name, res in ml.items():
        for m, s in res["models"].items():
            store.experiment("ml", f"{m} beats baselines on {name}", {"horizon": res["horizon"]},
                             {"auc": s["mean_auc"], "net": s["backtest"]["net_return_pct"]}, s["verdict"])
    write_json("ml.json", ml)
    rl = rl_experiment(limits)
    write_json("rl.json", rl)
    tfs = timeframe_study(limits)
    write_json("timeframes.json", tfs)

    # Challenge: default parameters (no in-sample tuning on the evaluated windows) for every strategy,
    # plus walk-forward-validated parameters where a strategy passed every gate.
    datasets = {n: load_market(n) for n in PRIMARY + SECONDARY}
    strats = {n: (s, dict(s.defaults)) for n, s in STRATEGIES.items()}
    validated = [r for r in wf if r["verdict"] == "VALIDATED" and r["strategy"] in STRATEGIES]
    for r in validated:
        strats[f"{r['strategy']}@validated:{r['dataset']}"] = (STRATEGIES[r["strategy"]], r["final_params"])
    fwd_start = {n: int(len(df) * (1 - FORWARD_FRAC)) for n, (df, _) in datasets.items()}
    ch = run_challenge(datasets, strats, limits, min_start={k: fwd_start for k in strats if "@validated" in k})
    traded = {k: v for k, v in ch["summary"].items() if v["prob_no_trade_pct"] < 100}
    best = max(traded.items() or ch["summary"].items(), key=lambda kv: kv[1]["mean_return_pct"])
    ch["best_by_mean"] = best[0]
    ch["doubling_analysis"] = sessions_to_double(np.array([x["ret_pct"] for x in ch["sessions_detail"][best[0]]]))
    detail = ch.pop("sessions_detail")
    write_json("challenge.json", ch)
    write_json("challenge_sessions.json", detail)
    store.experiment("challenge_4h", "$100 -> $200 within 4h is achievable under risk limits", {"sessions": ch["oracle"]["sessions"]},
                     {"best": best[0], "hit_rate": best[1]["target_hit_rate_pct"], "oracle_hit_rate": ch["oracle"]["oracle_target_hit_rate_pct"]},
                     "REJECTED" if best[1]["target_hit_rate_pct"] == 0 else "PARTIAL")

    summary.update(
        finished=pd.Timestamp.utcnow().isoformat(), seconds=round(time.time() - t0, 1),
        walk_forward_runs=len(wf), validated=[(r["strategy"], r["dataset"]) for r in wf if r["verdict"] == "VALIDATED"],
        total_backtest_trials=total_trials,
        bonferroni_bootstrap_threshold=Gates(n_candidates=n_cand).bootstrap_threshold,
        forward_reserved_frac=FORWARD_FRAC,
        ml_candidates=[(n, m) for n, res in ml.items() for m, s in res["models"].items() if s["verdict"] == "CANDIDATE"],
        rl_candidates=[n for n, r in rl.items() if r["verdict"] == "CANDIDATE"],
        challenge_best=best[0], challenge_best_hit_rate=best[1]["target_hit_rate_pct"],
        oracle_hit_rate=ch["oracle"]["oracle_target_hit_rate_pct"],
        system_should_trade=bool([r for r in wf if r["verdict"] == "VALIDATED"]),
    )
    write_json("summary.json", summary)
    store.audit("research_supervisor", "cycle_end", {"seconds": summary["seconds"], "validated": len(summary["validated"])})
    return summary
