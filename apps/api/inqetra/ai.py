"""Provider-neutral AI gateway with the 14-tool contract (spec 11).

Every tool executes deterministic project/catalogue logic. Dataset claims always
carry dataset_id + field + source provenance. The LLM layer (optional) only
structures or drafts from tool outputs — it can never invent sources.
"""
from __future__ import annotations

import os

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

TOOL_NAMES = ["search_datasets", "get_dataset", "search_variables", "compare_datasets",
              "get_project", "get_rq_alignment", "get_aim_coverage", "find_data_gaps",
              "search_external_sources", "explain_compatibility", "generate_acquisition_plan",
              "draft_methods", "draft_abstract", "trace_statement"]

SYSTEM = ("You assist INQETRA research design. Use only the supplied tool outputs. "
          "Never invent datasets, licences, coverage, results, methods or citations. "
          "Every dataset claim must cite dataset_id + field + source URL. "
          "If results are absent, use proposal/future tense.")


def _cat():
    from . import catalogue as cat
    return cat


def t_search_datasets(q: str = "", domain: str = "", limit: int = 5):
    r = _cat().list_datasets(q=q, domain=domain, limit=min(limit, 10), offset=0)
    return {"label": "Search relevance — not dataset quality.",
            "items": [{k: i[k] for k in ("id", "title", "publisher", "landing_url",
                                        "link_type", "verification_state", "licence", "access_type")}
                       | {"provenance": {"dataset_id": i["id"], "source": i["landing_url"]}}
                       for i in r["items"]]}


def t_get_dataset(dataset_id: str):
    d = _cat().get_dataset(dataset_id)
    i = d["item"]
    return {"dataset_id": i["id"], "title": i["title"], "publisher": i["publisher"],
            "landing_url": {"value": i["landing_url"], "provenance": "seed.landing_url"},
            "licence": {"value": i["licence"], "provenance": "seed.licence (source-declared or Unknown)"},
            "access_type": i["access_type"], "link_type": i["link_type"],
            "verification_state": i["verification_state"]}


def t_search_variables(q: str):
    out = []
    for r in _cat()._project_subset():
        if q.lower() in (r["variables"] or "").lower():
            out.append({"dataset_id": r["id"], "title": r["title"],
                        "field": "variables", "source": r["landing_url"]})
            if len(out) >= 20:
                break
    return {"items": out, "note": "Seed variable metadata is sparse; confirm fields on landing pages."}


def t_compare_datasets(ids: list[str]):
    return _cat().compare({"ids": ids})


def t_get_project(project_id: str):
    from .projects import get_project
    p = get_project(project_id)
    p.pop("basket", None)
    return p


def t_get_rq_alignment(project_id: str):
    from .store import Aim, MatrixLink, ResearchQuestion, session
    db = session()
    rqs = db.query(ResearchQuestion).filter_by(project_id=project_id).all()
    aims = db.query(Aim).filter_by(project_id=project_id).all()
    links = db.query(MatrixLink).filter_by(project_id=project_id, kind="rq-aim").all()
    linked_rqs = {x.row_id for x in links}
    linked_aims = {x.col_id for x in links}
    return {"rq_count": len(rqs), "aim_count": len(aims),
            "unlinked_rqs": [r.id for r in rqs if r.id not in linked_rqs],
            "unlinked_aims": [a.id for a in aims if a.id not in linked_aims],
            "links": len(links)}


def t_get_aim_coverage(project_id: str):
    from .evaluate import gaps
    g = gaps(project_id)
    return g


def t_find_data_gaps(project_id: str):
    return t_get_aim_coverage(project_id)


def t_search_external_sources(query: str):
    from .harvest import PORTAL_SEARCH
    from urllib.parse import quote_plus
    return {"leads": [{"portal": h, "search_url": t.format(q=quote_plus(query), slug="", h=h)}
                      for h, t in PORTAL_SEARCH.items()],
            "note": "Leads only. Discoveries enter the Candidate Inbox for resolution/validation."}


def t_explain_compatibility(requirement: dict, dataset_id: str):
    from .compat import evaluate
    ds = next((r for r in _cat()._project_subset() if r["id"] == dataset_id), None)
    if not ds:
        raise HTTPException(404, "Unknown dataset")
    return evaluate(requirement, ds)


def t_generate_acquisition_plan(project_id: str):
    from .store import ProjectDataset, session
    db = session()
    items = db.query(ProjectDataset).filter_by(project_id=project_id).all()
    known = {r["id"]: r for r in _cat()._project_subset()}
    steps = []
    for b in items:
        ds = known.get(b.dataset_id, {})
        access = ds.get("access_type", "")
        gated = any(k in access.lower() for k in ("subscription", "licensed", "registration", "commercial"))
        steps.append({"dataset_id": b.dataset_id, "title": ds.get("title", b.dataset_id),
                      "order": 2 if gated else 1,
                      "action": f"Request access first ({access})" if gated else "Fetch from landing page",
                      "licence": ds.get("licence", "Unknown"),
                      "provenance": {"dataset_id": b.dataset_id, "source": ds.get("landing_url", "")}})
    steps.sort(key=lambda s: s["order"])
    return {"steps": steps, "note": "Access-gated sources first (lead time); open sources in parallel."}


