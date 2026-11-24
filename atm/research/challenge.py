"""$100 -> $200 FOUR-HOUR QUANTITATIVE RESEARCH CHALLENGE.

Every non-overlapping 4-hour window in every dataset is an independent session that
starts with a fresh $100 virtual balance and a fresh risk session. Indicators may use
history before the window (warm-up) but trades only happen inside it. No window is
skipped, reset or cherry-picked; every result is reported.

It also computes a perfect-foresight upper bound: the best possible long-only spot
result in each window if every future price were known (fees included, 100% of capital,
no risk limits). If even that bound almost never reaches +100%, the target is infeasible
for spot trading without leverage.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..backtest.engine import run_backtest
from ..backtest.execution import CostModel, MarketSpec
from ..backtest.metrics import summarize_returns
from ..risk.limits import RiskLimits
from ..strategies.library import StrategySpec

TARGET_PCT = 100.0


def oracle_long_only(close: np.ndarray, fee: float = 0.001) -> float:
    """Max achievable compounded return (%) trading close-to-close long-only with
    proportional fee per side. DP over states flat/long (log space)."""
    lf = np.log(1 - fee)
    flat, long_ = 0.0, -np.inf
    for t in range(len(close)):
        if t > 0:
            long_ += np.log(close[t] / close[t - 1])
        flat, long_ = max(flat, long_ + lf), max(long_, flat + lf)
    return float(100 * (np.exp(max(flat, long_ + lf)) - 1))


def windows(df: pd.DataFrame, hours: float = 4.0, warmup: int = 300) -> list[tuple[int, int]]:
    step = pd.Series(df.index).diff().median()
    n = int(pd.Timedelta(hours=hours) / step)
    return [(s, s + n) for s in range(warmup, len(df) - n + 1, n)]


def run_challenge(datasets: dict[str, tuple[pd.DataFrame, MarketSpec]], strategies: dict[str, tuple[StrategySpec, dict]],
                  limits: RiskLimits, costs: CostModel = CostModel(), capital: float = 100.0) -> dict:
    per_strategy: dict[str, list[dict]] = {k: [] for k in strategies}
    oracle_rows = []
    for dname, (df, market) in datasets.items():
        wins = windows(df)
        c = df.close.to_numpy()
        for s, e in wins:
            oracle_rows.append({"dataset": dname, "start": str(df.index[s]), "oracle_pct": oracle_long_only(c[s:e]),
                                "price_change_pct": 100 * (c[e - 1] / c[s] - 1)})
        for sname, (spec, params) in strategies.items():
            sig = spec.signals(df, params)
            for s, e in wins:
                r = run_backtest(df, sig, market, limits, costs, capital_usd=capital, start=s, end=e)
                m = r.metrics
                per_strategy[sname].append({"dataset": dname, "start": str(df.index[s]), "ret_pct": m["net_return_pct"],
                                            "pnl_usd": m["net_pnl_usd"], "trades": m["trades"], "fees_usd": m["total_fees"] * market.usd_per_quote,
                                            "max_dd_pct": m["max_drawdown_pct"]})
    summary = {}
    for sname, rows in per_strategy.items():
        r = np.array([x["ret_pct"] for x in rows])
        dd = np.array([x["max_dd_pct"] for x in rows])
        summary[sname] = {
            "sessions": len(rows),
            "target_hits": int((r >= TARGET_PCT).sum()),
            "target_hit_rate_pct": float(100 * (r >= TARGET_PCT).mean()) if len(r) else 0.0,
            "prob_loss_pct": float(100 * (r < 0).mean()) if len(r) else 0.0,
            "prob_no_trade_pct": float(100 * np.mean([x["trades"] == 0 for x in rows])) if rows else 0.0,
            "median_return_pct": float(np.median(r)) if len(r) else 0.0,
            "mean_return_pct": float(r.mean()) if len(r) else 0.0,
            "worst_return_pct": float(r.min()) if len(r) else 0.0,
            "best_return_pct": float(r.max()) if len(r) else 0.0,
            "worst_max_dd_pct": float(dd.max()) if len(dd) else 0.0,
            "mean_fees_usd": float(np.mean([x["fees_usd"] for x in rows])) if rows else 0.0,
            "sharpe_like": float(r.mean() / r.std()) if len(r) and r.std() > 0 else 0.0,
            "consistency_pct_positive": float(100 * (r > 0).mean()) if len(r) else 0.0,
            "by_dataset": {d: summarize_returns(np.array([x["ret_pct"] for x in rows if x["dataset"] == d])) for d in datasets},
        }
    o = np.array([x["oracle_pct"] for x in oracle_rows])
    pc = np.array([x["price_change_pct"] for x in oracle_rows])
    oracle = {"sessions": len(o), "oracle_target_hit_rate_pct": float(100 * (o >= TARGET_PCT).mean()),
              "oracle_median_pct": float(np.median(o)), "oracle_p95_pct": float(np.percentile(o, 95)), "oracle_max_pct": float(o.max()),
              "abs_price_change_median_pct": float(np.median(np.abs(pc))), "abs_price_change_max_pct": float(np.abs(pc).max())}
    # Bootstrap: probability of ever reaching +100% cumulatively over many sessions with the best strategy
    return {"target_pct": TARGET_PCT, "capital_usd": capital, "summary": summary, "oracle": oracle,
            "sessions_detail": per_strategy, "oracle_detail": oracle_rows}


def sessions_to_double(session_returns_pct: np.ndarray, n_sims: int = 5000, max_sessions: int = 500, seed: int = 3) -> dict:
    """How many consecutive 4h sessions (bootstrapped) would it take to double $100?"""
    r = np.asarray(session_returns_pct) / 100
    if len(r) == 0 or r.mean() <= 0:
        return {"doubling_possible": False, "reason": "mean session return <= 0 after costs"}
    rng = np.random.default_rng(seed)
    paths = np.cumprod(1 + rng.choice(r, size=(n_sims, max_sessions)), axis=1)
    hit = (paths >= 2).any(axis=1)
    first = np.where(hit, (paths >= 2).argmax(axis=1) + 1, np.nan)
    return {"doubling_possible": True, "p_double_within_max": float(hit.mean()), "median_sessions": float(np.nanmedian(first)) if hit.any() else None,
            "max_sessions": max_sessions, "p_ruin_50pct": float((paths <= 0.5).any(axis=1).mean())}
