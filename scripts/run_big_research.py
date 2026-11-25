#!/usr/bin/env python3
"""Research on 2 years of official Binance archives (5 USDT markets): walk-forward validation of
every strategy with default parameters (no tuning -> minimal multiple-testing), ML on 15m bars,
and the 4-hour challenge over every window. Writes reports/big_*.json."""
import json
import time
from concurrent.futures import ProcessPoolExecutor

import _path  # noqa: F401
from atm.backtest.validation import Gates, walk_forward
from atm.data.loader import BINANCE_ARCHIVE, resample
from atm.ml.models import evaluate_ml
from atm.research.challenge import run_challenge
from atm.research.cycle import load_market, research_slice, write_json
from atm.risk.limits import RiskLimits
from atm.storage.db import Store
from atm.strategies.library import STRATEGIES

DS = list(BINANCE_ARCHIVE)
N_CAND = len(DS) * len(STRATEGIES)


def wf_job(a):
    d, s = a
    df, m = load_market(d)
    r = walk_forward(research_slice(df), STRATEGIES[s], m, RiskLimits.load(), n_folds=6, gates=Gates(n_candidates=N_CAND))
    r["dataset"] = d
    return r


if __name__ == "__main__":
    t0 = time.time()
    with ProcessPoolExecutor(4) as ex:
        wf = list(ex.map(wf_job, [(d, s) for d in DS for s in STRATEGIES]))
    write_json("big_walk_forward.json", wf)
    st = Store()
    for r in wf:
        st.register(r["strategy"], r["family"], r["final_params"], r["verdict"], {"oos_return_pct": r["oos_compound_return_pct"],
                    "oos_trades": r["oos_trades"], "holdout_return_pct": r["holdout"]["net_return_pct"], "gates": r["gates"]}, r["dataset"])
    print("walk-forward done", round(time.time() - t0), "s; validated:", [(r["strategy"], r["dataset"]) for r in wf if r["verdict"] == "VALIDATED"], flush=True)
    ml = {}
    for d in DS:
        df, m = load_market(d)
        ml[d] = evaluate_ml(resample(research_slice(df), "15m"), m, RiskLimits.load(), horizon=4, n_folds=6)
    write_json("big_ml.json", ml)
    print("ml done", round(time.time() - t0), "s", flush=True)
    ch = run_challenge({d: load_market(d) for d in DS}, {n: (s, dict(s.defaults)) for n, s in STRATEGIES.items()}, RiskLimits.load())
    det = ch.pop("sessions_detail")
    write_json("big_challenge.json", ch)
    write_json("big_challenge_sessions.json", det)
    s = {"seconds": round(time.time() - t0), "walk_forward_runs": len(wf), "validated": [(r["strategy"], r["dataset"]) for r in wf if r["verdict"] == "VALIDATED"],
         "positive_oos": sum(r["oos_compound_return_pct"] > 0 for r in wf), "bonferroni_threshold": Gates(n_candidates=N_CAND).bootstrap_threshold,
         "ml_candidates": [(d, k) for d, r in ml.items() for k, v in r["models"].items() if v["verdict"] == "CANDIDATE"],
         "challenge_sessions": ch["oracle"]["sessions"], "challenge_max_hits": max(v["target_hits"] for v in ch["summary"].values()),
         "oracle": ch["oracle"]}
    write_json("big_summary.json", s)
    print(json.dumps(s, default=str), flush=True)
