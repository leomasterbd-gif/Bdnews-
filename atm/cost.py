"""Operational cost tracking. Every figure is either measured or an explicit estimate
labelled as such. Nothing here can purchase anything."""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_START = time.time()

# Owner-editable assumptions (USD/month). Zero until the owner approves a purchase.
ASSUMPTIONS = {
    "vps_monthly_usd": float(os.environ.get("ATM_VPS_MONTHLY_USD", 0) or 0),
    "claude_api_monthly_budget_usd": float(os.environ.get("ATM_CLAUDE_BUDGET_USD", 0) or 0),
    "gpu_monthly_usd": 0.0,
    "data_feeds_monthly_usd": 0.0,  # Binance public data + testnet are free
}


def resources() -> dict:
    du = shutil.disk_usage(ROOT)
    out = {"disk_total_gb": du.total / 1e9, "disk_used_gb": du.used / 1e9, "uptime_s": time.time() - _START,
           "cpu_count": os.cpu_count()}
    try:
        la = os.getloadavg()
        out["load_avg"] = la
    except OSError:
        pass
    try:
        mem = {}
        for line in Path("/proc/meminfo").read_text().splitlines()[:3]:
            k, v = line.split(":")
            mem[k] = int(v.split()[0]) / 1e6
        out["mem_total_gb"], out["mem_free_gb"] = mem.get("MemTotal"), mem.get("MemAvailable", mem.get("MemFree"))
    except OSError:
        pass
    db = ROOT / "data" / "atm.db"
    out["db_size_mb"] = db.stat().st_size / 1e6 if db.exists() else 0.0
    out["reports_size_mb"] = sum(p.stat().st_size for p in (ROOT / "reports").glob("*")) / 1e6 if (ROOT / "reports").exists() else 0.0
    return out


def monthly_report(ledger: dict | None = None) -> dict:
    ledger = ledger or {}
    measured = sum(v["usd"] or 0 for v in ledger.values())
    fixed = sum(ASSUMPTIONS.values())
    return {"assumptions_usd_month": ASSUMPTIONS, "ledger": ledger, "measured_usd": measured,
            "projected_monthly_usd": fixed + measured,
            "note": "All components are free/open-source. Paid items stay at $0 until the owner approves them."}
