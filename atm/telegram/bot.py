"""Owner-only Telegram control center (long polling, Bengali replies).

* Only messages from the approved numeric user ID (TELEGRAM_OWNER_ID) are processed; all
  others are ignored and audited.
* The bot reads state from the control-center API using the owner token held server-side.
* It never sends secrets; every outgoing message passes through redact().
* /stop triggers the emergency stop. Resuming requires the dashboard (typed confirmation).
"""
from __future__ import annotations

import logging
import os
import time

import requests

from ..security.secrets import get_secret, redact

log = logging.getLogger("atm.telegram")
API = "https://api.telegram.org"

HELP_BN = (
    "🤖 AI Trading Master — কমান্ড তালিকা\n"
    "/status — সিস্টেমের অবস্থা\n/balance — ভার্চুয়াল ব্যালেন্স\n/trades — বর্তমান সিমুলেটেড ট্রেড\n"
    "/pnl — নিট লাভ/ক্ষতি\n/research — গবেষণার অগ্রগতি\n/risk — ঝুঁকি সতর্কতা\n/challenge — ৪ ঘণ্টার চ্যালেঞ্জ রিপোর্ট\n"
    "/strategies — স্ট্র্যাটেজি পারফরম্যান্স\n/health — সার্ভার হেলথ\n/stop — জরুরি স্টপ (সব ট্রেড বন্ধ)\n/explain — সহজ বাংলায় ব্যাখ্যা\n"
    "⚠️ সব ব্যালেন্স ভার্চুয়াল (সিমুলেশন)। কোনো আসল টাকা নেই।"
)


class ControlAPI:
    def __init__(self, base: str, token: str, session=None):
        self.base, self.token = base.rstrip("/"), token
        self.s = session or requests.Session()

    def get(self, path):
        r = self.s.get(self.base + path, headers={"Authorization": f"Bearer {self.token}"}, timeout=10)
        r.raise_for_status()
        return r.json()

    def post(self, path, body=None):
        r = self.s.post(self.base + path, json=body or {}, headers={"Authorization": f"Bearer {self.token}"}, timeout=10)
        r.raise_for_status()
        return r.json()


def _f(x, nd=2):
    try:
        return f"{float(x):,.{nd}f}"
    except (TypeError, ValueError):
        return "—"


def handle(cmd: str, api: ControlAPI) -> str:
    cmd = cmd.strip().split()[0].split("@")[0].lower() if cmd.strip() else ""
    if cmd in ("/start", "/help"):
        return HELP_BN
    if cmd == "/status":
        o = api.get("/api/overview")
        p = o.get("paper") or {}
        return (f"📊 মোড: {o['mode']} (লাইভ ট্রেডিং বন্ধ)\nপেপার ফিড: {o['data_sources']['paper_feed']}\n"
                f"টেস্টনেট: {o['data_sources']['testnet']}\nস্ট্র্যাটেজি: {p.get('strategy', '—')}\n"
                f"নিষ্ক্রিয় কারণ: {o.get('inactive_reason') or '—'}")
    if cmd == "/balance":
        p = api.get("/api/portfolio")
        return f"💰 ভার্চুয়াল ইকুইটি: ${_f(p.get('equity_usd'))} (শুরু ${_f(p.get('initial_usd', 100))})\nনগদ: ${_f(p.get('cash_usd'))}\n[সিমুলেটেড]"
    if cmd == "/trades":
        p = api.get("/api/portfolio")
        if p.get("position_qty"):
            return f"📈 খোলা পজিশন: {p['symbol']} qty {p['position_qty']:.6f} @ {_f(p['entry_px'], 4)}, স্টপ {_f(p['stop_px'], 4)}\n[সিমুলেটেড]"
        return "কোনো খোলা সিমুলেটেড পজিশন নেই।"
    if cmd == "/pnl":
        p = api.get("/api/portfolio")
        return f"🧾 নিট লাভ/ক্ষতি: ${_f(p.get('net_pnl_usd'))} | ফি: ${_f(p.get('fees_usd'))} | বন্ধ ট্রেড: {p.get('closed_trades', 0)} (জয় {p.get('wins', 0)})\n[সিমুলেটেড]"
    if cmd == "/research":
        s = api.get("/api/summary")
        if s.get("status") == "NOT_RUN":
            return "গবেষণা এখনো চালানো হয়নি।"
        return (f"🔬 ওয়াক-ফরোয়ার্ড টেস্ট: {s.get('walk_forward_runs')} | মোট ট্রায়াল: {s.get('total_backtest_trials')}\n"
                f"যাচাইকৃত (VALIDATED) স্ট্র্যাটেজি: {len(s.get('validated', []))}\nML প্রার্থী: {len(s.get('ml_candidates', []))}\n"
                f"ট্রেড করা উচিত? {'হ্যাঁ' if s.get('system_should_trade') else 'না — কোনো স্ট্র্যাটেজি সব পরীক্ষায় পাস করেনি'}")
    if cmd == "/risk":
        r = api.get("/api/risk")
        stt = r.get("state") or {}
        ev = (r.get("events") or [])[-3:]
        return (f"🛡️ কিল-সুইচ: {'চালু' if r['kill_file'] else 'বন্ধ'}\nহল্ট: {stt.get('halted_reason') or '—'}\nকিল: {stt.get('killed_reason') or '—'}\n"
                f"প্রতি ট্রেড সর্বোচ্চ ঝুঁকি: {r['limits']['max_risk_per_trade_pct']}% | সেশন লস সীমা: {r['limits']['max_session_loss_pct']}%\n"
                f"সাম্প্রতিক ইভেন্ট: {ev or '—'}")
    if cmd == "/challenge":
        c = api.get("/api/challenge")
        if c.get("status") == "NOT_RUN":
            return "চ্যালেঞ্জ এখনো চালানো হয়নি।"
        b = c["summary"][c["best_by_mean"]]
        o = c["oracle"]
        return (f"🎯 $100→$200 (৪ ঘণ্টা) চ্যালেঞ্জ\nসেশন: {b['sessions']} | লক্ষ্য অর্জন: {b['target_hits']} বার ({_f(b['target_hit_rate_pct'])}%)\n"
                f"সেরা স্ট্র্যাটেজি (গড়): {c['best_by_mean']} | মিডিয়ান রিটার্ন {_f(b['median_return_pct'], 3)}% | ক্ষতির সম্ভাবনা {_f(b['prob_loss_pct'])}%\n"
                f"নিখুঁত-ভবিষ্যৎজ্ঞান সীমা: মিডিয়ান {_f(o['oracle_median_pct'])}%, সর্বোচ্চ {_f(o['oracle_max_pct'])}% — লক্ষ্য {_f(o['oracle_target_hit_rate_pct'])}% সেশনে সম্ভব ছিল")
    if cmd == "/strategies":
        s = api.get("/api/strategies")["leaderboard"][:5]
        lines = [f"{i+1}. {x['strategy']} ({x['dataset']}): OOS {_f(x['oos_return_pct'], 3)}% · {x['verdict']}" for i, x in enumerate(s)]
        return "🏆 শীর্ষ ৫ (আউট-অব-স্যাম্পল):\n" + "\n".join(lines)
    if cmd == "/health":
        s = api.get("/api/system")
        r = s["resources"]
        return f"🖥️ আপটাইম {int(s['uptime_s'])}s | CPU {r.get('cpu_count')} | ফ্রি মেমরি {_f(r.get('mem_free_gb'))} GB | DB {_f(r.get('db_size_mb'))} MB"
    if cmd == "/stop":
        api.post("/api/emergency-stop")
        return "🛑 জরুরি স্টপ সক্রিয় হয়েছে। সব সিমুলেটেড পজিশন বন্ধ করা হচ্ছে। আবার চালু করতে ড্যাশবোর্ডে RESUME লিখে নিশ্চিত করুন।"
    if cmd == "/explain":
        return ("ℹ️ সহজ ব্যাখ্যা: সিস্টেমটি ঐতিহাসিক আসল বাজারের ডেটায় অনেক স্ট্র্যাটেজি পরীক্ষা করে। কোনো স্ট্র্যাটেজি ফি ও খরচ বাদ দিয়ে "
                "নতুন (আগে না-দেখা) ডেটায় লাভজনক প্রমাণিত না হলে সিস্টেম ট্রেড করে না। ৪ ঘণ্টায় টাকা দ্বিগুণ করা স্পট ট্রেডিংয়ে "
                "বাস্তবসম্মত নয় — রিপোর্টে প্রমাণ দেখুন (/challenge)।")
    return "অজানা কমান্ড। /help লিখুন।"


