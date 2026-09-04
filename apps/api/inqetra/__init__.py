"""INQETRA FastAPI application."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import admin, ai, catalogue, evaluate, harvest, inbox, jobs, kits, paths, projects, reports, studio, thumbs
from .bootstrap import ensure_defaults
from .store import engine

engine()  # ensure tables exist
try:
    ensure_defaults()  # rules, licences, sources, kits
except Exception:  # noqa: BLE001 — API must serve even if defaults seeding hiccups
    pass

app = FastAPI(title="INQETRA API", version="0.2.0",
              description="UK research-design studio + dataset hub. Catalogue facts are source-declared; "
                          "landing-page reachability never implies licence or fitness.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

for r in (catalogue.router, projects.router, studio.router, studio.pub, evaluate.router,
          inbox.router, reports.router, jobs.router, ai.router, admin.router,
          harvest.router, kits.router, thumbs.router, paths.router):
    app.include_router(r)


@app.get("/api/v1/openapi.json")
def _openapi():
    return app.openapi()


@app.get("/healthz")
def healthz():
    return {"ok": True, "service": "inqetra-api"}
