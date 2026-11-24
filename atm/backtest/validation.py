"""Out-of-sample validation: walk-forward, holdout, bootstrap, Monte Carlo, stress tests
and the promotion gates that decide whether a strategy may advance to paper trading."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..risk.limits import RiskLimits
from ..strategies.library import StrategySpec
from .engine import run_backtest
from .execution import CostModel, MarketSpec


@dataclass(frozen=True)
class Gates:
    min_oos_trades: int = 30
    min_profit_factor: float = 1.15
    min_positive_fold_frac: float = 0.6
    min_bootstrap_p_positive: float = 0.90
    stress_cost_mult: float = 2.0
    n_candidates: int = 1          # number of strategy x dataset candidates tested in the same cycle
    family_alpha: float = 0.10     # family-wise error budget (Bonferroni)

    @property
    def bootstrap_threshold(self) -> float:
        """Bonferroni-corrected: P(mean trade > 0) must exceed 1 - alpha / N."""
        return max(self.min_bootstrap_p_positive, 1 - self.family_alpha / max(1, self.n_candidates))


def split_points(n: int, n_folds: int, holdout_frac: float, warmup: int) -> tuple[list[tuple[int, int, int]], tuple[int, int]]:
    """Expanding-window walk-forward. Returns [(train_start, test_start, test_end)], holdout (start, end)."""
    hold_start = int(n * (1 - holdout_frac))
    usable = hold_start - warmup
    fold = usable // (n_folds + 1)
    folds = []
    for k in range(1, n_folds + 1):
        ts = warmup + k * fold
        folds.append((warmup, ts, min(ts + fold, hold_start)))
    return folds, (hold_start, n)


def bootstrap_mean(x: np.ndarray, n_boot: int = 20000, seed: int = 1) -> dict:
    x = np.asarray(x, float)
    if len(x) < 2:
        return {"p_positive": 0.0, "ci05": float("nan"), "ci95": float("nan")}
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n_boot, len(x)), replace=True).mean(axis=1)
    return {"p_positive": float((means > 0).mean()), "ci05": float(np.percentile(means, 5)), "ci95": float(np.percentile(means, 95))}


def monte_carlo_trades(trade_rets_pct: np.ndarray, n_trades: int, n_sims: int = 5000, seed: int = 2,
                       position_frac: float = 1.0) -> dict:
    """Resample trade returns (as % of position) into equity paths; position_frac = share of equity per trade."""
    r = np.asarray(trade_rets_pct, float) / 100 * position_frac
    if len(r) == 0 or n_trades == 0:
        return {"sims": 0}
    rng = np.random.default_rng(seed)
    paths = np.cumprod(1 + rng.choice(r, size=(n_sims, n_trades), replace=True), axis=1)
    final = paths[:, -1]
    peak = np.maximum.accumulate(paths, axis=1)
    dd = (1 - paths / peak).max(axis=1)
    return {"sims": n_sims, "trades_per_path": n_trades, "median_return_pct": float(100 * (np.median(final) - 1)),
            "p05_return_pct": float(100 * (np.percentile(final, 5) - 1)), "p95_return_pct": float(100 * (np.percentile(final, 95) - 1)),
            "prob_loss": float((final < 1).mean()), "median_max_dd_pct": float(100 * np.median(dd)),
            "p95_max_dd_pct": float(100 * np.percentile(dd, 95))}


def walk_forward(df: pd.DataFrame, spec: StrategySpec, market: MarketSpec, limits: RiskLimits,
                 optimizer=None, n_folds: int = 4, holdout_frac: float = 0.2, warmup: int = 300,
                 costs: CostModel = CostModel(), gates: Gates = Gates()) -> dict:
    """If `optimizer` is given it is called as optimizer(df_train_slice_bounds) -> params using ONLY
    data before test_start. Signals are computed on the full series but are causal by construction;
    the test backtest only trades inside [test_start, test_end)."""
    folds, (hs, he) = split_points(len(df), n_folds, holdout_frac, warmup)
    fold_rows, oos_trades = [], []
    params = dict(spec.defaults)
    for (tr0, ts0, te0) in folds:
        if optimizer is not None:
            params = optimizer(df.iloc[:ts0], spec, tr0)
        sig = spec.signals(df, params)
        r = run_backtest(df, sig, market, limits, costs, start=ts0, end=te0)
        fold_rows.append({"test_start": str(df.index[ts0]), "test_end": str(df.index[te0 - 1]), "params": params, **r.metrics})
        oos_trades.append(r.trades)
    trades = pd.concat(oos_trades) if oos_trades else pd.DataFrame()
    # holdout: params from the final optimisation on all pre-holdout data
    if optimizer is not None:
        params = optimizer(df.iloc[:hs], spec, warmup)
    sig = spec.signals(df, params)
    hold = run_backtest(df, sig, market, limits, costs, start=hs, end=he)
    # stress test on the untouched holdout only (the final params were optimised on data before it)
    stress = run_backtest(df, sig, market, limits, CostModel(**{**costs.__dict__, "stress_mult": gates.stress_cost_mult}), start=hs, end=he)
    rets = trades["ret_pct"].to_numpy() if len(trades) else np.array([])
    gp = trades.loc[trades.pnl > 0, "pnl"].sum() if len(trades) else 0.0
    gl = -trades.loc[trades.pnl <= 0, "pnl"].sum() if len(trades) else 0.0
    pf = gp / gl if gl > 0 else (float("inf") if gp > 0 else 0.0)
    boot = bootstrap_mean(rets)
    pos_folds = float(np.mean([f["net_return_pct"] > 0 for f in fold_rows])) if fold_rows else 0.0
    oos_ret = float(np.prod([1 + f["net_return_pct"] / 100 for f in fold_rows]) * 100 - 100)
    checks = {
        "oos_trades": (len(trades) >= gates.min_oos_trades, len(trades)),
        "oos_net_return_positive": (oos_ret > 0, round(oos_ret, 4)),
        "profit_factor": (pf >= gates.min_profit_factor, round(pf, 3) if np.isfinite(pf) else pf),
        "positive_folds": (pos_folds >= gates.min_positive_fold_frac, pos_folds),
        "bootstrap_p_positive_bonferroni": (boot["p_positive"] >= gates.bootstrap_threshold, round(boot["p_positive"], 4)),
        "holdout_positive": (hold.metrics["net_return_pct"] > 0, round(hold.metrics["net_return_pct"], 4)),
        "stress_2x_costs_nonnegative": (stress.metrics["net_return_pct"] >= 0, round(stress.metrics["net_return_pct"], 4)),
    }
    passed = all(v[0] for v in checks.values())
    return {"strategy": spec.name, "family": spec.family, "folds": fold_rows, "oos_compound_return_pct": oos_ret,
            "oos_trades": int(len(trades)), "oos_profit_factor": pf, "bootstrap": boot,
            "monte_carlo": monte_carlo_trades(rets, max(1, len(rets)), position_frac=limits.max_position_pct / 100),
            "holdout": hold.metrics, "stress": stress.metrics, "final_params": params,
            "gates": {k: {"pass": bool(v[0]), "value": v[1]} for k, v in checks.items()},
            "bootstrap_threshold": gates.bootstrap_threshold,
            "verdict": "VALIDATED" if passed else "REJECTED"}
