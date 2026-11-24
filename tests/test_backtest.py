import itertools

import numpy as np
import pandas as pd
import pytest

from atm.backtest.engine import run_backtest
from atm.backtest.execution import CostModel, ExecutionSimulator, MarketSpec, market_for
from atm.backtest.validation import bootstrap_mean, monte_carlo_trades, split_points
from atm.research.challenge import oracle_long_only, windows
from conftest import make_df

M = MarketSpec("TEST", "USDT", 1.0, 0.01, 0.0001, 5.0, 1.0)
NOFRICTION = CostModel(taker_fee=0.0, slippage_bps=0, range_slip_frac=0, latency_bps=0, reject_prob=0, network_fail_prob=0, max_participation=1.0)
M0 = MarketSpec("TEST", "USDT", 1.0, 0.0001, 0.000001, 5.0, 0.0)


def sig(df, entries=(), exits=(), stop=5.0, tp=np.nan):
    s = pd.DataFrame({"entry": False, "exit": False, "stop_dist": stop, "tp_dist": tp}, index=df.index)
    s.iloc[list(entries), 0] = True
    s.iloc[list(exits), 1] = True
    return s


def test_fill_next_bar_open_and_pnl_exact(limits):
    close = [100, 100, 101, 102, 103, 104, 105, 106]
    df = make_df(close, spread=0.0)
    r = run_backtest(df, sig(df, [1], [4], stop=2), M0, limits, NOFRICTION)
    t = r.trades.iloc[0]
    assert t.entry_px == pytest.approx(df.open.iloc[2]) and t.exit_px == pytest.approx(df.open.iloc[5])
    assert r.metrics["final_equity"] == pytest.approx(100 + t.pnl)
    assert t.pnl == pytest.approx(t.qty * (df.open.iloc[5] - df.open.iloc[2]))


def test_fees_reduce_equity(limits):
    df = make_df([100] * 20, spread=0.0)
    r = run_backtest(df, sig(df, [1], [5], stop=10), M0, limits, CostModel(taker_fee=0.001, slippage_bps=0, range_slip_frac=0,
                                                                              latency_bps=0, reject_prob=0, network_fail_prob=0))
    assert r.metrics["net_return_pct"] < 0 and r.metrics["total_fees"] > 0
    assert r.metrics["final_equity"] == pytest.approx(100 - r.metrics["total_fees"])


def test_stop_has_priority_over_take_profit(limits):
    df = make_df([100] * 10, spread=0.0)
    df.iloc[3, df.columns.get_loc("high")] = 120
    df.iloc[3, df.columns.get_loc("low")] = 80
    r = run_backtest(df, sig(df, [1], [], stop=5, tp=5), M0, limits, NOFRICTION)
    assert r.trades.iloc[0].reason == "stop_loss"


def test_gap_through_stop_fills_at_open(limits):
    close = [100, 100, 100, 90, 90, 90]
    df = make_df(close, spread=0.0)
    df.iloc[3, df.columns.get_loc("open")] = 88
    df.iloc[3, df.columns.get_loc("high")] = 90
    df.iloc[3, df.columns.get_loc("low")] = 87
    r = run_backtest(df, sig(df, [1], [], stop=5), M0, limits, NOFRICTION)
    assert r.trades.iloc[0].exit_px == pytest.approx(88)


def test_no_signal_no_trade(limits):
    df = make_df(np.linspace(100, 110, 100))
    r = run_backtest(df, sig(df), M, limits)
    assert r.metrics["trades"] == 0 and r.metrics["final_equity"] == pytest.approx(100)


def test_spot_never_exceeds_cash_or_risk(limits, btc):
    from atm.strategies.library import STRATEGIES
    from atm.risk.limits import RiskLimits
    L = RiskLimits.load()
    m = market_for("BTCUSDT", "USDT", 90000)
    r = run_backtest(btc, STRATEGIES["momentum"].signals(btc), m, L)
    assert (r.equity > 0).all()
    notional = r.trades.qty * r.trades.entry_px
    assert (notional <= 100 * 0.3 * 1.02).all()


