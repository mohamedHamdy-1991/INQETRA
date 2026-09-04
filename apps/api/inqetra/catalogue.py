"""Catalogue endpoints: search, detail, parity views, compare, publishers, taxonomy, kits, sources, health."""
from __future__ import annotations

import csv
import io
import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from .domain_filter import FILTERS, matches
from .seed import REPO_ROOT, catalogue_markdown, load_rows, enrich

router = APIRouter(prefix="/api/v1", tags=["catalogue"])

CAVEAT = ("Landing-page reachability does not prove download access, licence permission, "
          "scientific fitness or resolved metadata.")


@lru_cache(maxsize=1)
def _catalogue() -> list[dict]:
    return enrich(load_rows())


def _project_subset() -> list[dict]:
    # fresh (tests may overwrite seeds file) — bypass cache when env flag set
    import os
    if os.getenv("INQETRA_NOCACHE"):
        return enrich(load_rows())
    return _catalogue()


@router.get("/datasets")
def list_datasets(q: str = "", domain: str = "", topic: str = "", geography: str = "",
                  access: str = "", licence: str = "", publisher: str = "",
                  authority: str = "", method: str = "", role: str = "",
                  format: str = "", link_type: str = "", verification_state: str = "",
                  open_only: bool = False, has_api: bool = False,
                  limit: int = Query(24, le=200), offset: int = 0):
    rows = _project_subset()
    ql = q.strip().lower()
    out = []
    for r in rows:
        hay = " ".join([r["title"], r["publisher"], r["domain"], r["subdomain"],
                        r["variables"], r["coverage"], r["source_portal"]]).lower()
        if ql and ql not in hay:
            continue
        matched_by = ""
        if domain:
            ok, key = matches(r, domain)
            if not ok:
                continue
            matched_by = f"domain-facet:{domain}~{key}"
        if topic and topic.lower() not in (r["subdomain"] + " " + r["domain"]).lower():
            continue
        if geography and geography.lower() not in (r["coverage"] + " " + r["uk_nation"] + " " + r["country"]).lower():
            continue
        if access and access.lower() not in r["access_type"].lower():
            continue
        if licence and licence.lower() not in r["licence"].lower():
            continue
        if publisher and publisher.lower() not in r["publisher"].lower():
            continue
        if authority and authority.lower() not in r["authority_level"].lower():
            continue
        if method and method.lower() not in r["methods_supported"].lower():
            continue
        if role and role.lower() not in r["research_roles"].lower():
            continue
        if format and format.lower() not in r["formats"].lower():
            continue
        if link_type and link_type.lower() != r["link_type"].lower():
            continue
        if verification_state and verification_state.lower() != r["verification_state"].lower():
            continue
        if open_only and "open" not in r["access_type"].lower():
            continue
        if has_api and "api" not in (r["formats"] + " " + r["link_type"]).lower():
            continue
        score = hay.count(ql) if ql else 0
        out.append({**r, "search_relevance": score, "filter_matched_by": matched_by})
    out.sort(key=lambda r: (-r["search_relevance"], r["id"]))
    total = len(out)
    return {"total": total, "limit": limit, "offset": offset,
            "items": out[offset:offset + limit], "caveat": CAVEAT,
            "facets": {"domain": sorted(FILTERS.keys())}}


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str):
    for r in _project_subset():
        if r["id"] == dataset_id or r["slug"] == dataset_id.lower():
            related = [x for x in _project_subset()
                       if x["id"] != r["id"] and (x["domain"] == r["domain"] or x["publisher"] == r["publisher"])][:6]
            return {"item": r, "related_ids": [x["id"] for x in related], "caveat": CAVEAT}
    raise HTTPException(404, f"Dataset {dataset_id} not found")


@router.get("/datasets/views/csv", response_class=PlainTextResponse)
def view_csv():
    rows = _project_subset()
    buf = io.StringIO()
    fields = ["id", "title", "publisher", "domain", "subdomain", "coverage", "uk_nation",
              "access_type", "licence", "authority_level", "landing_url", "link_type",
              "verification_state", "last_catalogue_review"]
    w = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")


@router.get("/datasets/views/json")
def view_json():
    return {"count": len(_project_subset()), "items": _project_subset(), "caveat": CAVEAT}


@router.get("/datasets/views/markdown", response_class=PlainTextResponse)
def view_markdown():
    return PlainTextResponse(catalogue_markdown(_project_subset()), media_type="text/markdown")


@router.post("/datasets/compare")
def compare(payload: dict):
    ids = payload.get("ids", [])[:4]
    rows = {r["id"]: r for r in _project_subset()}
    items = [rows[i] for i in ids if i in rows]
    if len(items) < 2:
        raise HTTPException(400, "Provide 2–4 dataset ids")
    fields = ["authority_level", "coverage", "spatial_scale", "temporal_resolution",
              "research_roles", "formats", "access_type", "licence", "publisher",
              "link_type", "verification_state", "landing_url"]
    grid = [{f: it.get(f, "") for f in fields} | {"id": it["id"], "title": it["title"]} for it in items]
    notes = []
    covs = {it["coverage"] for it in items}
    if len(covs) > 1:
        notes.append(f"Coverage differs ({'; '.join(sorted(covs))}); confirm a shared study boundary before joining.")
    lics = {it["licence"] for it in items}
    if len(lics) > 1:
        notes.append("Licences differ across compared datasets; read each source licence — public availability does not imply compatible reuse.")
    return {"items": grid, "notes": notes,
            "explanation": "Side-by-side source-declared facts. Search relevance is not dataset quality.",
            "caveat": CAVEAT}


def _distinct(key: str) -> list[str]:
    return sorted({r[key] for r in _project_subset() if r[key].strip()})


@router.get("/publishers")
def publishers():
    pubs: dict[str, dict] = {}
    for r in _project_subset():
        p = pubs.setdefault(r["publisher"], {"name": r["publisher"], "count": 0, "authority": r["authority_level"]})
        p["count"] += 1
    return {"items": sorted(pubs.values(), key=lambda x: -x["count"])}


@router.get("/taxonomy")
def taxonomy():
    p = REPO_ROOT / "INQETRA_AI_BUILD_PACK" / "data" / "taxonomy.json"
    return json.loads(p.read_text(encoding="utf-8"))


@router.get("/health")
def health():
    for p in [REPO_ROOT / "data" / "seeds" / "link_health_summary.json",
              REPO_ROOT / "INQETRA_AI_BUILD_PACK" / "data" / "link_health" / "catalogue_link_health_summary.json"]:
        if p.exists():
            s = json.loads(p.read_text(encoding="utf-8"))
            return {**s, "definition": s.get("definition", CAVEAT)}
    return {"record_count": len(_project_subset()), "definition": CAVEAT}
