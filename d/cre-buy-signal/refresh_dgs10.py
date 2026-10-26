#!/usr/bin/env python3
"""Pull latest FRED DGS10 and write live_dgs10.json next to this script.

Usage:
  python3 refresh_dgs10.py
  python3 refresh_dgs10.py /path/to/live_dgs10.json

For GitHub Pages later: run via cron or Actions, commit the JSON sibling.
Browser CORS usually blocks direct fred.stlouisfed.org CSV fetches from a
static page, so this file is the supported live path.
"""
from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"
FRED_PAGE = "https://fred.stlouisfed.org/series/DGS10"


def latest_dgs10() -> tuple[str, float]:
    with urllib.request.urlopen(FRED_CSV, timeout=60) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    date, val = None, None
    for line in text.strip().splitlines()[1:]:
        parts = line.split(",")
        if len(parts) < 2:
            continue
        d, v = parts[0].strip(), parts[1].strip()
        if v in ("", "."):
            continue
        date, val = d, float(v)
    if date is None or val is None:
        raise SystemExit("No DGS10 observations found in FRED CSV")
    return date, val


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "live_dgs10.json"
    as_of, pct = latest_dgs10()
    # America/New_York-friendly local stamp when the box TZ is set that way
    refreshed = datetime.now().astimezone().isoformat(timespec="seconds")
    payload = {
        "series": "DGS10",
        "source": FRED_PAGE,
        "csv": FRED_CSV,
        "as_of": as_of,
        "dgs10_pct": pct,
        "refreshed_at": refreshed,
        "note": "Sibling file for GitHub Pages / cron. Browser CORS usually blocks direct FRED fetch.",
    }
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out}  DGS10={pct}% as_of={as_of}")


if __name__ == "__main__":
    main()
