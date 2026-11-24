"""ML research: purged walk-forward evaluation of classifiers vs simple baselines,
followed by a cost-aware backtest of each model's out-of-sample signals.

Deep sequence models (LSTM/GRU/Transformers) are deliberately not trained here: the
available real dataset (~3k bars per USDT market) is far too small; see docs/AUDIT.md.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ..backtest.engine import run_backtest
from ..backtest.execution import CostModel, MarketSpec
from ..features import indicators as ind
from ..features.engineering import build_features, forward_label
from ..risk.limits import RiskLimits

warnings.filterwarnings("ignore")


def model_zoo(seed: int = 0) -> dict:
    zoo = {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=500)),
        "random_forest": RandomForestClassifier(n_estimators=200, max_depth=4, min_samples_leaf=50, n_jobs=-1, random_state=seed),
        "mlp": make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(16,), alpha=1e-2, max_iter=300, early_stopping=True, random_state=seed)),
    }
    try:
        import lightgbm as lgb
        zoo["lightgbm"] = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.03, num_leaves=8, min_child_samples=50,
                                             subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=seed, verbose=-1)
    except ImportError:  # pragma: no cover
        pass
    return zoo


def purged_walk_forward(df: pd.DataFrame, horizon: int = 6, cost: float = 0.0025, n_folds: int = 4,
                        warmup: int = 300, seed: int = 0) -> dict:
    X = build_features(df)
    y = forward_label(df, horizon, cost)
    n = len(df)
    fold = (n - warmup) // (n_folds + 1)
    out = {name: {"proba": pd.Series(np.nan, df.index), "folds": []} for name in [*model_zoo(seed), "baseline_prior", "baseline_momentum"]}
    for k in range(1, n_folds + 1):
        ts, te = warmup + k * fold, min(warmup + (k + 1) * fold, n)
        tr_end = ts - horizon - 1  # purge: training labels must not overlap the test period
        tr = slice(warmup, tr_end)
        Xtr, ytr = X.iloc[tr], y.iloc[tr]
        mask = Xtr.notna().all(axis=1) & ytr.notna()
        Xtr, ytr = Xtr[mask], ytr[mask]
        Xte, yte = X.iloc[ts:te], y.iloc[ts:te]
        mte = Xte.notna().all(axis=1) & yte.notna()
        if ytr.nunique() < 2 or mte.sum() < 20:
            continue
        preds = {}
        for name, mdl in model_zoo(seed).items():
            mdl.fit(Xtr.values, ytr.values)
            preds[name] = mdl.predict_proba(Xte[mte].values)[:, 1]
        preds["baseline_prior"] = np.full(mte.sum(), ytr.mean())
        mom = Xte.loc[mte, "ret_12"].values
        preds["baseline_momentum"] = 1 / (1 + np.exp(-mom / (np.nanstd(Xtr["ret_12"]) + 1e-12)))
        for name, p in preds.items():
            out[name]["proba"].loc[Xte.index[mte]] = p
            yt = yte[mte].values
            auc = roc_auc_score(yt, p) if len(np.unique(yt)) > 1 and np.std(p) > 0 else 0.5
            out[name]["folds"].append({"test_start": str(df.index[ts]), "auc": float(auc), "brier": float(brier_score_loss(yt, p)),
                                       "pos_rate": float(yt.mean()), "train_rows": int(len(ytr))})
    return {"horizon": horizon, "cost": cost, "models": out, "label_pos_rate": float(y.mean())}


def ml_signals(df: pd.DataFrame, proba: pd.Series, threshold: float, horizon: int, atr_stop: float = 2.0) -> pd.DataFrame:
    at = ind.atr(df, 14)
    entry = proba > threshold
    # exit after `horizon` bars or when confidence collapses
    held = entry.astype(int).rolling(horizon, min_periods=1).max().shift().fillna(0).astype(bool)
    exit_ = ~held | (proba < threshold * 0.8)
    return pd.DataFrame({"entry": entry, "exit": exit_ & ~entry, "stop_dist": at * atr_stop, "tp_dist": np.nan})


def evaluate_ml(df: pd.DataFrame, market: MarketSpec, limits: RiskLimits, costs: CostModel = CostModel(),
                horizon: int = 6, n_folds: int = 4, warmup: int = 300) -> dict:
    res = purged_walk_forward(df, horizon=horizon, n_folds=n_folds, warmup=warmup)
    summary = {}
    first_test = None
    for name, r in res["models"].items():
        p = r["proba"]
        valid = p.dropna()
        if valid.empty:
            continue
        first_test = df.index.get_loc(valid.index[0]) if first_test is None else first_test
        # Threshold: fixed high-confidence cut (not tuned on test data)
        thr = 0.6
        sig = ml_signals(df, p.fillna(0), thr, horizon)
        bt = run_backtest(df, sig, market, limits, costs, start=df.index.get_loc(valid.index[0]))
        aucs = [f["auc"] for f in r["folds"]]
        summary[name] = {"mean_auc": float(np.mean(aucs)) if aucs else None, "fold_aucs": aucs,
                         "mean_brier": float(np.mean([f["brier"] for f in r["folds"]])) if r["folds"] else None,
                         "threshold": thr, "signals": int((p > thr).sum()), "backtest": bt.metrics}
    best_base = max(summary.get("baseline_prior", {}).get("mean_auc") or 0.5, summary.get("baseline_momentum", {}).get("mean_auc") or 0.5)
    for name, s in summary.items():
        if name.startswith("baseline"):
            s["verdict"] = "BASELINE"
            continue
        better = (s["mean_auc"] or 0) > best_base + 0.02
        profitable = s["backtest"]["net_return_pct"] > 0 and s["backtest"]["trades"] >= 10
        s["verdict"] = "CANDIDATE" if (better and profitable) else "REJECTED"
    return {"horizon": horizon, "cost_threshold": res["cost"], "label_pos_rate": res["label_pos_rate"], "models": summary}
