# AI Trading Master — Research Report / গবেষণা প্রতিবেদন

> **All results are simulated on real historical Binance candles (Freqtrade test fixtures). No real money, no live trades.**  
> **সব ফলাফল আসল ঐতিহাসিক ডেটায় সিমুলেশন। কোনো আসল টাকা বা লাইভ ট্রেড নেই।**

Cycle: 2026-11-24T23:12:52.282291+00:00 → 2026-11-24T23:30:27.827261+00:00 (1055.6 s). Walk-forward runs: **135**, total backtests incl. optimiser trials: **44415** (multiple-testing burden disclosed).

**Validated strategies:** 0 → none  
**ML candidates:** none · **RL candidates:** none  
**Should the system trade?** NO — nothing passed every gate; the system stays flat.

## 1. Data / ডেটা

| dataset | symbol | from | to | rows | gaps (missing bars) | OK |
|---|---|---|---|---|---|---|
| BTC_USDT-5m | BTCUSDT | 2025-11-24 00:00 | 2025-12-04 18:45 | 3106 | 0 (0) | ✅ |
| XRP_USDT-5m | XRPUSDT | 2025-11-24 00:00 | 2025-12-04 18:45 | 3106 | 0 (0) | ✅ |
| ETH_BTC-5m | ETHBTC | 2018-01-10 04:55 | 2018-01-30 04:50 | 5760 | 0 (0) | ✅ |
| LTC_BTC-5m | LTCBTC | 2018-01-10 04:55 | 2018-01-30 04:50 | 5760 | 0 (0) | ✅ |
| ADA_BTC-5m | ADABTC | 2018-01-10 04:55 | 2018-01-30 04:50 | 5720 | 5 (40) | ✅ |
| DASH_BTC-5m | DASHBTC | 2018-01-10 04:55 | 2018-01-30 04:50 | 5758 | 2 (2) | ✅ |
| ETC_BTC-5m | ETCBTC | 2018-01-10 04:55 | 2018-01-30 04:45 | 5759 | 0 (0) | ✅ |
| TRX_BTC-5m | TRXBTC | 2018-01-10 04:55 | 2018-01-30 04:50 | 5754 | 6 (6) | ✅ |
| XLM_BTC-5m | XLMBTC | 2018-01-10 04:55 | 2018-01-30 04:50 | 5760 | 0 (0) | ✅ |
| XMR_BTC-5m | XMRBTC | 2018-01-10 04:55 | 2018-01-30 04:50 | 5758 | 2 (2) | ✅ |
| ZEC_BTC-5m | ZECBTC | 2018-01-10 04:55 | 2018-01-30 04:45 | 5757 | 2 (2) | ✅ |
| NXT_BTC-5m | NXTBTC | 2018-01-10 04:55 | 2018-01-30 04:50 | 5760 | 0 (0) | ✅ |
| UNITTEST_BTC-1m | UNKNOWN-BTC | 2017-11-04 23:02 | 2017-11-14 22:59 | 13681 | 538 (717) | ⚠️ |
| XRP_ETH-1m | XRPETH | 2019-10-11 00:00 | 2019-10-13 11:19 | 2469 | 676 (1091) | ⚠️ |

## 2. Walk-forward validation (out-of-sample, after all costs) / ওয়াক-ফরোয়ার্ড যাচাই

Gates: ≥30 OOS trades · OOS return >0 · PF ≥1.15 · ≥60% positive folds · bootstrap P(mean>0) ≥0.90 · holdout >0 · 2× costs ≥0.

