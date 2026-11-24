"""Owner-only control-center API + dashboard host.

Auth: a single owner bearer token (env ATM_OWNER_TOKEN; if unset a random token is
generated and written to data/owner_token with 0600 permissions — never logged).
Every state-changing call is written to the hash-chained audit log.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import platform
import threading
import time
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from .. import cost
from ..backtest.execution import market_for
from ..data.loader import DATASETS, load_ohlcv, quality_check, resample
from ..data.stream import ReplayFeed
from ..exchange.binance import PublicMarketData, SpotTestnetClient, ExchangeError
from ..exchange.paper import PaperTrader
from ..features import indicators as ind
from ..features.regime import classify
from ..risk.limits import RiskLimits
from ..security.secrets import configured, install_log_redaction, new_token, token_matches
from ..storage.db import Store
from ..strategies.library import STRATEGIES

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"
DASH = ROOT / "dashboard"
DATA = ROOT / "data"
SETTINGS_PATH = DATA / "settings.json"
KILL_FILE = DATA / "KILL"
log = logging.getLogger("atm.api")
install_log_redaction()

DEFAULT_SETTINGS = {"language": "bn", "feed": "replay", "replay_dataset": "BTC_USDT-5m", "replay_speed_s": 1.0,
                    "shadow_strategy": None, "telegram_owner_id": None}


def _owner_token() -> str:
    t = os.environ.get("ATM_OWNER_TOKEN")
    if t:
        if len(t) < 16:
            log.warning("ATM_OWNER_TOKEN is shorter than 16 characters; use secrets.token_urlsafe(32) in production")
        return t
    p = DATA / "owner_token"
    DATA.mkdir(exist_ok=True)
    if not p.exists():
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)  # created 0600, never world-readable
        with os.fdopen(fd, "w") as fh:
            fh.write(new_token())
    return p.read_text().strip()


def _json(name: str, default=None):
    p = REPORTS / name
    if not p.exists():
        return default
    return json.loads(p.read_text())


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    return o


class State:
    def __init__(self, store: Store | None = None):
        self.store = store or Store()
        self.limits = RiskLimits.load()
        self.settings = {**DEFAULT_SETTINGS, **(json.loads(SETTINGS_PATH.read_text()) if SETTINGS_PATH.exists() else {})}
        self.trader: PaperTrader | None = None
        self.thread: threading.Thread | None = None
        self.started = time.time()
        self.login_attempts: dict[str, deque] = defaultdict(lambda: deque(maxlen=20))
        self.request_count = 0
        self.inactive_reason = ""

    def save_settings(self):
        DATA.mkdir(exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(self.settings, indent=1))

    def eligible_strategy(self, dataset: str):
        """Only strategies that passed every validation gate on this dataset may trade."""
        # only the LATEST registry version of each (strategy, dataset) counts: a later rejection revokes eligibility
        latest = {}
        for r in self.store.strategies():
            k = (r["name"], r["dataset"])
            if k not in latest or r["version"] > latest[k]["version"]:
                latest[k] = r
        rows = [r for r in latest.values() if r["status"] == "VALIDATED" and r["dataset"] == dataset and r["name"] in STRATEGIES]
        if rows:
            r = max(rows, key=lambda x: x["metrics"].get("oos_return_pct", 0))
            return STRATEGIES[r["name"]], r["params"], "VALIDATED"
        sh = self.settings.get("shadow_strategy")
        if sh in STRATEGIES:
            return STRATEGIES[sh], dict(STRATEGIES[sh].defaults), "EXPERIMENTAL_SHADOW"
        return None, None, None

    def start_trader(self):
        if self.thread and self.thread.is_alive():
            return
        if KILL_FILE.exists():
            self.inactive_reason = "emergency stop active (data/KILL present)"
            return
        ds = self.settings["replay_dataset"]
        spec, params, status = self.eligible_strategy(ds)
        if spec is None:
            self.inactive_reason = "no strategy has passed independent validation; the system stays flat (by design)"
            return
        df = load_ohlcv(ds)
        meta = DATASETS[ds]
        m = market_for(meta["symbol"], meta["quote"], float(df.close.iloc[-1]))
        from ..research.cycle import FORWARD_FRAC
        split = int(len(df) * (1 - FORWARD_FRAC))  # replay only the forward segment research never saw
        self.trader = PaperTrader(spec, params, m, self.limits, 100.0, history=df.iloc[split - 600:split], store=self.store)
        self.trader.strategy_status = status
        self.inactive_reason = ""
        feed = ReplayFeed(df, start=split, speed_s=float(self.settings["replay_speed_s"]))

        def run():
            for bar in feed:
                if not self.trader.running and not self.trader.pending:
                    break
                self.trader.on_bar(bar)
        self.thread = threading.Thread(target=run, daemon=True, name="paper-trader")
        self.thread.start()
        self.store.audit("system", "paper_session_start", {"dataset": ds, "strategy": spec.name, "status": status, "feed": "REPLAY"})


def create_app(state: State | None = None, start_background: bool = True) -> FastAPI:
    st = state or State()
    token = _owner_token()
    app = FastAPI(title="AI Trading Master — Control Center", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.st = st

    @app.middleware("http")
    async def headers(request: Request, call_next):
        st.request_count += 1
        resp = await call_next(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Content-Security-Policy"] = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                                                   "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self' ws: wss:; frame-ancestors 'none'")
        resp.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api") else "no-cache"
        return resp

    def auth(request: Request):
        h = request.headers.get("authorization", "")
        cand = h[7:] if h.lower().startswith("bearer ") else None
        if not token_matches(cand, token):
            raise HTTPException(401, "unauthorized")
        return True

    # ---------------- public ----------------
    @app.get("/api/health")
    def health():
        return {"status": "ok", "mode": "SIMULATION", "live_trading": False}

    @app.post("/api/login")
    async def login(request: Request):
        ip = request.client.host if request.client else "?"
        q = st.login_attempts[ip]
        now = time.time()
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= 5:
            raise HTTPException(429, "too many attempts; wait a minute")
        q.append(now)
        try:
            body = await request.json()
        except Exception:  # noqa: BLE001
            raise HTTPException(400, "invalid JSON") from None
        if not isinstance(body, dict):
            raise HTTPException(400, "invalid body")
        ok = token_matches(str(body.get("token", ""))[:200], token)
        st.store.audit("owner" if ok else "anonymous", "login_ok" if ok else "login_failed", {"ip": ip})
        if not ok:
            raise HTTPException(401, "invalid token")
        return {"ok": True}

    # ---------------- overview ----------------
    @app.get("/api/overview", dependencies=[Depends(auth)])
    def overview():
        s = _json("summary.json", {})
        ch = _json("challenge.json", {})
        snap = st.trader.snapshot() if st.trader else None
        return _clean({
            "mode": "SIMULATION", "live_trading_enabled": False,
            "data_sources": {"historical": "REAL — Binance OHLCV candles (Freqtrade test fixtures), see data/historical/MANIFEST.json",
                             "paper_feed": snap["data_source"] if snap else "INACTIVE",
                             "testnet": "BLOCKED — credentials / network" if not configured()["BINANCE_TESTNET_API_KEY"] else "CONFIGURED"},
            "research": s, "challenge_best": ch.get("best_by_mean"), "challenge_oracle": ch.get("oracle"),
            "paper": {k: snap[k] for k in ("equity_usd", "net_pnl_usd", "fees_usd", "running", "strategy", "data_source", "closed_trades", "wins")} if snap else None,
            "inactive_reason": st.inactive_reason, "risk": st.trader.risk.state() if st.trader else {"limits": st.limits.as_dict()},
        })

    @app.get("/api/portfolio", dependencies=[Depends(auth)])
    def portfolio():
        return _clean(st.trader.snapshot() if st.trader else {"inactive_reason": st.inactive_reason, "equity_usd": 100.0, "label": "VIRTUAL"})

    @app.get("/api/market", dependencies=[Depends(auth)])
    def market():
        out = []
        for name, meta in DATASETS.items():
            df = load_ohlcv(name)
            reg = classify(df).iloc[-1]
            c = df.close
            n4 = int(4 * 60 / max(1, (df.index[1] - df.index[0]).seconds // 60))
            out.append({"dataset": name, "symbol": meta["symbol"], "quote": meta["quote"], "era": meta["era"], "last": float(c.iloc[-1]),
                        "last_ts": str(df.index[-1]), "chg_4h_pct": float(100 * (c.iloc[-1] / c.iloc[-n4 - 1] - 1)),
                        "chg_total_pct": float(100 * (c.iloc[-1] / c.iloc[0] - 1)),
                        "atr_pct": float(100 * ind.atr(df).iloc[-1] / c.iloc[-1]), "rsi": float(ind.rsi(c).iloc[-1]),
                        "adx": float(ind.adx(df).iloc[-1]), "regime": reg, "quality_ok": quality_check(df).ok,
                        "source": "HISTORICAL (not live)"})
        corr = {}
        prim = [n for n in DATASETS if n.endswith("-5m")]
        rets = {n: np.log(load_ohlcv(n).close).diff() for n in prim}
        import pandas as pd
        rdf = pd.DataFrame(rets).dropna(how="all")
        for a in prim:
            corr[a] = {b: (None if not np.isfinite(v) else float(v)) for b, v in rdf.corr()[a].items()}
        return _clean({"markets": out, "correlation": corr})

    @app.get("/api/candles", dependencies=[Depends(auth)])
    def candles(dataset: str = "BTC_USDT-5m", interval: str = "5m", limit: int = 300):
        if dataset not in DATASETS:
            raise HTTPException(404, "unknown dataset")
        df = load_ohlcv(dataset)
        if interval != "5m" and interval in ("15m", "30m", "1h", "4h"):
            df = resample(df, interval)
        df = df.iloc[-min(max(limit, 10), 2000):]
        e20, e60 = ind.ema(df.close, 20), ind.ema(df.close, 60)
        bb = ind.bollinger(df.close)
        return _clean({"dataset": dataset, "interval": interval, "source": "HISTORICAL",
                       "t": [str(x) for x in df.index], "o": df.open.tolist(), "h": df.high.tolist(), "l": df.low.tolist(),
                       "c": df.close.tolist(), "v": df.volume.tolist(), "ema20": e20.tolist(), "ema60": e60.tolist(),
                       "bb_up": bb.upper.tolist(), "bb_lo": bb.lower.tolist(), "rsi": ind.rsi(df.close).tolist()})

    @app.get("/api/scanner", dependencies=[Depends(auth)])
    def scanner():
        rows = []
        for name in DATASETS:
            df = load_ohlcv(name)
            sig = {}
            for sname, spec in STRATEGIES.items():
                try:
                    s = spec.signals(df).iloc[-1]
                    sig[sname] = "ENTRY" if s.entry else ("EXIT" if s.exit else "—")
                except Exception:  # noqa: BLE001
                    sig[sname] = "n/a"
            rows.append({"dataset": name, "signals": sig, "regime": classify(df).iloc[-1], "as_of": str(df.index[-1])})
        return _clean({"rows": rows, "note": "Signals evaluated on the last stored historical bar; not live."})

    @app.get("/api/strategies", dependencies=[Depends(auth)])
    def strategies():
        reg = st.store.strategies()
        wf = _json("walk_forward.json", [])
        board = sorted(({"strategy": r["strategy"], "dataset": r["dataset"], "family": r["family"], "verdict": r["verdict"],
                         "oos_return_pct": r["oos_compound_return_pct"], "oos_trades": r["oos_trades"], "pf": r["oos_profit_factor"],
                         "holdout_return_pct": r["holdout"]["net_return_pct"], "stress_return_pct": r["stress"]["net_return_pct"],
                         "gates": r["gates"], "mc": r["monte_carlo"]} for r in wf), key=lambda x: -x["oos_return_pct"])
        return _clean({"leaderboard": board, "registry": reg[:300],
                       "library": [{"name": s.name, "family": s.family, "description": s.description, "defaults": s.defaults} for s in STRATEGIES.values()]})

    for route, fname in [("backtests", "walk_forward.json"), ("ml", "ml.json"), ("rl", "rl.json"), ("challenge", "challenge.json"),
                         ("timeframes", "timeframes.json"), ("data-quality", "data_quality.json"), ("summary", "summary.json"),
                         ("challenge-sessions", "challenge_sessions.json"), ("security-scan", "security_scan.json"), ("tests", "test_results.json")]:
        def _mk(f=fname):
            def h():
                return _clean(_json(f, {"status": "NOT_RUN"}))
            return h
        app.get(f"/api/{route}", dependencies=[Depends(auth)], name=route)(_mk())

    @app.get("/api/risk", dependencies=[Depends(auth)])
    def risk():
        return _clean({"limits": st.limits.as_dict(), "state": st.trader.risk.state() if st.trader else None,
                       "events": st.trader.risk.events[-100:] if st.trader else [], "kill_file": KILL_FILE.exists(),
                       "editable_via_api": False, "note": "Limits are owner-controlled in config/risk_limits.yaml and capped by code-level hard ceilings."})

    @app.get("/api/trades", dependencies=[Depends(auth)])
    def trades():
        return _clean({"paper_trades": st.store.paper_trades(), "label": "VIRTUAL (paper/replay) — not real trades"})

    @app.get("/api/learning", dependencies=[Depends(auth)])
    def learning():
        return _clean({"experiments": st.store.experiments(500)})

    @app.get("/api/reports", dependencies=[Depends(auth)])
    def reports():
        files = sorted(p.name for p in REPORTS.glob("*")) if REPORTS.exists() else []
        md = (REPORTS / "RESEARCH_REPORT.md").read_text() if (REPORTS / "RESEARCH_REPORT.md").exists() else ""
        return {"files": files, "research_report_md": md}

    @app.get("/api/agents", dependencies=[Depends(auth)])
    def agents():
        out = []
        for p in sorted((ROOT / ".claude" / "agents").glob("*.md")):
            txt = p.read_text().split("---")
            meta = {}
            if len(txt) >= 3:
                for line in txt[1].splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta[k.strip()] = v.strip()
            out.append({"file": p.name, "name": meta.get("name", p.stem), "description": meta.get("description", "")[:300],
                        "model": meta.get("model", "inherit"), "kind": "LLM subagent definition (on-demand, not always running)"})
        skills = [{"name": p.parent.name, "path": str(p.relative_to(ROOT))} for p in sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md"))]
        return {"agents": out, "skills": skills, "deterministic_services": ["risk engine", "backtester", "research cycle", "paper trader", "data quality"]}

    @app.get("/api/api-status", dependencies=[Depends(auth)])
    def api_status():
        out = {"secrets_configured": configured(), "public_data": None, "testnet": None}
        try:
            pm = PublicMarketData(timeout=4, retries=0)
            pm.ping()
            out["public_data"] = {"ok": True, "latency_ms": pm.health.latency_ms}
        except Exception as e:  # noqa: BLE001
            out["public_data"] = {"ok": False, "error": e.__class__.__name__}
        try:
            tc = SpotTestnetClient(timeout=4, retries=0)
            tc.sync_time()
            out["testnet"] = {"ok": True, "latency_ms": tc.health.latency_ms, "credentials": tc.has_credentials}
        except (ExchangeError, Exception) as e:  # noqa: BLE001
            out["testnet"] = {"ok": False, "error": e.__class__.__name__}
        return out

    @app.get("/api/security", dependencies=[Depends(auth)])
    def security():
        ok, n = st.store.verify_audit_chain()
        return _clean({"audit_chain_valid": ok, "audit_entries": n, "secrets_configured": configured(),
                       "live_trading_enabled": False, "withdrawal_capability": "none (no withdrawal code exists)",
                       "auth": "owner bearer token, constant-time compare, 5 login attempts/min/IP",
                       "scan": _json("security_scan.json", {"status": "NOT_RUN"})})

    @app.get("/api/system", dependencies=[Depends(auth)])
    def system():
        return _clean({"resources": cost.resources(), "python": platform.python_version(), "uptime_s": time.time() - st.started,
                       "requests": st.request_count, "paper_thread_alive": bool(st.thread and st.thread.is_alive()),
                       "inactive_reason": st.inactive_reason})

    @app.get("/api/costs", dependencies=[Depends(auth)])
    def costs():
        return _clean(cost.monthly_report(st.store.cost_summary()))

    @app.get("/api/audit", dependencies=[Depends(auth)])
    def audit(limit: int = 200):
        return {"entries": st.store.audit_tail(max(1, min(limit, 1000)))}

    @app.get("/api/settings", dependencies=[Depends(auth)])
    def get_settings():
        return {"settings": st.settings, "strategies": list(STRATEGIES), "datasets": list(DATASETS)}

    @app.post("/api/settings", dependencies=[Depends(auth)])
    async def set_settings(request: Request):
        try:
            body = await request.json()
        except Exception:  # noqa: BLE001
            raise HTTPException(400, "invalid JSON") from None
        if not isinstance(body, dict):
            raise HTTPException(400, "invalid body")
        allowed = {"language": ("bn", "en"), "feed": ("replay",), "replay_dataset": tuple(DATASETS),
                   "shadow_strategy": (None, *STRATEGIES)}
        new = {}
        for k, v in body.items():  # validate everything first; apply atomically
            try:
                if k == "replay_speed_s":
                    new[k] = float(min(10, max(0.05, float(v))))
                elif k == "telegram_owner_id":
                    new[k] = int(v) if v not in (None, "") else None
                elif k in allowed and v in allowed[k]:
                    new[k] = v
                else:
                    raise ValueError
            except (TypeError, ValueError):
                raise HTTPException(400, f"setting {k} not allowed") from None
        st.settings.update(new)
        st.save_settings()
        st.store.audit("owner", "settings_change", body)
        return {"settings": st.settings}

    @app.post("/api/paper/start", dependencies=[Depends(auth)])
    def paper_start():
        st.start_trader()
        return {"started": bool(st.thread and st.thread.is_alive()), "inactive_reason": st.inactive_reason}

    @app.post("/api/emergency-stop", dependencies=[Depends(auth)])
    def emergency_stop():
        DATA.mkdir(exist_ok=True)
        KILL_FILE.write_text(str(time.time()))
        if st.trader:
            st.trader.emergency_stop("owner emergency stop (dashboard)")
        st.store.audit("owner", "emergency_stop", {"via": "api"})
        return {"stopped": True}

    @app.post("/api/resume", dependencies=[Depends(auth)])
    async def resume(request: Request):
        try:
            body = await request.json()
        except Exception:  # noqa: BLE001
            body = {}
        if not isinstance(body, dict) or body.get("confirm") != "RESUME":
            raise HTTPException(400, "send {\"confirm\": \"RESUME\"}")
        KILL_FILE.unlink(missing_ok=True)
        if st.trader:
            st.trader.risk.owner_reset()
        st.store.audit("owner", "resume", {})
        return {"resumed": True}

    @app.get("/metrics", dependencies=[Depends(auth)], response_class=PlainTextResponse)
    def metrics():
        snap = st.trader.snapshot() if st.trader else {}
        lines = ["atm_up 1", f"atm_requests_total {st.request_count}", "atm_live_trading_enabled 0",
                 f"atm_paper_equity_usd {snap.get('equity_usd', 100.0)}", f"atm_paper_net_pnl_usd {snap.get('net_pnl_usd', 0.0)}",
                 f"atm_paper_running {int(bool(snap.get('running')))}", f"atm_kill_switch {int(KILL_FILE.exists())}"]
        return "\n".join(lines) + "\n"

    @app.websocket("/ws")
    async def ws(websocket: WebSocket):
        await websocket.accept()
        try:
            first = await asyncio.wait_for(websocket.receive_json(), timeout=10)
            if not token_matches(str(first.get("token", "")), token):
                await websocket.close(code=4401)
                return
            while True:
                snap = st.trader.snapshot() if st.trader else {"inactive_reason": st.inactive_reason}
                await websocket.send_text(json.dumps(_clean({"type": "paper", "data": snap}), default=str))
                await asyncio.sleep(2)
        except (WebSocketDisconnect, asyncio.TimeoutError):
            return

    if DASH.exists():
        app.mount("/static", StaticFiles(directory=DASH), name="static")

        @app.get("/")
        def index():
            return FileResponse(DASH / "index.html")

    @app.exception_handler(Exception)
    async def err(request, exc):  # never leak internals
        log.exception("unhandled error on %s", request.url.path)
        return JSONResponse({"error": "internal error"}, status_code=500)

    if start_background:
        @app.on_event("startup")
        def _start():
            st.start_trader()
    return app
