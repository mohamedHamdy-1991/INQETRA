"""Admin: source registry view, on-demand link check (SSRF-guarded), audit log,
compatibility-rule editor with fixture tests, submissions moderation, kit editor."""
from __future__ import annotations

import ipaddress
import os
from urllib.parse import urlparse
from urllib.request import Request, build_opener

from fastapi import APIRouter, HTTPException

from . import catalogue as cat
from .store import AuditEvent, CompatRule, LinkCheck, ResearchKit, Submission, session

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

ADMIN_TOKEN = os.getenv("INQETRA_ADMIN_TOKEN", "")


def _guard(url: str):
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise HTTPException(400, "Only http(s) URLs with a hostname may be checked")
    try:
        # Block literal private IPs; DNS-rebinding defence stays at proxy in production.
        ip = ipaddress.ip_address(u.hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise HTTPException(400, "Private-network URLs are not allowed")
    except ValueError:
        pass  # hostname, not literal IP


@router.get("/audit")
def audit():
    db = session()
    items = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100).all()
    return {"items": [{c.name: getattr(o, c.name) for c in o.__table__.columns} for o in items]}


@router.post("/link-check")
def link_check(payload: dict):
    limit = min(int(payload.get("limit", 5)), 25)
    opener = build_opener()
    out = []
    db = session()
    for r in cat._project_subset()[:limit]:
        url = r["landing_url"]
        row = {"dataset_id": r["id"], "url": url}
        try:
            _guard(url)
            req = Request(url, headers={"User-Agent": "INQETRA-link-health/1.0"})
            with opener.open(req, timeout=10) as resp:
                row.update(final_url=resp.geturl(), http_status=str(resp.getcode()), reachable=True)
        except HTTPException as e:
            row.update(error=e.detail, reachable=False)
        except Exception as e:  # noqa: BLE001 — surfaced as evidence, not hidden
            row.update(error=str(e)[:200], reachable=False)
        out.append(row)
        db.add(LinkCheck(dataset_id=r["id"], url=url, final_url=row.get("final_url", ""),
                         http_status=row.get("http_status", ""), reachable=bool(row.get("reachable")),
                         error=row.get("error", "")))
    db.add(AuditEvent(actor="admin", action="link-check", entity="datasets",
                      entity_id=f"first-{limit}", detail=f"checked {len(out)}"))
    db.commit()
    return {"items": out, "note": "Reachability only; not a licence/fitness finding."}


def _dump(o) -> dict:
    out = {}
    for c in o.__table__.columns:
        v = getattr(o, c.name)
        out[c.name] = v.isoformat() if hasattr(v, "isoformat") else v
    return out


@router.get("/rules")
def list_rules():
    db = session()
    return {"items": [_dump(r) for r in db.query(CompatRule).order_by(CompatRule.rule).all()]}


@router.patch("/rules/{rule}")
def patch_rule(rule: str, payload: dict):
    db = session()
    r = db.query(CompatRule).filter_by(rule=rule).first()
    if not r:
        raise HTTPException(404, "Unknown rule")
    if "active" in payload:
        r.active = bool(payload["active"])
    if "severity" in payload:
        r.severity = payload["severity"]
    if "description" in payload:
        r.description = payload["description"]
    db.add(AuditEvent(actor="admin", action="rule-edit", entity="compatibility_rules",
                      entity_id=rule, detail=str(payload)[:300]))
    db.commit()
    return _dump(r)


@router.post("/rules/test")
def test_rules(payload: dict):
    """Fixture test: run two fixed fixtures through the engine with current rule flags."""
    from .compat import evaluate
    db = session()
    on = {r.rule for r in db.query(CompatRule).filter_by(active=True).all()}
    ds = next(iter(cat._project_subset()))
    req = {"id": "fixture", "geography": "Leeds, England", "start_date": "2020-01-01",
           "end_date": "2024-12-31", "desired_spatial_scale": "LSOA",
           "required_variables": ["temperature"], "preferred_identifiers": ["LSOA"],
           "preferred_formats": ["CSV"]}
    full = evaluate(req, ds)
    scoped = evaluate(req, ds, on)
    return {"active_rules": sorted(on), "full_overall": full["overall"],
            "scoped_overall": scoped["overall"], "skipped": scoped.get("skipped_rules", []),
            "checks": len(scoped["checks"])}


@router.get("/submissions")
def list_submissions(status: str = "pending"):
    db = session()
    q = db.query(Submission)
    if status != "all":
        q = q.filter_by(status=status)
    return {"items": [_dump(s) for s in q.order_by(Submission.created_at.desc()).limit(100).all()]}


@router.post("/submissions/{sid}/moderate")
def moderate(sid: str, payload: dict):
    db = session()
    s = db.get(Submission, sid)
    if not s:
        raise HTTPException(404, "Submission not found")
    decision = payload.get("decision", "rejected")
    if decision not in ("accepted", "rejected"):
        raise HTTPException(400, "decision must be accepted|rejected")
    s.status, s.moderator_notes = decision, payload.get("moderator_notes", "")
    db.add(AuditEvent(actor="admin", action="moderate-submission", entity="submissions",
                      entity_id=sid, detail=decision))
    db.commit()
    return {**_dump(s), "published_to_catalogue": False,
            "note": "Accepted submissions become staged candidates, never direct catalogue records."}


@router.get("/kits")
def admin_kits():
    db = session()
    return {"items": [_dump(k) for k in db.query(ResearchKit).order_by(ResearchKit.slug).all()]}


@router.patch("/kits/{slug}")
def patch_kit(slug: str, payload: dict):
    db = session()
    k = db.query(ResearchKit).filter_by(slug=slug).first()
    if not k:
        raise HTTPException(404, "Kit not found")
    if "graph" in payload:
        k.graph = payload["graph"]
    if "version" in payload:
        k.version = payload["version"]
    db.add(AuditEvent(actor="admin", action="kit-edit", entity="research_kits",
                      entity_id=slug, detail=f"version {k.version}"))
    db.commit()
    return _dump(k)