def t_draft_methods(project_id: str):
    from .store import AnalysisStep, Method, Methodology, session
    db = session()
    m = db.query(Methodology).filter_by(project_id=project_id).first()
    return {"design": m.design if m else "",
            "methods": [{"name": x.name, "purpose": x.purpose}
                        for x in db.query(Method).filter_by(project_id=project_id).all()],
            "steps": [x.description for x in db.query(AnalysisStep).filter_by(project_id=project_id).order_by(AnalysisStep.order).all()],
            "note": "Structured from project facts only."}


def t_draft_abstract(project_id: str, mode: str = "proposal", word_limit: int = 250):
    from .reports import draft_abstract
    return draft_abstract(project_id, {"mode": mode, "word_limit": word_limit})


def t_trace_statement(project_id: str, sentence: str):
    from .store import AbstractDraft, session
    db = session()
    out = []
    for d in db.query(AbstractDraft).filter_by(project_id=project_id).all():
        for t in (d.traces or []):
            if sentence.lower() in (t.get("text") or "").lower():
                out.append(t)
    return {"matches": out}


TOOLS = {"search_datasets": t_search_datasets, "get_dataset": t_get_dataset,
         "search_variables": t_search_variables, "compare_datasets": t_compare_datasets,
         "get_project": t_get_project, "get_rq_alignment": t_get_rq_alignment,
         "get_aim_coverage": t_get_aim_coverage, "find_data_gaps": t_find_data_gaps,
         "search_external_sources": t_search_external_sources,
         "explain_compatibility": t_explain_compatibility,
         "generate_acquisition_plan": t_generate_acquisition_plan,
         "draft_methods": t_draft_methods, "draft_abstract": t_draft_abstract,
         "trace_statement": t_trace_statement}


@router.get("/status")
def status():
    provider = os.getenv("INQETRA_AI_PROVIDER", "")
    return {"enabled": bool(provider and os.getenv("INQETRA_AI_API_KEY", "")),
            "provider": provider or "none", "tools": TOOL_NAMES,
            "note": "INQETRA is fully usable without AI. AI structures/drafts from tool outputs only."}


@router.get("/tools")
def tools():
    return {"tools": TOOL_NAMES}


@router.post("/tools/{name}")
def run_tool(name: str, payload: dict | None = None):
    fn = TOOLS.get(name)
    if not fn:
        raise HTTPException(404, f"Unknown tool {name}")
    return fn(**(payload or {}))


@router.post("/draft")
def draft(payload: dict):
    facts = (payload.get("facts") or [])[:10]
    if not os.getenv("INQETRA_AI_PROVIDER"):
        return {"enabled": False,
                "text": "AI is disabled. Deterministic tools remain available at /api/v1/ai/tools/*.",
                "provenance": []}
    return {"enabled": True, "text": "Draft from supplied facts: " + " ".join(map(str, facts)),
            "provenance": [{"fact": f} for f in facts]}


@router.post("/chat")
def chat(payload: dict):
    """Keyword-routed deterministic answer; optional LLM structuring on top."""
    message = (payload.get("message") or "")
    pid = payload.get("project_id", "")
    ml = message.lower()
    tool, result = "get_project", None
    try:
        if "gap" in ml and pid:
            tool, result = "find_data_gaps", t_find_data_gaps(pid)
        elif "compat" in ml or "fit" in ml:
            from .evaluate import compatibility
            tool, result = "compatibility", compatibility(pid) if pid else {"detail": "pass project_id"}
        elif "acquis" in ml or "download" in ml or "access" in ml:
            tool, result = "generate_acquisition_plan", t_generate_acquisition_plan(pid) if pid else {"detail": "pass project_id"}
        elif "method" in ml:
            tool, result = "draft_methods", t_draft_methods(pid) if pid else {"detail": "pass project_id"}
        elif "abstract" in ml:
            tool, result = "draft_abstract", t_draft_abstract(pid) if pid else {"detail": "pass project_id"}
        elif "search" in ml or "find data" in ml or "dataset" in ml:
            import re
            q = re.sub(r"(search|find|dataset|data|for|me|the|a|about)", "", ml).strip()[:80]
            tool, result = "search_datasets", t_search_datasets(q or message[:80])
    except HTTPException as e:
        return {"tool": tool, "error": e.detail}
    base = {"tool": tool, "result": result, "system": SYSTEM}
    if os.getenv("INQETRA_AI_PROVIDER") and os.getenv("INQETRA_AI_API_KEY"):
        try:
            r = httpx.post(os.getenv("INQETRA_AI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions",
                           headers={"Authorization": f"Bearer {os.getenv('INQETRA_AI_API_KEY')}"},
                           json={"model": os.getenv("INQETRA_AI_MODEL", "gpt-4o-mini"),
                                 "messages": [{"role": "system", "content": SYSTEM},
                                              {"role": "user", "content": message + "\n\nTOOL OUTPUT (only facts allowed): " + str(result)[:6000]}],
                                 "max_tokens": 500}, timeout=30)
            base["assistant"] = r.json()["choices"][0]["message"]["content"]
        except Exception as e:  # noqa: BLE001 — degrade to deterministic output
            base["assistant_error"] = f"Provider failed; deterministic result stands: {str(e)[:160]}"
    return base