| rank | strategy | dataset | OOS % | OOS trades | PF | holdout % | 2× cost % | gates passed | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ichimoku_trend | NXT_BTC-5m | +3.870 | 8 | 2.63 | +0.094 | +0.012 | 4/7 | **REJECTED** |
| 2 | pullback | TRX_BTC-5m | +3.417 | 8 | 2.36 | +0.000 | +0.000 | 4/7 | **REJECTED** |
| 3 | pair_relative | DASH_BTC-5m | +2.649 | 36 | 1.56 | -0.243 | -0.344 | 3/7 | **REJECTED** |
| 4 | macd_stochrsi | XLM_BTC-5m | +2.465 | 60 | 1.23 | +0.920 | +0.270 | 5/7 | **REJECTED** |
| 5 | ema_trend | TRX_BTC-5m | +1.711 | 11 | 1.62 | -0.663 | -0.702 | 2/7 | **REJECTED** |
| 6 | pair_relative | XMR_BTC-5m | +1.484 | 26 | 1.31 | -0.167 | -0.199 | 2/7 | **REJECTED** |
| 7 | vwap_reversion | XLM_BTC-5m | +1.283 | 27 | 1.19 | +1.383 | +1.174 | 4/7 | **REJECTED** |
| 8 | ema_trend | XLM_BTC-5m | +0.730 | 25 | 1.11 | -0.925 | -1.010 | 1/7 | **REJECTED** |
| 9 | ema_trend | BTC_USDT-5m | +0.621 | 8 | 1.89 | +1.441 | +1.411 | 4/7 | **REJECTED** |
| 10 | ema_trend | ADA_BTC-5m | +0.599 | 16 | 1.16 | -0.313 | -0.356 | 2/7 | **REJECTED** |
| 11 | mean_reversion | ZEC_BTC-5m | +0.426 | 22 | 1.12 | -0.105 | -0.149 | 1/7 | **REJECTED** |
| 12 | pair_relative | LTC_BTC-5m | +0.385 | 27 | 1.12 | -0.297 | -0.846 | 1/7 | **REJECTED** |
| 13 | pullback | XLM_BTC-5m | +0.031 | 13 | 1.03 | +2.165 | +1.967 | 3/7 | **REJECTED** |
| 14 | momentum | XRP_USDT-5m | -0.037 | 16 | 0.98 | -0.327 | -0.580 | 0/7 | **REJECTED** |
| 15 | vol_expansion | XMR_BTC-5m | -0.175 | 11 | 0.92 | +0.000 | +0.000 | 1/7 | **REJECTED** |
| 16 | regime_adaptive | ADA_BTC-5m | -0.218 | 25 | 0.97 | -1.102 | -1.467 | 0/7 | **REJECTED** |
| 17 | mean_reversion | BTC_USDT-5m | -0.421 | 15 | 0.59 | -0.127 | -0.133 | 0/7 | **REJECTED** |
| 18 | macd_stochrsi | LTC_BTC-5m | -0.432 | 8 | 0.67 | -0.512 | -0.586 | 0/7 | **REJECTED** |
| 19 | breakout | XRP_USDT-5m | -0.655 | 13 | 0.51 | +1.755 | +1.704 | 2/7 | **REJECTED** |
| 20 | ichimoku_trend | BTC_USDT-5m | -0.696 | 18 | 0.55 | +0.780 | +0.700 | 2/7 | **REJECTED** |
| 21 | ichimoku_trend | ZEC_BTC-5m | -0.740 | 6 | 0.33 | -0.306 | -0.349 | 0/7 | **REJECTED** |
| 22 | vwap_reversion | BTC_USDT-5m | -0.766 | 12 | 0.35 | +0.000 | +0.000 | 1/7 | **REJECTED** |
| 23 | momentum | BTC_USDT-5m | -0.817 | 9 | 0.17 | +0.212 | +0.153 | 2/7 | **REJECTED** |
| 24 | mean_reversion | XRP_USDT-5m | -0.909 | 17 | 0.45 | +0.216 | +0.201 | 2/7 | **REJECTED** |
| 25 | regime_adaptive | XRP_USDT-5m | -0.913 | 15 | 0.33 | +1.141 | +1.050 | 2/7 | **REJECTED** |
| 26 | pullback | NXT_BTC-5m | -0.940 | 14 | 0.85 | +0.000 | +0.000 | 1/7 | **REJECTED** |
| 27 | vwap_reversion | XRP_USDT-5m | -0.975 | 20 | 0.64 | +0.825 | +0.772 | 2/7 | **REJECTED** |
| 28 | buy_hold | BTC_USDT-5m | -1.014 | 6 | 0.59 | +2.355 | +2.342 | 2/7 | **REJECTED** |
| 29 | pullback | ADA_BTC-5m | -1.022 | 13 | 0.81 | -1.495 | -2.055 | 0/7 | **REJECTED** |
| 30 | breakout | BTC_USDT-5m | -1.072 | 14 | 0.28 | +1.035 | +1.017 | 2/7 | **REJECTED** |
| 31 | ichimoku_trend | TRX_BTC-5m | -1.080 | 7 | 0.30 | -0.277 | -0.327 | 0/7 | **REJECTED** |
| 32 | vol_expansion | XRP_USDT-5m | -1.106 | 14 | 0.27 | +0.063 | +0.034 | 2/7 | **REJECTED** |
| 33 | ichimoku_trend | XMR_BTC-5m | -1.118 | 12 | 0.70 | -0.333 | -0.532 | 0/7 | **REJECTED** |
| 34 | ichimoku_trend | XRP_USDT-5m | -1.149 | 11 | 0.00 | +1.475 | +1.432 | 2/7 | **REJECTED** |
| 35 | macd_stochrsi | BTC_USDT-5m | -1.199 | 31 | 0.54 | -0.182 | -0.194 | 1/7 | **REJECTED** |
| 36 | ema_trend | XRP_USDT-5m | -1.250 | 13 | 0.33 | -0.312 | -0.334 | 0/7 | **REJECTED** |
| 37 | pullback | XRP_USDT-5m | -1.258 | 13 | 0.20 | +0.308 | +0.256 | 2/7 | **REJECTED** |
| 38 | macd_stochrsi | ZEC_BTC-5m | -1.266 | 15 | 0.52 | -0.328 | -0.372 | 0/7 | **REJECTED** |
| 39 | regime_adaptive | BTC_USDT-5m | -1.286 | 14 | 0.05 | +0.682 | +0.598 | 2/7 | **REJECTED** |
| 40 | mean_reversion | DASH_BTC-5m | -1.343 | 21 | 0.76 | -0.684 | -1.180 | 0/7 | **REJECTED** |

