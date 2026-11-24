"""Immutable risk limits with code-level hard ceilings.

The YAML file can make limits *stricter* but can never exceed the ceilings below.
Nothing in the research / ML / optimisation layers receives a mutable handle.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "config" / "risk_limits.yaml"

# Absolute ceilings (upper bounds for "max_*", lower bounds for "min_*").
HARD_CEILINGS = {
    "max_risk_per_trade_pct": 2.0,
    "max_session_loss_pct": 5.0,
    "max_daily_loss_pct": 8.0,
    "max_drawdown_pct": 20.0,
    "max_exposure_pct": 100.0,
    "max_position_pct": 50.0,
    "max_open_positions": 5,
    "max_consecutive_losses": 6,
    "max_atr_pct": 5.0,
    "max_data_staleness_s": 600,
    "max_spread_bps": 50,
}
HARD_FLOORS = {
    "pause_bars_after_losses": 1,
    "min_bar_quote_volume": 0.0,
    "min_order_notional": 5.0,
}


class RiskConfigError(ValueError):
    pass


@dataclass(frozen=True)
class RiskLimits:
    max_risk_per_trade_pct: float = 1.0
    max_session_loss_pct: float = 3.0
    max_daily_loss_pct: float = 5.0
    max_drawdown_pct: float = 10.0
    max_exposure_pct: float = 60.0
    max_position_pct: float = 30.0
    max_open_positions: int = 2
    max_consecutive_losses: int = 4
    pause_bars_after_losses: int = 12
    max_atr_pct: float = 2.5
    min_bar_quote_volume: float = 20000.0
    max_data_staleness_s: int = 180
    max_spread_bps: float = 15.0
    min_order_notional: float = 5.0
    allow_leverage: bool = False
    allow_short: bool = False
    live_trading_enabled: bool = False

    def __post_init__(self) -> None:
        for k, ceil in HARD_CEILINGS.items():
            v = getattr(self, k)
            if v is None or v <= 0 or v > ceil:
                raise RiskConfigError(f"{k}={v} outside (0, {ceil}]")
        for k, floor in HARD_FLOORS.items():
            if getattr(self, k) < floor:
                raise RiskConfigError(f"{k} below floor {floor}")
        if self.allow_leverage or self.allow_short:
            raise RiskConfigError("leverage/short selling are not permitted in this system")
        if self.live_trading_enabled:
            raise RiskConfigError(
                "live_trading_enabled=true is refused: real-money execution requires legal "
                "eligibility, independent validation and explicit owner authorisation (docs/SECURITY.md)"
            )
        if self.max_position_pct > self.max_exposure_pct:
            raise RiskConfigError("max_position_pct cannot exceed max_exposure_pct")

    @classmethod
    def load(cls, path: Path | str = DEFAULT_PATH) -> "RiskLimits":
        data = yaml.safe_load(Path(path).read_text()) or {}
        known = {f.name for f in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise RiskConfigError(f"unknown risk keys: {sorted(unknown)}")
        return cls(**data)

    def as_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}
