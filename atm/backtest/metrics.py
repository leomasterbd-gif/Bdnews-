"""Performance metrics computed from an equity curve and a trade list."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    if len(equity) == 0:
        return 0.0
    peak = equity.cummax()
    return float(100 * (1 - equity / peak).max())


def compute(equity: pd.Series, trades: pd.DataFrame, bars_per_year: float, initial: float) -> dict:
    final = float(equity.iloc[-1]) if len(equity) else initial
    rets = equity.pct_change().dropna()
    n = len(trades)
    pnl = trades["pnl"] if n else pd.Series(dtype=float)
    fees = float(trades["fees"].sum()) if n else 0.0
    wins, losses = pnl[pnl > 0], pnl[pnl <= 0]
    gp, gl = float(wins.sum()), float(-losses.sum())
    sd = rets.std(ddof=0)
    dsd = rets[rets < 0].std(ddof=0) if (rets < 0).any() else 0.0
    ann = math.sqrt(bars_per_year)
    return {
        "initial_equity": initial,
        "final_equity": final,
        "net_return_pct": 100 * (final / initial - 1),
        "gross_return_pct": 100 * ((final + fees) / initial - 1),
        "total_fees": fees,
        "total_slippage": float(trades["slippage"].sum()) if n else 0.0,
        "trades": n,
        "win_rate_pct": 100 * len(wins) / n if n else 0.0,
        "profit_factor": (gp / gl) if gl > 0 else (math.inf if gp > 0 else 0.0),
        "expectancy": float(pnl.mean()) if n else 0.0,
        "avg_win": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss": float(losses.mean()) if len(losses) else 0.0,
        "sharpe": float(rets.mean() / sd * ann) if sd > 0 else 0.0,
        "sortino": float(rets.mean() / dsd * ann) if dsd > 0 else 0.0,
        "max_drawdown_pct": max_drawdown(equity),
        "exposure_pct": float(100 * trades["bars"].sum() / max(1, len(equity))) if n else 0.0,
    }


def summarize_returns(r: np.ndarray) -> dict:
    r = np.asarray(r, dtype=float)
    if len(r) == 0:
        return {}
    return {
        "n": int(len(r)), "mean": float(r.mean()), "median": float(np.median(r)), "std": float(r.std(ddof=0)),
        "p05": float(np.percentile(r, 5)), "p95": float(np.percentile(r, 95)),
        "min": float(r.min()), "max": float(r.max()), "pct_positive": float(100 * (r > 0).mean()),
    }