13/135 runs had positive OOS return; 0 passed all gates. Full table (all 135 runs incl. folds, Monte Carlo and parameters) in `reports/walk_forward.json`.

| family | runs | mean OOS % | best OOS % |
|---|---|---|---|
| stat_arb | 3 | +1.506 | +2.649 |
| pullback | 12 | -1.704 | +3.417 |
| trend_following | 24 | -2.061 | +3.870 |
| adaptive | 12 | -2.225 | -0.218 |
| volatility | 12 | -2.356 | -0.175 |
| momentum | 24 | -3.074 | +2.465 |
| mean_reversion | 24 | -3.127 | +1.283 |
| breakout | 12 | -3.291 | -0.655 |
| baseline | 12 | -5.669 | -1.014 |

## 3. Machine learning vs baselines / মেশিন লার্নিং বনাম সাধারণ বেসলাইন

Purged walk-forward, label = 30-min forward return > 0.25% cost. Threshold fixed at p>0.6 (not tuned on test).

| dataset | model | mean AUC | OOS net % | trades | verdict |
|---|---|---|---|---|---|
| BTC_USDT-5m | logistic | 0.619 | -1.339 | 12 | REJECTED |
| BTC_USDT-5m | random_forest | 0.602 | +0.000 | 0 | REJECTED |
| BTC_USDT-5m | mlp | 0.547 | -1.428 | 14 | REJECTED |
| BTC_USDT-5m | lightgbm | 0.550 | -1.830 | 21 | REJECTED |
| BTC_USDT-5m | baseline_prior | 0.500 | +0.000 | 0 | BASELINE |
| BTC_USDT-5m | baseline_momentum | 0.475 | -4.936 | 73 | BASELINE |
| XRP_USDT-5m | logistic | 0.529 | -1.857 | 13 | REJECTED |
| XRP_USDT-5m | random_forest | 0.561 | +0.000 | 0 | REJECTED |
| XRP_USDT-5m | mlp | 0.555 | -1.852 | 14 | REJECTED |
| XRP_USDT-5m | lightgbm | 0.538 | -2.891 | 33 | REJECTED |
| XRP_USDT-5m | baseline_prior | 0.500 | +0.000 | 0 | BASELINE |
| XRP_USDT-5m | baseline_momentum | 0.491 | -4.687 | 67 | BASELINE |
| ETH_BTC-5m | logistic | 0.520 | -0.675 | 27 | REJECTED |
| ETH_BTC-5m | random_forest | 0.541 | +0.000 | 0 | REJECTED |
| ETH_BTC-5m | mlp | 0.522 | -3.471 | 45 | REJECTED |
| ETH_BTC-5m | lightgbm | 0.526 | -5.567 | 59 | REJECTED |
| ETH_BTC-5m | baseline_prior | 0.500 | +0.000 | 0 | BASELINE |
| ETH_BTC-5m | baseline_momentum | 0.466 | -10.017 | 71 | BASELINE |

### Reinforcement learning (tabular Q-learning, fee-aware reward)

| dataset | OOS net % | trades | verdict |
|---|---|---|---|
| BTC_USDT-5m | -0.560 | 13 | REJECTED |
| XRP_USDT-5m | -1.789 | 18 | REJECTED |
| ETH_BTC-5m | -4.409 | 42 | REJECTED |

## 4. Timeframe study (default parameters, full period, in-sample) / টাইমফ্রেম তুলনা

