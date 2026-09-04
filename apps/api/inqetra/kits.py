"""Research Kits: browse, detail, instantiate a full project graph (spec 12).

Instantiating creates questions, aims, methods and dataset requirements —
never just a basket — plus rationale notes linking them.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .store import (Aim, DatasetRequirement, Method, Note, Project,
                    ResearchKit, ResearchQuestion, session)

router = APIRouter(prefix="/api/v1/kits", tags=["kits"])


def _dump(o) -> dict:
    out = {}
    for c in o.__table__.columns:
        v = getattr(o, c.name)
        out[c.name] = v.isoformat() if hasattr(v, "isoformat") else v
    return out


def _all() -> list[dict]:
    db = session()
    return [_dump(k) for k in db.query(ResearchKit).order_by(ResearchKit.title).all()]


@router.get("")
def list_kits():
    return {"items": [{"slug": k["slug"], "title": k["title"], "version": k["version"],
                       **k["graph"]} for k in _all()]}


@router.get("/{slug}")
def kit_detail(slug: str):
    for k in _all():
        if k["slug"] == slug:
            return {"slug": k["slug"], "title": k["title"], "version": k["version"], **k["graph"]}
    raise HTTPException(404, "Kit not found")


@router.post("")
def create_custom_kit(payload: dict):
    """Create a custom kit (e.g. customised from a built-in one). graph.custom marks provenance."""
    db = session()
    base_slug = str(payload.get("slug") or payload.get("title") or "my-kit").strip().lower()
    import re as _re
    slug = _re.sub(r"[^a-z0-9]+", "-", base_slug).strip("-")[:110] or "my-kit"
    if db.query(ResearchKit).filter_by(slug=slug).first():
        i = 2
        while db.query(ResearchKit).filter_by(slug=f"{slug}-{i}").first():
            i += 1
        slug = f"{slug}-{i}"
    graph = payload.get("graph") or {}
    graph = {**graph, "custom": True}
    k = ResearchKit(slug=slug, title=str(payload.get("title") or "My kit")[:300],
                    version=str(payload.get("version") or "1.0"), graph=graph)
    db.add(k)
    db.commit()
    db.refresh(k)
    return _dump(k)


@router.delete("/{slug}")
def delete_custom_kit(slug: str):
    """Only custom kits can be deleted — built-in seeds stay."""
    db = session()
    k = db.query(ResearchKit).filter_by(slug=slug).first()
    if not k:
        raise HTTPException(404, "Kit not found")
    if not (k.graph or {}).get("custom"):
        raise HTTPException(400, "Built-in kits cannot be deleted")
    db.delete(k)
    db.commit()
    return {"removed": slug}


@router.post("/{slug}/instantiate")
def instantiate(slug: str, payload: dict | None = None):
    payload = payload or {}
    kit = kit_detail(slug)
    db = session()
    p = Project(title=payload.get("title") or f"{kit['title']} — project",
                geography=payload.get("geography", "United Kingdom"),
                domain=", ".join((kit.get("recommended_domains") or [])[:3]))
    db.add(p)
    db.flush()
    for i, q in enumerate(kit.get("questions", [])):
        db.add(ResearchQuestion(project_id=p.id, order=i, text=q, status="draft"))
    aim_ids: list[str] = []
    for i, a in enumerate(kit.get("aims", [])):
        o = Aim(project_id=p.id, order=i, title=a if isinstance(a, str) else a.get("title", ""),
                statement=a if isinstance(a, str) else a.get("statement", ""), status="draft")
        db.add(o)
        db.flush()
        aim_ids.append(o.id)
    method_ids: list[str] = []
    for m in kit.get("methods", []):
        o = Method(project_id=p.id, name=m, purpose=f"Suggested by kit '{kit['slug']}'")
        db.add(o)
        db.flush()
        method_ids.append(o.id)
    for role in kit.get("required_roles", []):
        db.add(DatasetRequirement(project_id=p.id, title=f"{role} — evidence requirement",
                                  research_role=role, requirement_level="required",
                                  geography=p.geography, linked_aim_ids=aim_ids,
                                  linked_method_ids=method_ids))
    db.add(Note(project_id=p.id, note_type="General", title="Kit provenance",
                body=f"Graph instantiated from research kit '{kit['slug']}' v{kit['version']}. "
                     "Dataset records themselves were NOT copied — discover and assign catalogue datasets next."))
    db.commit()
    return {"project_id": p.id, "kit": slug,
            "created": {"questions": len(kit.get("questions", [])), "aims": len(kit.get("aims", [])),
                        "methods": len(kit.get("methods", [])), "requirements": len(kit.get("required_roles", []))}}
