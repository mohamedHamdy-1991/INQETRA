"""Extended studio entities: knowledge gaps, concepts/graph, methodology,
variables, transformations, analysis steps, contributions, citations, submissions.
All first-class relations with rationale/status/created_by where the spec requires it.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .store import (AnalysisStep, Citation, Concept, ConceptRelationship, Contribution,
                    KnowledgeGap, Methodology, Project, Transformation,
                    VariableRequirement, session)

router = APIRouter(prefix="/api/v1/projects", tags=["studio"])
pub = APIRouter(prefix="/api/v1", tags=["submissions"])


def _s():
    return session()


def _dump(o) -> dict:
    out = {}
    for c in o.__table__.columns:
        v = getattr(o, c.name)
        out[c.name] = v.isoformat() if hasattr(v, "isoformat") else v
    return out


def _proj(db, pid: str) -> Project:
    p = db.get(Project, pid)
    if not p:
        raise HTTPException(404, "Project not found")
    return p


def _create(db, cls, pid: str, payload: dict):
    _proj(db, pid)
    o = cls(project_id=pid)
    for k, v in payload.items():
        if hasattr(o, k) and k not in ("id", "project_id", "created_at"):
            setattr(o, k, v)
    db.add(o)
    db.commit()
    db.refresh(o)
    return _dump(o)


@router.post("/{pid}/kgaps")
def add_gap(pid: str, payload: dict):
    return _create(_s(), KnowledgeGap, pid, payload)


@router.post("/{pid}/concepts")
def add_concept(pid: str, payload: dict):
    return _create(_s(), Concept, pid, payload)


@router.patch("/{pid}/concepts/{cid}")
def move_concept(pid: str, cid: str, payload: dict):
    db = _s()
    o = db.get(Concept, cid)
    if not o or o.project_id != pid:
        raise HTTPException(404, "Concept not found")
    for k in ("label", "kind", "x", "y", "description"):
        if k in payload:
            setattr(o, k, payload[k])
    db.commit()
    return _dump(o)


@router.get("/{pid}/graph")
def get_graph(pid: str):
    db = _s()
    _proj(db, pid)
    return {"nodes": [_dump(c) for c in db.query(Concept).filter_by(project_id=pid).all()],
            "edges": [_dump(e) for e in db.query(ConceptRelationship).filter_by(project_id=pid).all()]}


@router.post("/{pid}/edges")
def add_edge(pid: str, payload: dict):
    db = _s()
    _proj(db, pid)
    e = ConceptRelationship(project_id=pid, from_id=payload.get("from_id", ""),
                            to_id=payload.get("to_id", ""),
                            relation=payload.get("relation", "influences"),
                            rationale=payload.get("rationale", ""))
    db.add(e)
    db.commit()
    db.refresh(e)
    return _dump(e)


@router.delete("/{pid}/edges/{eid}")
def del_edge(pid: str, eid: str):
    db = _s()
    e = db.get(ConceptRelationship, eid)
    if not e or e.project_id != pid:
        raise HTTPException(404, "Edge not found")
    db.delete(e)
    db.commit()
    return {"removed": eid}


@router.post("/{pid}/methodology")
def set_methodology(pid: str, payload: dict):
    db = _s()
    _proj(db, pid)
    m = db.query(Methodology).filter_by(project_id=pid).first() or Methodology(project_id=pid)
    for k in ("design", "description", "ethics", "limitations"):
        if k in payload:
            setattr(m, k, payload[k])
    db.add(m)
    db.commit()
    db.refresh(m)
    return _dump(m)


@router.post("/{pid}/requirements/{rid}/variables")
def add_variable(pid: str, rid: str, payload: dict):
    db = _s()
    _proj(db, pid)
    v = VariableRequirement(project_id=pid, requirement_id=rid, name=payload.get("name", ""),
                            unit=payload.get("unit", ""), role_hint=payload.get("role_hint", ""))
    db.add(v)
    db.commit()
    db.refresh(v)
    return _dump(v)


@router.post("/{pid}/transformations")
def add_transformation(pid: str, payload: dict):
    return _create(_s(), Transformation, pid, payload)


@router.get("/{pid}/transformations")
def list_transformations(pid: str):
    db = _s()
    return {"items": [_dump(t) for t in db.query(Transformation).filter_by(project_id=pid).all()]}


@router.post("/{pid}/steps")
def add_step(pid: str, payload: dict):
    db = _s()
    _proj(db, pid)
    n = db.query(AnalysisStep).filter_by(project_id=pid).count()
    return _create(_s(), AnalysisStep, pid, {**payload, "order": n})


@router.patch("/{pid}/steps/{sid}")
def patch_step(pid: str, sid: str, payload: dict):
    db = _s()
    o = db.get(AnalysisStep, sid)
    if not o or o.project_id != pid:
        raise HTTPException(404, "Step not found")
    for k in ("stage", "description", "inputs", "outputs", "software", "order"):
        if k in payload:
            setattr(o, k, payload[k])
    db.commit()
    return _dump(o)


@router.get("/{pid}/steps")
def list_steps(pid: str):
    db = _s()
    return {"items": [_dump(s) for s in db.query(AnalysisStep).filter_by(project_id=pid).order_by(AnalysisStep.order).all()]}


@router.post("/{pid}/contributions")
def add_contribution(pid: str, payload: dict):
    return _create(_s(), Contribution, pid, payload)


@router.post("/{pid}/citations")
def add_citation(pid: str, payload: dict):
    return _create(_s(), Citation, pid, payload)


@router.delete("/{pid}/citations/{cid}")
def del_citation(pid: str, cid: str):
    db = _s()
    o = db.get(Citation, cid)
    if not o or o.project_id != pid:
        raise HTTPException(404, "Citation not found")
    db.delete(o)
    db.commit()
    return {"removed": cid}


@pub.post("/submissions")
def submit(payload: dict):
    from .store import Submission
    db = _s()
    url = (payload.get("url") or "").strip()
    if not (url.startswith("https://") or url.startswith("http://")):
        raise HTTPException(400, "Provide an http(s) dataset URL")
    s = Submission(url=url, title=payload.get("title", "")[:500],
                   publisher=payload.get("publisher", "")[:300], status="pending")
    db.add(s)
    db.commit()
    db.refresh(s)
    return _dump(s)
