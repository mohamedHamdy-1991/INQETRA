"""Project + studio CRUD: problem/gap, questions, aims/objectives, hypotheses,
methods, requirements, basket, matrices, notes, results."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from . import catalogue as cat
from .store import (Aim, AnalysisStep, Candidate, Citation, Concept,
                    ConceptRelationship, Contribution, DatasetRequirement, Hypothesis,
                    KnowledgeGap, MatrixLink, Method, Methodology, Note, Objective,
                    Project, ProjectDataset, ResearchQuestion, Result,
                    Transformation, VariableRequirement, session)

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


def _s():
    return session()


def _get(db, project_id: str) -> Project:
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "Project not found")
    return p


def _dump(o) -> dict:
    return {c.name: getattr(o, c.name) for c in o.__table__.columns}


@router.post("")
def create_project(payload: dict):
    db = _s()
    p = Project(title=payload.get("title", "Untitled project")[:300],
                geography=payload.get("geography", ""),
                start_date=payload.get("start_date", ""), end_date=payload.get("end_date", ""),
                domain=payload.get("domain", ""), problem=payload.get("problem", ""),
                gap=payload.get("gap", ""), background=payload.get("background", ""))
    db.add(p)
    db.commit()
    return _dump(p)


@router.get("")
def list_projects():
    db = _s()
    items = db.query(Project).order_by(Project.created_at.desc()).all()
    out = []
    for p in items:
        d = _dump(p)
        d["counts"] = {"questions": db.query(ResearchQuestion).filter_by(project_id=p.id).count(),
                       "aims": db.query(Aim).filter_by(project_id=p.id).count(),
                       "datasets": db.query(ProjectDataset).filter_by(project_id=p.id).count()}
        out.append(d)
    return {"items": out}


@router.get("/{pid}")
def get_project(pid: str):
    db = _s()
    p = _get(db, pid)
    d = _dump(p)
    d["questions"] = [_dump(x) for x in db.query(ResearchQuestion).filter_by(project_id=pid).order_by(ResearchQuestion.order).all()]
    d["aims"] = [_dump(x) for x in db.query(Aim).filter_by(project_id=pid).order_by(Aim.order).all()]
    d["methods"] = [_dump(x) for x in db.query(Method).filter_by(project_id=pid).all()]
    d["requirements"] = [_dump(x) for x in db.query(DatasetRequirement).filter_by(project_id=pid).all()]
    d["basket"] = [_dump(x) for x in db.query(ProjectDataset).filter_by(project_id=pid).all()]
    d["notes"] = [_dump(x) for x in db.query(Note).filter_by(project_id=pid).all()]
    d["results"] = [_dump(x) for x in db.query(Result).filter_by(project_id=pid).all()]
    d["hypotheses"] = [_dump(x) for x in db.query(Hypothesis).filter_by(project_id=pid).all()]
    d["matrices"] = [_dump(x) for x in db.query(MatrixLink).filter_by(project_id=pid).all()]
    d["candidates"] = [_dump(x) for x in db.query(Candidate).filter_by(project_id=pid).all()]
    d["kgaps"] = [_dump(x) for x in db.query(KnowledgeGap).filter_by(project_id=pid).all()]
    d["concepts"] = [_dump(x) for x in db.query(Concept).filter_by(project_id=pid).all()]
    d["edges"] = [_dump(x) for x in db.query(ConceptRelationship).filter_by(project_id=pid).all()]
    meth = db.query(Methodology).filter_by(project_id=pid).first()
    d["methodology"] = _dump(meth) if meth else None
    d["transformations"] = [_dump(x) for x in db.query(Transformation).filter_by(project_id=pid).all()]
    d["steps"] = [_dump(x) for x in db.query(AnalysisStep).filter_by(project_id=pid).order_by(AnalysisStep.order).all()]
    d["contributions"] = [_dump(x) for x in db.query(Contribution).filter_by(project_id=pid).all()]
    d["citations"] = [_dump(x) for x in db.query(Citation).filter_by(project_id=pid).all()]
    d["readiness"] = readiness(db, pid)
    return d


@router.patch("/{pid}")
def patch_project(pid: str, payload: dict):
    db = _s()
    p = _get(db, pid)
    for k in ("title", "geography", "start_date", "end_date", "domain", "problem", "gap", "background", "status", "export_path"):
        if k in payload:
            setattr(p, k, payload[k])
    db.commit()
    return _dump(p)


def readiness(db, pid: str) -> dict:
    """Component coverage only — never a scientific-quality score."""
    dims = {
        "questions": db.query(ResearchQuestion).filter_by(project_id=pid).count() > 0,
        "aims": db.query(Aim).filter_by(project_id=pid).count() > 0,
        "methods": db.query(Method).filter_by(project_id=pid).count() > 0,
        "requirements": db.query(DatasetRequirement).filter_by(project_id=pid).count() > 0,
        "basket": db.query(ProjectDataset).filter_by(project_id=pid).count() > 0,
        "notes": db.query(Note).filter_by(project_id=pid).count() > 0,
        "results": db.query(Result).filter_by(project_id=pid).count() > 0,
        "methodology": db.query(Methodology).filter_by(project_id=pid).count() > 0,
        "analysis": db.query(AnalysisStep).filter_by(project_id=pid).count() > 0,
    }
    return {"dimensions": dims, "complete": sum(1 for v in dims.values() if v),
            "of": len(dims), "note": "Coverage of components, not scientific quality."}


# ---- generic sub-resource helpers ----

def _create(db, cls, pid: str, payload: dict, extra: dict | None = None):
    obj = cls(project_id=pid, **{k: v for k, v in (extra or {}).items()})
    for k, v in payload.items():
        if hasattr(obj, k) and k not in ("id", "project_id", "created_at"):
            setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _dump(obj)


@router.post("/{pid}/questions")
def add_question(pid: str, payload: dict):
    db = _s()
    _get(db, pid)
    n = db.query(ResearchQuestion).filter_by(project_id=pid).count()
    return _create(db, ResearchQuestion, pid, payload, {"order": n})


@router.patch("/{pid}/questions/{qid}")
def patch_question(pid: str, qid: str, payload: dict):
    db = _s()
    o = db.get(ResearchQuestion, qid)
    if not o or o.project_id != pid:
        raise HTTPException(404, "Question not found")
    for k, v in payload.items():
        if hasattr(o, k) and k not in ("id", "project_id"):
            setattr(o, k, v)
    db.commit()
    return _dump(o)


@router.post("/{pid}/aims")
def add_aim(pid: str, payload: dict):
    db = _s()
    _get(db, pid)
    n = db.query(Aim).filter_by(project_id=pid).count()
    return _create(db, Aim, pid, payload, {"order": n})


@router.post("/{pid}/aims/{aid}/objectives")
def add_objective(pid: str, aid: str, payload: dict):
    db = _s()
    a = db.get(Aim, aid)
    if not a or a.project_id != pid:
        raise HTTPException(404, "Aim not found")
    o = Objective(project_id=pid, aim_id=aid, text=payload.get("text", ""), status=payload.get("status", "draft"))
    db.add(o)
    db.commit()
    db.refresh(o)
    return _dump(o)


@router.get("/{pid}/objectives")
def list_objectives(pid: str):
    db = _s()
    aims = db.query(Aim).filter_by(project_id=pid).all()
    ids = [a.id for a in aims]
    items = db.query(Objective).filter(Objective.aim_id.in_(ids)).all() if ids else []
    return {"items": [_dump(o) for o in items]}


@router.post("/{pid}/hypotheses")
def add_hypothesis(pid: str, payload: dict):
    db = _s()
    _get(db, pid)
    return _create(db, Hypothesis, pid, payload)


@router.post("/{pid}/methods")
def add_method(pid: str, payload: dict):
    db = _s()
    _get(db, pid)
    return _create(db, Method, pid, payload)


@router.post("/{pid}/requirements")
def add_requirement(pid: str, payload: dict):
    db = _s()
    _get(db, pid)
    return _create(db, DatasetRequirement, pid, payload)


@router.post("/{pid}/requirements/{rid}/match")
def match_requirement(pid: str, rid: str):
    """Explainable candidate ranking for one requirement (no 'best dataset' language)."""
    from .compat import evaluate
    db = _s()
    req = db.get(DatasetRequirement, rid)
    if not req or req.project_id != pid:
        raise HTTPException(404, "Requirement not found")
    rdict = _dump(req)
    scored = []
    for ds in cat._project_subset():
        ev = evaluate(rdict, ds)
        score = sum(1 for c in ev["checks"] if c["status"] == "PASS") - 2 * sum(1 for c in ev["checks"] if c["status"] == "FAIL")
        scored.append({"dataset_id": ds["id"], "title": ds["title"], "publisher": ds["publisher"],
                       "search_relevance": score, "overall": ev["overall"], "evaluation": ev})
    scored.sort(key=lambda x: -x["search_relevance"])
    return {"requirement_id": rid, "candidates": scored[:20],
            "label": "Search relevance — not dataset quality."}


@router.post("/{pid}/basket")
def basket_add(pid: str, payload: dict):
    db = _s()
    _get(db, pid)
    dsid = payload.get("dataset_id", "")
    known = {r["id"]: r for r in cat._project_subset()}
    if dsid not in known:
        raise HTTPException(404, f"Unknown dataset {dsid}")
    ds = known[dsid]
    obj = ProjectDataset(project_id=pid, dataset_id=dsid, role=payload.get("role", ""),
                         rationale=payload.get("rationale", ""),
                         priority=payload.get("priority", "recommended"),
                         requirement_id=payload.get("requirement_id", ""),
                         provenance={"landing_url": ds["landing_url"],
                                     "verification_state": ds["verification_state"],
                                     "link_type": ds["link_type"], "publisher": ds["publisher"]})
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _dump(obj)


@router.delete("/{pid}/basket/{bid}")
def basket_remove(pid: str, bid: str):
    db = _s()
    o = db.get(ProjectDataset, bid)
    if not o or o.project_id != pid:
        raise HTTPException(404, "Basket item not found")
    db.delete(o)
    db.commit()
    return {"removed": bid}


@router.get("/{pid}/matrices/{kind}")
def get_matrix(pid: str, kind: str):
    if kind not in ("rq-aim", "aim-method", "aim-dataset"):
        raise HTTPException(400, "Unknown matrix")
    db = _s()
    items = db.query(MatrixLink).filter_by(project_id=pid, kind=kind).all()
    return {"kind": kind, "items": [_dump(x) for x in items]}


@router.post("/{pid}/matrices/{kind}")
def set_cell(pid: str, kind: str, payload: dict):
    if kind not in ("rq-aim", "aim-method", "aim-dataset"):
        raise HTTPException(400, "Unknown matrix")
    db = _s()
    _get(db, pid)
    cell = db.query(MatrixLink).filter_by(project_id=pid, kind=kind,
                                          row_id=payload.get("row_id", ""),
                                          col_id=payload.get("col_id", "")).first()
    if not cell:
        cell = MatrixLink(project_id=pid, kind=kind, row_id=payload.get("row_id", ""),
                          col_id=payload.get("col_id", ""))
        db.add(cell)
    cell.relationship_type = payload.get("relationship_type", cell.relationship_type or "Supporting")
    cell.rationale = payload.get("rationale", cell.rationale or "")
    cell.status = payload.get("status", cell.status or "active")
    cell.created_by = payload.get("created_by", "researcher")
    db.commit()
    db.refresh(cell)
    return _dump(cell)


@router.post("/{pid}/notes")
def add_note(pid: str, payload: dict):
    db = _s()
    _get(db, pid)
    return _create(db, Note, pid, payload)


@router.post("/{pid}/results")
def add_result(pid: str, payload: dict):
    """Results are entered by the researcher only — never generated."""
    db = _s()
    _get(db, pid)
    return _create(db, Result, pid, payload)
