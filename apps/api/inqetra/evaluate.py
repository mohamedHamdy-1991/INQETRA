"""Compatibility, gap radar, candidate search (find-data)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from . import catalogue as cat
from .compat import DISCLAIMER, evaluate
from .store import Aim, Candidate, DatasetRequirement, Method, ProjectDataset, session

router = APIRouter(prefix="/api/v1/projects", tags=["evaluation"])


def _dump(o) -> dict:
    return {c.name: getattr(o, c.name) for c in o.__table__.columns}


@router.post("/{pid}/evaluate")
def evaluate_project(pid: str, payload: dict | None = None):
    """Run compatibility for every basket item × linked requirement. Persists results."""
    from .compat import active_rules
    from .store import CompatResult, Project
    db = session()
    if not db.get(Project, pid):
        raise HTTPException(404, "Project not found")
    on = active_rules()
    reqs = [_dump(r) for r in db.query(DatasetRequirement).filter_by(project_id=pid).all()]
    basket = [_dump(b) for b in db.query(ProjectDataset).filter_by(project_id=pid).all()]
    known = {r["id"]: r for r in cat._project_subset()}
    out = []
    targets = [r for r in reqs if not payload or not payload.get("requirement_ids") or r["id"] in payload["requirement_ids"]]
    if not targets:
        targets = [{"id": None, "geography": "", "required_variables": [],
                    "desired_spatial_scale": "", "preferred_identifiers": [], "preferred_formats": []}]
    for b in basket:
        ds = known.get(b["dataset_id"])
        if not ds:
            continue
        for rq in targets:
            if b.get("requirement_id") and rq.get("id") and b["requirement_id"] != rq["id"]:
                continue
            ev = evaluate(rq, ds, on)
            out.append({"basket_id": b["id"], **ev})
            row = db.query(CompatResult).filter_by(project_id=pid, requirement_id=str(ev.get("requirement_id") or ""),
                                                   dataset_id=ev["dataset_id"] or "").first()
            if not row:
                row = CompatResult(project_id=pid, requirement_id=str(ev.get("requirement_id") or ""),
                                   dataset_id=ev["dataset_id"] or "")
                db.add(row)
            row.overall, row.detail = ev["overall"], ev
    db.commit()
    return {"evaluations": out, "disclaimer": DISCLAIMER}


@router.get("/{pid}/compatibility")
def compatibility(pid: str):
    return evaluate_project(pid, None)


@router.get("/{pid}/gaps")
def gaps(pid: str):
    """COVERED/PARTIAL/MISSING/INCOMPATIBLE/RESTRICTED/UNKNOWN per requirement."""
    db = session()
    reqs = db.query(DatasetRequirement).filter_by(project_id=pid).all()
    basket = db.query(ProjectDataset).filter_by(project_id=pid).all()
    known = {r["id"]: r for r in cat._project_subset()}
    evals = evaluate_project(pid, None)["evaluations"]
    by_req: dict[str, list[dict]] = {}
    for e in evals:
        by_req.setdefault(str(e.get("requirement_id")), []).append(e)
    items = []
    for r in reqs:
        linked = [b for b in basket if b.requirement_id == r.id] or basket
        evs = by_req.get(r.id, [])
        if not linked:
            status, why = "MISSING", "No basket dataset is assigned to this requirement yet. Use Find Data."
        else:
            worst = "COVERED"
            whys = []
            for e in evs:
                if e["overall"] == "FAIL":
                    worst = "INCOMPATIBLE"
                    whys.append(f"{e['dataset_id']}: mechanical incompatibility — see compatibility detail.")
                elif e["overall"] == "WARN" and worst not in ("INCOMPATIBLE",):
                    worst = "PARTIAL"
                    whys.append(f"{e['dataset_id']}: partial fit — see warnings.")
            restricted = [b.dataset_id for b in linked
                          if "subscription" in (known.get(b.dataset_id, {}).get("access_type", "").lower()
                                                + known.get(b.dataset_id, {}).get("licence", "").lower())]
            if restricted and worst == "COVERED":
                worst, whys = "RESTRICTED", [f"{i}: access/licence needs entitlement review." for i in restricted]
            if worst == "COVERED" and not evs:
                worst, whys = "UNKNOWN", ["Not yet evaluated."]
            status, why = worst, " ".join(whys) if whys else "Assigned datasets pass mechanical checks."
        items.append({"requirement_id": r.id, "requirement_title": r.title,
                      "status": status, "explanation": why,
                      "find_data": {"method": "POST", "href": f"/api/v1/projects/{pid}/requirements/{r.id}/find-data"}})
    aims = db.query(Aim).filter_by(project_id=pid).all()
    methods = db.query(Method).filter_by(project_id=pid).all()
    return {"requirements": items,
            "aims": [{"aim_id": a.id, "title": a.title,
                      "uncovered": [i["requirement_id"] for i in items if i["status"] != "COVERED"
                                    and (not r_linked(a.id, i["requirement_id"], db)) or False]} for a in aims],
            "methods_count": len(methods), "disclaimer": DISCLAIMER}


def r_linked(aim_id: str, req_id: str, db) -> bool:
    r = db.get(DatasetRequirement, req_id)
    return bool(r and aim_id in (r.linked_aim_ids or []))


@router.post("/{pid}/requirements/{rid}/find-data")
def find_data(pid: str, rid: str, payload: dict | None = None):
    """Internal catalogue first; external query staged to Candidate Inbox (never auto-published)."""
    from .projects import match_requirement
    internal = match_requirement(pid, rid)
    external_query = (payload or {}).get("external_query", "")
    staged = []
    if external_query:
        db = session()
        c = Candidate(project_id=pid, url="", source="researcher query (staged, unresolved)",
                      rationale=f"External search requested: {external_query}. Resolve to a concrete source URL before curation.",
                      requirement_id=rid, status="inbox", licence_state="Unknown")
        db.add(c)
        db.commit()
        db.refresh(c)
        staged.append(_dump(c))
    return {"internal_candidates": internal["candidates"][:10],
            "staged_external": staged,
            "note": "External results enter the Candidate Inbox and require resolution/validation before becoming catalogue records."}
