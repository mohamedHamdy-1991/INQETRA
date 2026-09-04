#!/usr/bin/env python3
"""Validate every seed landing URL and emit a reproducible CSV/JSON report.

This checks the public landing page only.  A successful response means the
catalogue link was reachable at validation time; it does not certify the
underlying data, licensing, reuse terms, or availability of a download.
"""
from __future__ import annotations

import argparse
import csv
import json
import ssl
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler

USER_AGENT = "INQETRA-link-health/1.0 (+metadata catalogue validation)"
SUCCESS = set(range(200, 400))


class LimitedRedirects(HTTPRedirectHandler):
    max_redirections = 5


OPENER = build_opener(LimitedRedirects)


def check(url: str, timeout: int) -> dict[str, object]:
    started = time.monotonic()
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/json;q=0.9,*/*;q=0.1"})
    try:
        with OPENER.open(request, timeout=timeout) as response:
            status = response.getcode()
            return {"url": url, "final_url": response.geturl(), "http_status": status,
                    "reachable": status in SUCCESS, "error": "", "elapsed_ms": round((time.monotonic() - started) * 1000)}
    except HTTPError as exc:
        return {"url": url, "final_url": exc.geturl() or url, "http_status": exc.code,
                "reachable": exc.code in SUCCESS, "error": f"HTTP {exc.code}", "elapsed_ms": round((time.monotonic() - started) * 1000)}
    except (URLError, TimeoutError, ssl.SSLError, OSError) as exc:
        return {"url": url, "final_url": "", "http_status": "", "reachable": False,
                "error": str(exc.reason if isinstance(exc, URLError) else exc), "elapsed_ms": round((time.monotonic() - started) * 1000)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/datasets_seed.csv")
    parser.add_argument("--output-dir", default="data/link_health")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()
    with Path(args.input).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    urls = sorted({row["landing_url"].strip() for row in rows if row["landing_url"].strip()})
    results: dict[str, dict[str, object]] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(check, url, args.timeout): url for url in urls}
        for future in as_completed(futures):
            result = future.result()
            results[str(result["url"])] = result
    stamped = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    report_rows = [{"dataset_id": row["id"], "title": row["title"], **results[row["landing_url"].strip()]} for row in rows]
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    fields = ["dataset_id", "title", "url", "final_url", "http_status", "reachable", "error", "elapsed_ms"]
    with (output / "catalogue_link_health.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(report_rows)
    summary = {"checked_at_utc": stamped, "record_count": len(rows), "unique_url_count": len(urls),
               "reachable_record_count": sum(bool(r["reachable"]) for r in report_rows),
               "unreachable_record_count": sum(not bool(r["reachable"]) for r in report_rows),
               "reachable_unique_url_count": sum(bool(r["reachable"]) for r in results.values()),
               "unreachable_unique_url_count": sum(not bool(r["reachable"]) for r in results.values()),
               "definition": "Reachable means the catalogue landing URL returned HTTP 200-399 when checked; it does not prove data or licence validity."}
    (output / "catalogue_link_health_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["unreachable_record_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
