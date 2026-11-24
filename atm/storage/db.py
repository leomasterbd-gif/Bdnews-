"""SQLite storage: versioned strategy registry, experiments, paper trades, cost ledger and
a tamper-evident (hash-chained, append-only) audit log.

SQLite is chosen for a single-node $0 deployment; the schema is portable to PostgreSQL."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "atm.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS strategies (
  id INTEGER PRIMARY KEY, name TEXT, version INTEGER, family TEXT, params TEXT, status TEXT,
  metrics TEXT, dataset TEXT, created REAL, notes TEXT, UNIQUE(name, version, dataset));
CREATE TABLE IF NOT EXISTS experiments (
  id INTEGER PRIMARY KEY, kind TEXT, hypothesis TEXT, config TEXT, result TEXT, verdict TEXT, created REAL);
CREATE TABLE IF NOT EXISTS paper_trades (
  id INTEGER PRIMARY KEY, session TEXT, symbol TEXT, side TEXT, qty REAL, price REAL, fee REAL,
  ts TEXT, source TEXT, strategy TEXT, pnl REAL);
CREATE TABLE IF NOT EXISTS costs (
  id INTEGER PRIMARY KEY, category TEXT, amount_usd REAL, units REAL, note TEXT, ts REAL);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY, ts REAL, actor TEXT, action TEXT, detail TEXT, prev_hash TEXT, hash TEXT);
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit_log BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit_log BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;
"""

STATUSES = ("EXPERIMENTAL", "VALIDATED", "PAPER", "REJECTED", "ARCHIVED", "ROLLED_BACK")


class Store:
    def __init__(self, path: Path | str = DEFAULT_DB):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    # ---- audit ---------------------------------------------------------
    def audit(self, actor: str, action: str, detail: dict | str = "") -> str:
        with self._lock:
            row = self.conn.execute("SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
            prev = row["hash"] if row else "GENESIS"
            ts = time.time()
            d = detail if isinstance(detail, str) else json.dumps(detail, sort_keys=True, default=str)
            h = hashlib.sha256(f"{prev}|{ts:.6f}|{actor}|{action}|{d}".encode()).hexdigest()
            self.conn.execute("INSERT INTO audit_log(ts,actor,action,detail,prev_hash,hash) VALUES(?,?,?,?,?,?)", (ts, actor, action, d, prev, h))
            self.conn.commit()
            return h

    def verify_audit_chain(self) -> tuple[bool, int]:
        prev = "GENESIS"
        n = 0
        for r in self.conn.execute("SELECT * FROM audit_log ORDER BY id"):
            h = hashlib.sha256(f"{prev}|{r['ts']:.6f}|{r['actor']}|{r['action']}|{r['detail']}".encode()).hexdigest()
            if r["prev_hash"] != prev or r["hash"] != h:
                return False, n
            prev, n = h, n + 1
        return True, n

    def audit_tail(self, limit: int = 100) -> list[dict]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))]

    # ---- registry -------------------------------------------------------
    def register(self, name, family, params, status, metrics, dataset, notes="") -> int:
        if status not in STATUSES:
            raise ValueError(status)
        with self._lock:
            v = self.conn.execute("SELECT COALESCE(MAX(version),0)+1 FROM strategies WHERE name=? AND dataset=?", (name, dataset)).fetchone()[0]
            self.conn.execute("INSERT INTO strategies(name,version,family,params,status,metrics,dataset,created,notes) VALUES(?,?,?,?,?,?,?,?,?)",
                              (name, v, family, json.dumps(params, default=str), status, json.dumps(metrics, default=str), dataset, time.time(), notes))
            self.conn.commit()
        self.audit("research", "register_strategy", {"name": name, "version": v, "dataset": dataset, "status": status})
        return v

    def set_status(self, name, version, dataset, status, actor="research"):
        if status not in STATUSES:
            raise ValueError(status)
        with self._lock:
            self.conn.execute("UPDATE strategies SET status=? WHERE name=? AND version=? AND dataset=?", (status, name, version, dataset))
            self.conn.commit()
        self.audit(actor, "set_status", {"name": name, "version": version, "dataset": dataset, "status": status})

    def strategies(self, status: str | None = None) -> list[dict]:
        q, a = "SELECT * FROM strategies", ()
        if status:
            q, a = q + " WHERE status=?", (status,)
        rows = []
        for r in self.conn.execute(q + " ORDER BY created DESC", a):
            d = dict(r)
            d["params"], d["metrics"] = json.loads(d["params"]), json.loads(d["metrics"])
            rows.append(d)
        return rows

    def latest_validated(self, name: str, dataset: str) -> dict | None:
        r = self.conn.execute("SELECT * FROM strategies WHERE name=? AND dataset=? AND status IN ('VALIDATED','PAPER') ORDER BY version DESC LIMIT 1",
                              (name, dataset)).fetchone()
        return dict(r) if r else None

    # ---- experiments / trades / costs ------------------------------------
    def experiment(self, kind, hypothesis, config, result, verdict) -> None:
        with self._lock:
            self.conn.execute("INSERT INTO experiments(kind,hypothesis,config,result,verdict,created) VALUES(?,?,?,?,?,?)",
                              (kind, hypothesis, json.dumps(config, default=str), json.dumps(result, default=str), verdict, time.time()))
            self.conn.commit()

    def experiments(self, limit=200) -> list[dict]:
        return [dict(r) for r in self.conn.execute("SELECT id,kind,hypothesis,verdict,created FROM experiments ORDER BY id DESC LIMIT ?", (limit,))]

    PAPER_COLS = ("session", "symbol", "side", "qty", "price", "fee", "ts", "source", "strategy", "pnl")

    def add_paper_trade(self, **kw) -> None:
        bad = set(kw) - set(self.PAPER_COLS)
        if bad:
            raise ValueError(f"unknown columns {bad}")
        cols = ",".join(kw)  # whitelisted identifiers only
        with self._lock:
            self.conn.execute(f"INSERT INTO paper_trades({cols}) VALUES({','.join('?' * len(kw))})", tuple(kw.values()))  # nosec B608
            self.conn.commit()

    def paper_trades(self, limit=500) -> list[dict]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM paper_trades ORDER BY id DESC LIMIT ?", (limit,))]

    def add_cost(self, category: str, amount_usd: float, units: float = 0.0, note: str = "") -> None:
        with self._lock:
            self.conn.execute("INSERT INTO costs(category,amount_usd,units,note,ts) VALUES(?,?,?,?,?)", (category, amount_usd, units, note, time.time()))
            self.conn.commit()

    def cost_summary(self) -> dict:
        return {r["category"]: {"usd": r["s"], "units": r["u"]} for r in
                self.conn.execute("SELECT category, SUM(amount_usd) s, SUM(units) u FROM costs GROUP BY category")}