class TelegramBot:
    def __init__(self, token: str, owner_id: int, api: ControlAPI, session=None, store=None):
        self.token, self.owner_id, self.api = token, int(owner_id), api
        self.s = session or requests.Session()
        self.offset = 0
        self.store = store

    def _call(self, method, **params):
        r = self.s.post(f"{API}/bot{self.token}/{method}", json=params, timeout=40)
        r.raise_for_status()
        return r.json()

    def send(self, chat_id: int, text: str):
        return self._call("sendMessage", chat_id=chat_id, text=redact(text)[:4000])

    def process(self, update: dict) -> str | None:
        msg = update.get("message") or {}
        uid = (msg.get("from") or {}).get("id")
        text = msg.get("text") or ""
        if uid != self.owner_id:
            if self.store:
                self.store.audit("telegram", "unauthorized_message", {"user_id": uid})
            return None  # silently ignore non-owners
        try:
            reply = handle(text, self.api)
        except Exception as e:  # noqa: BLE001
            reply = f"ত্রুটি: সার্ভার থেকে তথ্য আনা যায়নি ({e.__class__.__name__})"
        if self.store and text.strip().startswith("/stop"):
            self.store.audit("owner", "telegram_emergency_stop", {})
        self.send(msg["chat"]["id"], reply)
        return reply

    def alert(self, text: str):
        self.send(self.owner_id, "⚠️ " + text)

    def poll_forever(self):
        while True:
            try:
                res = self._call("getUpdates", offset=self.offset, timeout=30)
                for u in res.get("result", []):
                    self.offset = u["update_id"] + 1
                    self.process(u)
            except Exception as e:  # noqa: BLE001
                log.warning("telegram poll error: %s", redact(str(e)))
                time.sleep(5)


def main():
    tok = get_secret("TELEGRAM_BOT_TOKEN")
    owner = os.environ.get("TELEGRAM_OWNER_ID")
    if not tok or not owner or not owner.isdigit():
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and numeric TELEGRAM_OWNER_ID in the server environment.")
    api = ControlAPI(os.environ.get("ATM_API_URL", "http://127.0.0.1:8000"), get_secret("ATM_OWNER_TOKEN") or "")
    TelegramBot(tok, int(owner), api).poll_forever()


if __name__ == "__main__":
    main()
