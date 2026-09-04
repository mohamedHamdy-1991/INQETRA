#!/usr/bin/env python3
"""Create the human-shareable dataset export from seed metadata and link health."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
seed_path = DATA / "datasets_seed.csv"
health_path = DATA / "link_health" / "catalogue_link_health.csv"
output_path = DATA / "INQETRA_751_DATASETS_WITH_TESTED_LINKS.csv"

with seed_path.open(newline="", encoding="utf-8") as handle:
    seed = list(csv.DictReader(handle))
with health_path.open(newline="", encoding="utf-8") as handle:
    health = {row["dataset_id"]: row for row in csv.DictReader(handle)}

if len(seed) < 750 or set(row["id"] for row in seed) != set(health):
    raise SystemExit("Seed and link-health records do not match; run validate_catalogue_links.py first.")

fields = list(seed[0]) + ["link_check_reachable", "link_check_http_status", "link_check_final_url", "link_checked_at_utc"]
summary_timestamp = (DATA / "link_health" / "catalogue_link_health_summary.json").read_text(encoding="utf-8")
import json
checked_at = json.loads(summary_timestamp)["checked_at_utc"]
with output_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for row in seed:
        link = health[row["id"]]
        writer.writerow({**row, "link_check_reachable": link["reachable"], "link_check_http_status": link["http_status"], "link_check_final_url": link["final_url"], "link_checked_at_utc": checked_at})
print(f"Wrote {len(seed)} datasets with tested landing links to {output_path}")
