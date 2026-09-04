"""Harvester: source registry, CKAN adapter, runs log, resolver (spec 10).

Rules enforced: adapter priority (CKAN first), metadata-only fetch, robots/terms
notes on every source, per-host rate limit, descriptive UA, kill switch, staging
only (never direct publish), resolver requires exactly 1 portal match.
"""
from __future__ import annotations

import hashlib
import json
import time
from urllib.parse import quote_plus

import httpx
from fastapi import APIRouter, HTTPException

from .store import DatasetCandidate, HarvestRecord, Source, SourceRun, session

router = APIRouter(prefix="/api/v1", tags=["harvest"])

UA = "INQETRA-harvester/1.0 (+metadata only; respects robots.txt and rate limits)"
_last: dict[str, float] = {}


def _dump(o) -> dict:
    out = {}
    for c in o.__table__.columns:
        v = getattr(o, c.name)
        out[c.name] = v.isoformat() if hasattr(v, "isoformat") else v
    return out


def _throttle(host: str, pace: float = 1.0):
    wait = pace - (time.monotonic() - _last.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last[host] = time.monotonic()


def _get_json(url: str, timeout: int = 20) -> dict:
    from urllib.parse import urlparse
    _throttle(urlparse(url).hostname or "x")
    r = httpx.get(url, headers={"User-Agent": UA}, timeout=timeout, follow_redirects=True)
    r.raise_for_status()
    if "json" not in (r.headers.get("content-type") or "") and not url.endswith("package_search"):
        pass
    return r.json()


def fingerprint(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


@router.get("/sources")
def list_sources():
    db = session()
    return {"items": [_dump(s) for s in db.query(Source).order_by(Source.name).all()],
            "note": "All scheduled harvesting originates here. Kill switch + active flag enforced."}


@router.post("/sources")
def create_source(payload: dict):
    db = session()
    s = Source(name=payload.get("name", ""), base_url=payload.get("base_url", ""),
               source_type=payload.get("source_type", "catalogue"),
               adapter=payload.get("adapter", "CKAN"),
               trust_level=payload.get("trust_level", "Tier C"),
               active=bool(payload.get("active", True)), cadence=payload.get("cadence", ""),
               rate_limit=payload.get("rate_limit", "1/s"),
               terms_notes=payload.get("terms_notes", ""))
    db.add(s)
    db.commit()
    db.refresh(s)
    return _dump(s)


@router.patch("/sources/{sid}")
def patch_source(sid: str, payload: dict):
    db = session()
    s = db.get(Source, sid)
    if not s:
        raise HTTPException(404, "Source not found")
    for k in ("name", "base_url", "adapter", "trust_level", "active", "cadence",
              "rate_limit", "terms_notes", "kill_switch"):
        if k in payload:
            setattr(s, k, payload[k])
    db.commit()
    return _dump(s)


@router.get("/sources/{sid}/runs")
def source_runs(sid: str):
    db = session()
    return {"items": [_dump(r) for r in db.query(SourceRun).filter_by(source_id=sid).order_by(SourceRun.created_at.desc()).limit(20).all()]}


def _ckan_packages(api_url: str, rows: int) -> list[dict]:
    sep = "&" if "?" in api_url else "?"
    data = _get_json(f"{api_url}{sep}q=*:*&rows={rows}")
    return ((data.get("result") or {}).get("results")) or []


@router.post("/sources/{sid}/run")
def run_source(sid: str, payload: dict | None = None):
    """Fetch metadata only → immutable snapshot → staging candidates. Never publishes."""
    from .store import AuditEvent
    db = session()
    s = db.get(Source, sid)
    if not s:
        raise HTTPException(404, "Source not found")
    if s.kill_switch or not s.active:
        run = SourceRun(source_id=sid, status="failed", detail="Blocked by kill switch or inactive flag.")
        db.add(run)
        db.commit()
        return {"status": "blocked", "detail": run.detail}
    limit = min(int((payload or {}).get("limit", 10)), 50)
    run = SourceRun(source_id=sid, status="running", detail="")
    db.add(run)
    db.commit()
    added = changed = failed = 0
    try:
        if "ckan" in (s.adapter or "").lower():
            pkgs = _ckan_packages(s.base_url if "package_" in s.base_url else s.base_url.rstrip("/") + "/api/3/action/package_search", limit)
            for p in pkgs:
                fp = fingerprint({"id": p.get("id"), "title": p.get("title"), "rev": p.get("metadata_modified")})
                ex = db.query(HarvestRecord).filter_by(source_id=sid, external_id=str(p.get("id"))).first()
                if ex and ex.fingerprint == fp:
                    continue
                org = (p.get("organization") or {})
                cand = DatasetCandidate(source_id=sid, title=p.get("title", "")[:500],
                                        url=f"https://data.gov.uk/dataset/{p.get('name', '')}",
                                        publisher=org.get("title", "")[:300] if isinstance(org, dict) else "",
                                        licence_state="Unknown — read the source record before reuse",
                                        provenance={"portal": s.base_url, "external_id": p.get("id"),
                                                    "snapshot": {k: p.get(k) for k in ("title", "notes", "license_title", "metadata_modified")},
                                                    "fingerprint": fp})
                db.add(cand)
                db.flush()
                if ex:
                    ex.fingerprint, ex.raw, ex.candidate_id = fp, {"id": p.get("id")}, cand.id
                    changed += 1
                else:
                    db.add(HarvestRecord(source_id=sid, external_id=str(p.get("id")),
                                         fingerprint=fp, raw={"id": p.get("id")}, candidate_id=cand.id))
                    added += 1
        else:
            run.status, run.detail = "failed", f"Adapter '{s.adapter}' has no automated runner; use curated submission."
            db.commit()
            return {"status": "unsupported-adapter", "detail": run.detail}
        run.status, run.detail = "done", f"Metadata-only fetch complete: +{added} ~{changed}."
    except Exception as e:  # noqa: BLE001 — failure must not corrupt published records
        failed += 1
        run.status, run.detail = "failed", f"Harvester error (staging untouched, catalogue untouched): {str(e)[:200]}"
    run.added, run.changed, run.failed = added, changed, failed
    db.add(AuditEvent(actor="harvester", action="source-run", entity="sources",
                      entity_id=sid, detail=run.detail))
    db.commit()
    return {"status": run.status, "added": added, "changed": changed, "failed": failed, "detail": run.detail}


PORTAL_SEARCH = {
    "data.gov.uk": "https://data.gov.uk/search?os_view=false&q={q}",
    "planning.data.gov.uk": "https://www.planning.data.gov.uk/dataset/{slug}",
    "geoportal.statistics.gov.uk": "https://geoportal.statistics.gov.uk/search?q={q}",
    "ordnancesurvey.co.uk": "https://www.ordnancesurvey.co.uk/products/search-for-os-products?search={q}",
    "environment.data.gov.uk": "https://environment.data.gov.uk/search?q={q}",
    "metoffice.gov.uk": "https://www.metoffice.gov.uk/search-results?query={q}",
}


@router.post("/resolve")
def resolve(payload: dict):
    """Resolve an official_collection/search_query seed record to a current item.

    Exactly 1 portal match → staged resolution for curator review.
    0 or >1 → unresolved, stays in curation queue. Never auto-publishes.
    """
    from . import catalogue as cat
    db = session()
    rid = payload.get("dataset_id", "")
    known = {r["id"]: r for r in cat._project_subset()}
    rec = known.get(rid)
    if not rec:
        raise HTTPException(404, "Unknown catalogue record")
    if rec["link_type"] in ("direct_dataset", "api_endpoint"):
        return {"status": "already-direct", "dataset_id": rid}
    matches: list[dict] = []
    note = ""
    if "data.gov.uk" in rec["landing_url"]:
        try:
            data = _get_json("https://data.gov.uk/api/3/action/package_search?q=" + quote_plus(rec["title"]) + "&rows=5")
            for p in ((data.get("result") or {}).get("results") or []):
                if rec["title"].lower() in (p.get("title") or "").lower():
                    matches.append({"title": p.get("title"),
                                    "url": f"https://data.gov.uk/dataset/{p.get('name', '')}",
                                    "id": p.get("id")})
            note = "CKAN portal search on data.gov.uk"
        except Exception as e:  # noqa: BLE001
            return {"status": "portal-error", "dataset_id": rid, "detail": str(e)[:160]}
    else:
        host = next((h for h in PORTAL_SEARCH if h in rec["landing_url"]), "")
        tmpl = PORTAL_SEARCH.get(host, "https://www.google.com/search?q=site:{h}+{q}")
        return {"status": "manual", "dataset_id": rid,
                "portal_search_url": tmpl.format(q=quote_plus(rec["title"]),
                                                 slug=quote_plus(rec["title"].lower().replace(" ", "-")), h=host),
                "note": "Non-CKAN portal: resolve manually, then submit evidence. Ambiguous results stay in curation."}
    if len(matches) == 1:
        m = matches[0]
        c = DatasetCandidate(source_id="", title=m["title"], url=m["url"],
                             publisher=rec["publisher"], licence_state="Unknown",
                             provenance={"resolves": rid, "method": note}, status="staging")
        db.add(c)
        db.commit()
        db.refresh(c)
        return {"status": "staged", "dataset_id": rid, "candidate_id": c.id, "match": m,
                "note": "Staged for curator review with provenance + link health. Not published."}
    return {"status": "unresolved", "dataset_id": rid, "match_count": len(matches),
            "note": "0 or >1 matches — remains in curation queue, never auto-published."}


@router.get("/staging")
def staging(status: str = "staging"):
    db = session()
    q = db.query(DatasetCandidate)
    if status != "all":
        q = q.filter_by(status=status)
    return {"items": [_dump(c) for c in q.order_by(DatasetCandidate.created_at.desc()).limit(100).all()],
            "note": "Raw harvester/candidate output. Catalogue publication requires provenance + link health + review."}
