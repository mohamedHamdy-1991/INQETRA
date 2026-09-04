"""First-run defaults: compatibility rules, licences, sources, kits (D-06, specs 06/09/12)."""
from __future__ import annotations

import json

from .seed import REPO_ROOT
from .store import CompatRule, Licence, ResearchKit, Source, session

RULES = [
    ("geography", "Block only when no overlap.", "fail"),
    ("time", "Warn/fail on no overlap.", "warn"),
    ("granularity", "Warn on large mismatch.", "warn"),
    ("identifiers", "Recommend spatial join if absent.", "warn"),
    ("units", "Warn where variable metadata exists.", "warn"),
    ("format", "Informational.", "warn"),
    ("access", "Warn before export.", "warn"),
    ("licence", "High-priority warning.", "warn"),
    ("freshness", "Warn on staleness.", "warn"),
]

LICENCES = [
    ("OGL-3.0", "Open Government Licence v3.0", "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/", "OGL"),
    ("OGL", "Open Government Licence", "https://www.nationalarchives.gov.uk/doc/open-government-licence/", "OGL"),
    ("PUBLISHER", "Licence stated by publisher", "", "Source-declared"),
    ("PRODUCT", "Product-specific / collection terms", "", "Source-declared"),
    ("UNKNOWN", "Unknown — read the source before reuse", "", "Unknown"),
]


def ensure_defaults() -> dict:
    db = session()
    out = {"rules": 0, "licences": 0, "sources": 0, "kits": 0}
    if db.query(CompatRule).count() == 0:
        for rule, desc, sev in RULES:
            db.add(CompatRule(rule=rule, description=desc, severity=sev, active=True))
        out["rules"] = len(RULES)
    if db.query(Licence).count() == 0:
        for code, name, url, fam in LICENCES:
            db.add(Licence(code=code, name=name, url=url, family=fam))
        out["licences"] = len(LICENCES)
    if db.query(Source).count() == 0:
        try:
            reg = json.loads((REPO_ROOT / "INQETRA_AI_BUILD_PACK" / "data" / "source_registry.json").read_text(encoding="utf-8"))
        except OSError:
            reg = []
        for r in reg:
            db.add(Source(name=r.get("source", ""), base_url=r.get("homepage", ""),
                          source_type="catalogue", adapter=r.get("adapter", ""),
                          trust_level=r.get("trust", "Tier C"), active=True,
                          cadence=r.get("cadence", ""), terms_notes=r.get("notes", "")))
        out["sources"] = len(reg)
    if db.query(ResearchKit).count() == 0:
        try:
            kits = json.loads((REPO_ROOT / "INQETRA_AI_BUILD_PACK" / "data" / "research_kits.json").read_text(encoding="utf-8"))
        except OSError:
            kits = []
        for k in kits:
            db.add(ResearchKit(slug=k.get("slug", ""), title=k.get("title", ""), version="1.0", graph=k))
        out["kits"] = len(kits)
    db.commit()
    return out
