"""Model / strategy degradation detection and rollback recommendation."""
from __future__ import annotations

import numpy as np


def degradation(expected_trade_ret_pct: float, expected_std_pct: float, live_trade_rets_pct: list[float],
                z_threshold: float = -2.0, min_trades: int = 10) -> dict:
    """One-sided z-test of live mean trade return vs the validated expectation, plus CUSUM."""
    r = np.asarray(live_trade_rets_pct, float)
    if len(r) < min_trades:
        return {"status": "INSUFFICIENT_DATA", "n": int(len(r)), "recommend_rollback": False}
    se = max(expected_std_pct, 1e-9) / np.sqrt(len(r))
    z = (r.mean() - expected_trade_ret_pct) / se
    k = 0.5 * expected_std_pct
    cusum, worst = 0.0, 0.0
    for x in r:
        cusum = min(0.0, cusum + (x - expected_trade_ret_pct + k))
        worst = min(worst, cusum)
    h = 5 * expected_std_pct
    degraded = bool(z < z_threshold or worst < -h)
    return {"status": "DEGRADED" if degraded else "OK", "n": int(len(r)), "z": float(z), "cusum_min": float(worst),
            "cusum_threshold": float(-h), "recommend_rollback": degraded}
