"""Candidate inbox: resolve / reject / curate. Never auto-publishes to catalogue."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .store import Candidate, session

router = APIRouter(prefix="/api/v1", tags=["candidates"])


def _dump(o) -> dict:
    return {c.name: getattr(o, c.name) for c in o.__table__.columns}


@router.get("/projects/{pid}/candidates")
def list_candidates(pid: str):
    db = session()
    return {"items": [_dump(c) for c in db.query(Candidate).filter_by(project_id=pid).all()],
            "note": "Candidates are unresolved leads. Resolution stores evidence; curation requires provenance + link health."}


@router.post("/candidates/{cid}/resolve")
def resolve(cid: str, payload: dict):
    db = session()
    c = db.get(Candidate, cid)
    if not c:
        raise HTTPException(404, "Candidate not found")
    url = (payload.get("url") or "").strip()
    if not (url.startswith("https://") or url.startswith("http://")):
        raise HTTPException(400, "Provide an http(s) URL to resolve this candidate")
    c.url = url
    c.source = payload.get("source", c.source)
    c.licence_state = payload.get("licence_state", "Unknown")
    c.status = "resolved"
    db.commit()
    return _dump(c)


@router.post("/candidates/{cid}/reject")
def reject(cid: str, payload: dict | None = None):
    db = session()
    c = db.get(Candidate, cid)
    if not c:
        raise HTTPException(404, "Candidate not found")
    c.status = "rejected"
    db.commit()
    return _dump(c)


@router.post("/candidates/{cid}/curate")
def curate(cid: str, payload: dict | None = None):
    """Curate = attach evidence snapshot; still NOT published to the public catalogue."""
    db = session()
    c = db.get(Candidate, cid)
    if not c:
        raise HTTPException(404, "Candidate not found")
    if c.status != "resolved":
        raise HTTPException(400, "Resolve to a concrete URL before curation")
    c.status = "curated"
    db.commit()
    return {**_dump(c), "published_to_catalogue": False,
            "note": "Curated candidates await catalogue review with provenance + link health; nothing auto-publishes."}