**BTC_USDT-5m** — net return % by strategy × timeframe

| strategy | 5m | 15m | 30m | 1h |
|---|---|---|---|---|
| buy_hold | +1.22 | +0.21 | +0.54 | +0.54 |
| ema_trend | -2.30 | +1.59 | +1.62 | -0.03 |
| momentum | -1.19 | -1.96 | -0.63 | -0.75 |
| mean_reversion | -0.68 | +0.00 | +0.00 | +0.00 |
| breakout | -1.23 | +0.55 | +0.48 | -0.42 |
| pullback | -1.54 | -0.69 | -0.37 | -0.35 |
| vol_expansion | -2.50 | -0.67 | -0.29 | -0.55 |
| vwap_reversion | -2.69 | -0.18 | -0.28 | +0.26 |
| macd_stochrsi | -1.62 | -0.57 | -0.68 | -0.31 |
| ichimoku_trend | -0.78 | +0.19 | -0.44 | -0.45 |
| regime_adaptive | -0.92 | +0.00 | -0.27 | -0.27 |

**XRP_USDT-5m** — net return % by strategy × timeframe

| strategy | 5m | 15m | 30m | 1h |
|---|---|---|---|---|
| buy_hold | -2.29 | -1.90 | -0.57 | -0.87 |
| ema_trend | -1.56 | -1.34 | -1.19 | -0.45 |
| momentum | -2.25 | -1.21 | -2.07 | -1.68 |
| mean_reversion | +0.49 | -0.29 | -0.38 | -0.73 |
| breakout | +0.93 | -0.39 | +0.45 | +0.00 |
| pullback | -3.26 | -0.63 | -0.73 | -0.63 |
| vol_expansion | -2.11 | -0.23 | -0.63 | -0.74 |
| vwap_reversion | -4.22 | -0.73 | +0.15 | +0.09 |
| macd_stochrsi | -5.92 | +0.29 | +1.15 | +1.67 |
| ichimoku_trend | -0.37 | +0.98 | -0.23 | -1.36 |
| regime_adaptive | -0.60 | -0.76 | -0.65 | -0.19 |

## 5. $100 → $200 four-hour challenge / ৪ ঘণ্টায় $100 → $200 চ্যালেঞ্জ

Independent 4-hour sessions: **1245** (every non-overlapping window of 12 real datasets, fresh $100 each, no resets or exclusions).

| strategy | sessions | target hits | hit rate % | P(loss) % | no-trade % | median % | mean % | worst % | best % | worst DD % | fees $/session |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mean_reversion | 1245 | 0 | 0.00 | 2.2 | 95.5 | +0.000 | -0.002 | -2.485 | +1.081 | 2.23 | 0.003 |
| ichimoku_trend | 1245 | 0 | 0.00 | 21.8 | 72.5 | +0.000 | -0.032 | -1.665 | +5.092 | 2.27 | 0.019 |
| pullback | 1245 | 0 | 0.00 | 15.6 | 77.3 | +0.000 | -0.032 | -1.818 | +1.729 | 1.85 | 0.018 |
| breakout | 1245 | 0 | 0.00 | 21.6 | 70.3 | +0.000 | -0.041 | -1.951 | +4.266 | 2.69 | 0.019 |
| regime_adaptive | 1245 | 0 | 0.00 | 19.4 | 75.4 | +0.000 | -0.041 | -2.408 | +2.890 | 2.15 | 0.019 |
| vol_expansion | 1245 | 0 | 0.00 | 21.8 | 73.0 | +0.000 | -0.043 | -1.415 | +1.278 | 1.51 | 0.020 |
| ema_trend | 1245 | 0 | 0.00 | 18.8 | 76.1 | +0.000 | -0.049 | -1.063 | +2.885 | 2.52 | 0.016 |
| vwap_reversion | 1245 | 0 | 0.00 | 22.3 | 63.1 | +0.000 | -0.050 | -2.103 | +3.222 | 2.70 | 0.029 |
| momentum | 1245 | 0 | 0.00 | 44.1 | 44.9 | +0.000 | -0.117 | -1.929 | +2.574 | 1.96 | 0.054 |
| macd_stochrsi | 1245 | 0 | 0.00 | 48.6 | 37.3 | +0.000 | -0.123 | -1.583 | +5.135 | 2.51 | 0.065 |
| buy_hold | 1245 | 0 | 0.00 | 61.9 | 1.3 | -0.132 | -0.159 | -3.870 | +5.523 | 4.19 | 0.074 |

