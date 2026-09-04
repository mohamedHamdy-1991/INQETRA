"""Document paths: thesis / grant / paper templates with sections, tools and
suggested working. Pure guidance — INQETRA never writes claims for the researcher;
phrasings are neutral sentence starters the researcher edits and owns.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/paths", tags=["paths"])

PATHS: dict[str, dict] = {
    "phd-thesis": {
        "slug": "phd-thesis",
        "title": "PhD Thesis",
        "tagline": "Full doctoral trajectory: from gap to defended contribution.",
        "audience": "Examiners and the doctoral community",
        "word_target": "70,000–90,000 words total",
        "sections": [
            {"heading": "Abstract", "words": "250–350", "guidance": "Problem, gap, method, headline finding, contribution.", "starters": ["This thesis investigates …", "Despite growing evidence, … remains poorly understood at the scale of …"]},
            {"heading": "Chapter 1 — Introduction", "words": "6,000–9,000", "guidance": "Context, problem statement, research questions, thesis outline.", "starters": ["The built environment is responsible for …", "This thesis asks three questions: first …"]},
            {"heading": "Chapter 2 — Literature Review", "words": "12,000–18,000", "guidance": "Thematic review ending in the identified gap (your Knowledge Gap object).", "starters": ["Scholarship on … has established …", "What these studies share is a reliance on …"]},
            {"heading": "Chapter 3 — Methodology", "words": "8,000–12,000", "guidance": "Design, data requirements, transformations, validation, ethics, limitations.", "starters": ["A mixed-methods design was adopted because …", "Dataset requirements were derived from the aims rather than availability …"]},
            {"heading": "Chapter 4 — Data", "words": "6,000–10,000", "guidance": "Every dataset in your basket: provenance, licence, transformations, joins.", "starters": ["The evidence base combines …", "Each source was assessed for coverage, licence and verification state …"]},
            {"heading": "Chapter 5 — Analysis & Results", "words": "12,000–16,000", "guidance": "Ordered analysis steps, outputs, sensitivity checks.", "starters": ["The analysis proceeded in three stages …", "Results are reported per aim to preserve traceability …"]},
            {"heading": "Chapter 6 — Discussion & Contribution", "words": "10,000–14,000", "guidance": "Interpretation against the gap; explicit contribution statement.", "starters": ["The findings extend current understanding by …", "The contribution is threefold …"]},
        ],
        "tools": ["requirements", "matrix", "gaps", "citations", "abstract", "transformations", "steps", "contributions"],
        "suggested_working": [
            "Keep every dataset claim tied to its basket entry — examiners check provenance.",
            "Write the contribution statement early and revise it after each results chapter.",
            "Use the gap radar before each supervisory meeting to show what remains uncovered.",
        ],
    },
    "masters-thesis": {
        "slug": "masters-thesis",
        "title": "Master's Thesis",
        "tagline": "Focused dissertation sized for an MSc/MRes cycle.",
        "audience": "Markers and programme accreditation",
        "word_target": "15,000–25,000 words total",
        "sections": [
            {"heading": "Abstract", "words": "200–300", "guidance": "One paragraph: problem, method, result, implication.", "starters": ["This dissertation examines …", "Using … data for …, the study finds …"]},
            {"heading": "Introduction", "words": "1,500–2,500", "guidance": "Context, aim, objectives, dissertation map.", "starters": ["Rising … has intensified interest in …", "The aim of this study is to …"]},
            {"heading": "Literature & Gap", "words": "3,000–5,000", "guidance": "Concise review; state the gap in one testable sentence.", "starters": ["Three strands of literature inform this study …", "However, existing work rarely …"]},
            {"heading": "Data & Methods", "words": "3,000–5,000", "guidance": "Datasets, joins, transformations, limitations.", "starters": ["The analysis draws on …", "Variables were harmonised to …"]},
            {"heading": "Results & Discussion", "words": "4,000–7,000", "guidance": "Findings per objective, then interpretation.", "starters": ["The results indicate …", "Consistent with …, the model shows …"]},
            {"heading": "Conclusion", "words": "800–1,500", "guidance": "Answer the questions, note limitations, next steps.", "starters": ["This dissertation set out to …", "Future work should …"]},
        ],
        "tools": ["requirements", "basket", "matrix", "gaps", "abstract", "citations"],
        "suggested_working": [
            "Scope ruthlessly: two or three research questions maximum.",
            "Record every transformation in the studio — markers reward auditability.",
            "State data limitations explicitly; it earns marks and pre-empts criticism.",
        ],
    },
    "research-grant": {
        "slug": "research-grant",
        "title": "Research Grant",
        "tagline": "Funding case: feasibility, impact, data management, value for money.",
        "audience": "Funding panel and reviewers",
        "word_target": "Case for support typically 8–12 pages",
        "sections": [
            {"heading": "Summary", "words": "150–300", "guidance": "Plain-English pitch: what, why, who benefits.", "starters": ["This project addresses …", "Our approach is novel because …"]},
            {"heading": "Track Record & Team", "words": "500–1,000", "guidance": "Prior work relevant to THIS call, not a full CV.", "starters": ["The team combines …", "Previous UKRI-funded work demonstrated …"]},
            {"heading": "Research Plan & Feasibility", "words": "2,000–3,500", "guidance": "Work packages, milestones, risk table. Your aims map to work packages.", "starters": ["The programme is organised in three work packages …", "WP1 establishes …; WP2 …"]},
            {"heading": "Data Management Plan", "words": "500–1,000", "guidance": "What data you will collect, storage, licensing, sharing, preservation.", "starters": ["All datasets will be deposited under …", "Access conditions follow the source licences recorded in our data plan …"]},
            {"heading": "Impact & Dissemination", "words": "500–1,000", "guidance": "Beneficiaries, pathways to impact, publication plan.", "starters": ["Findings will reach …", "We will engage … throughout, not only at the end."]},
            {"heading": "Justification of Resources", "words": "300–800", "guidance": "Why the budget: data costs, access entitlements, compute.", "starters": ["Resources are requested for …", "Access to … requires entitlement because …"]},
        ],
        "tools": ["requirements", "gaps", "acquisition-plan", "steps", "abstract", "transformations"],
        "suggested_working": [
            "Funders fund feasibility: show the data exists and you are entitled to use it.",
            "Tie each work package to an aim and each aim to at least one dataset requirement.",
            "Name the licence status of key datasets — panels notice hand-waving.",
        ],
    },
    "journal-article": {
        "slug": "journal-article",
        "title": "Journal Article",
        "tagline": "Peer-reviewed paper: contribution-first, methods reproducible.",
        "audience": "Editors and two or more reviewers",
        "word_target": "6,000–9,000 words (check the journal)",
        "sections": [
            {"heading": "Title & Abstract", "words": "150–250", "guidance": "Contribution in the first sentence; no filler.", "starters": ["We show that …", "… is strongly associated with …"]},
            {"heading": "Introduction", "words": "800–1,500", "guidance": "Gap, contribution, findings preview.", "starters": ["A persistent barrier to … is …", "This article makes two contributions …"]},
            {"heading": "Data & Methods", "words": "1,500–2,500", "guidance": "Reproducibility: sources, versions, transformations, robustness.", "starters": ["We combine … with …", "All processing steps are documented and repeatable …"]},
            {"heading": "Results", "words": "1,500–2,500", "guidance": "Findings ordered by research question; no discussion yet.", "starters": ["Table 2 reports …", "The strongest effect is …"]},
            {"heading": "Discussion & Conclusion", "words": "1,000–2,000", "guidance": "Mechanisms, limitations, implications, future work.", "starters": ["Three mechanisms could explain …", "A limitation of our design is …"]},
        ],
        "tools": ["abstract", "citations", "matrix", "gaps", "transformations", "results"],
        "suggested_working": [
            "Write Results before the Introduction — claims stay anchored to evidence.",
            "Every figure must answer one research question; cut the rest.",
            "Reviewer 2 reads the methods section first: make it reproducible.",
        ],
    },
    "conference-paper": {
        "slug": "conference-paper",
        "title": "Conference Paper",
        "tagline": "Short-format paper for a conference deadline.",
        "audience": "Session audience and program committee",
        "word_target": "4–12 pages (venue template)",
        "sections": [
            {"heading": "Abstract", "words": "120–200", "guidance": "Problem, approach, one headline result.", "starters": ["We present …", "This work demonstrates …"]},
            {"heading": "Introduction & Related Work", "words": "800–1,500", "guidance": "Compressed gap + contribution.", "starters": ["Recent work on … has focused on …", "In contrast, we …"]},
            {"heading": "Method", "words": "800–1,500", "guidance": "Design + data in the tightest defensible form.", "starters": ["Our pipeline uses …", "Data requirements were …"]},
            {"heading": "Findings & Conclusion", "words": "800–1,500", "guidance": "The one thing the audience should remember.", "starters": ["Across …, we find …", "We conclude that …"]},
        ],
        "tools": ["abstract", "basket", "gaps", "steps"],
        "suggested_working": [
            "Deadlines beat perfection: draft the abstract on day one, revise daily.",
            "One message per paper; move everything else to the extended version.",
            "Rehearse the 3-minute version — it exposes weak logic fast.",
        ],
    },
}


@router.get("")
def list_paths():
    return {"items": [{k: p[k] for k in ("slug", "title", "tagline", "audience", "word_target")} | {"sections": len(p["sections"])} for p in PATHS.values()]}


@router.get("/{slug}")
def get_path(slug: str):
    p = PATHS.get(slug)
    if not p:
        raise HTTPException(404, "Unknown path")
    return p
