"""INQETRA catalogue seed loader. Single authority: data/seeds/datasets.csv.

Preserves every seed field verbatim (never invents metadata). Builds JSON + Markdown
parity views from the same rows so CSV/JSON/MD stay in lockstep.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PACK_CSV = REPO_ROOT / "INQETRA_AI_BUILD_PACK" / "data" / "datasets_seed.csv"
SEED_CSV = REPO_ROOT / "data" / "seeds" / "datasets.csv"
SEED_JSON = REPO_ROOT / "data" / "seeds" / "datasets.json"
SEED_MD = REPO_ROOT / "data" / "seeds" / "catalogue.md"
HEALTH_SRC = REPO_ROOT / "INQETRA_AI_BUILD_PACK" / "data" / "link_health" / "catalogue_link_health_summary.json"
HEALTH_CSV = REPO_ROOT / "INQETRA_AI_BUILD_PACK" / "data" / "link_health" / "catalogue_link_health.csv"

COLUMNS = ["id", "title", "publisher", "source_portal", "country", "uk_nation",
           "domain", "subdomain", "research_roles", "methods_supported",
           "spatial_scale", "temporal_resolution", "coverage", "formats",
           "access_type", "licence", "authority_level", "landing_url",
           "link_type", "verification_state", "variables", "notes",
           "last_catalogue_review"]


def load_rows(csv_path: Path = SEED_CSV) -> list[dict]:
    if not csv_path.exists() and csv_path == SEED_CSV and PACK_CSV.exists():
        csv_path = PACK_CSV
    with csv_path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    # Normalise whitespace only; never invent values.
    return [{k: (r.get(k, "") or "").strip() for k in COLUMNS} for r in rows]


def slug_for(row: dict) -> str:
    return row["id"].lower()


def enrich(rows: list[dict]) -> list[dict]:
    health = _health_by_id()
    out = []
    for r in rows:
        h = health.get(r["id"], {})
        out.append({**r, "slug": slug_for(r),
                    "link_health": {"final_url": h.get("final_url", ""),
                                    "http_status": h.get("http_status", ""),
                                    "reachable": h.get("reachable", ""),
                                    "checked_at_utc": _health_summary().get("checked_at_utc", "")}})
    return out


def _health_summary() -> dict:
    for p in [REPO_ROOT / "data" / "seeds" / "link_health_summary.json", HEALTH_SRC]:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {}


def _health_by_id() -> dict:
    if not HEALTH_CSV.exists():
        return {}
    with HEALTH_CSV.open(encoding="utf-8") as fh:
        return {r["dataset_id"]: r for r in csv.DictReader(fh)}


def build_parity_views() -> dict:
    """Regenerate datasets.json + catalogue.md from datasets.csv. Returns stats."""
    rows = load_rows()
    SEED_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# INQETRA Dataset Catalogue", "",
             f"{len(rows)} records. Landing-page reachability is recorded in link-health evidence; "
             "reachability does not prove download access, licence permission or scientific fitness.", ""]
    for r in rows:
        lines.append(f"## {r['id']} — {r['title']}")
        lines.append(f"- Publisher: {r['publisher']} ({r['authority_level']})")
        lines.append(f"- Domain: {r['domain']} / {r['subdomain']}; Coverage: {r['coverage']} ({r['uk_nation']})")
        lines.append(f"- Access: {r['access_type']}; Licence: {r['licence']}")
        lines.append(f"- Landing URL: {r['landing_url']} [{r['link_type']} / {r['verification_state']}, reviewed {r['last_catalogue_review']}]")
        lines.append("")
    SEED_MD.write_text("\n".join(lines), encoding="utf-8")
    sha = hashlib.sha256(SEED_CSV.read_bytes()).hexdigest()[:16] if SEED_CSV.exists() else "pack"
    return {"count": len(rows), "seed_sha16": sha}


def catalogue_markdown(rows: list[dict]) -> str:
    lines = ["# INQETRA Dataset Catalogue (live view)", ""]
    for r in rows:
        lines.append(f"## {r['id']} — {r['title']}")
        lines.append(f"- Publisher: {r['publisher']} | {r['landing_url']}")
    return "\n".join(lines) + "\n"
