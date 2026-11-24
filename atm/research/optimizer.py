"""Parameter search restricted to training data: genetic algorithm (default) or Optuna TPE.

The objective penalises drawdown and too-few trades, and the number of trials is recorded
so reports can disclose the multiple-testing burden."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..backtest.engine import run_backtest
from ..backtest.execution import CostModel, MarketSpec
from ..risk.limits import RiskLimits
from ..strategies.library import StrategySpec

TRIALS_LOG: list[dict] = []
ERRORS = {"count": 0, "last": ""}


def objective(m: dict, min_trades: int = 8) -> float:
    if m["trades"] < min_trades:
        return -1e3 + m["trades"]
    return m["net_return_pct"] - 0.5 * m["max_drawdown_pct"]


def _sample(space: dict, rng) -> dict:
    out = {}
    for k, (lo, hi, t) in space.items():
        out[k] = int(rng.integers(lo, hi + 1)) if t is int else float(rng.uniform(lo, hi))
    return out


def _mutate(p: dict, space: dict, rng, rate=0.3) -> dict:
    q = dict(p)
    for k, (lo, hi, t) in space.items():
        if rng.random() < rate:
            span = (hi - lo) * 0.2
            v = q[k] + rng.normal(0, span)
            v = min(hi, max(lo, v))
            q[k] = int(round(v)) if t is int else float(v)
    return q


def _evaluate(df, spec, params, market, limits, costs, start):
    try:
        sig = spec.signals(df, params)
        return objective(run_backtest(df, sig, market, limits, costs, start=start).metrics)
    except Exception as e:  # noqa: BLE001 - a crashing parameter set scores worst, but is counted and reported
        ERRORS["count"] += 1
        ERRORS["last"] = f"{spec.name}: {e.__class__.__name__}: {e}"[:300]
        return -1e6


def genetic_optimizer(market: MarketSpec, limits: RiskLimits, costs: CostModel = CostModel(),
                      pop: int = 12, gens: int = 5, seed: int = 11):
    def opt(df_train: pd.DataFrame, spec: StrategySpec, start: int) -> dict:
        if not spec.space:
            return dict(spec.defaults)
        rng = np.random.default_rng(seed)
        popl = [dict(spec.defaults)] + [{**spec.defaults, **_sample(spec.space, rng)} for _ in range(pop - 1)]
        scores = [_evaluate(df_train, spec, p, market, limits, costs, start) for p in popl]
        for _ in range(gens):
            order = np.argsort(scores)[::-1]
            elite = [popl[i] for i in order[: max(2, pop // 4)]]
            children = []
            while len(children) < pop - len(elite):
                a, b = rng.choice(len(elite), 2, replace=True)
                child = {k: (elite[a][k] if rng.random() < 0.5 else elite[b][k]) for k in elite[a]}
                children.append(_mutate(child, spec.space, rng))
            popl = elite + children
            scores = [_evaluate(df_train, spec, p, market, limits, costs, start) for p in popl]
        best = int(np.argmax(scores))
        TRIALS_LOG.append({"strategy": spec.name, "method": "genetic", "trials": pop * (gens + 1),
                           "train_end": str(df_train.index[-1]), "best_score": float(scores[best])})
        return popl[best]
    return opt


def optuna_optimizer(market: MarketSpec, limits: RiskLimits, costs: CostModel = CostModel(), n_trials: int = 40, seed: int = 11):
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    def opt(df_train, spec, start):
        if not spec.space:
            return dict(spec.defaults)

        def f(trial):
            p = dict(spec.defaults)
            for k, (lo, hi, t) in spec.space.items():
                p[k] = trial.suggest_int(k, lo, hi) if t is int else trial.suggest_float(k, lo, hi)
            return _evaluate(df_train, spec, p, market, limits, costs, start)

        study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed))
        study.enqueue_trial({k: spec.defaults[k] for k in spec.space})
        study.optimize(f, n_trials=n_trials)
        TRIALS_LOG.append({"strategy": spec.name, "method": "optuna_tpe", "trials": n_trials,
                           "train_end": str(df_train.index[-1]), "best_score": float(study.best_value)})
        return {**spec.defaults, **study.best_params}
    return opt
