"""Background-job endpoints with explicit failure states (D-12)."""
from __future__ import annotations

from fastapi import APIRouter

from .store import Job, session

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


def _dump(o) -> dict:
    return {c.name: getattr(o, c.name) for c in o.__table__.columns}


@router.post("/exports")
def start_export(payload: dict):
    db = session()
    simulate = (payload.get("simulate") or "")
    job = Job(kind="export", project_id=payload.get("project_id", ""),
              status="failed" if simulate == "fail" else "done",
              detail=("Simulated worker failure: downstream export store unavailable. "
                       "Catalogue remains available; retry the job." if simulate == "fail"
                       else "Export materialised."),
              payload=payload)
    db.add(job)
    db.commit()
    db.refresh(job)
    return _dump(job)


@router.get("/{jid}")
def job_status(jid: str):
    from fastapi import HTTPException
    db = session()
    j = db.get(Job, jid)
    if not j:
        raise HTTPException(404, "Job not found")
    return _dump(j)
