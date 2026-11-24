"""Generate reports/RESEARCH_REPORT.md (English + Bengali) from the JSON evidence files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "reports"


def _j(n):
    p = R / n
    return json.loads(p.read_text()) if p.exists() else None


def _f(x, nd=3):
    try:
        return f"{float(x):+.{nd}f}" if x is not None else "—"
    except (TypeError, ValueError):
        return str(x)


def write_markdown() -> Path:
    s, wf, ml, rl, ch, tf, dq = (_j(n) for n in ("summary.json", "walk_forward.json", "ml.json", "rl.json", "challenge.json", "timeframes.json", "data_quality.json"))
    L = []
    a = L.append
    a("# AI Trading Master — Research Report / গবেষণা প্রতিবেদন\n")
    a("> **All results are simulated on real historical Binance candles (Freqtrade test fixtures). No real money, no live trades.**  ")
    a("> **সব ফলাফল আসল ঐতিহাসিক ডেটায় সিমুলেশন। কোনো আসল টাকা বা লাইভ ট্রেড নেই।**\n")
    if s:
        a(f"Cycle: {s['started']} → {s['finished']} ({s['seconds']} s). Walk-forward runs: **{s['walk_forward_runs']}**, total backtests incl. optimiser trials: **{s['total_backtest_trials']}** (multiple-testing burden disclosed).\n")
        a(f"**Validated strategies:** {len(s['validated'])} → {s['validated'] or 'none'}  ")
        a(f"**ML candidates:** {s['ml_candidates'] or 'none'} · **RL candidates:** {s['rl_candidates'] or 'none'}  ")
        a(f"**Should the system trade?** {'YES (validated strategy exists)' if s['system_should_trade'] else 'NO — nothing passed every gate; the system stays flat.'}\n")
    if dq:
        a("## 1. Data / ডেটা\n")
        a("| dataset | symbol | from | to | rows | gaps (missing bars) | OK |\n|---|---|---|---|---|---|---|")
        for k, v in dq.items():
            a(f"| {k} | {v['symbol']} | {v['start'][:16]} | {v['end'][:16]} | {v['rows']} | {v['gaps']} ({v['missing_bars']}) | {'✅' if v['ok'] else '⚠️'} |")
        a("")
    if wf:
        a("## 2. Walk-forward validation (out-of-sample, after all costs) / ওয়াক-ফরোয়ার্ড যাচাই\n")
        a("Gates: ≥30 OOS trades · OOS return >0 · PF ≥1.15 · ≥60% positive folds · bootstrap P(mean>0) ≥0.90 · holdout >0 · 2× costs ≥0.\n")
        rows = sorted(wf, key=lambda r: -r["oos_compound_return_pct"])
        a("| rank | strategy | dataset | OOS % | OOS trades | PF | holdout % | 2× cost % | gates passed | verdict |\n|---|---|---|---|---|---|---|---|---|---|")
        for i, r in enumerate(rows[:40], 1):
            g = sum(v["pass"] for v in r["gates"].values())
            pf = r["oos_profit_factor"]
            a(f"| {i} | {r['strategy']} | {r['dataset']} | {_f(r['oos_compound_return_pct'])} | {r['oos_trades']} | {pf if isinstance(pf, str) else f'{pf:.2f}'} | "
              f"{_f(r['holdout']['net_return_pct'])} | {_f(r['stress']['net_return_pct'])} | {g}/7 | **{r['verdict']}** |")
        n_pos = sum(r["oos_compound_return_pct"] > 0 for r in wf)
        a(f"\n{n_pos}/{len(wf)} runs had positive OOS return; {sum(r['verdict'] == 'VALIDATED' for r in wf)} passed all gates. "
          f"Full table (all {len(wf)} runs incl. folds, Monte Carlo and parameters) in `reports/walk_forward.json`.\n")
        fam = {}
        for r in wf:
            fam.setdefault(r["family"], []).append(r["oos_compound_return_pct"])
        a("| family | runs | mean OOS % | best OOS % |\n|---|---|---|---|")
        for k, v in sorted(fam.items(), key=lambda kv: -sum(kv[1]) / len(kv[1])):
            a(f"| {k} | {len(v)} | {_f(sum(v) / len(v))} | {_f(max(v))} |")
        a("")
    if ml:
        a("## 3. Machine learning vs baselines / মেশিন লার্নিং বনাম সাধারণ বেসলাইন\n")
        a("Purged walk-forward, label = 30-min forward return > 0.25% cost. Threshold fixed at p>0.6 (not tuned on test).\n")
        a("| dataset | model | mean AUC | OOS net % | trades | verdict |\n|---|---|---|---|---|---|")
        for d, res in ml.items():
            for m, v in res["models"].items():
                a(f"| {d} | {m} | {(v['mean_auc'] or 0):.3f} | {_f(v['backtest']['net_return_pct'])} | {v['backtest']['trades']} | {v['verdict']} |")
        a("")
    if rl:
        a("### Reinforcement learning (tabular Q-learning, fee-aware reward)\n")
        a("| dataset | OOS net % | trades | verdict |\n|---|---|---|---|")
        for d, v in rl.items():
            a(f"| {d} | {_f(v['oos']['net_return_pct'])} | {v['oos']['trades']} | {v['verdict']} |")
        a("")
    if tf:
        a("## 4. Timeframe study (default parameters, full period, in-sample) / টাইমফ্রেম তুলনা\n")
        for d, tfs in tf.items():
            a(f"**{d}** — net return % by strategy × timeframe\n")
            names = list(next(iter(tfs.values())).keys())
            a("| strategy | " + " | ".join(tfs) + " |\n|---|" + "---|" * len(tfs))
            for n in names:
                a(f"| {n} | " + " | ".join(_f(tfs[t][n]["net_return_pct"], 2) for t in tfs) + " |")
            a("")
    if ch:
        o = ch["oracle"]
        a("## 5. $100 → $200 four-hour challenge / ৪ ঘণ্টায় $100 → $200 চ্যালেঞ্জ\n")
        a(f"Independent 4-hour sessions: **{o['sessions']}** (every non-overlapping window of 12 real datasets, fresh $100 each, no resets or exclusions).\n")
        a("| strategy | sessions | target hits | hit rate % | P(loss) % | no-trade % | median % | mean % | worst % | best % | worst DD % | fees $/session |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
        for n, v in sorted(ch["summary"].items(), key=lambda kv: -kv[1]["mean_return_pct"]):
            a(f"| {n} | {v['sessions']} | {v['target_hits']} | {v['target_hit_rate_pct']:.2f} | {v['prob_loss_pct']:.1f} | {v['prob_no_trade_pct']:.1f} | "
              f"{_f(v['median_return_pct'])} | {_f(v['mean_return_pct'])} | {_f(v['worst_return_pct'])} | {_f(v['best_return_pct'])} | {v['worst_max_dd_pct']:.2f} | {v['mean_fees_usd']:.3f} |")
        a(f"\n**Perfect-foresight upper bound** (knows every future price, 100% capital, no risk limits, fees included): "
          f"median **{o['oracle_median_pct']:.2f}%**, 95th pct {o['oracle_p95_pct']:.2f}%, max **{o['oracle_max_pct']:.2f}%**, "
          f"target reached in **{o['oracle_target_hit_rate_pct']:.2f}%** of sessions. Median |4h price change| {o['abs_price_change_median_pct']:.2f}% (max {o['abs_price_change_max_pct']:.2f}%).\n")
        d = ch.get("doubling_analysis", {})
        a(f"Doubling analysis for best-by-mean strategy `{ch['best_by_mean']}`: {json.dumps(d)}\n")
        a("### Conclusion / উপসংহার\n")
        a("* **English:** Doubling $100 in four hours is not achievable with long-only spot trading under any acceptable risk: even an impossible "
          "perfect-foresight trader with 100% of capital and no stops reached +100% in the share of sessions shown above. Reaching it would require "
          "leverage far beyond what the risk policy allows (effectively gambling). Realistic alternatives: (1) measure success as risk-adjusted return per "
          "session and probability of loss; (2) longer horizons (weeks/months) where compounding of a small validated edge can matter; (3) keep capital "
          "flat when no strategy is validated — this preserves the $100.")
        a("* **বাংলা:** স্পট মার্কেটে লিভারেজ ছাড়া ৪ ঘণ্টায় $100 থেকে $200 করা বাস্তবে সম্ভব নয়। এমনকি যে কাল্পনিক ট্রেডার ভবিষ্যতের প্রতিটি দাম আগে থেকে জানে, "
          "সে-ও প্রায় কোনো সেশনেই লক্ষ্যে পৌঁছাতে পারেনি (উপরের সংখ্যা দেখুন)। লক্ষ্য পূরণ করতে বিপজ্জনক মাত্রার লিভারেজ লাগবে, যা জুয়ার সমান এবং আমাদের ঝুঁকি-নীতিতে নিষিদ্ধ। "
          "বাস্তবসম্মত বিকল্প: প্রতি সেশনে ঝুঁকি-সমন্বিত রিটার্ন ও ক্ষতির সম্ভাবনা মাপা, দীর্ঘ সময়ের লক্ষ্য রাখা, এবং কোনো স্ট্র্যাটেজি যাচাই না হলে ট্রেড না করে মূলধন রক্ষা করা।\n")
    a("## 6. Bengali summary / বাংলা সারসংক্ষেপ\n")
    if s:
        a(f"* মোট {s['walk_forward_runs']}টি ওয়াক-ফরোয়ার্ড পরীক্ষা ও {s['total_backtest_trials']}টি ব্যাকটেস্ট চালানো হয়েছে, ফি, স্প্রেড, স্লিপেজ ও লেটেন্সি সহ।")
        a(f"* সব পরীক্ষায় পাস করা (VALIDATED) স্ট্র্যাটেজি: {len(s['validated'])}টি। " + ("তাই সিস্টেম এখন কোনো ট্রেড করবে না — এটি ইচ্ছাকৃত, মূলধন রক্ষার জন্য।" if not s["system_should_trade"] else "শুধু এগুলোই পেপার ট্রেডিংয়ে যেতে পারবে।"))
        a("* মেশিন লার্নিং মডেলগুলোকে সাধারণ বেসলাইনের সাথে তুলনা করা হয়েছে; খরচ বাদে লাভ প্রমাণ না হলে বাতিল করা হয়েছে।")
        a("* ডেটা সীমাবদ্ধতা: USDT মার্কেটের ডেটা মাত্র ~১১ দিনের; ২০১৮ সালের BTC-পেয়ার ডেটা ২০ দিনের। লাইভ Binance ডেটা এই পরিবেশে ব্লকড ছিল। আরও ডেটা পেলে ফলাফল আরও নির্ভরযোগ্য হবে।")
    a("\n## 7. Limitations\n")
    a("* Real data covers ~10.8 days (BTC/USDT, XRP/USDT, Nov–Dec 2025) and 20 days (10 BTC-quoted pairs, Jan 2018). Small samples ⇒ wide uncertainty; a strategy that fails here might work elsewhere and vice-versa.")
    a("* No historical order-book data: spreads are assumed (0.5–5 bps) rather than measured; order-book imbalance and market-making research need recorded books.")
    a("* BTC-quoted pairs are measured in BTC; their $ figures use an approximate Jan-2018 BTC/USD rate for sizing only.")
    a("* Forward testing on live data was blocked by the session's network policy; paper sessions here are REPLAY of held-out history.")
    out = R / "RESEARCH_REPORT.md"
    out.write_text("\n".join(L) + "\n")
    return out
