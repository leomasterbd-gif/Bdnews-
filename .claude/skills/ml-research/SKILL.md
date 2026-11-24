---
name: ml-research
description: Machine-learning research with purged walk-forward evaluation against simple baselines (logistic regression, random forest, MLP, LightGBM, tabular Q-learning). Use for ML, deep learning, reinforcement learning, feature engineering, hyperparameter optimisation and financial data-science tasks.
---
# ml-research

Covers: Machine Learning · Deep Learning · Reinforcement Learning · Feature Engineering · Financial Data Science · Hyperparameter Optimization.

## Commands
- `python3 scripts/run_ml.py --dataset BTC_USDT-5m --horizon 6`
- Hyperparameter search for rule strategies: `atm/research/optimizer.py` (`genetic_optimizer`, `optuna_optimizer`) — training data only.

## Rules
- Features from `atm/features/engineering.py` only (all causal, tested). Labels = forward return beyond costs; purge gap = horizon + 1 bars between train and test.
- Compare to `baseline_prior` and `baseline_momentum`. A model is a CANDIDATE only if AUC beats the best baseline by >0.02 AND its OOS backtest is net-positive with ≥10 trades.
- Deep sequence models are not trained: ~3k bars/market is far too little. Any GPU spend needs owner approval.
