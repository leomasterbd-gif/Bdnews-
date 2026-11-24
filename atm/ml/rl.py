"""Lightweight reinforcement-learning experiment: tabular Q-learning on discretised,
causal state features with a cost-aware reward. Trained on the training split only and
evaluated out-of-sample through the standard backtest engine. It is a research baseline
for RL, not a production policy (Stable-Baselines3/PPO would need far more data)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..features import indicators as ind


def _states(df: pd.DataFrame) -> np.ndarray:
    r = ind.rsi(df.close, 14)
    g = (ind.ema(df.close, 20) - ind.ema(df.close, 100)) / df.close
    v = ind.realized_vol(df.close, 24)
    rb = np.digitize(r.fillna(50), [30, 45, 55, 70])
    gb = np.digitize(g.fillna(0), [-0.004, 0, 0.004])
    vb = np.digitize(v.fillna(v.median()), [v.quantile(0.33), v.quantile(0.66)])
    return (rb * 4 + gb) * 3 + vb  # 5*4*3 = 60 states


def train_q(df: pd.DataFrame, train_end: int, fee: float = 0.001, episodes: int = 30, alpha=0.05, gamma=0.95, eps=0.1, seed=0):
    rng = np.random.default_rng(seed)
    s = _states(df)
    lr = np.log(df.close).diff().shift(-1).fillna(0).to_numpy()  # reward for holding from t to t+1
    Q = np.zeros((60, 2, 2))  # state, position(0/1), action(0 flat / 1 long)
    for _ in range(episodes):
        pos = 0
        for t in range(300, train_end - 1):
            a = rng.integers(2) if rng.random() < eps else int(np.argmax(Q[s[t], pos]))
            reward = (lr[t] if a == 1 else 0.0) - (fee if a != pos else 0.0)
            nxt = np.max(Q[s[t + 1], a])
            Q[s[t], pos, a] += alpha * (reward + gamma * nxt - Q[s[t], pos, a])
            pos = a
    return Q


def q_signals(df: pd.DataFrame, Q: np.ndarray, atr_stop: float = 2.0) -> pd.DataFrame:
    s = _states(df)
    want_long = np.array([Q[st, 0, 1] > Q[st, 0, 0] for st in s])
    hold_long = np.array([Q[st, 1, 1] > Q[st, 1, 0] for st in s])
    at = ind.atr(df, 14)
    return pd.DataFrame({"entry": want_long, "exit": ~hold_long, "stop_dist": at * atr_stop, "tp_dist": np.nan}, index=df.index)
