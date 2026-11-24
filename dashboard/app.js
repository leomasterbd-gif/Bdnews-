/* AI Trading Master — owner control center (static SPA, no external JS).
 * Every figure shown comes from the API. Missing data renders as an explicit empty state.
 * All API-provided strings are inserted with textContent / DOM building (XSS-safe). */
'use strict';
(function () {

  // ------------------------------------------------------------------ i18n
  const I18N = {
    bn: {
      app_name: 'এআই ট্রেডিং মাস্টার', app_sub: 'মালিকের কন্ট্রোল সেন্টার · রিসার্চ ও সিমুলেশন',
      login_title: 'মালিক লগইন', login_desc: 'সার্ভারে সেট করা মালিকের টোকেন দিয়ে প্রবেশ করুন। টোকেনটি শুধু এই ব্রাউজার ট্যাবের সেশনে থাকে।',
      token: 'মালিকের টোকেন', token_ph: 'টোকেন লিখুন', login_btn: 'প্রবেশ করুন', logging_in: 'যাচাই করা হচ্ছে…',
      err_token: 'টোকেন সঠিক নয়।', err_rate: 'অনেকবার চেষ্টা হয়েছে — এক মিনিট অপেক্ষা করুন।', err_network: 'সার্ভারের সাথে সংযোগ হয়নি।',
      login_note: 'এই সিস্টেম কোনো আসল অর্ডার পাঠায় না।', logout: 'লগআউট', refresh: 'রিফ্রেশ', menu: 'মেনু',
      ws_open: 'সার্ভার সংযুক্ত', ws_retry: 'পুনঃসংযোগ…', ws_off: 'সার্ভার বিচ্ছিন্ন', session_expired: 'সেশন শেষ — আবার লগইন করুন।',
      g_command: 'কমান্ড', g_trading: 'ট্রেডিং (সিমুলেটেড)', g_research: 'রিসার্চ', g_risk: 'ঝুঁকি ও বিশ্লেষণ', g_system: 'সিস্টেম',
      s_overview: 'নির্বাহী সারসংক্ষেপ', s_portfolio: 'ভার্চুয়াল পোর্টফোলিও', s_market: 'মার্কেট ইন্টেলিজেন্স', s_scanner: 'মার্কেট স্ক্যানার',
      s_terminal: 'ট্রেডিং সিমুলেশন টার্মিনাল', s_agents: 'এআই এজেন্ট কন্ট্রোল', s_strategies: 'স্ট্র্যাটেজি রিসার্চ ল্যাব', s_backtests: 'ব্যাকটেস্টিং ল্যাব',
      s_ml: 'মেশিন লার্নিং সেন্টার', s_challenge: 'চার ঘণ্টার লক্ষ্য চ্যালেঞ্জ', s_risk: 'ঝুঁকি ব্যবস্থাপনা কেন্দ্র', s_pnl: 'লাভ-ক্ষতি বিশ্লেষণ',
      s_trades: 'ট্রেড ইতিহাস', s_heatmap: 'মার্কেট হিটম্যাপ', s_reports: 'রিসার্চ রিপোর্ট', s_learning: 'এআই শেখার ইতিহাস',
      s_leaderboard: 'স্ট্র্যাটেজি লিডারবোর্ড', s_apis: 'এপিআই ব্যবস্থাপনা', s_security: 'নিরাপত্তা কেন্দ্র', s_system: 'সিস্টেম স্বাস্থ্য',
      s_costs: 'অবকাঠামো খরচ', s_audit: 'অডিট লগ', s_settings: 'মালিকের সেটিংস',
      d_overview: 'সিস্টেমের অবস্থা, রিসার্চের ফলাফল ও পেপার-ট্রেডিং এক নজরে।',
      d_portfolio: 'ভার্চুয়াল $১০০ মূলধনের পেপার/রিপ্লে সেশন — প্রতি ২ সেকেন্ডে লাইভ আপডেট।',
      d_market: 'ঐতিহাসিক ডেটাসেটের মূল্য, ভোলাটিলিটি, রেজিম, পারস্পরিক সম্পর্ক ও ডেটার মান।',
      d_scanner: 'প্রতিটি ডেটাসেটের শেষ সংরক্ষিত বারে প্রতিটি স্ট্র্যাটেজির সিগন্যাল।',
      d_terminal: 'ক্যান্ডেলস্টিক চার্ট (EMA ও বলিঙ্গার) এবং পেপার সেশনের লাইভ লগ।',
      d_agents: 'এলএলএম সাব-এজেন্ট সংজ্ঞা, স্কিল ও নির্ধারিত (deterministic) সার্ভিস।',
      d_strategies: 'স্ট্র্যাটেজি লাইব্রেরি, ডিফল্ট প্যারামিটার, যাচাই-গেট ও রেজিস্ট্রি।',
      d_backtests: 'ওয়াক-ফরোয়ার্ড ফলাফল: ফোল্ড, হোল্ডআউট, স্ট্রেস টেস্ট, মন্টে কার্লো ও গেট।',
      d_ml: 'ক্লাসিফায়ার বনাম বেসলাইন (purged walk-forward) এবং রিইনফোর্সমেন্ট লার্নিং পরীক্ষা।',
      d_challenge: '৪ ঘণ্টায় $১০০ → $২০০ লক্ষ্য কি বাস্তবসম্মত? সৎ পরিসংখ্যানগত উত্তর।',
      d_risk: 'ঝুঁকির সীমা, বর্তমান অবস্থা, ঘটনা এবং জরুরি স্টপ।',
      d_pnl: 'ভার্চুয়াল ইকুইটি কার্ভ, ড্রডাউন ও প্রতি ট্রেডের লাভ-ক্ষতি।',
      d_trades: 'সংরক্ষিত সব ভার্চুয়াল (পেপার/রিপ্লে) ট্রেড।',
      d_heatmap: 'ডেটাসেটভিত্তিক মূল্য পরিবর্তন এবং স্ট্র্যাটেজি × টাইমফ্রেম নেট রিটার্ন।',
      d_reports: 'রিসার্চ চক্রের তৈরি রিপোর্ট ফাইল ও মূল রিসার্চ রিপোর্ট।',
      d_learning: 'প্রতিটি পরীক্ষার হাইপোথিসিস ও রায় — ব্যর্থ পরীক্ষাও সংরক্ষিত থাকে।',
      d_leaderboard: 'আউট-অব-স্যাম্পল রিটার্ন অনুযায়ী সাজানো ওয়াক-ফরোয়ার্ড ফলাফল।',
      d_apis: 'কোন সিক্রেট কনফিগার করা আছে (শুধু হ্যাঁ/না) এবং এক্সচেঞ্জ সংযোগের অবস্থা।',
      d_security: 'অডিট চেইনের অখণ্ডতা, প্রমাণীকরণ নীতি ও নিরাপত্তা স্ক্যান।',
      d_system: 'সার্ভারের রিসোর্স, আপটাইম ও টেস্টের ফলাফল।',
      d_costs: 'মাসিক খরচের অনুমান ও পরিমাপিত খরচ।',
      d_audit: 'হ্যাশ-চেইনযুক্ত, শুধু-সংযোজনযোগ্য অডিট লগ।',
      d_settings: 'ভাষা, রিপ্লে ডেটাসেট ও গতি, শ্যাডো স্ট্র্যাটেজি এবং টেলিগ্রাম আইডি।',
      loading: 'লোড হচ্ছে…', retry: 'আবার চেষ্টা', load_error: 'ডেটা লোড করা যায়নি', http_error: 'সার্ভার উত্তর: {code}',
      not_run: 'এখনো চালানো হয়নি', not_run_desc: 'রিসার্চ চক্র এই রিপোর্টটি এখনো তৈরি করেনি ({file})। চক্র শেষ হলে রিফ্রেশ করুন — এখানে কোনো অনুমিত সংখ্যা দেখানো হয় না।',
      no_data: 'কোনো ডেটা নেই', server_msg: 'সার্ভার বার্তা', yes: 'হ্যাঁ', no: 'না', none: 'কোনোটি নয়', all: 'সব',
      enabled: 'চালু', disabled: 'বন্ধ', configured: 'কনফিগার করা', not_configured: 'কনফিগার করা নেই', ok: 'ঠিক আছে', fail: 'ব্যর্থ',
      cancel: 'বাতিল', confirm: 'নিশ্চিত করুন', save: 'সংরক্ষণ', saved: 'সংরক্ষিত হয়েছে', save_failed: 'সংরক্ষণ ব্যর্থ',
      mode: 'মোড', live_trading: 'লাইভ ট্রেডিং', paper_feed: 'পেপার ফিড', testnet: 'টেস্টনেট', historical_data: 'ঐতিহাসিক ডেটা',
      data_sources: 'ডেটার উৎস', paper_session: 'পেপার সেশন', paper_inactive: 'পেপার সেশন সক্রিয় নয়',
      paper_inactive_desc: 'কোনো সক্রিয় ভার্চুয়াল সেশন নেই, তাই কোনো পোর্টফোলিও সংখ্যা দেখানো হচ্ছে না।',
      virtual_capital: 'ভার্চুয়াল প্রারম্ভিক মূলধন', research_summary: 'রিসার্চ সারসংক্ষেপ', research_not_run: 'রিসার্চ চক্র এখনো শেষ হয়নি',
      wf_runs: 'ওয়াক-ফরোয়ার্ড রান', validated: 'যাচাইকৃত', total_trials: 'মোট ব্যাকটেস্ট ট্রায়াল', should_trade: 'সিস্টেম কি ট্রেড করবে?',
      challenge_best: 'চ্যালেঞ্জে সেরা (গড়)', best_hit_rate: 'সেরার লক্ষ্য-অর্জন হার', oracle_hit_rate: 'ওরাকল লক্ষ্য-অর্জন হার',
      finished: 'শেষ হয়েছে', duration: 'সময়কাল', validated_list: 'যাচাইকৃত স্ট্র্যাটেজি', none_validated: 'কোনো স্ট্র্যাটেজি সব যাচাই-গেট পাস করেনি। সিস্টেম তাই ফ্ল্যাট থাকে (ডিজাইন অনুযায়ী)।',
      ml_candidates: 'এমএল ক্যান্ডিডেট', rl_candidates: 'আরএল ক্যান্ডিডেট', risk_limits: 'ঝুঁকির সীমা', oracle: 'ওরাকল (তাত্ত্বিক ঊর্ধ্বসীমা)',
      equity: 'ইকুইটি', cash: 'নগদ', net_pnl: 'নেট লাভ/ক্ষতি', fees: 'ফি', position: 'পজিশন', entry_px: 'এন্ট্রি মূল্য', stop_px: 'স্টপ মূল্য',
      last_price: 'শেষ মূল্য', closed_trades: 'বন্ধ ট্রেড', wins: 'লাভজনক', win_rate: 'জয়ের হার', strategy: 'স্ট্র্যাটেজি', symbol: 'সিম্বল',
      session_id: 'সেশন আইডি', running: 'চলমান', stopped: 'থেমে আছে', equity_curve: 'ইকুইটি কার্ভ', initial: 'প্রারম্ভিক', params: 'প্যারামিটার',
      no_curve: 'এখনো কোনো ইকুইটি পয়েন্ট নেই।', updated: 'আপডেট', live_ws: 'ওয়েবসকেট (২ সে.)',
      markets: 'মার্কেট', dataset: 'ডেটাসেট', era: 'সময়কাল', chg_4h: '৪ঘ পরিবর্তন', chg_total: 'মোট পরিবর্তন', regime: 'রেজিম',
      quality: 'ডেটার মান', correlation: 'রিটার্নের পারস্পরিক সম্পর্ক (৫ মিনিট, লগ রিটার্ন)', rows: 'সারি', gaps: 'গ্যাপ', missing_bars: 'অনুপস্থিত বার',
      dupes: 'ডুপ্লিকেট', bad_ohlc: 'ত্রুটিপূর্ণ OHLC', max_ret: 'সর্বোচ্চ |রিটার্ন|', issues: 'সমস্যা', start: 'শুরু', end: 'শেষ', last_bar: 'শেষ বার',
      corr_note: 'ভিন্ন সময়কালের ডেটাসেটে ওভারল্যাপ নেই — সেখানে ঘর ফাঁকা।',
      signals: 'সিগন্যাল', as_of: 'সময়', entry: 'এন্ট্রি', exit: 'এক্সিট', scanner_legend: 'ENTRY = প্রবেশ সংকেত · EXIT = প্রস্থান সংকেত · — = কোনো সংকেত নেই',
      entries_now: 'বর্তমানে এন্ট্রি সংকেত',
      interval: 'ইন্টারভাল', bars: 'বার', chart: 'চার্ট', start_paper: 'পেপার সেশন শুরু', paper_started: 'পেপার সেশন চলছে',
      paper_not_started: 'পেপার সেশন শুরু হয়নি', session_log: 'সেশন লগ', session_trades: 'সেশনের ট্রেড', no_log: 'লগে এখনো কিছু নেই।',
      no_trades: 'এখনো কোনো ভার্চুয়াল ট্রেড হয়নি।', side: 'দিক', qty: 'পরিমাণ', price: 'মূল্য', pnl: 'লাভ/ক্ষতি', reason: 'কারণ', source: 'উৎস', time: 'সময়',
      ohlc_hist_note: 'চার্টের ক্যান্ডেল ঐতিহাসিক ডেটা থেকে — লাইভ নয়।',
      agents: 'এজেন্ট', skills: 'স্কিল', services: 'নির্ধারিত সার্ভিস', model: 'মডেল', kind: 'ধরন', file: 'ফাইল', path: 'পথ', description: 'বিবরণ',
      no_agents: 'কোনো এজেন্ট সংজ্ঞা পাওয়া যায়নি (.claude/agents/*.md)।', no_skills: 'কোনো স্কিল পাওয়া যায়নি (.claude/skills/*/SKILL.md)।',
      agents_note: 'এজেন্টগুলো চাহিদা অনুযায়ী চলে; সব ট্রেডিং সিদ্ধান্ত নির্ধারিত পাইথন কোড নেয়, এলএলএম নয়।',
      library: 'স্ট্র্যাটেজি লাইব্রেরি', family: 'পরিবার', defaults: 'ডিফল্ট', gates: 'যাচাই-গেট', registry: 'স্ট্র্যাটেজি রেজিস্ট্রি',
      version: 'ভার্সন', status: 'অবস্থা', created: 'তৈরি', gate_results: 'গেট ফলাফল (ডেটাসেট অনুযায়ী)', no_wf: 'ওয়াক-ফরোয়ার্ড ফলাফল এখনো নেই।',
      passed_n: '{n}/{m} পাস', registry_empty: 'রেজিস্ট্রি খালি।',
      g_oos_trades: 'OOS ট্রেড সংখ্যা', g_oos_net_return_positive: 'OOS নেট রিটার্ন > 0', g_profit_factor: 'প্রফিট ফ্যাক্টর', g_positive_folds: 'লাভজনক ফোল্ড',
      g_bootstrap_p_positive: 'বুটস্ট্র্যাপ P(>0)', g_holdout_positive: 'হোল্ডআউট > 0', g_stress_2x_costs_nonnegative: '২× খরচে ≥ 0',
      runs: 'রান', oos_return: 'OOS রিটার্ন', oos_trades: 'OOS ট্রেড', pf: 'PF', holdout: 'হোল্ডআউট', stress: 'স্ট্রেস (২× খরচ)', verdict: 'রায়',
      folds: 'ফোল্ড', fold_returns: 'ফোল্ডভিত্তিক নেট রিটার্ন', monte_carlo: 'মন্টে কার্লো', bootstrap: 'বুটস্ট্র্যাপ', final_params: 'চূড়ান্ত প্যারামিটার',
      test_start: 'টেস্ট শুরু', test_end: 'টেস্ট শেষ', net_return: 'নেট রিটার্ন', trades_n: 'ট্রেড', max_dd: 'সর্বোচ্চ ড্রডাউন', sharpe: 'শার্প',
      select_run: 'বিস্তারিত দেখতে একটি রান বাছুন', optimised: 'অপ্টিমাইজড', filter_dataset: 'ডেটাসেট', filter_verdict: 'রায়', filter_strategy: 'স্ট্র্যাটেজি',
      sims: 'সিমুলেশন', median_ret: 'মিডিয়ান রিটার্ন', p05_ret: 'P05 রিটার্ন', p95_ret: 'P95 রিটার্ন', p95_dd: 'P95 ড্রডাউন', p_positive: 'P(গড় > 0)',
      ci: '৯০% আস্থা-সীমা', gross_return: 'গ্রস রিটার্ন', exposure: 'এক্সপোজার', expectancy: 'প্রত্যাশা', win_rate_short: 'জয়%',
      ml_models: 'মডেল তুলনা', horizon: 'হরাইজন (বার)', label_pos: 'লেবেল পজিটিভ হার', auc: 'গড় AUC', brier: 'ব্রায়ার', threshold: 'থ্রেশহোল্ড',
      ml_auc_chart: 'গড় AUC (০.৫ = এলোমেলো অনুমান)', rl_title: 'রিইনফোর্সমেন্ট লার্নিং (Q-learning)', train_bars: 'প্রশিক্ষণ বার',
      ml_not_run: 'এমএল রিপোর্ট এখনো নেই', rl_not_run: 'আরএল রিপোর্ট এখনো নেই',
      challenge_q: 'প্রশ্ন: ৪ ঘণ্টার সেশনে কি $১০০ কে $২০০ (+১০০%) করা যায়, ঝুঁকির সীমা মেনে?',
      sessions: 'সেশন', target_hits: 'লক্ষ্য অর্জন', hit_rate: 'অর্জন হার', prob_loss: 'ক্ষতির সম্ভাবনা', no_trade: 'ট্রেডহীন',
      median: 'মিডিয়ান', mean: 'গড়', worst: 'সবচেয়ে খারাপ', best: 'সেরা', worst_dd: 'সবচেয়ে খারাপ DD', mean_fees: 'গড় ফি', consistency: 'লাভজনক সেশন',
      oracle_desc: 'ভবিষ্যৎ জানা থাকলে (অসম্ভব) লং-অনলি ট্রেডিংয়ে সর্বোচ্চ কত হতো — এটি একটি তাত্ত্বিক ঊর্ধ্বসীমা, বাস্তব প্রত্যাশা নয়।',
      oracle_median: 'ওরাকল মিডিয়ান', oracle_p95: 'ওরাকল P95', oracle_max: 'ওরাকল সর্বোচ্চ', abs_move_med: '|মূল্য পরিবর্তন| মিডিয়ান', abs_move_max: '|মূল্য পরিবর্তন| সর্বোচ্চ',
      doubling: 'দ্বিগুণ হওয়ার বিশ্লেষণ (বুটস্ট্র্যাপ)', doubling_possible: 'দ্বিগুণ সম্ভব?', p_double: 'সীমার মধ্যে দ্বিগুণের সম্ভাবনা',
      median_sessions: 'মিডিয়ান সেশন সংখ্যা', max_sessions: 'সর্বোচ্চ সেশন', p_ruin: '৫০% হারানোর সম্ভাবনা',
      session_hist: 'সেশন রিটার্নের হিস্টোগ্রাম', target_line: 'লক্ষ্য', sessions_missing: 'এই স্ট্র্যাটেজির সেশন-ভিত্তিক ডেটা নেই।', capital: 'মূলধন', target: 'লক্ষ্য',
      limits: 'সীমা', risk_state: 'বর্তমান ঝুঁকি অবস্থা', risk_events: 'ঝুঁকির ঘটনা', kill_switch: 'কিল সুইচ', active: 'সক্রিয়', inactive: 'নিষ্ক্রিয়',
      no_risk_state: 'কোনো সক্রিয় সেশন নেই — রিয়েল-টাইম ঝুঁকি অবস্থা প্রযোজ্য নয়।', no_events: 'কোনো ঝুঁকির ঘটনা নেই।',
      estop: 'জরুরি স্টপ', estop_sub: 'সব ভার্চুয়াল পজিশন বন্ধ করে নতুন সেশন আটকে দেয়',
      estop_confirm_t: 'জরুরি স্টপ নিশ্চিত করবেন?', estop_confirm_b: 'এটি data/KILL ফাইল তৈরি করবে, চলমান পেপার সেশন ফ্ল্যাট করবে এবং অডিট লগে লিখবে। পুনরায় চালু করতে RESUME টাইপ করতে হবে।',
      estop_done: 'জরুরি স্টপ সক্রিয় হয়েছে।', resume: 'পুনরায় চালু', resume_t: 'পুনরায় চালু করবেন?', resume_b: 'নিশ্চিত করতে নিচে RESUME টাইপ করুন।',
      resume_done: 'কিল সুইচ সরানো হয়েছে। পেপার সেশন নিজে থেকে শুরু হয় না।', type_resume: 'RESUME লিখুন', risk_editable_note: 'সীমাগুলো API দিয়ে বদলানো যায় না।',
      peak: 'সর্বোচ্চ ইকুইটি', session_start_eq: 'সেশন শুরুর ইকুইটি', day_start_eq: 'দিনের শুরুর ইকুইটি', consec_losses: 'পরপর ক্ষতি', pause_remaining: 'বিরতি বাকি (বার)',
      halted: 'থামানো', killed: 'কিল', event_type: 'ঘটনা',
      drawdown: 'ড্রডাউন', trade_pnl: 'প্রতি ট্রেডের লাভ/ক্ষতি (বন্ধ ট্রেড)', cum_pnl: 'ক্রমবর্ধমান লাভ/ক্ষতি', pnl_none: 'কোনো বন্ধ ভার্চুয়াল ট্রেড নেই — লাভ-ক্ষতি বিশ্লেষণের ডেটা নেই।',
      gross_profit: 'মোট লাভ', gross_loss: 'মোট ক্ষতি', profit_factor: 'প্রফিট ফ্যাক্টর', total_fees: 'মোট ফি', max_dd_curve: 'সর্বোচ্চ ড্রডাউন (কার্ভ থেকে)',
      pnl_quote_note: 'লাভ/ক্ষতি ও ফি কোট মুদ্রায় (যেমন USDT/BTC) সংরক্ষিত।', session: 'সেশন', fee: 'ফি',
      heat_tiles: 'ডেটাসেট মূল্য পরিবর্তন', metric: 'মেট্রিক', tf_grid: 'স্ট্র্যাটেজি × টাইমফ্রেম নেট রিটার্ন (%)', tf_not_run: 'টাইমফ্রেম স্টাডি এখনো চালানো হয়নি',
      files: 'রিপোর্ট ফাইল', no_files: 'reports/ ফোল্ডারে কোনো ফাইল নেই।', report_md: 'RESEARCH_REPORT.md', report_missing: 'মূল রিসার্চ রিপোর্ট এখনো তৈরি হয়নি।',
      experiments: 'পরীক্ষা', hypothesis: 'হাইপোথিসিস', no_experiments: 'এখনো কোনো পরীক্ষা রেকর্ড হয়নি।', by_verdict: 'রায় অনুযায়ী',
      sort_hint: 'কলামের শিরোনামে ক্লিক করে সাজান।',
      secrets: 'সিক্রেট (শুধু হ্যাঁ/না)', connectivity: 'সংযোগ', public_data: 'পাবলিক মার্কেট ডেটা', latency: 'লেটেন্সি', error: 'ত্রুটি', credentials: 'ক্রেডেনশিয়াল',
      keys_note_t: 'কী কোথায় সেট করবেন?', keys_note: 'এপিআই কী ও সিক্রেট শুধুমাত্র সার্ভারের এনভায়রনমেন্ট ভেরিয়েবল হিসেবে সেট করা হয় (যেমন BINANCE_TESTNET_API_KEY)। ড্যাশবোর্ডে কখনো কী টাইপ করবেন না — এখানে শুধু দেখানো হয় কোনটি কনফিগার করা আছে, মান কখনো দেখানো হয় না।',
      audit_chain: 'অডিট চেইন', chain_valid: 'অখণ্ড (বৈধ)', chain_broken: 'ভাঙা — তদন্ত প্রয়োজন', audit_entries: 'অডিট এন্ট্রি', withdrawal: 'উত্তোলন সক্ষমতা',
      auth: 'প্রমাণীকরণ', security_scan: 'নিরাপত্তা স্ক্যান', scan_not_run: 'নিরাপত্তা স্ক্যান এখনো চালানো হয়নি',
      resources: 'রিসোর্স', disk: 'ডিস্ক', memory: 'মেমরি', cpu: 'সিপিইউ', load: 'লোড গড়', db_size: 'ডেটাবেস আকার', reports_size: 'রিপোর্ট আকার',
      python: 'পাইথন', uptime: 'আপটাইম', requests: 'অনুরোধ', paper_thread: 'পেপার থ্রেড', alive: 'চলমান', tests: 'টেস্টের ফলাফল', tests_not_run: 'টেস্ট রিপোর্ট এখনো নেই',
      used: 'ব্যবহৃত', free: 'খালি', cores: 'কোর',
      assumptions: 'মাসিক অনুমান', ledger: 'পরিমাপিত খরচ (লেজার)', measured: 'পরিমাপিত', projected: 'প্রক্ষেপিত মাসিক', ledger_empty: 'লেজারে কোনো খরচ রেকর্ড নেই।',
      cost_vps: 'ভিপিএস', cost_claude: 'Claude API বাজেট', cost_gpu: 'জিপিইউ', cost_data: 'ডেটা ফিড', units: 'ইউনিট', category: 'বিভাগ', amount: 'পরিমাণ (USD)',
      actor: 'কর্তা', action: 'কাজ', detail: 'বিবরণ', hash: 'হ্যাশ', no_audit: 'অডিট লগ খালি।',
      language: 'ভাষা', replay_dataset: 'রিপ্লে ডেটাসেট', replay_speed: 'রিপ্লে গতি (সেকেন্ড/বার)', shadow_strategy: 'শ্যাডো স্ট্র্যাটেজি',
      telegram_id: 'টেলিগ্রাম মালিক আইডি', feed: 'ফিড', shadow_warn: 'শ্যাডো স্ট্র্যাটেজি যাচাই-গেট পাস করেনি। এটি শুধু পর্যবেক্ষণের জন্য রিপ্লে ডেটায় ভার্চুয়াল ট্রেড করে (EXPERIMENTAL_SHADOW)।',
      settings_note: 'পরিবর্তন অডিট লগে লেখা হয়। চলমান সেশনে ডেটাসেট/গতির পরিবর্তন পরের সেশনে কার্যকর হবে।', speed_range: '০.০৫ – ১০ সেকেন্ড',
      telegram_ph: 'সংখ্যাসূচক আইডি (ঐচ্ছিক)', lang_bn: 'বাংলা', lang_en: 'English',
      b_virtual_t: 'ভার্চুয়াল অর্থ — কোনো আসল টাকা নয়', b_hist_t: 'সংরক্ষিত ঐতিহাসিক ডেটা — লাইভ নয়', b_replay_t: 'ঐতিহাসিক বার পুনরায় চালানো হচ্ছে',
      b_shadow_t: 'যাচাই-না-হওয়া পরীক্ষামূলক স্ট্র্যাটেজি', b_blocked_t: 'অনুপলব্ধ / আটকানো', b_research_t: 'রিসার্চ চক্রের ফলাফল',
      h_gain: 'লাভ', h_zero: '০% সহ বিন (ট্রেডহীন সেশনসহ)', h_loss: 'ক্ষতি',
      unknown: 'অজানা', count: 'সংখ্যা', value: 'মান', name: 'নাম', on: 'চালু',
    },
    en: {
      app_name: 'AI Trading Master', app_sub: 'Owner control center · research & simulation',
      login_title: 'Owner sign-in', login_desc: 'Enter the owner token configured on the server. It is kept only in this browser tab\'s session.',
      token: 'Owner token', token_ph: 'Enter token', login_btn: 'Sign in', logging_in: 'Verifying…',
      err_token: 'Invalid token.', err_rate: 'Too many attempts — wait a minute.', err_network: 'Could not reach the server.',
      login_note: 'This system never sends real orders.', logout: 'Log out', refresh: 'Refresh', menu: 'Menu',
      ws_open: 'Server connected', ws_retry: 'Reconnecting…', ws_off: 'Server offline', session_expired: 'Session expired — please sign in again.',
      g_command: 'Command', g_trading: 'Trading (simulated)', g_research: 'Research', g_risk: 'Risk & analytics', g_system: 'System',
      s_overview: 'Executive Overview', s_portfolio: 'Virtual Portfolio', s_market: 'Market Intelligence', s_scanner: 'Market Scanner',
      s_terminal: 'Trading Simulation Terminal', s_agents: 'AI Agent Control Center', s_strategies: 'Strategy Research Lab', s_backtests: 'Backtesting Lab',
      s_ml: 'Machine Learning Center', s_challenge: 'Four-Hour Target Challenge', s_risk: 'Risk Management Center', s_pnl: 'Profit & Loss Analytics',
      s_trades: 'Trade History', s_heatmap: 'Market Heatmap', s_reports: 'Research Reports', s_learning: 'AI Learning History',
      s_leaderboard: 'Strategy Leaderboard', s_apis: 'API Management', s_security: 'Security Center', s_system: 'System Health',
      s_costs: 'Infrastructure Cost', s_audit: 'Audit Logs', s_settings: 'Owner Settings',
      d_overview: 'System status, research outcomes and paper trading at a glance.',
      d_portfolio: 'Paper/replay session on $100 of virtual capital — live updates every 2 seconds.',
      d_market: 'Historical dataset prices, volatility, regime, correlation and data quality.',
      d_scanner: 'Each strategy\'s signal on the last stored bar of every dataset.',
      d_terminal: 'Candlestick chart (EMA & Bollinger) and the paper session\'s live log.',
      d_agents: 'LLM subagent definitions, skills and deterministic services.',
      d_strategies: 'Strategy library, default parameters, validation gates and registry.',
      d_backtests: 'Walk-forward results: folds, holdout, stress test, Monte Carlo and gates.',
      d_ml: 'Classifiers vs baselines (purged walk-forward) and reinforcement learning experiments.',
      d_challenge: 'Is $100 → $200 in 4 hours realistic? An honest statistical answer.',
      d_risk: 'Risk limits, current state, events and the emergency stop.',
      d_pnl: 'Virtual equity curve, drawdown and per-trade profit & loss.',
      d_trades: 'All stored virtual (paper/replay) trades.',
      d_heatmap: 'Per-dataset price change and strategy × timeframe net return.',
      d_reports: 'Report files produced by the research cycle and the main research report.',
      d_learning: 'Every experiment\'s hypothesis and verdict — failed experiments are kept.',
      d_leaderboard: 'Walk-forward results ranked by out-of-sample return.',
      d_apis: 'Which secrets are configured (yes/no only) and exchange connectivity.',
      d_security: 'Audit chain integrity, authentication policy and security scan.',
      d_system: 'Server resources, uptime and test results.',
      d_costs: 'Monthly cost assumptions and measured costs.',
      d_audit: 'Hash-chained, append-only audit log.',
      d_settings: 'Language, replay dataset & speed, shadow strategy and Telegram ID.',
      loading: 'Loading…', retry: 'Retry', load_error: 'Could not load data', http_error: 'Server replied: {code}',
      not_run: 'Not run yet', not_run_desc: 'The research cycle has not produced this report yet ({file}). Refresh when the cycle finishes — no estimated numbers are shown here.',
      no_data: 'No data', server_msg: 'Server message', yes: 'Yes', no: 'No', none: 'None', all: 'All',
      enabled: 'Enabled', disabled: 'Disabled', configured: 'Configured', not_configured: 'Not configured', ok: 'OK', fail: 'Failed',
      cancel: 'Cancel', confirm: 'Confirm', save: 'Save', saved: 'Saved', save_failed: 'Save failed',
      mode: 'Mode', live_trading: 'Live trading', paper_feed: 'Paper feed', testnet: 'Testnet', historical_data: 'Historical data',
      data_sources: 'Data sources', paper_session: 'Paper session', paper_inactive: 'Paper session inactive',
      paper_inactive_desc: 'There is no active virtual session, so no portfolio figures are shown.',
      virtual_capital: 'Virtual starting capital', research_summary: 'Research summary', research_not_run: 'Research cycle not finished yet',
      wf_runs: 'Walk-forward runs', validated: 'Validated', total_trials: 'Total backtest trials', should_trade: 'Should the system trade?',
      challenge_best: 'Challenge best (by mean)', best_hit_rate: 'Best target hit rate', oracle_hit_rate: 'Oracle target hit rate',
      finished: 'Finished', duration: 'Duration', validated_list: 'Validated strategies', none_validated: 'No strategy passed every validation gate, so the system stays flat (by design).',
      ml_candidates: 'ML candidates', rl_candidates: 'RL candidates', risk_limits: 'Risk limits', oracle: 'Oracle (theoretical upper bound)',
      equity: 'Equity', cash: 'Cash', net_pnl: 'Net P&L', fees: 'Fees', position: 'Position', entry_px: 'Entry price', stop_px: 'Stop price',
      last_price: 'Last price', closed_trades: 'Closed trades', wins: 'Wins', win_rate: 'Win rate', strategy: 'Strategy', symbol: 'Symbol',
      session_id: 'Session ID', running: 'Running', stopped: 'Stopped', equity_curve: 'Equity curve', initial: 'Initial', params: 'Parameters',
      no_curve: 'No equity points yet.', updated: 'Updated', live_ws: 'WebSocket (2 s)',
      markets: 'Markets', dataset: 'Dataset', era: 'Era', chg_4h: '4h change', chg_total: 'Total change', regime: 'Regime',
      quality: 'Data quality', correlation: 'Return correlation (5m log returns)', rows: 'Rows', gaps: 'Gaps', missing_bars: 'Missing bars',
      dupes: 'Duplicates', bad_ohlc: 'Bad OHLC', max_ret: 'Max |return|', issues: 'Issues', start: 'Start', end: 'End', last_bar: 'Last bar',
      corr_note: 'Datasets from different eras do not overlap — those cells are empty.',
      signals: 'Signals', as_of: 'As of', entry: 'Entry', exit: 'Exit', scanner_legend: 'ENTRY = entry signal · EXIT = exit signal · — = no signal',
      entries_now: 'Entry signals now',
      interval: 'Interval', bars: 'Bars', chart: 'Chart', start_paper: 'Start paper session', paper_started: 'Paper session running',
      paper_not_started: 'Paper session not started', session_log: 'Session log', session_trades: 'Session trades', no_log: 'Nothing in the log yet.',
      no_trades: 'No virtual trades yet.', side: 'Side', qty: 'Qty', price: 'Price', pnl: 'P&L', reason: 'Reason', source: 'Source', time: 'Time',
      ohlc_hist_note: 'Chart candles come from historical data — not live.',
      agents: 'Agents', skills: 'Skills', services: 'Deterministic services', model: 'Model', kind: 'Kind', file: 'File', path: 'Path', description: 'Description',
      no_agents: 'No agent definitions found (.claude/agents/*.md).', no_skills: 'No skills found (.claude/skills/*/SKILL.md).',
      agents_note: 'Agents run on demand; every trading decision is made by deterministic Python code, not an LLM.',
      library: 'Strategy library', family: 'Family', defaults: 'Defaults', gates: 'Validation gates', registry: 'Strategy registry',
      version: 'Version', status: 'Status', created: 'Created', gate_results: 'Gate results (by dataset)', no_wf: 'No walk-forward results yet.',
      passed_n: '{n}/{m} passed', registry_empty: 'Registry is empty.',
      g_oos_trades: 'OOS trade count', g_oos_net_return_positive: 'OOS net return > 0', g_profit_factor: 'Profit factor', g_positive_folds: 'Positive folds',
      g_bootstrap_p_positive: 'Bootstrap P(>0)', g_holdout_positive: 'Holdout > 0', g_stress_2x_costs_nonnegative: '≥ 0 at 2× costs',
      runs: 'Runs', oos_return: 'OOS return', oos_trades: 'OOS trades', pf: 'PF', holdout: 'Holdout', stress: 'Stress (2× costs)', verdict: 'Verdict',
      folds: 'Folds', fold_returns: 'Net return per fold', monte_carlo: 'Monte Carlo', bootstrap: 'Bootstrap', final_params: 'Final parameters',
      test_start: 'Test start', test_end: 'Test end', net_return: 'Net return', trades_n: 'Trades', max_dd: 'Max drawdown', sharpe: 'Sharpe',
      select_run: 'Select a run to see details', optimised: 'Optimised', filter_dataset: 'Dataset', filter_verdict: 'Verdict', filter_strategy: 'Strategy',
      sims: 'Simulations', median_ret: 'Median return', p05_ret: 'P05 return', p95_ret: 'P95 return', p95_dd: 'P95 drawdown', p_positive: 'P(mean > 0)',
      ci: '90% confidence interval', gross_return: 'Gross return', exposure: 'Exposure', expectancy: 'Expectancy', win_rate_short: 'Win%',
      ml_models: 'Model comparison', horizon: 'Horizon (bars)', label_pos: 'Label positive rate', auc: 'Mean AUC', brier: 'Brier', threshold: 'Threshold',
      ml_auc_chart: 'Mean AUC (0.5 = coin flip)', rl_title: 'Reinforcement learning (Q-learning)', train_bars: 'Training bars',
      ml_not_run: 'ML report not available yet', rl_not_run: 'RL report not available yet',
      challenge_q: 'Question: can a 4-hour session turn $100 into $200 (+100%) while respecting risk limits?',
      sessions: 'Sessions', target_hits: 'Target hits', hit_rate: 'Hit rate', prob_loss: 'P(loss)', no_trade: 'No trade',
      median: 'Median', mean: 'Mean', worst: 'Worst', best: 'Best', worst_dd: 'Worst DD', mean_fees: 'Mean fees', consistency: 'Positive sessions',
      oracle_desc: 'The best possible long-only result with perfect foresight (impossible) — a theoretical ceiling, not an expectation.',
      oracle_median: 'Oracle median', oracle_p95: 'Oracle P95', oracle_max: 'Oracle max', abs_move_med: '|Price change| median', abs_move_max: '|Price change| max',
      doubling: 'Doubling analysis (bootstrap)', doubling_possible: 'Doubling possible?', p_double: 'P(double within limit)',
      median_sessions: 'Median sessions', max_sessions: 'Max sessions', p_ruin: 'P(lose 50%)',
      session_hist: 'Histogram of session returns', target_line: 'Target', sessions_missing: 'No per-session data for this strategy.', capital: 'Capital', target: 'Target',
      limits: 'Limits', risk_state: 'Current risk state', risk_events: 'Risk events', kill_switch: 'Kill switch', active: 'Active', inactive: 'Inactive',
      no_risk_state: 'No active session — real-time risk state does not apply.', no_events: 'No risk events.',
      estop: 'EMERGENCY STOP', estop_sub: 'Flattens all virtual positions and blocks new sessions',
      estop_confirm_t: 'Confirm emergency stop?', estop_confirm_b: 'This creates data/KILL, flattens the running paper session and writes to the audit log. Resuming requires typing RESUME.',
      estop_done: 'Emergency stop is active.', resume: 'Resume', resume_t: 'Resume operations?', resume_b: 'Type RESUME below to confirm.',
      resume_done: 'Kill switch removed. The paper session does not restart by itself.', type_resume: 'Type RESUME', risk_editable_note: 'Limits cannot be changed through the API.',
      peak: 'Peak equity', session_start_eq: 'Session start equity', day_start_eq: 'Day start equity', consec_losses: 'Consecutive losses', pause_remaining: 'Pause remaining (bars)',
      halted: 'Halted', killed: 'Killed', event_type: 'Event',
      drawdown: 'Drawdown', trade_pnl: 'P&L per closed trade', cum_pnl: 'Cumulative P&L', pnl_none: 'No closed virtual trades — no P&L data to analyse.',
      gross_profit: 'Gross profit', gross_loss: 'Gross loss', profit_factor: 'Profit factor', total_fees: 'Total fees', max_dd_curve: 'Max drawdown (from curve)',
      pnl_quote_note: 'P&L and fees are stored in the quote currency (e.g. USDT/BTC).', session: 'Session', fee: 'Fee',
      heat_tiles: 'Dataset price change', metric: 'Metric', tf_grid: 'Strategy × timeframe net return (%)', tf_not_run: 'Timeframe study not run yet',
      files: 'Report files', no_files: 'No files in reports/.', report_md: 'RESEARCH_REPORT.md', report_missing: 'The main research report has not been generated yet.',
      experiments: 'Experiments', hypothesis: 'Hypothesis', no_experiments: 'No experiments recorded yet.', by_verdict: 'By verdict',
      sort_hint: 'Click a column header to sort.',
      secrets: 'Secrets (yes/no only)', connectivity: 'Connectivity', public_data: 'Public market data', latency: 'Latency', error: 'Error', credentials: 'Credentials',
      keys_note_t: 'Where are keys set?', keys_note: 'API keys and secrets are set only as server environment variables (e.g. BINANCE_TESTNET_API_KEY). Never type a key into the dashboard — it only shows which ones are configured, never their values.',
      audit_chain: 'Audit chain', chain_valid: 'Intact (valid)', chain_broken: 'Broken — investigate', audit_entries: 'Audit entries', withdrawal: 'Withdrawal capability',
      auth: 'Authentication', security_scan: 'Security scan', scan_not_run: 'Security scan not run yet',
      resources: 'Resources', disk: 'Disk', memory: 'Memory', cpu: 'CPU', load: 'Load average', db_size: 'Database size', reports_size: 'Reports size',
      python: 'Python', uptime: 'Uptime', requests: 'Requests', paper_thread: 'Paper thread', alive: 'Alive', tests: 'Test results', tests_not_run: 'Test report not available yet',
      used: 'used', free: 'free', cores: 'cores',
      assumptions: 'Monthly assumptions', ledger: 'Measured costs (ledger)', measured: 'Measured', projected: 'Projected monthly', ledger_empty: 'No costs recorded in the ledger.',
      cost_vps: 'VPS', cost_claude: 'Claude API budget', cost_gpu: 'GPU', cost_data: 'Data feeds', units: 'Units', category: 'Category', amount: 'Amount (USD)',
      actor: 'Actor', action: 'Action', detail: 'Detail', hash: 'Hash', no_audit: 'Audit log is empty.',
      language: 'Language', replay_dataset: 'Replay dataset', replay_speed: 'Replay speed (s/bar)', shadow_strategy: 'Shadow strategy',
      telegram_id: 'Telegram owner ID', feed: 'Feed', shadow_warn: 'A shadow strategy has NOT passed the validation gates. It paper-trades on replay data for observation only (EXPERIMENTAL_SHADOW).',
      settings_note: 'Changes are written to the audit log. Dataset/speed changes apply to the next session.', speed_range: '0.05 – 10 seconds',
      telegram_ph: 'Numeric ID (optional)', lang_bn: 'বাংলা', lang_en: 'English',
      b_virtual_t: 'Virtual money — no real funds', b_hist_t: 'Stored historical data — not live', b_replay_t: 'Historical bars being replayed',
      b_shadow_t: 'Unvalidated experimental strategy', b_blocked_t: 'Unavailable / blocked', b_research_t: 'Research cycle output',
      h_gain: 'Gain', h_zero: 'Bin containing 0% (incl. no-trade sessions)', h_loss: 'Loss',
      unknown: 'Unknown', count: 'Count', value: 'Value', name: 'Name', on: 'On',
    },
  };

  let LANG = 'bn';
  const MISSING = new Set();
  window.__i18nMissing = MISSING;
  function t(k, vars) {
    let s = I18N[LANG] && I18N[LANG][k];
    if (s == null) s = I18N.en[k];
    if (s == null) { MISSING.add(k); s = k; }
    if (vars) s = s.replace(/\{(\w+)\}/g, (m, n) => (vars[n] != null ? String(vars[n]) : m));
    return s;
  }

  // ------------------------------------------------------------------ storage (guarded)
  const store = {
    get(k, sess) { try { return (sess ? window.sessionStorage : window.localStorage).getItem(k); } catch (e) { return null; } },
    set(k, v, sess) { try { (sess ? window.sessionStorage : window.localStorage).setItem(k, v); } catch (e) { /* ignore */ } },
    del(k, sess) { try { (sess ? window.sessionStorage : window.localStorage).removeItem(k); } catch (e) { /* ignore */ } },
  };

  // ------------------------------------------------------------------ DOM helpers
  function el(tag, attrs) {
    const n = document.createElement(tag);
    if (attrs) {
      for (const k of Object.keys(attrs)) {
        const v = attrs[k];
        if (v == null || v === false) continue;
        if (k === 'class') n.className = v;
        else if (k === 'text') n.textContent = v;
        else if (k.slice(0, 2) === 'on' && typeof v === 'function') n.addEventListener(k.slice(2), v);
        else if (k === 'style') n.style.cssText = v;
        else n.setAttribute(k, v === true ? '' : String(v));
      }
    }
    for (let i = 2; i < arguments.length; i++) append(n, arguments[i]);
    return n;
  }
  function append(n, c) {
    if (c == null || c === false) return;
    if (Array.isArray(c)) { c.forEach((x) => append(n, x)); return; }
    n.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  const SVGNS = 'http://www.w3.org/2000/svg';
  const ICONS = {
    grid: 'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z',
    wallet: 'M3 7h18v13H3zM3 7l3-4h12l3 4M16 13.5h2',
    trend: 'M3 17l6-6 4 4 8-8M14 7h7v7',
    radar: 'M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0-18 0M12 12m-4 0a4 4 0 1 0 8 0a4 4 0 1 0-8 0M12 12l6.5-6.5',
    candle: 'M7 3v18M17 3v18M5 7h4v9H5zM15 6h4v6h-4z',
    cpu: 'M6 6h12v12H6zM9.5 9.5h5v5h-5zM9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4',
    flask: 'M9 3h6M10 3v6L4.5 18.5A1.7 1.7 0 0 0 6 21h12a1.7 1.7 0 0 0 1.5-2.5L14 9V3M7 15h10',
    rewind: 'M3 12a9 9 0 1 0 3-6.7L3 8M3 3v5h5M12 7v5l3 3',
    brain: 'M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 6 1V5a3 3 0 0 0-3-1zM15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-6 1',
    target: 'M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0-18 0M12 12m-5 0a5 5 0 1 0 10 0a5 5 0 1 0-10 0M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0-2 0',
    shield: 'M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z',
    chart: 'M3 3v18h18M7 15l4-4 3 3 5-6',
    list: 'M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01',
    heat: 'M3 3h5v5H3zM10 3h4v5h-4zM16 3h5v5h-5zM3 10h5v4H3zM10 10h4v4h-4zM16 10h5v4h-5zM3 16h5v5H3zM10 16h4v5h-4zM16 16h5v5h-5z',
    doc: 'M6 2h9l5 5v15H6zM14 2v6h6M9 13h8M9 17h8',
    book: 'M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4zM20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z',
    trophy: 'M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0zM7 6H4v2a3 3 0 0 0 3 3M17 6h3v2a3 3 0 0 1-3 3',
    key: 'M14.5 4a5.5 5.5 0 1 1-4.9 8L3 18.5V21h3v-2h2v-2h2l1.6-1.6A5.5 5.5 0 0 1 14.5 4zM16 8h.01',
    lock: 'M5 11h14v10H5zM8 11V7a4 4 0 0 1 8 0v4',
    pulse: 'M3 12h4l3-8 4 16 3-8h4',
    coin: 'M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0-18 0M14.5 9H11a1.5 1.5 0 0 0 0 3h2a1.5 1.5 0 0 1 0 3H9.5M12 7v2M12 15v2',
    scroll: 'M5 3h14v18H5zM9 8h6M9 12h6M9 16h4',
    gear: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1',
    menu: 'M3 6h18M3 12h18M3 18h18',
    refresh: 'M21 12a9 9 0 1 1-3-6.7L21 8M21 3v5h-5',
    logout: 'M9 21H5V3h4M16 17l5-5-5-5M21 12H9',
    info: 'M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0-18 0M12 11v5M12 8h.01',
    alert: 'M12 3l10 18H2zM12 10v5M12 18h.01',
    empty: 'M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10',
    stop: 'M7.9 3h8.2L21 7.9v8.2L16.1 21H7.9L3 16.1V7.9zM9 9h6v6H9z',
    play: 'M6 4l14 8-14 8z',
    check: 'M4 12l5 5L20 6',
    logo: 'M4 18l5-6 4 3 7-9M15 6h5v5',
  };
  function icon(name, cls) {
    const s = document.createElementNS(SVGNS, 'svg');
    s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('fill', 'none'); s.setAttribute('stroke', 'currentColor');
    s.setAttribute('stroke-width', '1.8'); s.setAttribute('stroke-linecap', 'round'); s.setAttribute('stroke-linejoin', 'round');
    s.setAttribute('aria-hidden', 'true');
    if (cls) s.setAttribute('class', cls);
    const p = document.createElementNS(SVGNS, 'path'); p.setAttribute('d', ICONS[name] || ICONS.info); s.append(p);
    return s;
  }

  // ------------------------------------------------------------------ formatting
  const isNum = (v) => typeof v === 'number' && isFinite(v);
  function fmtN(v, d) {
    if (d == null) d = 2;
    if (!isNum(v)) return '—';
    if (Math.abs(v) >= 1e8) return v > 0 ? '∞' : '−∞'; // research writes ±1e9 for infinite profit factor
    return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function fmtInt(v) { return isNum(v) ? Math.round(v).toLocaleString('en-US') : '—'; }
  function fmtPct(v, d, sign) {
    if (!isNum(v)) return '—';
    const s = fmtN(v, d == null ? 2 : d);
    return (sign !== false && v > 0 ? '+' : '') + s + '%';
  }
  function fmtUsd(v, d) { if (!isNum(v)) return '—'; return (v < 0 ? '−$' : '$') + fmtN(Math.abs(v), d == null ? 2 : d); }
  function fmtSignedUsd(v) { if (!isNum(v)) return '—'; return (v > 0 ? '+' : v < 0 ? '−' : '') + '$' + fmtN(Math.abs(v), 2); }
  function fmtPx(v) {
    if (!isNum(v)) return '—';
    const a = Math.abs(v);
    const d = a >= 1000 ? 2 : a >= 1 ? 4 : a >= 0.01 ? 6 : 8;
    return fmtN(v, d);
  }
  function fmtQty(v) { if (!isNum(v)) return '—'; return fmtN(v, Math.abs(v) >= 100 ? 2 : 6); }
  function fmtFrac(v) { return isNum(v) ? fmtPct(v * 100, 1, false) : '—'; }
  function pad2(n) { return n < 10 ? '0' + n : String(n); }
  function fmtEpoch(s) {
    if (!isNum(s)) return '—';
    const d = new Date(s * 1000);
    return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate()) + ' ' + pad2(d.getHours()) + ':' + pad2(d.getMinutes()) + ':' + pad2(d.getSeconds());
  }
  function fmtTs(s) { // ISO-like strings from the API, shown compactly in UTC
    if (s == null || s === '') return '—';
    return String(s).replace('T', ' ').replace(/(\.\d+)?\+00:00$/, ' UTC').replace(/(\.\d+)?Z$/, ' UTC');
  }
  function fmtDur(s) {
    if (!isNum(s)) return '—';
    s = Math.max(0, Math.round(s));
    const d = Math.floor(s / 86400), h = Math.floor((s % 86400) / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    if (d) return d + 'd ' + h + 'h ' + m + 'm';
    if (h) return h + 'h ' + m + 'm';
    if (m) return m + 'm ' + sec + 's';
    return sec + 's';
  }
  function sgn(v) { return !isNum(v) ? '' : v > 0 ? 'gain' : v < 0 ? 'loss' : ''; }
  function signed(text, v) { return el('span', { class: 'num ' + sgn(v) }, text); }

  // ------------------------------------------------------------------ UI atoms
  const BADGES = {
    VIRTUAL: ['b-virtual', 'VIRTUAL / SIMULATED', 'b_virtual_t'],
    HISTORICAL: ['b-hist', 'HISTORICAL (not live)', 'b_hist_t'],
    REPLAY: ['b-replay', 'REPLAY', 'b_replay_t'],
    SHADOW: ['b-shadow', 'EXPERIMENTAL_SHADOW', 'b_shadow_t'],
    BLOCKED: ['b-blocked', 'BLOCKED', 'b_blocked_t'],
    RESEARCH: ['b-research', 'RESEARCH OUTPUT', 'b_research_t'],
  };
  function badge(kind, text) {
    const b = BADGES[kind];
    if (b) return el('span', { class: 'badge ' + b[0], title: t(b[2]) }, text || b[1]);
    return el('span', { class: 'badge ' + verdictClass(kind) }, text || kind);
  }
  function verdictClass(v) {
    const s = String(v || '').toUpperCase();
    if (s === 'VALIDATED' || s === 'PASS' || s === 'OK' || s === 'PAPER' || s === 'CONFIGURED' || s === 'ENABLED') return 'b-validated';
    if (s === 'REJECTED' || s === 'FAIL' || s === 'FAILED' || s === 'BLOCKED' || s === 'KILLED' || s === 'HALTED') return 'b-rejected';
    if (s === 'CANDIDATE' || s === 'PARTIAL' || s === 'EXPERIMENTAL_SHADOW') return 'b-candidate';
    if (s === 'BASELINE') return 'b-baseline';
    if (s === 'REPLAY') return 'b-replay';
    return 'b-neutral';
  }
  function verdictBadge(v) { return v == null ? el('span', { class: 'muted' }, '—') : el('span', { class: 'badge ' + verdictClass(v) }, String(v)); }
  function sourceBadge(src) {
    const s = String(src || '').toUpperCase();
    if (s.indexOf('REPLAY') >= 0) return badge('REPLAY');
    if (s.indexOf('HISTORICAL') >= 0) return badge('HISTORICAL');
    if (s.indexOf('BLOCKED') >= 0) return badge('BLOCKED');
    if (s.indexOf('SHADOW') >= 0) return badge('SHADOW');
    if (s === 'INACTIVE' || s === 'NONE' || !s) return el('span', { class: 'badge b-inactive' }, s || 'NONE');
    return el('span', { class: 'badge b-neutral' }, String(src));
  }

  function panel(title, opts) {
    opts = opts || {};
    const body = el('div', { class: 'panel-body' + (opts.flush ? ' flush' : '') });
    const head = title != null ? el('div', { class: 'panel-head' },
      el('div', { class: 'panel-title' }, title, opts.badges || null),
      opts.tools ? el('div', { class: 'panel-tools' }, opts.tools) : null) : null;
    const p = el('section', { class: 'panel' + (opts.cls ? ' ' + opts.cls : '') }, head, body, opts.note ? el('div', { class: 'panel-note' }, opts.note) : null);
    append(body, opts.body);
    p.body = body;
    return p;
  }
  function kpi(label, value, opts) {
    opts = opts || {};
    const v = el('div', { class: 'kpi-value' + (opts.small ? ' sm' : '') + (opts.cls ? ' ' + opts.cls : '') });
    append(v, value);
    const k = el('div', { class: 'panel kpi' + (opts.accent ? ' accent ' + opts.accent : '') },
      el('div', { class: 'kpi-label' }, label, opts.badge || null), v, opts.foot ? el('div', { class: 'kpi-foot' }, opts.foot) : null);
    k.valueEl = v;
    return k;
  }
  function kpiGrid(items) { return el('div', { class: 'grid grid-kpi' }, items); }
  function kv(pairs) {
    const g = el('div', { class: 'kv' });
    pairs.forEach((p) => { if (!p) return; g.append(el('div', { class: 'k' }, p[0]), el('div', { class: 'v' }, p[1])); });
    return g;
  }
  function empty(title, desc, srv, ico) {
    return el('div', { class: 'empty' },
      el('div', { class: 'ico' }, icon(ico || 'empty')),
      el('h3', null, title), desc ? el('p', null, desc) : null,
      srv ? el('div', { class: 'srv' }, t('server_msg') + ': ' + srv) : null);
  }
  function notRunState(file, title) {
    const e = empty(title || t('not_run'), t('not_run_desc', { file: file }), null, 'empty');
    e.insertBefore(el('span', { class: 'badge b-notrun' }, 'NOT_RUN'), e.children[1]);
    return e;
  }
  function isNotRun(d) { return !d || (typeof d === 'object' && !Array.isArray(d) && d.status === 'NOT_RUN'); }
  function callout(kind, iconName, content) { return el('div', { class: 'callout ' + kind }, icon(iconName), el('div', null, content)); }
  function seg(options, value, onChange) {
    const s = el('div', { class: 'seg', role: 'group' });
    options.forEach((o) => {
      const b = el('button', { type: 'button', class: o[0] === value ? 'on' : '', 'aria-pressed': o[0] === value ? 'true' : 'false' }, o[1]);
      b.addEventListener('click', () => {
        s.querySelectorAll('button').forEach((x) => { x.classList.remove('on'); x.setAttribute('aria-pressed', 'false'); });
        b.classList.add('on'); b.setAttribute('aria-pressed', 'true'); onChange(o[0]);
      });
      s.append(b);
    });
    return s;
  }
  function select(options, value, onChange, attrs) {
    const s = el('select', Object.assign({ class: 'input' }, attrs || {}));
    options.forEach((o) => {
      const val = Array.isArray(o) ? o[0] : o, lab = Array.isArray(o) ? o[1] : o;
      const op = el('option', { value: val == null ? '' : val }, lab);
      if (String(val == null ? '' : val) === String(value == null ? '' : value)) op.selected = true;
      s.append(op);
    });
    if (onChange) s.addEventListener('change', () => onChange(s.value));
    return s;
  }
  function toast(msg, kind) {
    const host = document.getElementById('toasts');
    const n = el('div', { class: 'toast ' + (kind || '') }, msg);
    host.append(n);
    setTimeout(() => { n.remove(); }, 4200);
  }
  function modal(opts) {
    return new Promise((resolve) => {
      let input = null;
      const ok = el('button', { class: 'btn ' + (opts.danger ? 'btn-danger' : 'btn-primary'), type: 'button' }, opts.okText || t('confirm'));
      const cancel = el('button', { class: 'btn', type: 'button' }, t('cancel'));
      if (opts.requireText) {
        input = el('input', { class: 'input mono', autocomplete: 'off', spellcheck: 'false', placeholder: opts.requireText, 'aria-label': t('type_resume') });
        ok.disabled = true;
        input.addEventListener('input', () => { ok.disabled = input.value.trim() !== opts.requireText; });
      }
      const box = el('div', { class: 'modal' + (opts.danger ? ' danger' : ''), role: 'dialog', 'aria-modal': 'true' },
        el('h2', null, opts.title), el('p', null, opts.body), input, el('div', { class: 'actions' }, cancel, ok));
      const scrim = el('div', { class: 'modal-scrim' }, box);
      const done = (v) => { document.removeEventListener('keydown', onKey); scrim.remove(); resolve(v); };
      const onKey = (e) => { if (e.key === 'Escape') done(false); };
      document.addEventListener('keydown', onKey);
      scrim.addEventListener('click', (e) => { if (e.target === scrim) done(false); });
      cancel.addEventListener('click', () => done(false));
      ok.addEventListener('click', () => done(input ? input.value.trim() : true));
      document.body.append(scrim);
      (input || ok).focus();
    });
  }

  // Sortable/scrolling table. cols: {key,label,num,fmt(v,row),sort(row),cls}
  function table(cols, rows, opts) {
    opts = opts || {};
    const wrap = el('div', { class: 'tbl-wrap' + (opts.tall ? ' tall' : '') });
    if (!rows || !rows.length) { wrap.append(empty(opts.emptyText || t('no_data'), opts.emptyDesc || null)); return wrap; }
    const tbl = el('table', { class: 'tbl' });
    const thead = el('thead'); const tr = el('tr'); thead.append(tr);
    const tbody = el('tbody');
    let sortKey = opts.sortKey || null, sortDir = opts.sortDir || -1;
    const getV = (c, r) => (c.sort ? c.sort(r) : r[c.key]);
    function renderBody() {
      let data = rows.slice();
      if (sortKey != null) {
        const c = cols.find((x) => x.key === sortKey);
        if (c) {
          data.sort((a, b) => {
            const va = getV(c, a), vb = getV(c, b);
            const na = va == null || (typeof va === 'number' && !isFinite(va)), nb = vb == null || (typeof vb === 'number' && !isFinite(vb));
            if (na && nb) return 0; if (na) return 1; if (nb) return -1;
            if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * sortDir;
            return String(va).localeCompare(String(vb)) * sortDir;
          });
        }
      }
      if (opts.limit) data = data.slice(0, opts.limit);
      tbody.replaceChildren();
      data.forEach((r) => {
        const row = el('tr', { class: (opts.onRow ? 'clickable ' : '') + (opts.rowClass ? opts.rowClass(r) : '') });
        cols.forEach((c) => {
          const v = r[c.key];
          const td = el('td', { class: (c.num ? 'num ' : '') + (c.cls || '') });
          append(td, c.fmt ? c.fmt(v, r) : (v == null ? '—' : String(v)));
          row.append(td);
        });
        if (opts.onRow) {
          row.tabIndex = 0;
          row.addEventListener('click', () => { tbody.querySelectorAll('tr.sel').forEach((x) => x.classList.remove('sel')); row.classList.add('sel'); opts.onRow(r); });
          row.addEventListener('keydown', (e) => { if (e.key === 'Enter') row.click(); });
        }
        tbody.append(row);
      });
    }
    cols.forEach((c) => {
      const th = el('th', { class: (c.num ? 'num ' : '') + (opts.sortable !== false ? 'sortable' : ''), scope: 'col' }, c.label);
      if (opts.sortable !== false) {
        th.tabIndex = 0;
        const arr = el('span', { class: 'arr', 'aria-hidden': 'true' }, '↕');
        th.append(arr);
        const act = () => {
          if (sortKey === c.key) sortDir = -sortDir; else { sortKey = c.key; sortDir = c.num ? -1 : 1; }
          tr.querySelectorAll('th').forEach((x) => { x.classList.remove('sorted'); const a = x.querySelector('.arr'); if (a) a.textContent = '↕'; });
          th.classList.add('sorted'); arr.textContent = sortDir > 0 ? '↑' : '↓';
          renderBody();
        };
        th.addEventListener('click', act);
        th.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); act(); } });
        if (sortKey === c.key) { th.classList.add('sorted'); arr.textContent = sortDir > 0 ? '↑' : '↓'; }
      }
      tr.append(th);
    });
    tbl.append(thead, tbody);
    renderBody();
    wrap.append(tbl);
    return wrap;
  }

  // Generic safe renderer for report JSON whose shape is not fixed (security scan, tests).
  function jsonTree(v, depth) {
    depth = depth || 0;
    if (v == null) return el('span', { class: 'muted' }, '—');
    if (typeof v === 'boolean') return verdictBadge(v ? 'OK' : 'FAIL');
    if (typeof v === 'number') return el('span', { class: 'num' }, Number.isInteger(v) ? fmtInt(v) : fmtN(v, 4));
    if (typeof v === 'string') return el('span', { class: 'wrap-any' }, v);
    if (Array.isArray(v)) {
      if (!v.length) return el('span', { class: 'muted' }, '[]');
      if (v.every((x) => x && typeof x === 'object' && !Array.isArray(x))) {
        const keys = []; v.slice(0, 200).forEach((x) => Object.keys(x).forEach((k) => { if (keys.indexOf(k) < 0) keys.push(k); }));
        return table(keys.slice(0, 12).map((k) => ({ key: k, label: k, fmt: (x) => (x != null && typeof x === 'object' ? JSON.stringify(x) : jsonTree(x, depth + 1)) })), v.slice(0, 500), { sortable: true });
      }
      return el('span', { class: 'wrap-any' }, v.map((x) => (typeof x === 'object' ? JSON.stringify(x) : String(x))).join(', '));
    }
    const g = el('div', { class: 'kv' });
    Object.keys(v).forEach((k) => {
      const x = v[k];
      if (x && typeof x === 'object' && !Array.isArray(x) && depth < 4) {
        g.append(el('div', { class: 'k', style: 'grid-column:1/-1;color:var(--text);font-weight:600' }, k));
        g.append(el('div', { class: 'nest', style: 'grid-column:1/-1' }, jsonTree(x, depth + 1)));
      } else if (Array.isArray(x) && x.length && typeof x[0] === 'object') {
        g.append(el('div', { class: 'k', style: 'grid-column:1/-1;color:var(--text);font-weight:600' }, k));
        g.append(el('div', { style: 'grid-column:1/-1' }, jsonTree(x, depth + 1)));
      } else {
        g.append(el('div', { class: 'k' }, k), el('div', { class: 'v' }, jsonTree(x, depth + 1)));
      }
    });
    return el('div', { class: 'jtree' }, g);
  }

  // ------------------------------------------------------------------ safe markdown
  function renderMarkdown(md) {
    const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    const inline = (s) => {
      const codes = [];
      s = s.replace(/`([^`]+)`/g, (m, c) => { codes.push(c); return '\u0000' + (codes.length - 1) + '\u0000'; });
      s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/__([^_]+)__/g, '<strong>$1</strong>');
      s = s.replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?!\w)/g, '$1<em>$2</em>');
      return s.replace(/\u0000(\d+)\u0000/g, (m, i) => '<code>' + codes[+i] + '</code>');
    };
    const lines = esc(String(md || '').replace(/\r\n?/g, '\n')).split('\n');
    const out = [];
    let i = 0;
    while (i < lines.length) {
      const ln = lines[i];
      if (/^\s*```/.test(ln)) {
        const buf = []; i++;
        while (i < lines.length && !/^\s*```/.test(lines[i])) { buf.push(lines[i]); i++; }
        i++; out.push('<pre><code>' + buf.join('\n') + '</code></pre>'); continue;
      }
      let m = /^(#{1,6})\s+(.*)$/.exec(ln);
      if (m) { const lv = Math.min(4, m[1].length); out.push('<h' + lv + '>' + inline(m[2]) + '</h' + lv + '>'); i++; continue; }
      if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(ln)) { out.push('<hr>'); i++; continue; }
      if (/^\s*\|.*\|\s*$/.test(ln) && i + 1 < lines.length && /^\s*\|?\s*:?-{2,}/.test(lines[i + 1])) {
        const cells = (r) => r.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => inline(c.trim()));
        const head = cells(ln); i += 2;
        const body = [];
        while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) { body.push(cells(lines[i])); i++; }
        out.push('<div class="tbl-wrap"><table><thead><tr>' + head.map((c) => '<th>' + c + '</th>').join('') + '</tr></thead><tbody>' +
          body.map((r) => '<tr>' + r.map((c) => '<td>' + c + '</td>').join('') + '</tr>').join('') + '</tbody></table></div>');
        continue;
      }
      if (/^\s*[-*+]\s+/.test(ln) || /^\s*\d+[.)]\s+/.test(ln)) {
        const ordered = /^\s*\d+[.)]\s+/.test(ln);
        const items = [];
        while (i < lines.length && (ordered ? /^\s*\d+[.)]\s+/ : /^\s*[-*+]\s+/).test(lines[i])) {
          items.push(inline(lines[i].replace(ordered ? /^\s*\d+[.)]\s+/ : /^\s*[-*+]\s+/, ''))); i++;
        }
        out.push((ordered ? '<ol>' : '<ul>') + items.map((x) => '<li>' + x + '</li>').join('') + (ordered ? '</ol>' : '</ul>'));
        continue;
      }
      if (/^&gt;\s?/.test(ln)) {
        const buf = [];
        while (i < lines.length && /^&gt;\s?/.test(lines[i])) { buf.push(inline(lines[i].replace(/^&gt;\s?/, ''))); i++; }
        out.push('<blockquote><p>' + buf.join('<br>') + '</p></blockquote>'); continue;
      }
      if (!ln.trim()) { i++; continue; }
      const buf = [];
      while (i < lines.length && lines[i].trim() && !/^(#{1,6})\s|^\s*```|^\s*[-*+]\s+|^\s*\d+[.)]\s+|^\s*\|.*\|\s*$|^&gt;/.test(lines[i])) { buf.push(inline(lines[i])); i++; }
      if (!buf.length) { buf.push(inline(lines[i])); i++; }
      out.push('<p>' + buf.join(' ') + '</p>');
    }
    const div = el('div', { class: 'md' });
    div.innerHTML = out.join('\n'); // all text escaped above; only our own tags are produced
    return div;
  }

  // ------------------------------------------------------------------ charts (canvas, no libraries)
  const C = {
    grid: 'rgba(120,145,190,0.10)', axis: '#6f7f9b', text: '#a9b6cc', gain: '#22c55e', loss: '#ef4444', accent: '#22d3ee',
    teal: '#14b8a6', amber: '#f59e0b', violet: '#a78bfa', blue: '#60a5fa', bb: 'rgba(167,139,250,0.55)', bbFill: 'rgba(167,139,250,0.06)',
  };
  const FONT = '11px Inter, "Noto Sans Bengali", system-ui, sans-serif';
  let CLEANUP = [];
  function onCleanup(f) { CLEANUP.push(f); }

  function niceTicks(lo, hi, n) {
    if (!isFinite(lo) || !isFinite(hi)) return [];
    if (lo === hi) { const d = Math.abs(lo) * 0.05 || 1; lo -= d; hi += d; }
    const span = hi - lo, step0 = span / Math.max(1, n);
    const mag = Math.pow(10, Math.floor(Math.log10(step0)));
    const err = step0 / mag;
    const step = (err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1) * mag;
    const out = [];
    for (let v = Math.ceil(lo / step) * step; v <= hi + step * 1e-9; v += step) out.push(+v.toPrecision(12));
    return out;
  }
  function stepDecimals(ticks) { const st = ticks.length > 1 ? Math.abs(ticks[1] - ticks[0]) : 1; return Math.max(0, Math.min(6, -Math.floor(Math.log10(st) + 1e-9))); }
  function makeChart(height, draw, opts) {
    opts = opts || {};
    const wrap = el('div', { class: 'chart', style: 'height:' + height + 'px', role: 'img', 'aria-label': opts.label || '' });
    const cv = el('canvas');
    const tip = el('div', { class: 'chart-tip' });
    wrap.append(cv, tip);
    let hover = null;
    function paint() {
      const w = wrap.clientWidth, h = wrap.clientHeight;
      if (!w || !h) return;
      const dpr = window.devicePixelRatio || 1;
      if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) {
        cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
        cv.style.width = w + 'px'; cv.style.height = h + 'px';
      }
      const ctx = cv.getContext('2d');
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      ctx.font = FONT; ctx.textBaseline = 'middle';
      const tipInfo = draw(ctx, w, h, hover);
      if (tipInfo && hover) {
        tip.replaceChildren();
        tipInfo.lines.forEach((l, idx) => {
          const row = el('div', null);
          if (Array.isArray(l)) { row.append(el('span', { class: 'tk' }, l[0] + ' '), document.createTextNode(l[1])); } else row.textContent = l;
          if (idx === 0) row.style.fontWeight = '600';
          tip.append(row);
        });
        tip.classList.add('on');
        const tw = tip.offsetWidth, th = tip.offsetHeight;
        let x = tipInfo.x + 14, y = tipInfo.y - th - 10;
        if (x + tw > w) x = tipInfo.x - tw - 14;
        if (x < 0) x = 4;
        if (y < 0) y = tipInfo.y + 14;
        tip.style.left = x + 'px'; tip.style.top = y + 'px';
      } else tip.classList.remove('on');
    }
    let raf = 0;
    const schedule = () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; paint(); }); };
    const ro = new ResizeObserver(schedule);
    ro.observe(wrap);
    onCleanup(() => ro.disconnect());
    const move = (e) => { const r = cv.getBoundingClientRect(); hover = { x: e.clientX - r.left, y: e.clientY - r.top }; schedule(); };
    cv.addEventListener('pointermove', move);
    cv.addEventListener('pointerdown', move);
    cv.addEventListener('pointerleave', () => { hover = null; schedule(); });
    wrap.repaint = schedule;
    return wrap;
  }
  function drawYAxis(ctx, ticks, y, x0, x1, fmt, right) {
    ctx.strokeStyle = C.grid; ctx.lineWidth = 1; ctx.fillStyle = C.axis; ctx.textAlign = right ? 'left' : 'right';
    ticks.forEach((v) => {
      const yy = Math.round(y(v)) + 0.5;
      ctx.beginPath(); ctx.moveTo(x0, yy); ctx.lineTo(x1, yy); ctx.stroke();
      ctx.fillText(fmt(v), right ? x1 + 6 : x0 - 6, yy);
    });
  }
  function shortTs(s) { const m = /(\d{4})-(\d\d)-(\d\d)[ T](\d\d):(\d\d)/.exec(String(s)); return m ? m[2] + '-' + m[3] + ' ' + m[4] + ':' + m[5] : String(s); }

  function candleChart(d) {
    return makeChart(window.innerWidth < 600 ? 380 : 470, (ctx, w, h, hov) => {
      const n = d.c.length; if (!n) return null;
      const padL = 8, padR = 72, padT = 10, padB = 24, gap = 14;
      const plotW = w - padL - padR;
      const rsiH = Math.round((h - padT - padB) * 0.2);
      const priceH = h - padT - padB - rsiH - gap;
      let lo = Infinity, hi = -Infinity;
      for (let i = 0; i < n; i++) {
        [d.l[i], d.bb_lo && d.bb_lo[i]].forEach((v) => { if (isNum(v)) lo = Math.min(lo, v); });
        [d.h[i], d.bb_up && d.bb_up[i]].forEach((v) => { if (isNum(v)) hi = Math.max(hi, v); });
      }
      const pd = (hi - lo) * 0.05 || hi * 0.01 || 1; lo -= pd; hi += pd;
      const cw = plotW / n;
      const x = (i) => padL + cw * (i + 0.5);
      const y = (p) => padT + (hi - p) / (hi - lo) * priceH;
      drawYAxis(ctx, niceTicks(lo, hi, 6), y, padL, padL + plotW, fmtPx, true);
      // volume overlay (bottom 18% of price pane)
      let vmax = 0; d.v.forEach((v) => { if (isNum(v)) vmax = Math.max(vmax, v); });
      if (vmax > 0) {
        const vh = priceH * 0.18, base = padT + priceH;
        for (let i = 0; i < n; i++) {
          const v = d.v[i]; if (!isNum(v)) continue;
          ctx.fillStyle = d.c[i] >= d.o[i] ? 'rgba(34,197,94,0.18)' : 'rgba(239,68,68,0.18)';
          const bh = v / vmax * vh;
          ctx.fillRect(x(i) - Math.max(1, cw * 0.35), base - bh, Math.max(1, cw * 0.7), bh);
        }
      }
      // Bollinger band fill + edges
      if (d.bb_up && d.bb_lo) {
        ctx.beginPath(); let started = false;
        for (let i = 0; i < n; i++) { if (!isNum(d.bb_up[i])) continue; if (!started) { ctx.moveTo(x(i), y(d.bb_up[i])); started = true; } else ctx.lineTo(x(i), y(d.bb_up[i])); }
        for (let i = n - 1; i >= 0; i--) { if (!isNum(d.bb_lo[i])) continue; ctx.lineTo(x(i), y(d.bb_lo[i])); }
        ctx.closePath(); ctx.fillStyle = C.bbFill; ctx.fill();
        ctx.setLineDash([3, 3]); line(ctx, d.bb_up, x, y, C.bb, 1); line(ctx, d.bb_lo, x, y, C.bb, 1); ctx.setLineDash([]);
      }
      // candles
      const bw = Math.max(1, Math.min(12, cw * 0.66));
      for (let i = 0; i < n; i++) {
        const o = d.o[i], c = d.c[i], hh = d.h[i], ll = d.l[i];
        if (![o, c, hh, ll].every(isNum)) continue;
        const up = c >= o; const col = up ? C.gain : C.loss;
        ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 1;
        const xx = Math.round(x(i)) + 0.5;
        ctx.beginPath(); ctx.moveTo(xx, y(hh)); ctx.lineTo(xx, y(ll)); ctx.stroke();
        const y0 = y(Math.max(o, c)), y1 = y(Math.min(o, c));
        ctx.fillRect(x(i) - bw / 2, y0, bw, Math.max(1, y1 - y0));
      }
      line(ctx, d.ema20, x, y, C.accent, 1.6);
      line(ctx, d.ema60, x, y, C.amber, 1.6);
      // last price tag
      const last = d.c[n - 1];
      if (isNum(last)) {
        const yy = y(last);
        ctx.setLineDash([2, 3]); ctx.strokeStyle = 'rgba(230,237,247,.35)'; ctx.beginPath(); ctx.moveTo(padL, yy); ctx.lineTo(padL + plotW, yy); ctx.stroke(); ctx.setLineDash([]);
        ctx.fillStyle = last >= d.o[n - 1] ? C.gain : C.loss;
        roundRect(ctx, padL + plotW + 2, yy - 9, padR - 4, 18, 4); ctx.fill();
        ctx.fillStyle = '#04121b'; ctx.textAlign = 'left'; ctx.font = '600 11px Inter, system-ui, sans-serif'; ctx.fillText(fmtPx(last), padL + plotW + 7, yy); ctx.font = FONT;
      }
      // RSI pane
      const r0 = padT + priceH + gap;
      const ry = (v) => r0 + (100 - v) / 100 * rsiH;
      ctx.fillStyle = 'rgba(120,145,190,0.04)'; ctx.fillRect(padL, ry(70), plotW, ry(30) - ry(70));
      drawYAxis(ctx, [30, 70], ry, padL, padL + plotW, (v) => String(v), true);
      ctx.fillStyle = C.axis; ctx.textAlign = 'left'; ctx.fillText('RSI 14', padL + 4, r0 + 8);
      line(ctx, d.rsi, x, ry, C.violet, 1.3);
      // x labels
      ctx.fillStyle = C.axis; ctx.textAlign = 'center';
      const nl = Math.max(2, Math.floor(plotW / 110));
      for (let k = 0; k < nl; k++) {
        const i = Math.round((n - 1) * (k + 0.5) / nl);
        ctx.fillText(shortTs(d.t[i]), x(i), h - padB / 2);
      }
      // hover
      if (hov && hov.x >= padL && hov.x <= padL + plotW) {
        const i = Math.max(0, Math.min(n - 1, Math.floor((hov.x - padL) / cw)));
        ctx.strokeStyle = 'rgba(230,237,247,.35)'; ctx.lineWidth = 1; ctx.setLineDash([3, 3]);
        ctx.beginPath(); ctx.moveTo(Math.round(x(i)) + 0.5, padT); ctx.lineTo(Math.round(x(i)) + 0.5, r0 + rsiH); ctx.stroke(); ctx.setLineDash([]);
        return { x: x(i), y: Math.max(padT + 20, Math.min(hov.y, r0)), lines: [fmtTs(d.t[i]),
          ['O', fmtPx(d.o[i])], ['H', fmtPx(d.h[i])], ['L', fmtPx(d.l[i])], ['C', fmtPx(d.c[i])],
          ['EMA20', fmtPx(d.ema20 && d.ema20[i])], ['EMA60', fmtPx(d.ema60 && d.ema60[i])],
          ['BB', fmtPx(d.bb_lo && d.bb_lo[i]) + ' – ' + fmtPx(d.bb_up && d.bb_up[i])], ['RSI', fmtN(d.rsi && d.rsi[i], 1)], ['Vol', fmtN(d.v[i], 2)]] };
      }
      return null;
    }, { label: 'candlestick chart' });
  }
  function line(ctx, arr, x, y, color, width) {
    if (!arr) return;
    ctx.strokeStyle = color; ctx.lineWidth = width || 1.5; ctx.lineJoin = 'round';
    ctx.beginPath(); let pen = false;
    for (let i = 0; i < arr.length; i++) {
      const v = arr[i];
      if (!isNum(v)) { pen = false; continue; }
      if (!pen) { ctx.moveTo(x(i), y(v)); pen = true; } else ctx.lineTo(x(i), y(v));
    }
    ctx.stroke();
  }
  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }

  // Line chart. getData() -> {xs:[labels], ys:[numbers]}; opts: color, fill, ref (horizontal reference), fmtY, height, signColor
  function lineChart(getData, opts) {
    opts = opts || {};
    return makeChart(opts.height || 240, (ctx, w, h, hov) => {
      const d = getData(); if (!d || !d.ys || d.ys.length < 1) return null;
      const n = d.ys.length;
      const padL = 62, padR = 14, padT = 12, padB = 24;
      const pw = w - padL - padR, ph = h - padT - padB;
      let lo = Infinity, hi = -Infinity;
      d.ys.forEach((v) => { if (isNum(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); } });
      if (isNum(opts.ref)) { lo = Math.min(lo, opts.ref); hi = Math.max(hi, opts.ref); }
      if (!isFinite(lo)) return null;
      const pdd = (hi - lo) * 0.08 || Math.abs(hi) * 0.01 || 1; lo -= pdd; hi += pdd;
      const x = (i) => padL + (n === 1 ? pw / 2 : pw * i / (n - 1));
      const y = (v) => padT + (hi - v) / (hi - lo) * ph;
      const fy = opts.fmtY || ((v) => fmtN(v, 2));
      ctx.textAlign = 'right';
      drawYAxis(ctx, niceTicks(lo, hi, 5), y, padL, padL + pw, fy, false);
      if (isNum(opts.ref)) {
        ctx.setLineDash([4, 4]); ctx.strokeStyle = 'rgba(230,237,247,.3)'; ctx.beginPath(); ctx.moveTo(padL, y(opts.ref)); ctx.lineTo(padL + pw, y(opts.ref)); ctx.stroke(); ctx.setLineDash([]);
      }
      const lastV = d.ys[n - 1];
      const col = opts.color || (opts.signColor && isNum(opts.ref) ? (lastV >= opts.ref ? C.gain : C.loss) : C.accent);
      if (opts.fill !== false && n > 1) {
        const g = ctx.createLinearGradient(0, padT, 0, padT + ph);
        g.addColorStop(0, hexA(col, 0.22)); g.addColorStop(1, hexA(col, 0));
        ctx.beginPath(); ctx.moveTo(x(0), padT + ph);
        for (let i = 0; i < n; i++) if (isNum(d.ys[i])) ctx.lineTo(x(i), y(d.ys[i]));
        ctx.lineTo(x(n - 1), padT + ph); ctx.closePath(); ctx.fillStyle = g; ctx.fill();
      }
      line(ctx, d.ys, x, y, col, 2);
      if (n === 1) { ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x(0), y(d.ys[0]), 4, 0, 7); ctx.fill(); }
      ctx.fillStyle = C.axis; ctx.textAlign = 'center';
      if (d.xs && n > 1) {
        const nl = Math.max(2, Math.floor(pw / 120));
        for (let k = 0; k < nl; k++) { const i = Math.round((n - 1) * (k + 0.5) / nl); ctx.fillText(shortTs(d.xs[i]), x(i), h - padB / 2); }
      }
      if (hov && hov.x >= padL - 4 && hov.x <= padL + pw + 4) {
        const i = n === 1 ? 0 : Math.max(0, Math.min(n - 1, Math.round((hov.x - padL) / pw * (n - 1))));
        const v = d.ys[i]; if (!isNum(v)) return null;
        ctx.strokeStyle = 'rgba(230,237,247,.3)'; ctx.setLineDash([3, 3]); ctx.beginPath(); ctx.moveTo(x(i), padT); ctx.lineTo(x(i), padT + ph); ctx.stroke(); ctx.setLineDash([]);
        ctx.fillStyle = '#070d1a'; ctx.beginPath(); ctx.arc(x(i), y(v), 5, 0, 7); ctx.fill();
        ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x(i), y(v), 3.5, 0, 7); ctx.fill();
        return { x: x(i), y: y(v), lines: [d.xs ? fmtTs(d.xs[i]) : '#' + (i + 1), [opts.yLabel || t('value'), fy(v)]] };
      }
      return null;
    }, { label: opts.label });
  }
  function hexA(hex, a) {
    const m = /^#([0-9a-f]{6})$/i.exec(hex); if (!m) return hex;
    const n = parseInt(m[1], 16); return 'rgba(' + (n >> 16) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')';
  }

  // Histogram of values with optional vertical markers [{v,label,color}]
  function histogram(values, opts) {
    opts = opts || {};
    const vals = values.filter(isNum);
    return makeChart(opts.height || 260, (ctx, w, h, hov) => {
      if (!vals.length) return null;
      const padL = 44, padR = 14, padT = 20, padB = 28;
      const pw = w - padL - padR, ph = h - padT - padB;
      let lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
      (opts.markers || []).forEach((m) => { if (isNum(m.v) && opts.includeMarkers) { lo = Math.min(lo, m.v); hi = Math.max(hi, m.v); } });
      if (lo === hi) { lo -= 1; hi += 1; }
      const nb = Math.max(8, Math.min(opts.bins || 40, Math.ceil(Math.sqrt(vals.length) * 2)));
      const bw = (hi - lo) / nb;
      const counts = new Array(nb).fill(0);
      vals.forEach((v) => { counts[Math.min(nb - 1, Math.floor((v - lo) / bw))]++; });
      const cmax = Math.max.apply(null, counts);
      const x = (v) => padL + (v - lo) / (hi - lo) * pw;
      const y = (c) => padT + ph - c / cmax * ph;
      drawYAxis(ctx, niceTicks(0, cmax, 4).filter((v) => Number.isInteger(v)), y, padL, padL + pw, (v) => String(v), false);
      for (let b = 0; b < nb; b++) {
        if (!counts[b]) continue;
        const a = lo + b * bw, mid = a + bw / 2;
        ctx.fillStyle = (a <= 0 && a + bw > 0) ? 'rgba(169,182,204,0.6)' : mid > 0 ? 'rgba(34,197,94,0.75)' : 'rgba(239,68,68,0.75)';
        const x0 = x(a) + 1, x1 = x(a + bw) - 1;
        roundRect(ctx, x0, y(counts[b]), Math.max(1, x1 - x0), padT + ph - y(counts[b]), Math.min(3, (x1 - x0) / 2)); ctx.fill();
      }
      ctx.fillStyle = C.axis; ctx.textAlign = 'center';
      const xT = niceTicks(lo, hi, Math.max(3, Math.floor(pw / 80))), xDec = stepDecimals(xT);
      xT.forEach((v) => ctx.fillText(fmtN(v, xDec) + (opts.unit || ''), x(v), h - padB / 2 + 2));
      (opts.markers || []).forEach((m) => {
        if (!isNum(m.v)) return;
        const inRange = m.v >= lo && m.v <= hi;
        const xx = inRange ? x(m.v) : (m.v > hi ? padL + pw : padL);
        ctx.strokeStyle = m.color || C.amber; ctx.lineWidth = 1.5; ctx.setLineDash(inRange ? [] : [4, 3]);
        ctx.beginPath(); ctx.moveTo(xx, padT - 4); ctx.lineTo(xx, padT + ph); ctx.stroke(); ctx.setLineDash([]);
        ctx.fillStyle = m.color || C.amber; ctx.textAlign = xx > w - 120 ? 'right' : 'left';
        ctx.fillText(m.label + (inRange ? '' : (m.v > hi ? ' →' : ' ←')), xx + (ctx.textAlign === 'right' ? -4 : 4), padT - 10 + (m.row || 0) * 0);
      });
      if (hov && hov.x >= padL && hov.x <= padL + pw) {
        const b = Math.max(0, Math.min(nb - 1, Math.floor((hov.x - padL) / pw * nb)));
        const a = lo + b * bw;
        return { x: x(a + bw / 2), y: y(counts[b]), lines: [fmtN(a, 2) + (opts.unit || '') + ' … ' + fmtN(a + bw, 2) + (opts.unit || ''), [t('count'), String(counts[b])]] };
      }
      return null;
    }, { label: opts.label });
  }

  // Horizontal signed bars: items [{label, value}]
  function hbars(items, opts) {
    opts = opts || {};
    const rowH = 24;
    return makeChart(items.length * rowH + 34, (ctx, w, h, hov) => {
      if (!items.length) return null;
      ctx.font = FONT;
      let maxLab = 0; items.forEach((it) => { maxLab = Math.max(maxLab, ctx.measureText(it.label).width); });
      const padL = Math.min(Math.max(70, maxLab + 14), w * 0.42), padR = 64, padT = 6, padB = 24;
      const pw = w - padL - padR;
      let lo = isNum(opts.base) ? opts.base : 0, hi = lo; items.forEach((it) => { if (isNum(it.value)) { lo = Math.min(lo, it.value); hi = Math.max(hi, it.value); } });
      if (isNum(opts.ref)) { lo = Math.min(lo, opts.ref); hi = Math.max(hi, opts.ref); }
      if (opts.min != null) lo = Math.min(lo, opts.min);
      if (opts.max != null) hi = Math.max(hi, opts.max);
      if (lo === hi) hi = lo + 1;
      const x = (v) => padL + (v - lo) / (hi - lo) * pw;
      ctx.strokeStyle = C.grid; ctx.fillStyle = C.axis; ctx.textAlign = 'center';
      const hT = niceTicks(lo, hi, Math.max(2, Math.floor(pw / 90))), hDec = stepDecimals(hT);
      hT.forEach((v) => {
        ctx.beginPath(); ctx.moveTo(x(v) + 0.5, padT); ctx.lineTo(x(v) + 0.5, h - padB); ctx.stroke();
        ctx.fillText((opts.fmtTick || ((q) => fmtN(q, hDec)))(v), x(v), h - padB / 2 + 2);
      });
      const base = isNum(opts.base) ? opts.base : 0;
      items.forEach((it, i) => {
        const yc = padT + i * rowH + rowH / 2;
        ctx.fillStyle = C.text; ctx.textAlign = 'right';
        let lab = it.label; while (ctx.measureText(lab).width > padL - 12 && lab.length > 3) lab = lab.slice(0, -2);
        ctx.fillText(lab === it.label ? lab : lab + '…', padL - 8, yc);
        if (!isNum(it.value)) { ctx.fillStyle = C.axis; ctx.textAlign = 'left'; ctx.fillText('—', x(base) + 4, yc); return; }
        const pos = it.value >= base;
        ctx.fillStyle = it.color || (pos ? 'rgba(34,197,94,0.8)' : 'rgba(239,68,68,0.8)');
        const xa = x(Math.min(base, it.value)), xb = x(Math.max(base, it.value));
        roundRect(ctx, xa, yc - 7, Math.max(2, xb - xa), 14, 3); ctx.fill();
        ctx.fillStyle = C.text; ctx.textAlign = 'left';
        ctx.fillText((opts.fmt || ((v) => fmtN(v, 2)))(it.value), xb + 6, yc);
      });
      ctx.strokeStyle = 'rgba(230,237,247,.35)'; ctx.beginPath(); ctx.moveTo(x(base) + 0.5, padT); ctx.lineTo(x(base) + 0.5, h - padB); ctx.stroke();
      if (isNum(opts.ref)) {
        ctx.strokeStyle = C.amber; ctx.setLineDash([4, 3]); ctx.beginPath(); ctx.moveTo(x(opts.ref), padT); ctx.lineTo(x(opts.ref), h - padB); ctx.stroke(); ctx.setLineDash([]);
      }
      if (hov) {
        const i = Math.floor((hov.y - padT) / rowH);
        if (i >= 0 && i < items.length) {
          const it = items[i];
          return { x: Math.min(hov.x, w - 10), y: padT + i * rowH, lines: [it.label, [opts.valueLabel || t('value'), (opts.fmt || ((v) => fmtN(v, 2)))(it.value)]].concat(it.extra || []) };
        }
      }
      return null;
    }, { label: opts.label });
  }

  // Diverging color for heat cells. v in units, scale = |v| at full intensity
  function divColor(v, scale, pos, neg) {
    if (!isNum(v)) return null;
    const a = Math.max(-1, Math.min(1, v / (scale || 1)));
    const base = [19, 32, 58];
    const tgt = a >= 0 ? (pos || [34, 197, 94]) : (neg || [239, 68, 68]);
    const k = Math.pow(Math.abs(a), 0.7) * 0.85;
    const c = base.map((b, i) => Math.round(b + (tgt[i] - b) * k));
    return 'rgb(' + c.join(',') + ')';
  }
  function heatTable(rowLabels, colLabels, getV, opts) {
    opts = opts || {};
    const tbl = el('table', { class: 'heat' });
    const hr = el('tr', null, el('th', null, opts.corner || ''));
    colLabels.forEach((c) => hr.append(el('th', { scope: 'col', title: c }, opts.colFmt ? opts.colFmt(c) : c)));
    tbl.append(el('thead', null, hr));
    const tb = el('tbody');
    rowLabels.forEach((r) => {
      const tr = el('tr', null, el('th', { class: 'rl', scope: 'row' }, opts.rowFmt ? opts.rowFmt(r) : r));
      colLabels.forEach((c) => {
        const v = getV(r, c);
        const td = el('td', { class: isNum(v) ? '' : 'na', title: r + ' × ' + c + ': ' + (isNum(v) ? (opts.fmt || fmtN)(v) : '—') });
        if (isNum(v)) { td.style.background = divColor(v, opts.scale, opts.pos, opts.neg); td.textContent = (opts.fmt || fmtN)(v); } else td.textContent = '—';
        tr.append(td);
      });
      tb.append(tr);
    });
    tbl.append(tb);
    const legend = el('div', { class: 'scale-bar' },
      el('span', null, (opts.fmt || fmtN)(-opts.scale)),
      el('span', { class: 'grad', style: 'background:linear-gradient(90deg,' + divColor(-opts.scale, opts.scale, opts.pos, opts.neg) + ',' + divColor(0, 1) + ',' + divColor(opts.scale, opts.scale, opts.pos, opts.neg) + ')' }),
      el('span', null, (opts.fmt || fmtN)(opts.scale)), opts.legendNote ? el('span', null, '· ' + opts.legendNote) : null);
    return el('div', null, el('div', { class: 'heat-wrap' }, tbl), legend);
  }
  function legend(items) { return el('div', { class: 'legend' }, items.map((it) => el('span', null, el('i', { class: it[2] ? 'box' : '', style: 'background:' + it[1] }), it[0]))); }

  // ------------------------------------------------------------------ API
  let TOKEN = null;
  class ApiError extends Error { constructor(status, msg) { super(msg); this.status = status; } }
  async function api(path, opts) {
    opts = opts || {};
    const headers = { Authorization: 'Bearer ' + TOKEN, Accept: 'application/json' };
    const init = { method: opts.method || (opts.body !== undefined ? 'POST' : 'GET'), headers, cache: 'no-store' };
    if (opts.body !== undefined) { headers['Content-Type'] = 'application/json'; init.body = JSON.stringify(opts.body); }
    let r;
    try { r = await fetch(path, init); } catch (e) { throw new ApiError(0, t('err_network')); }
    if (r.status === 401) { logout(true); throw new ApiError(401, 'unauthorized'); }
    let data = null;
    try { data = await r.json(); } catch (e) { data = null; }
    if (!r.ok) throw new ApiError(r.status, (data && (data.detail || data.error)) || r.statusText || 'error');
    return data;
  }
  // Resolve to {ok,data} or {ok:false,error} so one failing endpoint never blanks a screen.
  function tryApi(path) { return api(path).then((d) => ({ ok: true, data: d }), (e) => ({ ok: false, error: e })); }
  function errorState(e, retry) {
    const box = empty(t('load_error'), e && e.status ? t('http_error', { code: e.status }) : null, e && e.message ? e.message : String(e), 'alert');
    box.classList.add('error-box');
    if (retry) box.append(el('button', { class: 'btn btn-sm', type: 'button', onclick: retry }, icon('refresh'), t('retry')));
    return box;
  }
  function section(res, render, retry) { return res.ok ? render(res.data) : errorState(res.error, retry); }

  // ------------------------------------------------------------------ live paper feed (WebSocket)
  let PAPER = null, PAPER_AT = 0, ws = null, wsRetry = 0, wsTimer = null, wsState = 'off';
  const paperListeners = new Set();
  function onPaper(f) { paperListeners.add(f); onCleanup(() => paperListeners.delete(f)); }
  function setWsState(s) {
    wsState = s;
    const p = document.getElementById('ws-pill');
    if (p) { p.className = 'ws-pill ' + s; p.lastChild.textContent = t(s === 'open' ? 'ws_open' : s === 'retry' ? 'ws_retry' : 'ws_off'); }
  }
  function wsConnect() {
    clearTimeout(wsTimer);
    if (!TOKEN) return;
    let sock;
    try { sock = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws'); } catch (e) { wsSchedule(); return; }
    ws = sock;
    sock.onopen = () => { try { sock.send(JSON.stringify({ token: TOKEN })); } catch (e) { /* closed */ } };
    sock.onmessage = (ev) => {
      let m; try { m = JSON.parse(ev.data); } catch (e) { return; }
      if (m && m.type === 'paper') {
        wsRetry = 0; if (wsState !== 'open') setWsState('open');
        PAPER = m.data; PAPER_AT = Date.now();
        paperListeners.forEach((f) => { try { f(PAPER); } catch (e) { console.warn(e); } });
      }
    };
    sock.onclose = (ev) => {
      if (ws === sock) ws = null;
      if (ev.code === 4401) { logout(true); return; }
      if (TOKEN) wsSchedule(); else setWsState('off');
    };
    sock.onerror = () => { /* onclose handles retry */ };
  }
  function wsSchedule() {
    setWsState('retry');
    const delay = Math.min(30000, 1000 * Math.pow(2, wsRetry++)) + Math.random() * 400;
    wsTimer = setTimeout(wsConnect, delay);
  }
  function wsStop() { clearTimeout(wsTimer); if (ws) { const s = ws; ws = null; s.onclose = null; try { s.close(); } catch (e) { /* ignore */ } } setWsState('off'); }
  function paperActive(s) { return !!(s && s.session_id); }

  // ------------------------------------------------------------------ screens
  const SCREENS = [
    { id: 'overview', g: 'g_command', ic: 'grid', r: scrOverview },
    { id: 'portfolio', g: 'g_trading', ic: 'wallet', r: scrPortfolio, b: ['VIRTUAL'] },
    { id: 'terminal', g: 'g_trading', ic: 'candle', r: scrTerminal, b: ['VIRTUAL', 'HISTORICAL'] },
    { id: 'trades', g: 'g_trading', ic: 'list', r: scrTrades, b: ['VIRTUAL'] },
    { id: 'pnl', g: 'g_trading', ic: 'chart', r: scrPnl, b: ['VIRTUAL'] },
    { id: 'market', g: 'g_research', ic: 'trend', r: scrMarket, b: ['HISTORICAL'] },
    { id: 'scanner', g: 'g_research', ic: 'radar', r: scrScanner, b: ['HISTORICAL'] },
    { id: 'heatmap', g: 'g_research', ic: 'heat', r: scrHeatmap, b: ['HISTORICAL'] },
    { id: 'strategies', g: 'g_research', ic: 'flask', r: scrStrategies, b: ['RESEARCH'] },
    { id: 'backtests', g: 'g_research', ic: 'rewind', r: scrBacktests, b: ['HISTORICAL', 'RESEARCH'] },
    { id: 'leaderboard', g: 'g_research', ic: 'trophy', r: scrLeaderboard, b: ['HISTORICAL', 'RESEARCH'] },
    { id: 'ml', g: 'g_research', ic: 'brain', r: scrMl, b: ['HISTORICAL', 'RESEARCH'] },
    { id: 'challenge', g: 'g_research', ic: 'target', r: scrChallenge, b: ['HISTORICAL', 'RESEARCH'] },
    { id: 'learning', g: 'g_research', ic: 'book', r: scrLearning, b: ['RESEARCH'] },
    { id: 'reports', g: 'g_research', ic: 'doc', r: scrReports, b: ['RESEARCH'] },
    { id: 'risk', g: 'g_risk', ic: 'shield', r: scrRisk, b: ['VIRTUAL'] },
    { id: 'agents', g: 'g_system', ic: 'cpu', r: scrAgents },
    { id: 'apis', g: 'g_system', ic: 'key', r: scrApis },
    { id: 'security', g: 'g_system', ic: 'lock', r: scrSecurity },
    { id: 'system', g: 'g_system', ic: 'pulse', r: scrSystem },
    { id: 'costs', g: 'g_system', ic: 'coin', r: scrCosts },
    { id: 'audit', g: 'g_system', ic: 'scroll', r: scrAudit },
    { id: 'settings', g: 'g_system', ic: 'gear', r: scrSettings },
  ];
  const GROUPS = ['g_command', 'g_trading', 'g_risk', 'g_research', 'g_system'];

  // 1 — Executive overview
  async function scrOverview() {
    const [ovR, smR] = await Promise.all([tryApi('/api/overview'), tryApi('/api/summary')]);
    if (!ovR.ok) return errorState(ovR.error, route);
    const ov = ovR.data;
    const ds = ov.data_sources || {};
    const root = el('div', { class: 'stack' });
    root.append(kpiGrid([
      kpi(t('mode'), ov.mode || '—', { accent: 'k-warn', small: true, badge: badge('VIRTUAL') }),
      kpi(t('live_trading'), ov.live_trading_enabled ? t('enabled') : t('disabled'), { accent: ov.live_trading_enabled ? 'k-loss' : 'k-gain', small: true }),
      kpi(t('paper_feed'), ds.paper_feed || '—', { small: true, badge: sourceBadge(ds.paper_feed) }),
      kpi(t('testnet'), String(ds.testnet || '—').split(' — ')[0], { small: true, badge: sourceBadge(ds.testnet), foot: String(ds.testnet || '').split(' — ')[1] || null }),
    ]));

    // paper
    const pp = ov.paper;
    if (pp) {
      const wr = pp.closed_trades ? 100 * pp.wins / pp.closed_trades : null;
      root.append(panel(t('paper_session'), {
        badges: [badge('VIRTUAL'), sourceBadge(pp.data_source)],
        body: kpiGrid([
          kpi(t('equity'), fmtUsd(pp.equity_usd), { accent: 'accent' }),
          kpi(t('net_pnl'), signed(fmtSignedUsd(pp.net_pnl_usd), pp.net_pnl_usd), { accent: pp.net_pnl_usd >= 0 ? 'k-gain' : 'k-loss' }),
          kpi(t('fees'), fmtUsd(pp.fees_usd)),
          kpi(t('closed_trades'), fmtInt(pp.closed_trades), { foot: t('win_rate') + ': ' + (wr == null ? '—' : fmtPct(wr, 1, false)) }),
          kpi(t('strategy'), pp.strategy || '—', { small: true, foot: pp.running ? t('running') : t('stopped') }),
        ]),
      }));
    } else {
      root.append(panel(t('paper_session'), { badges: [badge('VIRTUAL')], body: empty(t('paper_inactive'), t('paper_inactive_desc'), ov.inactive_reason, 'wallet') }));
    }

    // research summary
    let rs = smR.ok && !isNotRun(smR.data) ? smR.data : (ov.research && Object.keys(ov.research).length ? ov.research : null);
    if (!rs) {
      root.append(panel(t('research_summary'), { badges: [badge('RESEARCH')], body: notRunState('reports/summary.json', t('research_not_run')) }));
    } else {
      const val = rs.validated || [];
      root.append(panel(t('research_summary'), {
        badges: [badge('RESEARCH'), badge('HISTORICAL')],
        body: [
          kpiGrid([
            kpi(t('wf_runs'), fmtInt(rs.walk_forward_runs)),
            kpi(t('validated'), fmtInt(val.length), { accent: val.length ? 'k-gain' : 'k-warn' }),
            kpi(t('total_trials'), fmtInt(rs.total_backtest_trials)),
            kpi(t('should_trade'), rs.system_should_trade == null ? '—' : (rs.system_should_trade ? t('yes') : t('no')), { accent: rs.system_should_trade ? 'k-gain' : 'k-warn', small: true }),
            kpi(t('challenge_best'), rs.challenge_best || '—', { small: true, cls: 'mono-num' }),
            kpi(t('best_hit_rate'), fmtPct(rs.challenge_best_hit_rate, 2, false), { foot: t('target') + ' +100% / 4h' }),
            kpi(t('oracle_hit_rate'), fmtPct(rs.oracle_hit_rate, 2, false), { foot: t('oracle') }),
            kpi(t('finished'), fmtTs(rs.finished), { small: true, foot: t('duration') + ': ' + fmtDur(rs.seconds) }),
          ]),
          el('div', { class: 'mt' },
            el('div', { class: 'kpi-label' }, t('validated_list')),
            val.length ? el('div', { class: 'mt' }, val.map((v) => el('span', { class: 'chip' }, el('b', null, String(v[0])), ' · ', String(v[1]))))
              : el('div', { class: 'mt' }, callout('warn', 'info', t('none_validated')))),
          el('div', { class: 'grid grid-2 mt' },
            el('div', null, el('div', { class: 'kpi-label' }, t('ml_candidates')), el('div', { class: 'mt' }, (rs.ml_candidates || []).length ? rs.ml_candidates.map((c) => el('span', { class: 'chip' }, el('b', null, String(c[1])), ' · ', String(c[0]))) : el('span', { class: 'muted' }, t('none')))),
            el('div', null, el('div', { class: 'kpi-label' }, t('rl_candidates')), el('div', { class: 'mt' }, (rs.rl_candidates || []).length ? rs.rl_candidates.map((c) => el('span', { class: 'chip' }, String(c))) : el('span', { class: 'muted' }, t('none'))))),
        ],
      }));
    }

    const lim = (ov.risk && ov.risk.limits) || {};
    const orc = ov.challenge_oracle;
    root.append(el('div', { class: 'grid grid-2' },
      panel(t('data_sources'), {
        body: kv([
          [t('historical_data'), el('span', null, badge('HISTORICAL'))],
          [el('span', { class: 'muted wrap-any' }, ds.historical || '—'), ''],
          [t('paper_feed'), sourceBadge(ds.paper_feed)],
          [t('testnet'), el('span', { class: 'wrap-any' }, ds.testnet || '—')],
        ]),
      }),
      panel(t('risk_limits'), {
        body: kv([
          ['max_risk_per_trade_pct', fmtPct(lim.max_risk_per_trade_pct, 2, false)],
          ['max_session_loss_pct', fmtPct(lim.max_session_loss_pct, 2, false)],
          ['max_daily_loss_pct', fmtPct(lim.max_daily_loss_pct, 2, false)],
          ['max_drawdown_pct', fmtPct(lim.max_drawdown_pct, 2, false)],
          ['max_position_pct', fmtPct(lim.max_position_pct, 2, false)],
          ['allow_leverage / allow_short', (lim.allow_leverage ? t('yes') : t('no')) + ' / ' + (lim.allow_short ? t('yes') : t('no'))],
          ['live_trading_enabled', lim.live_trading_enabled ? t('yes') : t('no')],
        ]),
      })));
    if (orc) {
      root.append(panel(t('oracle'), {
        badges: [badge('HISTORICAL')], note: t('oracle_desc'),
        body: kpiGrid([
          kpi(t('sessions'), fmtInt(orc.sessions)), kpi(t('oracle_hit_rate'), fmtPct(orc.oracle_target_hit_rate_pct, 2, false)),
          kpi(t('oracle_median'), fmtPct(orc.oracle_median_pct)), kpi(t('oracle_p95'), fmtPct(orc.oracle_p95_pct)), kpi(t('oracle_max'), fmtPct(orc.oracle_max_pct)),
        ]),
      }));
    }
    return root;
  }

  // 2 — Virtual portfolio (REST + live WS)
  async function scrPortfolio() {
    const r = await tryApi('/api/portfolio');
    if (!r.ok) return errorState(r.error, route);
    const host = el('div', { class: 'stack' });
    let curveData = { xs: [], ys: [] }, chart = null, kpis = null, lastSession = null, ref = null;
    const stamp = el('span', { class: 'muted num' });
    function build(s) {
      host.replaceChildren();
      lastSession = s.session_id || null;
      if (!paperActive(s)) {
        kpis = null; chart = null;
        host.append(panel(t('paper_session'), {
          badges: [badge('VIRTUAL')],
          body: [empty(t('paper_inactive'), t('paper_inactive_desc'), s.inactive_reason, 'wallet'),
            el('div', { class: 'mt' }, kv([[t('virtual_capital') + ' (' + (s.label || 'VIRTUAL') + ')', fmtUsd(s.equity_usd)]]))],
        }));
        return;
      }
      ref = s.initial_usd;
      kpis = {
        eq: kpi(t('equity'), '', { accent: 'accent' }), pnl: kpi(t('net_pnl'), ''), cash: kpi(t('cash'), ''), fees: kpi(t('fees'), ''),
        pos: kpi(t('position'), '', { small: true }), last: kpi(t('last_price'), '', { small: true }), closed: kpi(t('closed_trades'), ''), wr: kpi(t('win_rate'), ''),
      };
      chart = lineChart(() => curveData, { ref: ref, signColor: true, height: 280, fmtY: (v) => '$' + fmtN(v, 2), yLabel: t('equity'), label: 'equity curve' });
      const info = el('div');
      host.append(
        el('div', { class: 'toolbar' }, badge('VIRTUAL'), sourceBadge(s.data_source), s.mode ? el('span', { class: 'badge b-neutral' }, String(s.mode).toUpperCase()) : null,
          el('span', { class: 'muted' }, t('live_ws') + ' · ' + t('updated') + ': '), stamp),
        kpiGrid(Object.values(kpis)),
        el('div', { class: 'grid grid-main-side' },
          panel(t('equity_curve'), { badges: [badge('VIRTUAL')], body: chart }),
          panel(t('paper_session'), { body: info })));
      host.info = info;
    }
    function update(s) {
      if (!s) return;
      if ((s.session_id || null) !== lastSession || !kpis) build(s);
      if (!kpis) return;
      const set = (k, v, cls) => { const n = kpis[k].valueEl; const txt = typeof v === 'string' ? v : null; if (txt !== null && n.textContent !== txt) { n.textContent = txt; n.classList.remove('flash'); void n.offsetWidth; n.classList.add('flash'); } else if (txt === null) n.replaceChildren(v); if (cls != null) n.className = 'kpi-value ' + cls; };
      set('eq', fmtUsd(s.equity_usd));
      set('pnl', fmtSignedUsd(s.net_pnl_usd), sgn(s.net_pnl_usd));
      set('cash', fmtUsd(s.cash_usd));
      set('fees', fmtUsd(s.fees_usd));
      set('pos', s.position_qty ? fmtQty(s.position_qty) + ' ' + (s.symbol || '') : '0', 'sm');
      set('last', fmtPx(s.last_price), 'sm');
      set('closed', fmtInt(s.closed_trades));
      set('wr', s.closed_trades ? fmtPct(100 * s.wins / s.closed_trades, 1, false) : '—');
      const ec = s.equity_curve || [];
      curveData = { xs: ec.map((p) => p[0]), ys: ec.map((p) => p[1]) };
      if (chart) {
        if (!ec.length && !chart.__empty) { chart.__empty = true; chart.parentNode.replaceChildren(chart, el('div', { class: 'muted' }, t('no_curve'))); }
        chart.repaint();
      }
      if (host.info) {
        host.info.replaceChildren(kv([
          [t('strategy'), el('span', { class: 'mono' }, s.strategy || '—')], [t('symbol'), s.symbol || '—'],
          [t('status'), s.running ? verdictBadge('RUNNING') : verdictBadge('STOPPED')],
          [t('initial'), fmtUsd(s.initial_usd)], [t('entry_px'), fmtPx(s.entry_px)], [t('stop_px'), fmtPx(s.stop_px)],
          [t('session_id'), el('span', { class: 'mono wrap-any' }, String(s.session_id || '—'))],
          [t('params'), el('span', { class: 'mono wrap-any' }, s.params ? JSON.stringify(s.params) : '—')],
        ]));
      }
      stamp.textContent = new Date().toLocaleTimeString('en-GB');
    }
    update(r.data);
    onPaper(update);
    return host;
  }

  // 3 — Market intelligence
  async function scrMarket() {
    const [mR, qR] = await Promise.all([tryApi('/api/market'), tryApi('/api/data-quality')]);
    const root = el('div', { class: 'stack' });
    root.append(section(mR, (m) => {
      const rows = m.markets || [];
      const names = Object.keys(m.correlation || {});
      const pieces = [panel(t('markets'), {
        badges: [badge('HISTORICAL')], flush: true,
        body: table([
          { key: 'dataset', label: t('dataset'), fmt: (v) => el('span', { class: 'mono' }, v) },
          { key: 'era', label: t('era') },
          { key: 'last', label: t('last_price'), num: true, fmt: fmtPx },
          { key: 'chg_4h_pct', label: t('chg_4h'), num: true, fmt: (v) => signed(fmtPct(v), v) },
          { key: 'chg_total_pct', label: t('chg_total'), num: true, fmt: (v) => signed(fmtPct(v), v) },
          { key: 'atr_pct', label: 'ATR %', num: true, fmt: (v) => fmtN(v, 3) },
          { key: 'rsi', label: 'RSI', num: true, fmt: (v) => fmtN(v, 1) },
          { key: 'adx', label: 'ADX', num: true, fmt: (v) => fmtN(v, 1) },
          { key: 'regime', label: t('regime'), fmt: (v) => el('span', { class: 'badge b-neutral' }, v || '—') },
          { key: 'quality_ok', label: t('quality'), fmt: (v) => verdictBadge(v ? 'OK' : 'FAIL') },
          { key: 'last_ts', label: t('last_bar'), fmt: (v) => el('span', { class: 'muted' }, fmtTs(v)) },
        ], rows),
      })];
      if (names.length) {
        pieces.push(panel(t('correlation'), {
          badges: [badge('HISTORICAL')], note: t('corr_note'),
          body: heatTable(names, names, (a, b) => (m.correlation[a] || {})[b], {
            scale: 1, fmt: (v) => fmtN(v, 2), pos: [20, 184, 166], neg: [239, 68, 68],
            rowFmt: (s) => s.replace('-5m', ''), colFmt: (s) => s.replace('-5m', '').replace('_', '/'),
          }),
        }));
      }
      return el('div', { class: 'stack' }, pieces);
    }, route));
    root.append(section(qR, (q) => {
      if (isNotRun(q)) return panel(t('quality'), { body: notRunState('reports/data_quality.json') });
      const rows = Object.keys(q).map((k) => Object.assign({ dataset: k }, q[k]));
      return panel(t('quality'), {
        badges: [badge('HISTORICAL')], flush: true,
        body: table([
          { key: 'dataset', label: t('dataset'), fmt: (v) => el('span', { class: 'mono' }, v) },
          { key: 'ok', label: t('status'), fmt: (v) => verdictBadge(v ? 'OK' : 'FAIL') },
          { key: 'rows', label: t('rows'), num: true, fmt: fmtInt },
          { key: 'gaps', label: t('gaps'), num: true, fmt: fmtInt },
          { key: 'missing_bars', label: t('missing_bars'), num: true, fmt: fmtInt },
          { key: 'duplicates', label: t('dupes'), num: true, fmt: fmtInt },
          { key: 'bad_ohlc', label: t('bad_ohlc'), num: true, fmt: fmtInt },
          { key: 'max_abs_return', label: t('max_ret'), num: true, fmt: (v) => fmtPct(isNum(v) ? v * 100 : v, 2, false) },
          { key: 'start', label: t('start'), fmt: (v) => el('span', { class: 'muted' }, fmtTs(v)) },
          { key: 'end', label: t('end'), fmt: (v) => el('span', { class: 'muted' }, fmtTs(v)) },
          { key: 'issues', label: t('issues'), cls: 'wrap', fmt: (v) => (v && v.length ? v.join('; ') : el('span', { class: 'muted' }, '—')) },
        ], rows),
      });
    }, route));
    return root;
  }

  // 4 — Scanner
  async function scrScanner() {
    const r = await tryApi('/api/scanner');
    if (!r.ok) return errorState(r.error, route);
    const rows = r.data.rows || [];
    if (!rows.length) return empty(t('no_data'));
    const strats = Object.keys(rows[0].signals || {});
    const sig = (v) => el('span', { class: 'sig ' + (v === 'ENTRY' ? 'sig-entry' : v === 'EXIT' ? 'sig-exit' : v === 'n/a' ? 'sig-na' : 'sig-none') }, v || '—');
    const entries = [];
    rows.forEach((row) => Object.keys(row.signals || {}).forEach((s) => { if (row.signals[s] === 'ENTRY') entries.push([row.dataset, s]); }));
    return el('div', { class: 'stack' },
      callout('info', 'info', [r.data.note || '', ' ', el('span', { class: 'muted' }, t('scanner_legend'))]),
      panel(t('entries_now'), { badges: [badge('HISTORICAL')], body: entries.length ? entries.map((e) => el('span', { class: 'chip' }, el('b', null, e[1]), ' · ', e[0])) : el('span', { class: 'muted' }, t('none')) }),
      panel(t('signals'), {
        badges: [badge('HISTORICAL')], flush: true,
        body: table([{ key: 'dataset', label: t('dataset'), fmt: (v) => el('span', { class: 'mono' }, v) },
          { key: 'regime', label: t('regime'), fmt: (v) => el('span', { class: 'badge b-neutral' }, v || '—') }]
          .concat(strats.map((s) => ({ key: 's_' + s, label: s, sort: (row) => row.signals[s], fmt: (v, row) => sig(row.signals[s]) })))
          .concat([{ key: 'as_of', label: t('as_of'), fmt: (v) => el('span', { class: 'muted' }, fmtTs(v)) }]), rows),
      }));
  }

  // 5 — Trading simulation terminal
  async function scrTerminal() {
    const sR = await tryApi('/api/settings');
    const datasets = sR.ok ? sR.data.datasets : ['BTC_USDT-5m'];
    let ds = store.get('atm.term.ds') || (sR.ok && sR.data.settings.replay_dataset) || datasets[0];
    if (datasets.indexOf(ds) < 0) ds = datasets[0];
    let itv = store.get('atm.term.itv') || '5m', lim = +(store.get('atm.term.lim') || 300);
    const chartHost = el('div');
    const legendEl = legend([['EMA 20', C.accent], ['EMA 60', C.amber], ['Bollinger (20, 2)', C.violet], ['RSI 14', C.violet]]);
    async function loadChart() {
      chartHost.replaceChildren(el('div', { class: 'sk tall' }));
      const r = await tryApi('/api/candles?dataset=' + encodeURIComponent(ds) + '&interval=' + encodeURIComponent(itv) + '&limit=' + lim);
      if (!r.ok) { chartHost.replaceChildren(errorState(r.error, loadChart)); return; }
      if (!r.data.c || !r.data.c.length) { chartHost.replaceChildren(empty(t('no_data'))); return; }
      const d = r.data; const n = d.c.length;
      const chg = 100 * (d.c[n - 1] / d.c[0] - 1);
      chartHost.replaceChildren(
        el('div', { class: 'toolbar', style: 'margin-bottom:6px' }, el('b', { class: 'mono' }, d.dataset), el('span', { class: 'muted' }, d.interval + ' · ' + n + ' ' + t('bars')),
          el('span', { class: 'num' }, fmtPx(d.c[n - 1])), signed(fmtPct(chg), chg), badge('HISTORICAL')),
        legendEl, candleChart(d));
    }
    const controls = el('div', { class: 'toolbar' },
      el('label', null, t('dataset'), select(datasets, ds, (v) => { ds = v; store.set('atm.term.ds', v); loadChart(); })),
      el('label', null, t('interval'), seg(['5m', '15m', '30m', '1h', '4h'].map((x) => [x, x]), itv, (v) => { itv = v; store.set('atm.term.itv', v); loadChart(); })),
      el('label', null, t('bars'), select([120, 300, 600, 1000], lim, (v) => { lim = +v; store.set('atm.term.lim', v); loadChart(); })));

    // paper side
    const status = el('div'); const logEl = el('div', { class: 'log' }); const tradesEl = el('div');
    const startBtn = el('button', { class: 'btn btn-primary', type: 'button' }, icon('play'), t('start_paper'));
    const startMsg = el('div', { class: 'mt' });
    startBtn.addEventListener('click', async () => {
      startBtn.disabled = true;
      try {
        const res = await api('/api/paper/start', { method: 'POST', body: {} });
        startMsg.replaceChildren(res.started ? callout('ok', 'check', t('paper_started'))
          : callout('warn', 'alert', [el('b', null, t('paper_not_started')), el('div', { class: 'mono wrap-any' }, t('server_msg') + ': ' + (res.inactive_reason || '—'))]));
      } catch (e) { startMsg.replaceChildren(errorState(e)); }
      startBtn.disabled = false;
    });
    function renderPaper(s) {
      if (!paperActive(s)) {
        status.replaceChildren(empty(t('paper_inactive'), t('paper_inactive_desc'), s && s.inactive_reason, 'wallet'));
        logEl.replaceChildren(el('div', null, el('span', { class: 'lt' }, ''), el('span', { class: 'lm' }, t('no_log'))));
        tradesEl.replaceChildren(empty(t('no_trades')));
        return;
      }
      status.replaceChildren(el('div', { class: 'toolbar' }, badge('VIRTUAL'), sourceBadge(s.data_source), s.running ? verdictBadge('RUNNING') : verdictBadge('STOPPED')),
        kv([[t('strategy'), el('span', { class: 'mono' }, s.strategy || '—')], [t('equity'), fmtUsd(s.equity_usd)],
          [t('net_pnl'), signed(fmtSignedUsd(s.net_pnl_usd), s.net_pnl_usd)], [t('position'), fmtQty(s.position_qty)], [t('last_price'), fmtPx(s.last_price)]]));
      const lg = (s.log || []).slice().reverse();
      logEl.replaceChildren();
      if (!lg.length) logEl.append(el('div', null, el('span', { class: 'lt' }, ''), el('span', { class: 'lm' }, t('no_log'))));
      lg.forEach((l) => logEl.append(el('div', null, el('span', { class: 'lt' }, fmtEpoch(l.t).slice(11)), el('span', { class: 'lm' }, l.msg))));
      tradesEl.replaceChildren(table([
        { key: 'ts', label: t('time'), fmt: (v) => fmtTs(v) }, { key: 'side', label: t('side'), fmt: (v) => el('span', { class: v === 'BUY' ? 'gain' : 'loss' }, v) },
        { key: 'qty', label: t('qty'), num: true, fmt: fmtQty }, { key: 'price', label: t('price'), num: true, fmt: fmtPx },
        { key: 'fee_usd', label: t('fee'), num: true, fmt: (v) => fmtUsd(v, 4) }, { key: 'pnl_usd', label: t('pnl'), num: true, fmt: (v) => (v == null ? '—' : signed(fmtSignedUsd(v), v)) },
        { key: 'reason', label: t('reason') }, { key: 'source', label: t('source'), fmt: (v, r) => sourceBadge(v) },
      ], (s.trades || []).slice().reverse(), { emptyText: t('no_trades'), sortable: false }));
    }
    const pr = await tryApi('/api/portfolio');
    renderPaper(PAPER && PAPER_AT > Date.now() - 6000 ? PAPER : (pr.ok ? pr.data : null));
    onPaper(renderPaper);
    loadChart();
    return el('div', { class: 'stack' },
      panel(t('chart'), { badges: [badge('HISTORICAL')], body: [controls, chartHost], note: t('ohlc_hist_note') }),
      el('div', { class: 'grid grid-2' },
        panel(t('paper_session'), { badges: [badge('VIRTUAL')], tools: startBtn, body: [status, startMsg] }),
        panel(t('session_log'), { badges: [badge('REPLAY')], flush: true, body: logEl })),
      panel(t('session_trades'), { badges: [badge('VIRTUAL')], flush: true, body: tradesEl }));
  }

  // 6 — Agents
  async function scrAgents() {
    const r = await tryApi('/api/agents');
    if (!r.ok) return errorState(r.error, route);
    const d = r.data;
    return el('div', { class: 'stack' },
      callout('info', 'info', t('agents_note')),
      panel(t('agents'), { flush: true, body: (d.agents || []).length ? table([
        { key: 'name', label: t('name'), fmt: (v) => el('b', { class: 'mono' }, v) }, { key: 'description', label: t('description'), cls: 'wrap' },
        { key: 'model', label: t('model') }, { key: 'kind', label: t('kind'), cls: 'wrap' }, { key: 'file', label: t('file'), fmt: (v) => el('span', { class: 'mono muted' }, v) },
      ], d.agents) : empty(t('no_agents')) }),
      el('div', { class: 'grid grid-2' },
        panel(t('skills'), { flush: true, body: (d.skills || []).length ? table([{ key: 'name', label: t('name'), fmt: (v) => el('b', { class: 'mono' }, v) }, { key: 'path', label: t('path'), fmt: (v) => el('span', { class: 'mono muted' }, v) }], d.skills) : empty(t('no_skills')) }),
        panel(t('services'), { body: (d.deterministic_services || []).map((s) => el('span', { class: 'chip' }, icon('check'), s)) })));
  }

  const GATE_ORDER = ['oos_trades', 'oos_net_return_positive', 'profit_factor', 'positive_folds', 'bootstrap_p_positive', 'holdout_positive', 'stress_2x_costs_nonnegative'];
  function gateKeys(g) { const ks = Object.keys(g || {}); return GATE_ORDER.filter((k) => ks.indexOf(k) >= 0).concat(ks.filter((k) => GATE_ORDER.indexOf(k) < 0)); }
  function gateLabel(k) { const s = t('g_' + k); return s === 'g_' + k ? k : s; }
  function gateVal(k, v) {
    if (!isNum(v)) return v == null ? '—' : String(v);
    if (k === 'positive_folds' || k === 'bootstrap_p_positive') return fmtN(v, 2);
    if (k === 'oos_trades') return fmtInt(v);
    if (k === 'profit_factor') return fmtN(v, 2);
    return fmtPct(v);
  }
  function gateChips(g) { return el('div', { class: 'gates' }, gateKeys(g).map((k) => el('span', { class: 'gate ' + (g[k].pass ? 'p' : 'f'), title: gateLabel(k) }, (g[k].pass ? '✓ ' : '✗ ') + gateLabel(k) + ': ' + gateVal(k, g[k].value)))); }
  function gateDots(g) {
    const ks = gateKeys(g); const n = ks.filter((k) => g[k].pass).length;
    return el('span', { title: t('passed_n', { n: n, m: ks.length }) }, el('span', { class: 'gate-dots' }, ks.map((k) => el('i', { class: g[k].pass ? 'p' : '', title: gateLabel(k) }))), ' ', el('span', { class: 'muted num' }, n + '/' + ks.length));
  }
  function gatesPassed(g) { return Object.keys(g || {}).filter((k) => g[k].pass).length; }

  // 7 — Strategy research lab
  async function scrStrategies() {
    const r = await tryApi('/api/strategies');
    if (!r.ok) return errorState(r.error, route);
    const d = r.data;
    const board = d.leaderboard || [];
    const byStrat = {};
    board.forEach((b) => { (byStrat[b.strategy] = byStrat[b.strategy] || []).push(b); });
    const cards = el('div', { class: 'cards' }, (d.library || []).map((s) => {
      const runs = byStrat[s.name] || [];
      const nVal = runs.filter((x) => x.verdict === 'VALIDATED').length;
      return el('div', { class: 'panel scard' },
        el('h3', null, s.name, el('span', { class: 'badge b-neutral' }, s.family)),
        el('p', null, s.description),
        el('div', null, Object.keys(s.defaults || {}).map((k) => el('span', { class: 'chip mono' }, k + '=', el('b', null, String(s.defaults[k]))))),
        runs.length ? el('div', { class: 'kpi-foot' }, t('runs') + ': ' + runs.length + ' · ' + t('validated') + ': ' + nVal) : el('div', { class: 'kpi-foot' }, t('no_wf')));
    }));
    const pieces = [panel(t('library'), { body: cards })];
    if (board.length) {
      pieces.push(panel(t('gate_results'), {
        badges: [badge('HISTORICAL'), badge('RESEARCH')], flush: true,
        body: table([
          { key: 'strategy', label: t('strategy'), fmt: (v) => el('b', { class: 'mono' }, v) },
          { key: 'dataset', label: t('dataset'), fmt: (v) => el('span', { class: 'mono' }, v) },
          { key: 'verdict', label: t('verdict'), fmt: verdictBadge },
          { key: 'gates', label: t('gates'), sort: (r2) => gatesPassed(r2.gates), fmt: (v) => gateChips(v || {}) },
        ], board, { sortKey: 'strategy', sortDir: 1, tall: true }),
      }));
    } else pieces.push(panel(t('gate_results'), { body: notRunState('reports/walk_forward.json', t('no_wf')) }));
    const reg = d.registry || [];
    pieces.push(panel(t('registry'), {
      flush: true,
      body: reg.length ? table([
        { key: 'name', label: t('strategy'), fmt: (v) => el('b', { class: 'mono' }, v) }, { key: 'version', label: t('version'), num: true },
        { key: 'dataset', label: t('dataset'), fmt: (v) => el('span', { class: 'mono' }, v) }, { key: 'status', label: t('status'), fmt: verdictBadge },
        { key: 'oos', label: t('oos_return'), num: true, sort: (x) => (x.metrics || {}).oos_return_pct, fmt: (v, x) => signed(fmtPct((x.metrics || {}).oos_return_pct), (x.metrics || {}).oos_return_pct) },
        { key: 'hold', label: t('holdout'), num: true, sort: (x) => (x.metrics || {}).holdout_return_pct, fmt: (v, x) => signed(fmtPct((x.metrics || {}).holdout_return_pct), (x.metrics || {}).holdout_return_pct) },
        { key: 'params', label: t('params'), cls: 'trunc', fmt: (v) => el('span', { class: 'mono muted', title: JSON.stringify(v) }, JSON.stringify(v)) },
        { key: 'created', label: t('created'), fmt: (v) => el('span', { class: 'muted' }, fmtEpoch(v)) },
      ], reg, { tall: true }) : empty(t('registry_empty')),
    }));
    return el('div', { class: 'stack' }, pieces);
  }

  // 8 — Backtesting lab
  async function scrBacktests() {
    const r = await tryApi('/api/backtests');
    if (!r.ok) return errorState(r.error, route);
    if (isNotRun(r.data) || !Array.isArray(r.data)) return notRunState('reports/walk_forward.json');
    const all = r.data.map((x, i) => Object.assign({ _i: i }, x));
    if (!all.length) return empty(t('no_wf'));
    const dsets = Array.from(new Set(all.map((x) => x.dataset))).sort();
    const strats = Array.from(new Set(all.map((x) => x.strategy))).sort();
    let fD = '', fS = '', fV = '';
    const listHost = el('div'); const detail = el('div');
    detail.append(empty(t('select_run'), null, null, 'rewind'));
    function renderList() {
      const rows = all.filter((x) => (!fD || x.dataset === fD) && (!fS || x.strategy === fS) && (!fV || x.verdict === fV));
      listHost.replaceChildren(table([
        { key: 'strategy', label: t('strategy'), fmt: (v) => el('b', { class: 'mono' }, v) },
        { key: 'dataset', label: t('dataset'), fmt: (v) => el('span', { class: 'mono' }, v) },
        { key: 'verdict', label: t('verdict'), fmt: verdictBadge },
        { key: 'oos_compound_return_pct', label: t('oos_return'), num: true, fmt: (v) => signed(fmtPct(v), v) },
        { key: 'oos_trades', label: t('oos_trades'), num: true, fmt: fmtInt },
        { key: 'oos_profit_factor', label: t('pf'), num: true, fmt: (v) => fmtN(v, 2) },
        { key: 'hold', label: t('holdout'), num: true, sort: (x) => (x.holdout || {}).net_return_pct, fmt: (v, x) => signed(fmtPct((x.holdout || {}).net_return_pct), (x.holdout || {}).net_return_pct) },
        { key: 'stress', label: t('stress'), num: true, sort: (x) => (x.stress || {}).net_return_pct, fmt: (v, x) => signed(fmtPct((x.stress || {}).net_return_pct), (x.stress || {}).net_return_pct) },
        { key: 'gates', label: t('gates'), sort: (x) => gatesPassed(x.gates), fmt: (v) => gateDots(v || {}) },
      ], rows, { sortKey: 'oos_compound_return_pct', tall: true, onRow: showDetail }));
    }
    function metricsKv(m) {
      m = m || {};
      return kv([[t('net_return'), signed(fmtPct(m.net_return_pct), m.net_return_pct)], [t('gross_return'), fmtPct(m.gross_return_pct)],
        [t('trades_n'), fmtInt(m.trades)], [t('win_rate_short'), fmtPct(m.win_rate_pct, 1, false)], [t('pf'), fmtN(m.profit_factor, 2)],
        [t('max_dd'), fmtPct(m.max_drawdown_pct, 2, false)], [t('sharpe'), fmtN(m.sharpe, 2)], [t('total_fees'), fmtN(m.total_fees, 6)], [t('exposure'), fmtPct(m.exposure_pct, 1, false)]]);
    }
    function showDetail(x) {
      const mc = x.monte_carlo || {}, bs = x.bootstrap || {};
      const folds = x.folds || [];
      detail.replaceChildren(el('div', { class: 'stack' },
        el('div', { class: 'toolbar' }, el('b', { class: 'mono', style: 'font-size:15px' }, x.strategy + ' · ' + x.dataset), verdictBadge(x.verdict), badge('HISTORICAL'),
          x.optimised ? el('span', { class: 'badge b-neutral' }, t('optimised')) : null, isNum(x.seconds) ? el('span', { class: 'muted' }, fmtDur(x.seconds)) : null),
        panel(t('gates'), { body: gateChips(x.gates || {}) }),
        panel(t('fold_returns'), { body: folds.length ? hbars(folds.map((f, i) => ({ label: '#' + (i + 1) + ' ' + shortTs(f.test_start), value: f.net_return_pct, extra: [[t('trades_n'), fmtInt(f.trades)], [t('pf'), fmtN(f.profit_factor, 2)]] })), { fmt: (v) => fmtPct(v), valueLabel: t('net_return') }) : empty(t('no_data')) }),
        panel(t('folds'), { flush: true, body: table([
          { key: 'test_start', label: t('test_start'), fmt: fmtTs }, { key: 'test_end', label: t('test_end'), fmt: fmtTs },
          { key: 'net_return_pct', label: t('net_return'), num: true, fmt: (v) => signed(fmtPct(v), v) }, { key: 'trades', label: t('trades_n'), num: true, fmt: fmtInt },
          { key: 'win_rate_pct', label: t('win_rate_short'), num: true, fmt: (v) => fmtPct(v, 1, false) }, { key: 'profit_factor', label: t('pf'), num: true, fmt: (v) => fmtN(v, 2) },
          { key: 'max_drawdown_pct', label: t('max_dd'), num: true, fmt: (v) => fmtPct(v, 2, false) }, { key: 'sharpe', label: t('sharpe'), num: true, fmt: (v) => fmtN(v, 2) },
          { key: 'params', label: t('params'), cls: 'trunc', fmt: (v) => el('span', { class: 'mono muted', title: JSON.stringify(v) }, JSON.stringify(v)) },
        ], folds, { sortable: false }) }),
        el('div', { class: 'grid grid-2' },
          panel(t('holdout'), { body: metricsKv(x.holdout) }),
          panel(t('stress'), { body: metricsKv(x.stress) })),
        el('div', { class: 'grid grid-2' },
          panel(t('monte_carlo'), { body: mc.sims ? kv([[t('sims'), fmtInt(mc.sims)], ['trades/path', fmtInt(mc.trades_per_path)], [t('median_ret'), signed(fmtPct(mc.median_return_pct), mc.median_return_pct)],
            [t('p05_ret'), signed(fmtPct(mc.p05_return_pct), mc.p05_return_pct)], [t('p95_ret'), signed(fmtPct(mc.p95_return_pct), mc.p95_return_pct)], [t('p95_dd'), fmtPct(mc.p95_max_dd_pct, 2, false)]]) : empty(t('no_data'), 'sims = 0') }),
          panel(t('bootstrap'), { body: kv([[t('p_positive'), fmtN(bs.p_positive, 3)], [t('ci'), fmtN(bs.ci05, 4) + ' … ' + fmtN(bs.ci95, 4)]]) })),
        panel(t('final_params'), { body: el('div', null, Object.keys(x.final_params || {}).map((k) => el('span', { class: 'chip mono' }, k + '=', el('b', null, String(x.final_params[k]))))) })));
      if (window.innerWidth < 1180) detail.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    }
    const filters = el('div', { class: 'toolbar' },
      el('label', null, t('filter_dataset'), select([['', t('all')]].concat(dsets.map((x) => [x, x])), '', (v) => { fD = v; renderList(); })),
      el('label', null, t('filter_strategy'), select([['', t('all')]].concat(strats.map((x) => [x, x])), '', (v) => { fS = v; renderList(); })),
      el('label', null, t('filter_verdict'), select([['', t('all')], ['VALIDATED', 'VALIDATED'], ['REJECTED', 'REJECTED']], '', (v) => { fV = v; renderList(); })));
    renderList();
    const nVal = all.filter((x) => x.verdict === 'VALIDATED').length;
    return el('div', { class: 'stack' },
      kpiGrid([kpi(t('runs'), fmtInt(all.length)), kpi(t('validated'), fmtInt(nVal), { accent: nVal ? 'k-gain' : 'k-warn' }), kpi(t('dataset'), fmtInt(dsets.length)), kpi(t('strategy'), fmtInt(strats.length))]),
      panel(t('runs'), { badges: [badge('HISTORICAL')], body: [filters, listHost], note: t('sort_hint') }),
      detail);
  }

  // 9 — ML center
  async function scrMl() {
    const [mR, rR] = await Promise.all([tryApi('/api/ml'), tryApi('/api/rl')]);
    const root = el('div', { class: 'stack' });
    root.append(section(mR, (ml) => {
      if (isNotRun(ml)) return panel(t('ml_models'), { body: notRunState('reports/ml.json', t('ml_not_run')) });
      return el('div', { class: 'stack' }, Object.keys(ml).map((name) => {
        const res = ml[name] || {}; const models = res.models || {};
        const rows = Object.keys(models).map((k) => Object.assign({ model: k }, models[k]));
        return panel(name, {
          badges: [badge('HISTORICAL')],
          body: [
            el('div', { class: 'toolbar' }, el('span', { class: 'chip' }, t('horizon') + ': ', el('b', null, fmtInt(res.horizon))),
              el('span', { class: 'chip' }, t('label_pos') + ': ', el('b', null, fmtFrac(res.label_pos_rate))),
              el('span', { class: 'chip' }, 'cost: ', el('b', null, fmtN(res.cost_threshold, 5)))),
            el('div', { class: 'grid grid-main-side' },
              table([
                { key: 'model', label: 'model', fmt: (v) => el('b', { class: 'mono' }, v) },
                { key: 'verdict', label: t('verdict'), fmt: verdictBadge },
                { key: 'mean_auc', label: t('auc'), num: true, fmt: (v) => fmtN(v, 4) },
                { key: 'mean_brier', label: t('brier'), num: true, fmt: (v) => fmtN(v, 4) },
                { key: 'signals', label: t('signals'), num: true, fmt: fmtInt },
                { key: 'bt', label: t('net_return'), num: true, sort: (x) => (x.backtest || {}).net_return_pct, fmt: (v, x) => signed(fmtPct((x.backtest || {}).net_return_pct), (x.backtest || {}).net_return_pct) },
                { key: 'bt_tr', label: t('trades_n'), num: true, sort: (x) => (x.backtest || {}).trades, fmt: (v, x) => fmtInt((x.backtest || {}).trades) },
              ], rows, { sortKey: 'mean_auc' }),
              el('div', null, el('div', { class: 'kpi-label', style: 'margin-bottom:6px' }, t('ml_auc_chart')),
                hbars(rows.map((x) => ({ label: x.model, value: x.mean_auc, color: x.model.indexOf('baseline') === 0 ? 'rgba(169,182,204,0.55)' : x.verdict === 'CANDIDATE' ? 'rgba(245,158,11,0.85)' : 'rgba(34,211,238,0.75)' })),
                  { base: 0.5, min: 0.45, max: 0.6, fmt: (v) => fmtN(v, 3), fmtTick: (v) => fmtN(v, 2), valueLabel: 'AUC' }))),
          ],
        });
      }));
    }, route));
    root.append(section(rR, (rl) => {
      if (isNotRun(rl)) return panel(t('rl_title'), { body: notRunState('reports/rl.json', t('rl_not_run')) });
      const rows = Object.keys(rl).map((k) => Object.assign({ dataset: k }, rl[k]));
      return panel(t('rl_title'), {
        badges: [badge('HISTORICAL')], flush: true,
        body: table([
          { key: 'dataset', label: t('dataset'), fmt: (v) => el('span', { class: 'mono' }, v) }, { key: 'verdict', label: t('verdict'), fmt: verdictBadge },
          { key: 'train_bars', label: t('train_bars'), num: true, fmt: fmtInt },
          { key: 'r', label: t('net_return'), num: true, sort: (x) => (x.oos || {}).net_return_pct, fmt: (v, x) => signed(fmtPct((x.oos || {}).net_return_pct), (x.oos || {}).net_return_pct) },
          { key: 'tr', label: t('trades_n'), num: true, sort: (x) => (x.oos || {}).trades, fmt: (v, x) => fmtInt((x.oos || {}).trades) },
          { key: 'pf', label: t('pf'), num: true, sort: (x) => (x.oos || {}).profit_factor, fmt: (v, x) => fmtN((x.oos || {}).profit_factor, 2) },
          { key: 'dd', label: t('max_dd'), num: true, sort: (x) => (x.oos || {}).max_drawdown_pct, fmt: (v, x) => fmtPct((x.oos || {}).max_drawdown_pct, 2, false) },
          { key: 'fees', label: t('total_fees'), num: true, sort: (x) => (x.oos || {}).total_fees, fmt: (v, x) => fmtN((x.oos || {}).total_fees, 6) },
        ], rows),
      });
    }, route));
    return root;
  }

  // 10 — Four-hour challenge
  async function scrChallenge() {
    const [cR, sR] = await Promise.all([tryApi('/api/challenge'), tryApi('/api/challenge-sessions')]);
    if (!cR.ok) return errorState(cR.error, route);
    const ch = cR.data;
    const root = el('div', { class: 'stack' }, callout('info', 'target', t('challenge_q')));
    if (isNotRun(ch)) { root.append(notRunState('reports/challenge.json')); return root; }
    const summ = ch.summary || {};
    const rows = Object.keys(summ).map((k) => Object.assign({ strategy: k }, summ[k]));
    const orc = ch.oracle || {}, dbl = ch.doubling_analysis || null;
    const best = ch.best_by_mean && summ[ch.best_by_mean];
    root.append(kpiGrid([
      kpi(t('capital'), fmtUsd(ch.capital_usd), { badge: badge('VIRTUAL') }),
      kpi(t('target'), fmtPct(ch.target_pct), { foot: fmtUsd(ch.capital_usd) + ' → ' + (isNum(ch.capital_usd) && isNum(ch.target_pct) ? fmtUsd(ch.capital_usd * (1 + ch.target_pct / 100)) : '—') }),
      kpi(t('challenge_best'), ch.best_by_mean || '—', { small: true }),
      kpi(t('best_hit_rate'), best ? fmtPct(best.target_hit_rate_pct, 2, false) : '—', { accent: best && best.target_hit_rate_pct > 0 ? 'k-gain' : 'k-loss', foot: best ? t('target_hits') + ': ' + fmtInt(best.target_hits) + ' / ' + fmtInt(best.sessions) : null }),
      kpi(t('oracle_hit_rate'), fmtPct(orc.oracle_target_hit_rate_pct, 2, false), { accent: 'k-warn', foot: t('oracle') }),
    ]));
    root.append(panel(t('s_challenge') + ' — ' + t('strategy'), {
      badges: [badge('HISTORICAL'), badge('VIRTUAL')], flush: true, note: t('sort_hint'),
      body: table([
        { key: 'strategy', label: t('strategy'), fmt: (v) => el('b', { class: 'mono' }, v) },
        { key: 'sessions', label: t('sessions'), num: true, fmt: fmtInt },
        { key: 'target_hits', label: t('target_hits'), num: true, fmt: fmtInt },
        { key: 'target_hit_rate_pct', label: t('hit_rate'), num: true, fmt: (v) => fmtPct(v, 2, false) },
        { key: 'mean_return_pct', label: t('mean'), num: true, fmt: (v) => signed(fmtPct(v, 3), v) },
        { key: 'median_return_pct', label: t('median'), num: true, fmt: (v) => signed(fmtPct(v, 3), v) },
        { key: 'best_return_pct', label: t('best'), num: true, fmt: (v) => signed(fmtPct(v), v) },
        { key: 'worst_return_pct', label: t('worst'), num: true, fmt: (v) => signed(fmtPct(v), v) },
        { key: 'prob_loss_pct', label: t('prob_loss'), num: true, fmt: (v) => fmtPct(v, 1, false) },
        { key: 'prob_no_trade_pct', label: t('no_trade'), num: true, fmt: (v) => fmtPct(v, 1, false) },
        { key: 'consistency_pct_positive', label: t('consistency'), num: true, fmt: (v) => fmtPct(v, 1, false) },
        { key: 'worst_max_dd_pct', label: t('worst_dd'), num: true, fmt: (v) => fmtPct(v, 2, false) },
        { key: 'mean_fees_usd', label: t('mean_fees'), num: true, fmt: (v) => fmtUsd(v, 3) },
        { key: 'sharpe_like', label: 'μ/σ', num: true, fmt: (v) => fmtN(v, 3) },
      ], rows, { sortKey: 'mean_return_pct', tall: true }),
    }));
    // histogram
    const sessions = sR.ok && !isNotRun(sR.data) ? sR.data : null;
    const strategies = sessions ? Object.keys(sessions) : [];
    let sel = store.get('atm.ch.strat');
    if (strategies.indexOf(sel) < 0) sel = ch.best_by_mean && strategies.indexOf(ch.best_by_mean) >= 0 ? ch.best_by_mean : strategies[0];
    const histHost = el('div');
    function renderHist() {
      const list = (sessions && sessions[sel]) || [];
      if (!list.length) { histHost.replaceChildren(empty(t('sessions_missing'))); return; }
      const vals = list.map((x) => x.ret_pct);
      const s = summ[sel] || {};
      histHost.replaceChildren(
        el('div', { class: 'toolbar' }, el('span', { class: 'chip' }, t('sessions') + ': ', el('b', null, fmtInt(vals.length))),
          el('span', { class: 'chip' }, t('mean') + ': ', el('b', { class: sgn(s.mean_return_pct) }, fmtPct(s.mean_return_pct, 3))),
          el('span', { class: 'chip' }, t('best') + ': ', el('b', null, fmtPct(s.best_return_pct))),
          el('span', { class: 'chip' }, t('target') + ': ', el('b', { class: 'warn' }, fmtPct(ch.target_pct)))),
        legend([[t('h_gain'), 'rgba(34,197,94,0.75)', true], [t('h_zero'), 'rgba(169,182,204,0.6)', true], [t('h_loss'), 'rgba(239,68,68,0.75)', true]]),
        histogram(vals, { unit: '%', markers: [{ v: 0, label: '0%', color: 'rgba(230,237,247,.6)' }, { v: ch.target_pct, label: t('target_line') + ' ' + fmtPct(ch.target_pct, 0), color: C.amber }], label: 'session return histogram' }));
    }
    const histPanel = panel(t('session_hist'), {
      badges: [badge('HISTORICAL')],
      tools: strategies.length ? select(strategies, sel, (v) => { sel = v; store.set('atm.ch.strat', v); renderHist(); }, { 'aria-label': t('strategy') }) : null,
      body: sessions ? histHost : (sR.ok ? notRunState('reports/challenge_sessions.json') : errorState(sR.error)),
    });
    if (sessions) renderHist();
    root.append(histPanel);
    root.append(el('div', { class: 'grid grid-2' },
      panel(t('oracle'), { badges: [badge('HISTORICAL')], note: t('oracle_desc'), body: kv([
        [t('sessions'), fmtInt(orc.sessions)], [t('oracle_hit_rate'), fmtPct(orc.oracle_target_hit_rate_pct, 2, false)],
        [t('oracle_median'), fmtPct(orc.oracle_median_pct)], [t('oracle_p95'), fmtPct(orc.oracle_p95_pct)], [t('oracle_max'), fmtPct(orc.oracle_max_pct)],
        [t('abs_move_med'), fmtPct(orc.abs_price_change_median_pct, 3, false)], [t('abs_move_max'), fmtPct(orc.abs_price_change_max_pct, 2, false)]]) }),
      panel(t('doubling') + (ch.best_by_mean ? ' · ' + ch.best_by_mean : ''), { body: !dbl ? empty(t('no_data')) : kv([
        [t('doubling_possible'), verdictBadge(dbl.doubling_possible ? 'YES' : 'NO')],
        dbl.reason ? [t('reason'), el('span', { class: 'wrap-any' }, dbl.reason)] : null,
        dbl.doubling_possible ? [t('p_double'), fmtFrac(dbl.p_double_within_max)] : null,
        dbl.doubling_possible ? [t('median_sessions'), dbl.median_sessions == null ? '—' : fmtN(dbl.median_sessions, 0)] : null,
        dbl.doubling_possible ? [t('max_sessions'), fmtInt(dbl.max_sessions)] : null,
        dbl.doubling_possible ? [t('p_ruin'), fmtFrac(dbl.p_ruin_50pct)] : null]) })));
    return root;
  }

  // 11 — Risk
  async function scrRisk() {
    const r = await tryApi('/api/risk');
    if (!r.ok) return errorState(r.error, route);
    const d = r.data; const L = d.limits || {}; const S = d.state;
    const estop = el('button', { class: 'estop', type: 'button' }, icon('stop'), t('estop'), el('small', null, t('estop_sub')));
    estop.addEventListener('click', async () => {
      const ok = await modal({ title: t('estop_confirm_t'), body: t('estop_confirm_b'), danger: true, okText: t('estop') });
      if (!ok) return;
      try { await api('/api/emergency-stop', { method: 'POST', body: {} }); toast(t('estop_done'), 'err'); route(); } catch (e) { toast(t('save_failed') + ': ' + e.message, 'err'); }
    });
    const resume = el('button', { class: 'btn', type: 'button' }, icon('play'), t('resume'));
    resume.addEventListener('click', async () => {
      const v = await modal({ title: t('resume_t'), body: t('resume_b'), requireText: 'RESUME', okText: t('resume') });
      if (v !== 'RESUME') return;
      try { await api('/api/resume', { method: 'POST', body: { confirm: 'RESUME' } }); toast(t('resume_done'), 'ok'); route(); } catch (e) { toast(t('save_failed') + ': ' + e.message, 'err'); }
    });
    const limRows = Object.keys(L).map((k) => ({ k: k, v: L[k] }));
    return el('div', { class: 'stack' },
      el('div', { class: 'grid grid-main-side' },
        panel(t('kill_switch'), {
          badges: [d.kill_file ? el('span', { class: 'badge b-rejected' }, 'KILL ' + t('active')) : el('span', { class: 'badge b-validated' }, 'KILL ' + t('inactive'))],
          body: [d.kill_file ? callout('danger', 'alert', t('estop_done')) : null, el('div', { class: d.kill_file ? 'mt' : '' }, estop), el('div', { class: 'mt', style: 'display:flex;justify-content:flex-end' }, resume)],
        }),
        panel(t('risk_state'), { badges: [badge('VIRTUAL')], body: S ? kv([
          [t('peak'), fmtUsd(S.peak)], [t('session_start_eq'), fmtUsd(S.session_start_equity)], [t('day_start_eq'), fmtUsd(S.day_start_equity)],
          [t('consec_losses'), fmtInt(S.consecutive_losses)], [t('pause_remaining'), fmtInt(S.pause_remaining)],
          [t('halted'), S.halted_reason ? el('span', { class: 'loss wrap-any' }, S.halted_reason) : t('no')], [t('killed'), S.killed_reason ? el('span', { class: 'loss wrap-any' }, S.killed_reason) : t('no')]]) : empty(t('no_risk_state'), null, null, 'shield') })),
      panel(t('limits'), { flush: true, note: (d.note || '') + ' ' + (d.editable_via_api === false ? t('risk_editable_note') : ''), body: table([
        { key: 'k', label: t('name'), fmt: (v) => el('span', { class: 'mono' }, v) },
        { key: 'v', label: t('value'), num: true, fmt: (v, row) => (typeof v === 'boolean' ? verdictBadge(v ? (row.k.indexOf('allow') === 0 || row.k.indexOf('live') === 0 ? 'ENABLED' : 'YES') : 'DISABLED') : (/_pct$/.test(row.k) ? fmtPct(v, 2, false) : fmtN(v, Number.isInteger(v) ? 0 : 2))) },
      ], limRows, { sortable: false }) }),
      panel(t('risk_events'), { flush: true, body: (d.events || []).length ? table([
        { key: 'type', label: t('event_type'), fmt: verdictBadge }, { key: 'ts', label: t('time'), fmt: (v) => fmtTs(v) }, { key: 'reason', label: t('reason'), cls: 'wrap' },
      ], d.events.slice().reverse(), { sortable: false }) : empty(t('no_events')) }));
  }

  // 12 — P&L analytics
  async function scrPnl() {
    const [pR, tR] = await Promise.all([tryApi('/api/portfolio'), tryApi('/api/trades')]);
    const root = el('div', { class: 'stack' });
    let snap = pR.ok ? pR.data : null;
    let curve = { xs: [], ys: [] }, dd = { xs: [], ys: [] };
    const curveHost = el('div');
    let eqChart = null, ddChart = null;
    function calc(s) {
      const ec = (s && s.equity_curve) || [];
      curve = { xs: ec.map((p) => p[0]), ys: ec.map((p) => p[1]) };
      let pk = -Infinity; dd = { xs: curve.xs, ys: curve.ys.map((v) => { pk = Math.max(pk, v); return pk > 0 ? 100 * (v / pk - 1) : 0; }) };
    }
    function renderCurves(s) {
      calc(s);
      if (!paperActive(s) || !curve.ys.length) {
        eqChart = ddChart = null;
        curveHost.replaceChildren(panel(t('equity_curve'), { badges: [badge('VIRTUAL')], body: empty(t('paper_inactive'), t('no_curve'), s && s.inactive_reason, 'chart') }));
        return;
      }
      if (!eqChart) {
        eqChart = lineChart(() => curve, { ref: s.initial_usd, signColor: true, height: 260, fmtY: (v) => '$' + fmtN(v, 2), yLabel: t('equity') });
        ddChart = lineChart(() => dd, { color: C.loss, height: 160, fmtY: (v) => fmtN(v, 2) + '%', yLabel: t('drawdown') });
        curveHost.replaceChildren(el('div', { class: 'grid grid-main-side' },
          panel(t('equity_curve'), { badges: [badge('VIRTUAL'), sourceBadge(s.data_source)], body: eqChart }),
          panel(t('drawdown'), { badges: [badge('VIRTUAL')], body: [ddChart, el('div', { class: 'mt' }, kv([[t('max_dd_curve'), fmtPct(Math.min.apply(null, dd.ys), 2)]]))] })));
      } else { eqChart.repaint(); ddChart.repaint(); }
    }
    renderCurves(snap);
    onPaper((s) => { const was = paperActive(snap); snap = s; if (was !== paperActive(s)) eqChart = null; renderCurves(s); });
    root.append(curveHost);
    root.append(section(tR, (td) => {
      const closed = (td.paper_trades || []).filter((x) => isNum(x.pnl)).slice().reverse();
      if (!closed.length) return panel(t('trade_pnl'), { badges: [badge('VIRTUAL')], body: empty(t('pnl_none'), null, null, 'chart') });
      const pnl = closed.map((x) => x.pnl);
      const gp = pnl.filter((v) => v > 0).reduce((a, b) => a + b, 0), gl = -pnl.filter((v) => v <= 0).reduce((a, b) => a + b, 0);
      const fees = (td.paper_trades || []).reduce((a, x) => a + (isNum(x.fee) ? x.fee : 0), 0);
      let cum = 0; const cumS = { xs: closed.map((x) => x.ts), ys: pnl.map((v) => (cum += v)) };
      const wins = pnl.filter((v) => v > 0).length;
      return el('div', { class: 'stack' },
        kpiGrid([kpi(t('closed_trades'), fmtInt(closed.length)), kpi(t('win_rate'), fmtPct(100 * wins / closed.length, 1, false)),
          kpi(t('gross_profit'), el('span', { class: 'gain' }, fmtN(gp, 6))), kpi(t('gross_loss'), el('span', { class: 'loss' }, fmtN(-gl, 6))),
          kpi(t('profit_factor'), gl > 0 ? fmtN(gp / gl, 2) : (gp > 0 ? '∞' : '—')), kpi(t('total_fees'), fmtN(fees, 6))]),
        el('div', { class: 'grid grid-2' },
          panel(t('cum_pnl'), { badges: [badge('VIRTUAL')], body: lineChart(() => cumS, { ref: 0, signColor: true, height: 220, fmtY: (v) => fmtN(v, 4), yLabel: t('cum_pnl') }) }),
          panel(t('trade_pnl'), { badges: [badge('VIRTUAL')], body: hbars(closed.slice(-30).map((x, i) => ({ label: shortTs(x.ts) + ' ' + (x.symbol || ''), value: x.pnl })), { fmt: (v) => fmtN(v, 4), valueLabel: t('pnl') }) })),
        el('div', { class: 'muted' }, t('pnl_quote_note')));
    }, route));
    return root;
  }

  // 13 — Trade history
  async function scrTrades() {
    const r = await tryApi('/api/trades');
    if (!r.ok) return errorState(r.error, route);
    const rows = r.data.paper_trades || [];
    return el('div', { class: 'stack' },
      callout('info', 'info', [badge('VIRTUAL'), ' ', r.data.label || '']),
      panel(t('s_trades'), { badges: [badge('VIRTUAL')], flush: true, note: rows.length ? t('pnl_quote_note') : null, body: table([
        { key: 'id', label: '#', num: true }, { key: 'ts', label: t('time'), fmt: fmtTs },
        { key: 'symbol', label: t('symbol'), fmt: (v) => el('span', { class: 'mono' }, v) },
        { key: 'side', label: t('side'), fmt: (v) => el('span', { class: v === 'BUY' ? 'gain' : 'loss' }, v) },
        { key: 'qty', label: t('qty'), num: true, fmt: fmtQty }, { key: 'price', label: t('price'), num: true, fmt: fmtPx },
        { key: 'fee', label: t('fee'), num: true, fmt: (v) => fmtN(v, 6) }, { key: 'pnl', label: t('pnl'), num: true, fmt: (v) => (v == null ? '—' : signed(fmtN(v, 6), v)) },
        { key: 'strategy', label: t('strategy'), fmt: (v) => el('span', { class: 'mono' }, v) }, { key: 'source', label: t('source'), fmt: sourceBadge },
        { key: 'session', label: t('session'), fmt: (v) => el('span', { class: 'mono muted' }, String(v || '').slice(0, 12)) },
      ], rows, { tall: true, emptyText: t('no_trades'), sortKey: 'id' }) }));
  }

  // 14 — Heatmap
  async function scrHeatmap() {
    const [mR, tR] = await Promise.all([tryApi('/api/market'), tryApi('/api/timeframes')]);
    const root = el('div', { class: 'stack' });
    root.append(section(mR, (m) => {
      const rows = m.markets || [];
      let metric = store.get('atm.heat.metric') || 'chg_4h_pct';
      const tiles = el('div', { class: 'tiles' });
      function draw() {
        const vals = rows.map((x) => x[metric]).filter(isNum);
        const scale = Math.max(0.1, Math.max.apply(null, vals.map(Math.abs).concat([0.1])));
        tiles.replaceChildren();
        rows.slice().sort((a, b) => (b[metric] || 0) - (a[metric] || 0)).forEach((x) => {
          const v = x[metric];
          tiles.append(el('div', { class: 'tile', style: 'background:' + (divColor(v, scale) || '#0d1628'), title: x.dataset + ' · ' + x.era },
            el('div', null, el('div', { class: 't-name' }, x.symbol), el('div', { class: 't-sub' }, x.dataset + ' · ' + x.era)),
            el('div', { class: 't-val' }, fmtPct(v)), el('div', { class: 't-sub' }, x.regime + ' · RSI ' + fmtN(x.rsi, 0))));
        });
      }
      draw();
      return panel(t('heat_tiles'), {
        badges: [badge('HISTORICAL')], tools: seg([['chg_4h_pct', t('chg_4h')], ['chg_total_pct', t('chg_total')]], metric, (v) => { metric = v; store.set('atm.heat.metric', v); draw(); }),
        body: tiles,
      });
    }, route));
    root.append(section(tR, (tf) => {
      if (isNotRun(tf)) return panel(t('tf_grid'), { body: notRunState('reports/timeframes.json', t('tf_not_run')) });
      return el('div', { class: 'grid grid-2' }, Object.keys(tf).map((ds) => {
        const tfs = Object.keys(tf[ds] || {});
        const strats = Array.from(new Set([].concat.apply([], tfs.map((x) => Object.keys(tf[ds][x] || {})))));
        const vals = []; tfs.forEach((x) => strats.forEach((s) => { const v = ((tf[ds][x] || {})[s] || {}).net_return_pct; if (isNum(v)) vals.push(Math.abs(v)); }));
        const scale = Math.max(0.5, Math.max.apply(null, vals.concat([0.5])));
        return panel(ds, { badges: [badge('HISTORICAL')], body: heatTable(strats, tfs, (s, x) => (((tf[ds] || {})[x] || {})[s] || {}).net_return_pct, { scale: scale, fmt: (v) => fmtN(v, 2), corner: t('strategy') }) });
      }).concat([el('div', { class: 'muted', style: 'grid-column:1/-1' }, t('tf_grid'))]));
    }, route));
    return root;
  }

  // 15 — Reports
  async function scrReports() {
    const r = await tryApi('/api/reports');
    if (!r.ok) return errorState(r.error, route);
    const files = r.data.files || [];
    return el('div', { class: 'grid grid-main-side' },
      panel(t('report_md'), { badges: [badge('RESEARCH')], body: r.data.research_report_md ? renderMarkdown(r.data.research_report_md) : notRunState('reports/RESEARCH_REPORT.md', t('report_missing')) }),
      panel(t('files'), { body: files.length ? files.map((f) => el('div', { class: 'chip mono', style: 'display:flex' }, icon('doc'), f)) : empty(t('no_files')) }));
  }

  // 16 — Learning history
  async function scrLearning() {
    const r = await tryApi('/api/learning');
    if (!r.ok) return errorState(r.error, route);
    const ex = r.data.experiments || [];
    if (!ex.length) return empty(t('no_experiments'), null, null, 'book');
    const kinds = Array.from(new Set(ex.map((x) => x.kind))).sort();
    const counts = {}; ex.forEach((x) => { counts[x.verdict] = (counts[x.verdict] || 0) + 1; });
    let fk = '';
    const host = el('div');
    const draw = () => host.replaceChildren(table([
      { key: 'id', label: '#', num: true }, { key: 'kind', label: t('kind'), fmt: (v) => el('span', { class: 'badge b-neutral' }, v) },
      { key: 'hypothesis', label: t('hypothesis'), cls: 'wrap' }, { key: 'verdict', label: t('verdict'), fmt: verdictBadge },
      { key: 'created', label: t('created'), fmt: (v) => el('span', { class: 'muted' }, fmtEpoch(v)) },
    ], ex.filter((x) => !fk || x.kind === fk), { tall: true, sortKey: 'id' }));
    draw();
    return el('div', { class: 'stack' },
      kpiGrid([kpi(t('experiments'), fmtInt(ex.length))].concat(Object.keys(counts).map((k) => kpi(k, fmtInt(counts[k]), { accent: k === 'VALIDATED' || k === 'CANDIDATE' ? 'k-gain' : k === 'REJECTED' ? 'k-loss' : '' })))),
      panel(t('experiments'), { badges: [badge('RESEARCH')], tools: select([['', t('all')]].concat(kinds.map((k) => [k, k])), '', (v) => { fk = v; draw(); }, { 'aria-label': t('kind') }), flush: true, body: host }));
  }

  // 17 — Leaderboard
  async function scrLeaderboard() {
    const r = await tryApi('/api/strategies');
    if (!r.ok) return errorState(r.error, route);
    const board = r.data.leaderboard || [];
    if (!board.length) return notRunState('reports/walk_forward.json', t('no_wf'));
    const dsets = Array.from(new Set(board.map((x) => x.dataset))).sort();
    let fD = '', fV = '';
    const host = el('div');
    const draw = () => host.replaceChildren(table([
      { key: 'rank', label: '#', num: true, sort: (x) => -x.oos_return_pct, fmt: (v, x) => String(board.indexOf(x) + 1) },
      { key: 'strategy', label: t('strategy'), fmt: (v) => el('b', { class: 'mono' }, v) },
      { key: 'dataset', label: t('dataset'), fmt: (v) => el('span', { class: 'mono' }, v) },
      { key: 'family', label: t('family'), fmt: (v) => el('span', { class: 'badge b-neutral' }, v) },
      { key: 'verdict', label: t('verdict'), fmt: verdictBadge },
      { key: 'oos_return_pct', label: t('oos_return'), num: true, fmt: (v) => signed(fmtPct(v), v) },
      { key: 'oos_trades', label: t('oos_trades'), num: true, fmt: fmtInt },
      { key: 'pf', label: t('pf'), num: true, fmt: (v) => fmtN(v, 2) },
      { key: 'holdout_return_pct', label: t('holdout'), num: true, fmt: (v) => signed(fmtPct(v), v) },
      { key: 'stress_return_pct', label: t('stress'), num: true, fmt: (v) => signed(fmtPct(v), v) },
      { key: 'mc', label: 'MC ' + t('median'), num: true, sort: (x) => (x.mc || {}).median_return_pct, fmt: (v) => signed(fmtPct((v || {}).median_return_pct), (v || {}).median_return_pct) },
      { key: 'gates', label: t('gates'), sort: (x) => gatesPassed(x.gates), fmt: (v) => gateDots(v || {}) },
    ], board.filter((x) => (!fD || x.dataset === fD) && (!fV || x.verdict === fV)), { sortKey: 'oos_return_pct', tall: true }));
    draw();
    const top = board.slice(0, 12);
    return el('div', { class: 'stack' },
      panel(t('oos_return') + ' — top 12', { badges: [badge('HISTORICAL'), badge('RESEARCH')], body: hbars(top.map((x) => ({ label: x.strategy + ' · ' + x.dataset.replace('-5m', ''), value: x.oos_return_pct, extra: [[t('verdict'), x.verdict]] })), { fmt: (v) => fmtPct(v), valueLabel: t('oos_return') }) }),
      panel(t('s_leaderboard'), {
        badges: [badge('HISTORICAL')], flush: true, note: t('sort_hint'),
        tools: [select([['', t('all')]].concat(dsets.map((x) => [x, x])), '', (v) => { fD = v; draw(); }, { 'aria-label': t('dataset') }),
          select([['', t('all')], ['VALIDATED', 'VALIDATED'], ['REJECTED', 'REJECTED']], '', (v) => { fV = v; draw(); }, { 'aria-label': t('verdict') })],
        body: host,
      }));
  }

  // 18 — API management
  async function scrApis() {
    const r = await tryApi('/api/api-status');
    if (!r.ok) return errorState(r.error, route);
    const d = r.data; const sc = d.secrets_configured || {};
    const conn = (x) => (!x ? el('span', { class: 'muted' }, '—') : x.ok ? el('span', null, verdictBadge('OK'), ' ', el('span', { class: 'muted num' }, isNum(x.latency_ms) ? fmtN(x.latency_ms, 0) + ' ms' : '')) : el('span', null, badge('BLOCKED'), ' ', el('span', { class: 'muted mono' }, x.error || '')));
    return el('div', { class: 'stack' },
      callout('warn', 'key', [el('b', null, t('keys_note_t')), el('div', null, t('keys_note'))]),
      el('div', { class: 'grid grid-2' },
        panel(t('secrets'), { body: kv(Object.keys(sc).map((k) => [el('span', { class: 'mono' }, k), sc[k] ? verdictBadge('CONFIGURED') : el('span', { class: 'badge b-neutral' }, 'NOT CONFIGURED')])) }),
        panel(t('connectivity'), { body: kv([
          [t('public_data') + ' (Binance)', conn(d.public_data)],
          [t('testnet') + ' (Binance Spot)', conn(d.testnet)],
          d.testnet && d.testnet.ok ? [t('credentials'), d.testnet.credentials ? t('configured') : t('not_configured')] : null,
          [t('live_trading'), el('span', { class: 'badge b-rejected' }, 'DISABLED')]]) })));
  }

  // 19 — Security
  async function scrSecurity() {
    const [sR, scR] = await Promise.all([tryApi('/api/security'), tryApi('/api/security-scan')]);
    if (!sR.ok) return errorState(sR.error, route);
    const s = sR.data; const sc = s.secrets_configured || {};
    const scan = scR.ok ? scR.data : s.scan;
    return el('div', { class: 'stack' },
      kpiGrid([
        kpi(t('audit_chain'), s.audit_chain_valid ? t('chain_valid') : t('chain_broken'), { small: true, accent: s.audit_chain_valid ? 'k-gain' : 'k-loss', cls: s.audit_chain_valid ? 'gain' : 'loss' }),
        kpi(t('audit_entries'), fmtInt(s.audit_entries)),
        kpi(t('live_trading'), s.live_trading_enabled ? t('enabled') : t('disabled'), { small: true, accent: s.live_trading_enabled ? 'k-loss' : 'k-gain' }),
        kpi(t('withdrawal'), String(s.withdrawal_capability || '—'), { small: true }),
      ]),
      el('div', { class: 'grid grid-2' },
        panel(t('auth'), { body: el('div', { class: 'wrap-any text-2' }, s.auth || '—') }),
        panel(t('secrets'), { body: kv(Object.keys(sc).map((k) => [el('span', { class: 'mono' }, k), sc[k] ? verdictBadge('CONFIGURED') : el('span', { class: 'badge b-neutral' }, 'NOT CONFIGURED')])) })),
      panel(t('security_scan'), { body: isNotRun(scan) ? notRunState('reports/security_scan.json', t('scan_not_run')) : jsonTree(scan) }));
  }

  // 20 — System health
  async function scrSystem() {
    const [sR, tR] = await Promise.all([tryApi('/api/system'), tryApi('/api/tests')]);
    if (!sR.ok) return errorState(sR.error, route);
    const s = sR.data; const res = s.resources || {};
    const meter = (used, total) => { const p = isNum(used) && isNum(total) && total > 0 ? 100 * used / total : null; return el('div', { class: 'meter' + (p > 85 ? ' hot' : ''), style: 'margin-top:8px' }, el('i', { style: 'width:' + (p == null ? 0 : p.toFixed(1)) + '%' })); };
    const memUsed = isNum(res.mem_total_gb) && isNum(res.mem_free_gb) ? res.mem_total_gb - res.mem_free_gb : null;
    const diskK = kpi(t('disk'), fmtN(res.disk_used_gb, 1) + ' / ' + fmtN(res.disk_total_gb, 0) + ' GB', { small: true }); diskK.append(meter(res.disk_used_gb, res.disk_total_gb));
    const memK = kpi(t('memory'), fmtN(memUsed, 1) + ' / ' + fmtN(res.mem_total_gb, 1) + ' GB', { small: true }); memK.append(meter(memUsed, res.mem_total_gb));
    const la = res.load_avg || [];
    const loadK = kpi(t('load'), la.length ? la.map((v) => fmtN(v, 2)).join(' · ') : '—', { small: true, foot: fmtInt(res.cpu_count) + ' ' + t('cores') });
    if (la.length && isNum(res.cpu_count)) loadK.append(meter(la[0], res.cpu_count));
    return el('div', { class: 'stack' },
      kpiGrid([
        kpi(t('uptime'), fmtDur(s.uptime_s), { small: true }), kpi(t('requests'), fmtInt(s.requests)), kpi(t('python'), s.python || '—', { small: true }),
        kpi(t('paper_thread'), s.paper_thread_alive ? t('alive') : t('stopped'), { small: true, accent: s.paper_thread_alive ? 'k-gain' : 'k-warn' }),
      ]),
      s.inactive_reason ? callout('warn', 'info', [el('b', null, t('paper_inactive') + ' — '), el('span', { class: 'mono wrap-any' }, s.inactive_reason)]) : null,
      panel(t('resources'), { body: kpiGrid([diskK, memK, loadK, kpi(t('db_size'), fmtN(res.db_size_mb, 2) + ' MB', { small: true }), kpi(t('reports_size'), fmtN(res.reports_size_mb, 2) + ' MB', { small: true })]) }),
      panel(t('tests'), { body: !tR.ok ? errorState(tR.error) : isNotRun(tR.data) ? notRunState('reports/test_results.json', t('tests_not_run')) : jsonTree(tR.data) }));
  }

  // 21 — Costs
  async function scrCosts() {
    const r = await tryApi('/api/costs');
    if (!r.ok) return errorState(r.error, route);
    const d = r.data; const a = d.assumptions_usd_month || {}; const lg = d.ledger || {};
    const names = { vps_monthly_usd: t('cost_vps'), claude_api_monthly_budget_usd: t('cost_claude'), gpu_monthly_usd: t('cost_gpu'), data_feeds_monthly_usd: t('cost_data') };
    const lrows = Object.keys(lg).map((k) => ({ category: k, usd: lg[k].usd, units: lg[k].units }));
    return el('div', { class: 'stack' },
      kpiGrid([kpi(t('projected'), fmtUsd(d.projected_monthly_usd), { accent: 'accent' }), kpi(t('measured'), fmtUsd(d.measured_usd))]),
      d.note ? callout('ok', 'coin', d.note) : null,
      el('div', { class: 'grid grid-2' },
        panel(t('assumptions'), { body: kv(Object.keys(a).map((k) => [names[k] || k, fmtUsd(a[k])])) }),
        panel(t('ledger'), { flush: true, body: lrows.length ? table([{ key: 'category', label: t('category') }, { key: 'usd', label: t('amount'), num: true, fmt: (v) => fmtUsd(v, 4) }, { key: 'units', label: t('units'), num: true, fmt: (v) => fmtN(v, 2) }], lrows) : empty(t('ledger_empty')) })));
  }

  // 22 — Audit
  async function scrAudit() {
    const [aR, sR] = await Promise.all([tryApi('/api/audit?limit=500'), tryApi('/api/security')]);
    if (!aR.ok) return errorState(aR.error, route);
    const rows = aR.data.entries || [];
    const chain = sR.ok ? sR.data.audit_chain_valid : null;
    return el('div', { class: 'stack' },
      kpiGrid([
        kpi(t('audit_chain'), chain == null ? '—' : chain ? t('chain_valid') : t('chain_broken'), { small: true, accent: chain ? 'k-gain' : 'k-loss', cls: chain ? 'gain' : chain === false ? 'loss' : '' }),
        kpi(t('audit_entries'), sR.ok ? fmtInt(sR.data.audit_entries) : '—'),
      ]),
      panel(t('s_audit'), { flush: true, body: table([
        { key: 'id', label: '#', num: true }, { key: 'ts', label: t('time'), fmt: (v) => el('span', { class: 'num' }, fmtEpoch(v)) },
        { key: 'actor', label: t('actor'), fmt: (v) => el('span', { class: 'badge b-neutral' }, v) }, { key: 'action', label: t('action'), fmt: (v) => el('b', { class: 'mono' }, v) },
        { key: 'detail', label: t('detail'), cls: 'trunc', fmt: (v) => el('span', { class: 'mono muted', title: v || '' }, v || '') },
        { key: 'hash', label: t('hash'), fmt: (v) => el('span', { class: 'mono muted', title: v || '' }, String(v || '').slice(0, 12) + '…') },
      ], rows, { tall: true, sortKey: 'id', emptyText: t('no_audit') }) }));
  }

  // 23 — Settings
  async function scrSettings() {
    const r = await tryApi('/api/settings');
    if (!r.ok) return errorState(r.error, route);
    const s = r.data.settings || {};
    const lang = select([['bn', t('lang_bn')], ['en', t('lang_en')]], s.language || LANG, null, { id: 'f-lang' });
    const dsSel = select(r.data.datasets || [], s.replay_dataset, null, { id: 'f-ds' });
    const speed = el('input', { class: 'input num', id: 'f-speed', type: 'number', min: '0.05', max: '10', step: '0.05', value: s.replay_speed_s != null ? String(s.replay_speed_s) : '1' });
    const shadow = select([['', t('none')]].concat((r.data.strategies || []).map((x) => [x, x])), s.shadow_strategy || '', null, { id: 'f-shadow' });
    const tg = el('input', { class: 'input num', id: 'f-tg', inputmode: 'numeric', autocomplete: 'off', placeholder: t('telegram_ph'), value: s.telegram_owner_id != null ? String(s.telegram_owner_id) : '' });
    const warn = el('div');
    const showWarn = () => warn.replaceChildren(shadow.value ? callout('warn', 'alert', [badge('SHADOW'), ' ', t('shadow_warn')]) : null);
    shadow.addEventListener('change', showWarn); showWarn();
    const msg = el('div', { class: 'form-error', role: 'status' });
    const saveBtn = el('button', { class: 'btn btn-primary', type: 'submit' }, icon('check'), t('save'));
    const field = (id, label, input, hint) => el('div', { class: 'field' }, el('label', { for: id }, label), input, hint ? el('div', { class: 'kpi-foot' }, hint) : null);
    const form = el('form', { novalidate: true },
      el('div', { class: 'grid grid-2' },
        field('f-lang', t('language'), lang), field('f-ds', t('replay_dataset'), dsSel),
        field('f-speed', t('replay_speed'), speed, t('speed_range')), field('f-shadow', t('shadow_strategy'), shadow),
        field('f-tg', t('telegram_id'), tg), field('f-feed', t('feed'), el('input', { class: 'input', id: 'f-feed', value: String(s.feed || 'replay').toUpperCase(), disabled: true }))),
      warn, msg, el('div', { style: 'display:flex;gap:8px;flex-wrap:wrap' }, saveBtn));
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const tgv = tg.value.trim();
      if (tgv && !/^\d{1,15}$/.test(tgv)) { msg.textContent = t('telegram_id') + ': 0-9'; return; }
      const sp = parseFloat(speed.value);
      if (!isFinite(sp)) { msg.textContent = t('replay_speed') + ': ' + t('speed_range'); return; }
      saveBtn.disabled = true; msg.textContent = '';
      try {
        const res = await api('/api/settings', { method: 'POST', body: { language: lang.value, replay_dataset: dsSel.value, replay_speed_s: sp, shadow_strategy: shadow.value || null, telegram_owner_id: tgv || null } });
        toast(t('saved'), 'ok');
        const nl = res.settings && res.settings.language;
        if (nl && nl !== LANG) { applyLang(nl, false); return; }
        speed.value = String(res.settings.replay_speed_s);
      } catch (err) { msg.textContent = t('save_failed') + ': ' + err.message; }
      saveBtn.disabled = false;
    });
    return el('div', { class: 'stack' }, panel(t('s_settings'), { body: form, note: t('settings_note') }));
  }

  // ------------------------------------------------------------------ shell, routing, auth
  const root = document.getElementById('root');
  let NAV = 0, contentEl = null, navEl = null, crumbEl = null;

  function setBannerVar() {
    const b = document.getElementById('sim-banner');
    if (b) document.documentElement.style.setProperty('--banner-h', b.offsetHeight + 'px');
  }
  window.addEventListener('resize', setBannerVar);

  function applyLang(l, persistServer) {
    LANG = l === 'en' ? 'en' : 'bn';
    document.documentElement.lang = LANG;
    document.body.classList.toggle('lang-bn', LANG === 'bn');
    store.set('atm.lang', LANG);
    if (persistServer && TOKEN) api('/api/settings', { method: 'POST', body: { language: LANG } }).catch(() => { /* local choice still applies */ });
    if (TOKEN) renderShell(); else renderLogin();
  }
  function langToggle() {
    return seg([['bn', 'বাংলা'], ['en', 'EN']], LANG, (v) => applyLang(v, true));
  }

  function renderLogin(msg) {
    wsStop();
    document.title = t('app_name') + ' — ' + t('login_title');
    const inp = el('input', { class: 'input mono', id: 'token', type: 'password', autocomplete: 'current-password', placeholder: t('token_ph'), required: true, spellcheck: 'false' });
    const err = el('div', { class: 'form-error', role: 'alert' }, msg || '');
    const btn = el('button', { class: 'btn btn-primary btn-block', type: 'submit' }, t('login_btn'));
    const form = el('form', { autocomplete: 'off' }, el('div', { class: 'field' }, el('label', { for: 'token' }, t('token')), inp), err, btn);
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const tok = inp.value.trim(); if (!tok) return;
      btn.disabled = true; btn.textContent = t('logging_in'); err.textContent = '';
      try {
        const r = await fetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token: tok }), cache: 'no-store' });
        if (r.ok) {
          TOKEN = tok; store.set('atm.token', tok, true);
          if (store.get('atm.lang') == null) {
            try { const s = await api('/api/settings'); if (s && s.settings && (s.settings.language === 'en' || s.settings.language === 'bn')) LANG = s.settings.language; } catch (x) { /* keep */ }
          }
          applyLang(LANG, false);
          return;
        }
        err.textContent = r.status === 429 ? t('err_rate') : t('err_token');
      } catch (x) { err.textContent = t('err_network'); }
      btn.disabled = false; btn.textContent = t('login_btn');
    });
    root.replaceChildren(el('div', { class: 'login-wrap' }, el('div', { class: 'login-card' },
      el('div', { class: 'brand' }, el('div', { class: 'brand-mark' }, icon('logo')), el('div', null, el('div', { class: 'brand-name' }, t('app_name')), el('div', { class: 'brand-sub' }, t('app_sub')))),
      el('h1', null, t('login_title')), el('p', null, t('login_desc')), form,
      el('div', { class: 'login-foot' }, el('span', null, badge('VIRTUAL'), ' ', t('login_note')), langToggle()))));
    setTimeout(() => inp.focus(), 30);
  }

  function logout(expired) {
    const had = !!TOKEN;
    TOKEN = null; store.del('atm.token', true); PAPER = null;
    CLEANUP.forEach((f) => { try { f(); } catch (e) { /* ignore */ } }); CLEANUP = [];
    wsStop();
    if (had || !expired) renderLogin(expired ? t('session_expired') : '');
  }

  function renderShell() {
    document.body.classList.remove('drawer-open');
    navEl = el('nav', { class: 'sidebar', id: 'sidebar', 'aria-label': t('menu') });
    navEl.append(el('div', { class: 'brand' }, el('div', { class: 'brand-mark' }, icon('logo')), el('div', null, el('div', { class: 'brand-name' }, t('app_name')), el('div', { class: 'brand-sub' }, 'SIMULATION · v1'))));
    GROUPS.forEach((g) => {
      const items = SCREENS.filter((s) => s.g === g);
      const grp = el('div', { class: 'nav-group' }, el('div', { class: 'nav-group-title' }, t(g)));
      items.forEach((s) => grp.append(el('a', { class: 'nav-item', href: '#' + s.id, 'data-id': s.id }, icon(s.ic), el('span', null, t('s_' + s.id)))));
      navEl.append(grp);
    });
    navEl.addEventListener('click', (e) => { if (e.target.closest('a')) document.body.classList.remove('drawer-open'); });
    const menuBtn = el('button', { class: 'btn btn-ghost menu-btn', type: 'button', 'aria-label': t('menu'), 'aria-controls': 'sidebar' }, icon('menu'));
    menuBtn.addEventListener('click', () => document.body.classList.toggle('drawer-open'));
    crumbEl = el('div', { class: 'crumb' });
    const pill = el('span', { class: 'ws-pill ' + wsState, id: 'ws-pill', title: '/ws' }, el('i'), el('span', { class: 'hide-sm' }, ''));
    const top = el('header', { class: 'topbar' }, menuBtn, crumbEl, el('div', { class: 'spacer' }), pill, langToggle(),
      el('button', { class: 'btn btn-ghost', type: 'button', title: t('logout'), 'aria-label': t('logout'), onclick: () => logout(false) }, icon('logout'), el('span', { class: 'hide-sm' }, t('logout'))));
    contentEl = el('main', { class: 'content', id: 'content' });
    const scrim = el('div', { class: 'scrim', onclick: () => document.body.classList.remove('drawer-open') });
    root.replaceChildren(el('div', { class: 'shell' }, navEl, el('div', { class: 'main' }, top, contentEl)), scrim);
    setBannerVar();
    setWsState(wsState === 'off' ? 'retry' : wsState);
    if (!ws) wsConnect();
    route();
  }

  async function route() {
    if (!TOKEN || !contentEl) return;
    const id = (location.hash || '#overview').slice(1);
    const scr = SCREENS.find((s) => s.id === id) || SCREENS[0];
    const my = ++NAV;
    CLEANUP.forEach((f) => { try { f(); } catch (e) { /* ignore */ } }); CLEANUP = [];
    navEl.querySelectorAll('.nav-item').forEach((a) => { const on = a.getAttribute('data-id') === scr.id; a.classList.toggle('active', on); if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    crumbEl.replaceChildren(el('span', { class: 'hide-sm' }, t(scr.g) + ' / '), el('b', null, t('s_' + scr.id)));
    document.title = t('s_' + scr.id) + ' · ' + t('app_name');
    const body = el('div', null, el('div', { class: 'skeleton' }, el('div', { class: 'grid grid-kpi' }, el('div', { class: 'sk' }), el('div', { class: 'sk' }), el('div', { class: 'sk' }), el('div', { class: 'sk' })), el('div', { class: 'sk tall' })));
    const refresh = el('button', { class: 'btn btn-sm', type: 'button', onclick: route }, icon('refresh'), t('refresh'));
    const head = el('div', { class: 'page-head' },
      el('div', null, el('h1', null, t('s_' + scr.id)), el('div', { class: 'sub' }, t('d_' + scr.id)), scr.b ? el('div', { class: 'badges' }, scr.b.map((b) => badge(b))) : null),
      el('div', { class: 'page-actions' }, refresh));
    const wrap = el('div', { class: 'view-enter' }, head, body);
    contentEl.replaceChildren(wrap);
    window.scrollTo(0, 0);
    try {
      const node = await scr.r();
      if (my !== NAV) return;
      body.replaceChildren(node);
    } catch (e) {
      if (my !== NAV || (e && e.status === 401)) return;
      console.warn(e);
      body.replaceChildren(errorState(e, route));
    }
  }
  window.addEventListener('hashchange', () => { if (TOKEN) route(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') document.body.classList.remove('drawer-open'); });

  // ------------------------------------------------------------------ boot
  function boot() {
    const l = store.get('atm.lang');
    LANG = l === 'en' ? 'en' : 'bn';
    document.documentElement.lang = LANG;
    document.body.classList.toggle('lang-bn', LANG === 'bn');
    setBannerVar();
    const tok = store.get('atm.token', true);
    if (tok) { TOKEN = tok; renderShell(); } else renderLogin();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
