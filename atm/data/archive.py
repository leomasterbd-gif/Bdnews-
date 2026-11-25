"""Download official Binance public spot kline archives (https://data.binance.vision) with
SHA-256 checksum verification, and convert them into the project's CSV.gz format.

Archives are untrusted input: every file's checksum must match Binance's published
.CHECKSUM, zips are read in memory (never extracted to disk), and only the expected
12 numeric columns are parsed."""
from __future__ import annotations

import hashlib
import io
import json
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

BASE = "https://data.binance.vision/data/spot/monthly/klines"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "historical" / "binance"
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "trades",
        "taker_base", "taker_quote", "ignore"]


class ArchiveError(RuntimeError):
    pass


def _get(url: str, session: requests.Session, tries: int = 4) -> bytes:
    for i in range(tries):
        try:
            r = session.get(url, timeout=60)
            if r.status_code == 404:
                raise ArchiveError(f"not found: {url}")
            r.raise_for_status()
            return r.content
        except requests.RequestException:
            if i == tries - 1:
                raise
            time.sleep(2 ** i)
    raise ArchiveError(url)


def parse_kline_zip(blob: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = [n for n in z.namelist() if n.endswith(".csv") and "/" not in n and ".." not in n]
        if len(names) != 1:
            raise ArchiveError(f"unexpected archive contents: {z.namelist()[:5]}")
        info = z.getinfo(names[0])
        if info.file_size > 200_000_000:
            raise ArchiveError("archive member too large")
        raw = z.read(names[0])
    df = pd.read_csv(io.BytesIO(raw), header=None)
    if not str(df.iloc[0, 0]).lstrip("-").isdigit():  # some months ship a header row
        df = df.iloc[1:]
    if df.shape[1] != 12:
        raise ArchiveError(f"expected 12 columns, got {df.shape[1]}")
    df.columns = COLS
    t = pd.to_numeric(df.open_time)
    unit = "us" if t.iloc[0] > 1e14 else "ms"  # Binance switched spot archives to microseconds in 2025
    out = pd.DataFrame({"date": pd.to_datetime(t, unit=unit, utc=True)})
    for c in ("open", "high", "low", "close", "volume"):
        out[c] = pd.to_numeric(df[c]).astype(float).values
    return out


def download_month(symbol: str, interval: str, month: str, session: requests.Session) -> pd.DataFrame:
    name = f"{symbol}-{interval}-{month}.zip"
    url = f"{BASE}/{symbol}/{interval}/{name}"
    blob = _get(url, session)
    expected = _get(url + ".CHECKSUM", session).decode().split()[0].strip().lower()
    got = hashlib.sha256(blob).hexdigest()
    if got != expected:
        raise ArchiveError(f"checksum mismatch for {name}")
    df = parse_kline_zip(blob)
    df.attrs["sha256"] = got
    return df


def months_back(n: int, last: str) -> list[str]:
    end = pd.Period(last, "M")
    return [str(end - i) for i in range(n - 1, -1, -1)]


def fetch(symbol: str, interval: str = "5m", n_months: int = 24, last_month: str | None = None) -> dict:
    last_month = last_month or str(pd.Timestamp.utcnow().to_period("M") - 1)
    s = requests.Session()
    s.headers["User-Agent"] = "atm-research/1.0"
    parts, sums, missing = [], {}, []
    for m in months_back(n_months, last_month):
        try:
            d = download_month(symbol, interval, m, s)
        except ArchiveError as e:
            missing.append(f"{m}: {e}")
            continue
        parts.append(d)
        sums[m] = d.attrs["sha256"]
    if not parts:
        raise ArchiveError(f"no data for {symbol}")
    df = pd.concat(parts).drop_duplicates("date").sort_values("date")
    OUT.mkdir(parents=True, exist_ok=True)
    name = f"{symbol}-{interval}"
    df.to_csv(OUT / f"{name}.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
    meta = {"dataset": f"binance/{name}", "symbol": symbol, "interval": interval, "rows": len(df),
            "start": str(df.date.iloc[0]), "end": str(df.date.iloc[-1]), "source": BASE,
            "archive_sha256": sums, "missing": missing}
    man_p = OUT / "MANIFEST.json"
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    man[name] = meta
    man_p.write_text(json.dumps(man, indent=1))
    return meta