def test_execution_costs_direction_and_precision():
    ex = ExecutionSimulator(M, CostModel(reject_prob=0, network_fail_prob=0))
    b = ex.fill("buy", 0.12345678, 100.0, 101, 99, 1000)
    s = ex.fill("sell", 0.12345678, 100.0, 101, 99, 1000)
    assert b.price > 100 > s.price
    assert abs(b.qty / M.step_size - round(b.qty / M.step_size)) < 1e-6
    assert abs(b.price / M.tick_size - round(b.price / M.tick_size)) < 1e-6
    assert b.fee == pytest.approx(b.qty * b.price * 0.001)


def test_partial_fill_and_min_notional():
    ex = ExecutionSimulator(M, CostModel(reject_prob=0, network_fail_prob=0, max_participation=0.05))
    f = ex.fill("buy", 10.0, 100.0, 101, 99, 100.0)
    assert f.ok and f.partial and f.qty == pytest.approx(5.0)
    f = ex.fill("buy", 0.01, 100.0, 101, 99, 1000)
    assert not f.ok and f.reason == "below_min_notional"


def test_rejects_and_network_failures_happen():
    ex = ExecutionSimulator(M, CostModel(reject_prob=0.5, network_fail_prob=0.2), seed=1)
    reasons = {ex.fill("buy", 1, 100, 101, 99, 1e6).reason for _ in range(200)}
    assert {"exchange_reject", "network_failure", ""} <= reasons


def test_stress_costs_monotone(limits, btc):
    from atm.strategies.library import STRATEGIES
    m = market_for("BTCUSDT", "USDT", 90000)
    s = STRATEGIES["momentum"].signals(btc)
    base = run_backtest(btc, s, m, limits, CostModel(reject_prob=0, network_fail_prob=0)).metrics["net_return_pct"]
    stressed = run_backtest(btc, s, m, limits, CostModel(reject_prob=0, network_fail_prob=0, stress_mult=3)).metrics["net_return_pct"]
    assert stressed < base


def test_market_specs():
    assert market_for("BTCUSDT", "USDT", 1).min_notional == 5.0
    m = market_for("ETHBTC", "BTC", 0.1)
    assert m.usd_per_quote > 1000 and m.min_notional == 0.0001


def test_walk_forward_splits_do_not_overlap():
    folds, (hs, he) = split_points(3000, 4, 0.2, 300)
    for (a, ts, te) in folds:
        assert a < ts < te <= hs
    assert all(folds[i][2] <= folds[i + 1][1] for i in range(len(folds) - 1))
    assert he == 3000


def test_bootstrap_and_monte_carlo():
    b = bootstrap_mean(np.r_[np.ones(50), -np.ones(5)])
    assert b["p_positive"] > 0.99
    mc = monte_carlo_trades(np.array([1.0, -1.0] * 20), 40)
    assert 0 <= mc["prob_loss"] <= 1 and mc["p05_return_pct"] <= mc["p95_return_pct"]


def _brute_oracle(c, fee):
    best = 0.0
    n = len(c)
    for mask in itertools.product([0, 1], repeat=n - 1):  # position held during interval t->t+1
        eq, pos = 1.0, 0
        for t, m in enumerate(mask):
            if m != pos:
                eq *= (1 - fee)
                pos = m
            if pos:
                eq *= c[t + 1] / c[t]
        if pos:
            eq *= (1 - fee)
        best = max(best, eq - 1)
    return 100 * best


@pytest.mark.parametrize("seed", range(5))
def test_oracle_matches_brute_force(seed):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 9)))
    assert oracle_long_only(c, 0.001) == pytest.approx(_brute_oracle(c, 0.001), abs=1e-9)


def test_challenge_windows_non_overlapping(btc):
    w = windows(btc)
    assert all(e - s == 48 for s, e in w)
    assert all(w[i][1] <= w[i + 1][0] for i in range(len(w) - 1))
