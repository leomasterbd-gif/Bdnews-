import pandas as pd
import pytest

from atm.risk.engine import EntryContext, RiskEngine
from atm.risk.limits import RiskConfigError, RiskLimits

TS = pd.Timestamp("2025-01-01", tz="UTC")


def ctx(**kw):
    base = dict(ts=TS, equity=100.0, cash=100.0, price=100.0, stop_price=99.0, atr_pct=0.5, bar_quote_volume=1e6, spread_bps=1)
    base.update(kw)
    return EntryContext(**base)


def test_yaml_loads_and_is_conservative():
    L = RiskLimits.load()
    assert L.max_risk_per_trade_pct <= 1.0 and not L.live_trading_enabled and not L.allow_leverage


@pytest.mark.parametrize("bad", [dict(max_risk_per_trade_pct=5), dict(max_drawdown_pct=50), dict(live_trading_enabled=True),
                                 dict(allow_leverage=True), dict(allow_short=True), dict(max_open_positions=50),
                                 dict(max_position_pct=70, max_exposure_pct=60), dict(min_order_notional=1.0)])
def test_hard_ceilings_reject(bad):
    with pytest.raises(RiskConfigError):
        RiskLimits(**bad)


def test_frozen():
    L = RiskLimits()
    import dataclasses
    with pytest.raises(dataclasses.FrozenInstanceError):
        L.max_risk_per_trade_pct = 2.0


def test_sizing_risk_and_caps():
    r = RiskEngine(RiskLimits(), 100.0)
    d = r.check_entry(ctx(stop_price=99.0))  # 1% stop -> risk-based notional 100 -> capped at 30% position
    assert d.approved and abs(d.notional - 30.0) < 1e-9
    d = r.check_entry(ctx(stop_price=90.0))  # 10% stop -> 1$ risk -> 10$ notional
    assert d.approved and abs(d.notional - 10.0) < 1e-9
    assert d.qty * (100 - 90) <= 1.0 + 1e-9  # loss at stop <= 1% equity


@pytest.mark.parametrize("kw,reason", [(dict(data_age_s=1000), "stale"), (dict(atr_pct=9), "volatility"),
                                       (dict(bar_quote_volume=10), "liquidity"), (dict(spread_bps=80), "spread"),
                                       (dict(stop_price=101), "invalid stop"), (dict(abnormal_market=True), "abnormal"),
                                       (dict(network_ok=False), "network"), (dict(open_positions=2), "max open"),
                                       (dict(stop_price=50.0), "below min notional")])
def test_rejections(kw, reason):
    d = RiskEngine(RiskLimits(), 100.0).check_entry(ctx(**kw))
    assert not d.approved and any(reason in x for x in d.reasons), d.reasons


def test_consecutive_losses_pause():
    r = RiskEngine(RiskLimits(), 100.0)
    for _ in range(4):
        r.on_trade_closed(-0.5)
    assert r.pause_remaining == RiskLimits().pause_bars_after_losses
    assert not r.check_entry(ctx()).approved
    for i in range(RiskLimits().pause_bars_after_losses):
        r.on_bar(TS + pd.Timedelta(minutes=5 * i), 100.0)
    assert r.check_entry(ctx()).approved


def test_session_halt_and_drawdown_kill():
    r = RiskEngine(RiskLimits(), 100.0)
    r.on_bar(TS, 96.9)  # 3.1% session loss
    assert r.halted_reason and r.must_flatten and not r.check_entry(ctx(equity=96.9, cash=96.9)).approved
    r.start_session(96.9)
    assert r.halted_reason is None
    r.on_bar(TS, 89.0)  # >10% from peak 100
    assert r.killed_reason
    r.start_session(89.0)
    assert r.killed_reason, "drawdown kill requires owner reset"
    r.owner_reset()
    assert not r.must_flatten


def test_emergency_stop_overrides_everything():
    r = RiskEngine(RiskLimits(), 100.0)
    r.emergency_stop("test")
    d = r.check_entry(ctx())
    assert not d.approved and "killed" in d.reasons[0]
