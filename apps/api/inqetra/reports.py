"""Abstract drafts (evidence-traced, no fabricated results), report model, exports, citations."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from . import catalogue as cat
from .store import (AbstractDraft, Aim, Citation, DatasetRequirement, Method, Note,
                    Project, ProjectDataset, ResearchQuestion, Result, session)

router = APIRouter(prefix="/api/v1/projects", tags=["reports"])


def _dump(o) -> dict:
    out = {}
    for c in o.__table__.columns:
        v = getattr(o, c.name)
        out[c.name] = v.isoformat() if hasattr(v, "isoformat") else v
    return out


def _sent(text: str, source: str) -> dict:
    return {"text": text, "sources": [source]}


@router.post("/{pid}/abstract/draft")
def draft_abstract(pid: str, payload: dict):
    db = session()
    p = db.get(Project, pid)
    if not p:
        raise HTTPException(404, "Project not found")
    mode = payload.get("mode", "proposal")
    word_limit = int(payload.get("word_limit", 250))
    rqs = db.query(ResearchQuestion).filter_by(project_id=pid).all()
    aims = db.query(Aim).filter_by(project_id=pid).all()
    methods = db.query(Method).filter_by(project_id=pid).all()
    basket = db.query(ProjectDataset).filter_by(project_id=pid).all()
    results = db.query(Result).filter_by(project_id=pid).all()
    known = {r["id"]: r for r in cat._project_subset()}

    sentences, traces = [], []
    sentences.append(f"This {mode} addresses: {(rqs[0].text if rqs else p.problem or 'the stated research problem').strip()}")
    traces.append(_sent(sentences[-1], f"project:{pid}/problem" if not rqs else f"rq:{rqs[0].id}"))
    if aims:
        sentences.append("Aims: " + "; ".join(a.title for a in aims[:4]) + ".")
        traces.append(_sent(sentences[-1], "aims:" + ",".join(a.id for a in aims[:4])))
    if methods:
        sentences.append("Methods: " + "; ".join(m.name for m in methods[:4]) + ".")
        traces.append(_sent(sentences[-1], "methods:" + ",".join(m.id for m in methods[:4])))
    if basket:
        parts = []
        for b in basket[:5]:
            ds = known.get(b.dataset_id, {})
            parts.append(f"{ds.get('title', b.dataset_id)} ({b.dataset_id}, {ds.get('publisher', 'publisher unknown')})")
        sentences.append("Evidence base: " + "; ".join(parts) + ".")
        traces.append(_sent(sentences[-1], "basket:" + ",".join(b.dataset_id for b in basket[:5])))
    if results:
        sentences.append("Results: " + " ".join(r.body[:200] for r in results[:3]))
        traces.append(_sent(sentences[-1], "results:" + ",".join(r.id for r in results[:3])))
    else:
        # No fabrication: proposal/future tense or explicit unresolved marker.
        sentences.append("Results are not yet recorded; findings will be reported after analysis of the above evidence base.")
        traces.append(_sent(sentences[-1], "results:unresolved"))
    text = " ".join(sentences)
    words = text.split()
    if len(words) > word_limit:
        text = " ".join(words[:word_limit])
    d = AbstractDraft(project_id=pid, mode=mode, word_limit=word_limit, text=text,
                      traces=[{**t} for t in traces])
    db.add(d)
    db.commit()
    db.refresh(d)
    return {**_dump(d), "modes": ["proposal", "thesis", "journal", "conference", "grant", "extended", "plain"]}


@router.get("/{pid}/abstract/traces")
def abstract_traces(pid: str):
    db = session()
    items = db.query(AbstractDraft).filter_by(project_id=pid).order_by(AbstractDraft.created_at.desc()).all()
    return {"items": [_dump(x) for x in items]}


@router.get("/{pid}/report-model")
def report_model(pid: str):
    db = session()
    p = db.get(Project, pid)
    if not p:
        raise HTTPException(404, "Project not found")
    known = {r["id"]: r for r in cat._project_subset()}
    basket = db.query(ProjectDataset).filter_by(project_id=pid).all()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": _dump(p),
        "questions": [_dump(x) for x in db.query(ResearchQuestion).filter_by(project_id=pid).all()],
        "aims": [_dump(x) for x in db.query(Aim).filter_by(project_id=pid).all()],
        "methods": [_dump(x) for x in db.query(Method).filter_by(project_id=pid).all()],
        "requirements": [_dump(x) for x in db.query(DatasetRequirement).filter_by(project_id=pid).all()],
        "inventory": [{"basket": _dump(b), "dataset": known.get(b.dataset_id, {})} for b in basket],
        "notes": [_dump(x) for x in db.query(Note).filter_by(project_id=pid).all()],
        "results": [_dump(x) for x in db.query(Result).filter_by(project_id=pid).all()],
        "provenance": "Every dataset claim carries dataset ID + landing URL + verification_state. "
                      "Landing-page reachability does not prove licence or fitness.",
    }


@router.get("/{pid}/export", response_class=PlainTextResponse)
def export_plan(pid: str, format: str = "markdown"):
    from .evaluate import gaps
    model = report_model(pid)
    g = gaps(pid)
    if format == "json":
        import json as _j
        return PlainTextResponse(_j.dumps(model, indent=2, default=str), media_type="application/json")
    p = model["project"]
    lines = [f"# Research Data Plan — {p['title']}", "",
             f"Generated {model['generated_at']}. INQETRA export: dataset IDs, source URLs, versions/timestamps included.", "",
             "## Research problem", p.get("problem", "") or "_Not yet stated._", "",
             "## Knowledge gap", p.get("gap", "") or "_Not yet stated._", "",
             "## Research questions"]
    for q in model["questions"]:
        lines.append(f"- [{q['id']}] {q['text']}")
    lines += ["", "## Aims"]
    for a in model["aims"]:
        lines.append(f"- [{a['id']}] {a['title']}: {a['statement']}")
    lines += ["", "## Methods"]
    for m in model["methods"]:
        lines.append(f"- {m['name']}: {m['purpose']}")
    lines += ["", "## Dataset inventory (with provenance)"]
    for inv in model["inventory"]:
        ds = inv["dataset"]
        lines.append(f"- {ds.get('id')} — {ds.get('title')} | {ds.get('publisher')} | {ds.get('landing_url')} "
                     f"[{ds.get('link_type')}/{ds.get('verification_state')}, reviewed {ds.get('last_catalogue_review')}]")
    lines += ["", "## Data gaps"]
    for item in g["requirements"]:
        lines.append(f"- {item['requirement_title']}: {item['status']} — {item['explanation']}")
    lines += ["", "## Limitations", "Landing-page checks do not prove download access, licence permission or scientific fitness. "
              "Read each source licence and confirm coverage before analysis.", ""]
    return PlainTextResponse("\n".join(lines), media_type="text/markdown")


@router.get("/{pid}/citations")
def citations(pid: str, style: str = "harvard"):
    from datetime import date
    db = session()
    basket = db.query(ProjectDataset).filter_by(project_id=pid).all()
    known = {r["id"]: r for r in cat._project_subset()}
    items = []
    for b in basket:
        ds = known.get(b.dataset_id, {})
        pub, title = ds.get("publisher", "Publisher unknown"), ds.get("title", b.dataset_id)
        url, ver = ds.get("landing_url", ""), ds.get("last_catalogue_review", "n.d.")
        today = date.today().isoformat()
        key = b.dataset_id.replace("-", "")
        items.append({"dataset_id": b.dataset_id,
                      "harvard": f"{pub} ({ver}). {title}. Available at: {url} (Accessed: {today}).",
                      "apa": f"{pub}. ({ver}). {title}. Retrieved {today}, from {url}",
                      "bibtex": "@misc{" + key + ",\n  title={" + title + "},\n  author={" + pub + "},\n  year={" + ver[:4] + "},\n  howpublished={\\url{" + url + "}}\n}",
                      "ris": f"TY  - DATA\nAU  - {pub}\nTI  - {title}\nUR  - {url}\nY1  - {ver}\nER  - ",
                      "landing_url": url, "version": ver})
    for c in db.query(Citation).filter_by(project_id=pid, ctype="literature").all():
        key = (c.authors.split(",")[0] if c.authors else "anon").strip().replace(" ", "") + (c.year or "")
        items.append({"citation_id": c.id, "dataset_id": "",
                      "harvard": f"{c.authors} ({c.year}). {c.title}. Available at: {c.url} (Accessed: {today}).",
                      "apa": f"{c.authors} ({c.year}). {c.title}. {c.url}",
                      "bibtex": "@misc{" + key + ",\n  title={" + c.title + "},\n  author={" + c.authors + "},\n  year={" + c.year + "},\n  howpublished={\\url{" + c.url + "}}\n}",
                      "ris": f"TY  - GEN\nAU  - {c.authors}\nTI  - {c.title}\nUR  - {c.url}\nY1  - {c.year}\nER  - ",
                      "landing_url": c.url, "version": c.version})
    if style in ("bibtex", "ris"):
        joined = "\n\n".join(i[style] for i in items)
        return {"style": style, "items": items, "download": joined}
    return {"style": style, "items": items}