**Perfect-foresight bounds** (knows every future price, 100% of capital, no stops or risk limits, 0.1% fee per side):

* *Realistic oracle* (trades at bar closes): median **4.96%**, max **55.06%** — never reached +100%.
* *Impossible intrabar oracle* (buys the exact low and sells the exact high of every 5-minute bar): median 27.46%, reached +100% in 4.42% of sessions. No real execution can do this; it is only a strict mathematical ceiling.
* Median |4h price change| 1.03% (max 21.98%).

Doubling analysis for best-by-mean strategy `mean_reversion`: {"doubling_possible": false, "reason": "mean session return <= 0 after costs"}

### Conclusion / উপসংহার

* **English:** Doubling $100 in four hours is not achievable with long-only spot trading under any acceptable risk. No tested strategy hit the target in any session; a trader who knew every future closing price, used 100% of capital and no stops, still never doubled; only a physically impossible trader buying every intrabar low and selling every high did so, in a small minority of sessions. Reaching it would require leverage far beyond what the risk policy allows (effectively gambling). Realistic alternatives: (1) measure success as risk-adjusted return per session and probability of loss; (2) longer horizons (weeks/months) where compounding of a small validated edge can matter; (3) keep capital flat when no strategy is validated — this preserves the $100.
* **বাংলা:** স্পট মার্কেটে লিভারেজ ছাড়া ৪ ঘণ্টায় $100 থেকে $200 করা বাস্তবে সম্ভব নয়। ১,২৪৫টি সেশনের একটিতেও কোনো স্ট্র্যাটেজি লক্ষ্যে পৌঁছায়নি। যে কাল্পনিক ট্রেডার ভবিষ্যতের প্রতিটি ক্লোজিং দাম আগে থেকে জানে, সে-ও একবারও দ্বিগুণ করতে পারেনি; শুধু প্রতিটি ক্যান্ডেলের ঠিক সর্বনিম্ন দামে কিনে সর্বোচ্চ দামে বেচা — যা অসম্ভব — তাতেই অল্প কিছু সেশনে সম্ভব হয়েছে। লক্ষ্য পূরণ করতে বিপজ্জনক মাত্রার লিভারেজ লাগবে, যা জুয়ার সমান এবং আমাদের ঝুঁকি-নীতিতে নিষিদ্ধ। বাস্তবসম্মত বিকল্প: প্রতি সেশনে ঝুঁকি-সমন্বিত রিটার্ন ও ক্ষতির সম্ভাবনা মাপা, দীর্ঘ সময়ের লক্ষ্য রাখা, এবং কোনো স্ট্র্যাটেজি যাচাই না হলে ট্রেড না করে মূলধন রক্ষা করা।

## 6. Bengali summary / বাংলা সারসংক্ষেপ

* মোট 135টি ওয়াক-ফরোয়ার্ড পরীক্ষা ও 44415টি ব্যাকটেস্ট চালানো হয়েছে, ফি, স্প্রেড, স্লিপেজ ও লেটেন্সি সহ।
* সব পরীক্ষায় পাস করা (VALIDATED) স্ট্র্যাটেজি: 0টি। তাই সিস্টেম এখন কোনো ট্রেড করবে না — এটি ইচ্ছাকৃত, মূলধন রক্ষার জন্য।
* মেশিন লার্নিং মডেলগুলোকে সাধারণ বেসলাইনের সাথে তুলনা করা হয়েছে; খরচ বাদে লাভ প্রমাণ না হলে বাতিল করা হয়েছে।
* ডেটা সীমাবদ্ধতা: USDT মার্কেটের ডেটা মাত্র ~১১ দিনের; ২০১৮ সালের BTC-পেয়ার ডেটা ২০ দিনের। লাইভ Binance ডেটা এই পরিবেশে ব্লকড ছিল। আরও ডেটা পেলে ফলাফল আরও নির্ভরযোগ্য হবে।

## 7. Limitations

* Real data covers ~10.8 days (BTC/USDT, XRP/USDT, Nov–Dec 2025) and 20 days (10 BTC-quoted pairs, Jan 2018). Small samples ⇒ wide uncertainty; a strategy that fails here might work elsewhere and vice-versa.
* No historical order-book data: spreads are assumed (0.5–5 bps) rather than measured; order-book imbalance and market-making research need recorded books.
* BTC-quoted pairs are measured in BTC; their $ figures use an approximate Jan-2018 BTC/USD rate for sizing only.
* Forward testing on live data was blocked by the session's network policy; paper sessions here are REPLAY of held-out history.
