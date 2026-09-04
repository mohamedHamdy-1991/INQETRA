"""Deterministic compatibility engine (D-06).

Nine rule families. Each check returns PASS/WARN/FAIL/UNKNOWN with a factual
explanation. Outputs NEVER claim scientific/methodological validity — every
payload carries the disclaimer constant.
"""
from __future__ import annotations

DISCLAIMER = ("Mechanical data-compatibility only. This does not assess scientific "
              "validity, fitness for a research question, or licence permission.")

UK_NATIONS = {"england", "scotland", "wales", "northern ireland", "uk", "great britain"}


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def check_geography(requirement: dict, dataset: dict) -> dict:
    req = _norm(requirement.get("geography", ""))
    cov = _norm(dataset.get("coverage", "")) + " " + _norm(dataset.get("uk_nation", ""))
    if not req:
        return {"rule": "geography", "status": "UNKNOWN",
                "explanation": "No project geography stated; cannot test overlap. Dataset covers: "
                               + (dataset.get("coverage", "not stated") or "not stated") + "."}
    if "uk" in req and ("uk" in cov or "england" in cov or "britain" in cov):
        return {"rule": "geography", "status": "PASS",
                "explanation": f"Project geography '{requirement['geography']}' overlaps dataset coverage '{dataset.get('coverage')}'."}
    for nation in ["england", "scotland", "wales", "northern ireland"]:
        if nation in req:
            if nation in cov or "uk" in cov or "britain" in cov or "england" in cov and nation == "england":
                return {"rule": "geography", "status": "PASS",
                        "explanation": f"Project nation '{nation}' is within dataset coverage '{dataset.get('coverage')}'."}
            return {"rule": "geography", "status": "FAIL",
                    "explanation": f"No geographic overlap: project needs '{nation}' but dataset covers '{dataset.get('coverage')}'."}
    return {"rule": "geography", "status": "WARN",
            "explanation": f"Could not confirm overlap between project geography '{requirement.get('geography')}' and dataset coverage '{dataset.get('coverage')}'. Check boundary manually."}


def check_time(requirement: dict, dataset: dict) -> dict:
    # Seed has no per-record dates; temporal_resolution/coverage text is all we have.
    res = _norm(dataset.get("temporal_resolution", ""))
    if not requirement.get("start_date") and not requirement.get("end_date"):
        return {"rule": "time", "status": "UNKNOWN",
                "explanation": "No project period stated; dataset temporal resolution is "
                               + (dataset.get("temporal_resolution") or "not stated") + ". State start/end dates to test overlap."}
    if res in ("varies", "", "static"):
        return {"rule": "time", "status": "WARN",
                "explanation": f"Dataset temporal resolution is '{dataset.get('temporal_resolution') or 'not stated'}'; confirm the project period "
                               + str(requirement.get("start_date", "")) + "–" + str(requirement.get("end_date", "")) + " against the source documentation."}
    return {"rule": "time", "status": "PASS",
            "explanation": f"Project period {requirement.get('start_date','?')}–{requirement.get('end_date','?')} can be tested against dataset resolution '{dataset.get('temporal_resolution')}'. Verify extent on the landing page."}


def check_granularity(requirement: dict, dataset: dict) -> dict:
    req = _norm(requirement.get("desired_spatial_scale", ""))
    ds = _norm(dataset.get("spatial_scale", ""))
    if not req:
        return {"rule": "granularity", "status": "UNKNOWN",
                "explanation": "No desired spatial scale stated; dataset unit is '" + (dataset.get("spatial_scale") or "not stated") + "'."}
    if req and req in ds or ds in req:
        return {"rule": "granularity", "status": "PASS",
                "explanation": f"Requested scale '{requirement['desired_spatial_scale']}' matches dataset unit '{dataset.get('spatial_scale')}'."}
    return {"rule": "granularity", "status": "WARN",
            "explanation": f"Requested scale '{requirement.get('desired_spatial_scale')}' differs from dataset unit '{dataset.get('spatial_scale')}'. Aggregation or apportionment may be needed; record the method."}


def check_identifiers(requirement: dict, dataset: dict) -> dict:
    want = [w for w in (requirement.get("preferred_identifiers") or []) if w] if isinstance(requirement.get("preferred_identifiers"), list) else []
    text = (_norm(dataset.get("notes", "")) + " " + _norm(dataset.get("subdomain", ""))).lower()
    joins = ["uprn", "usrn", "ons", "lsoa", "msoa", "oa ", "postcode", "toid", "os "]
    found = [j.strip() for j in joins if j.strip() in text]
    if not want:
        return {"rule": "identifiers", "status": "UNKNOWN" if not found else "PASS",
                "explanation": ("No preferred identifiers stated." + (f" Dataset mentions {', '.join(found)}; a spatial join may be possible." if found else " Check the source schema for join keys."))}
    for w in want:
        if _norm(str(w)) and _norm(str(w)) in text:
            return {"rule": "identifiers", "status": "PASS",
                    "explanation": f"Preferred identifier '{w}' is mentioned in dataset context. Confirm field name in source schema."}
    return {"rule": "identifiers", "status": "WARN",
            "explanation": f"No shared identifier found for {', '.join(map(str, want))}; a spatial join may be possible. Confirm in source schema."}


def check_units(requirement: dict, dataset: dict) -> dict:
    vars_needed = requirement.get("required_variables") or []
    ds_vars = _norm(dataset.get("variables", ""))
    if not vars_needed:
        return {"rule": "units", "status": "UNKNOWN", "explanation": "No required variables listed; units cannot be tested. List variables to enable this check."}
    if not ds_vars:
        return {"rule": "units", "status": "UNKNOWN",
                "explanation": "Seed record carries no variable/unit metadata; units must be checked on the landing page for: " + ", ".join(map(str, vars_needed)) + "."}
    return {"rule": "units", "status": "WARN",
            "explanation": "Variable-level units are not verified in seed metadata; confirm units for requested variables against source documentation."}


def check_format(requirement: dict, dataset: dict) -> dict:
    prefs = requirement.get("preferred_formats") or []
    have = _norm(dataset.get("formats", ""))
    if not prefs:
        return {"rule": "format", "status": "PASS" if have else "UNKNOWN",
                "explanation": "No preferred formats stated; dataset offers: " + (dataset.get("formats") or "not stated") + "."}
    for p in prefs:
        if _norm(str(p)) and _norm(str(p)) in have:
            return {"rule": "format", "status": "PASS", "explanation": f"Preferred format '{p}' is offered ({dataset.get('formats')})."}
    return {"rule": "format", "status": "WARN",
            "explanation": f"Preferred formats {prefs} not listed in dataset formats '{dataset.get('formats')}'. Conversion may be needed."}


def check_access(requirement: dict, dataset: dict) -> dict:
    a = _norm(dataset.get("access_type", ""))
    if "subscription" in a or "licensed" in a or "commercial" in a:
        return {"rule": "access", "status": "WARN",
                "explanation": f"Access is '{dataset.get('access_type')}' — entitlement, subscription or payment may be required before download."}
    if "registration" in a:
        return {"rule": "access", "status": "WARN", "explanation": "Registration is required for bulk/API access. Factor approval time into the acquisition plan."}
    if "open" in a:
        return {"rule": "access", "status": "PASS", "explanation": f"Access is '{dataset.get('access_type')}'. Public availability does not equal reuse permission — see licence check."}
    return {"rule": "access", "status": "UNKNOWN", "explanation": "Access terms are unclear; check the landing page before planning acquisition."}


def check_licence(requirement: dict, dataset: dict) -> dict:
    lic = _norm(dataset.get("licence", ""))
    if "open government licence" in lic:
        return {"rule": "licence", "status": "PASS",
                "explanation": "Licence is source-declared as Open Government Licence. Confirm version and attribution on the landing page; OGL permits reuse with attribution."}
    if "unknown" in lic or not lic:
        return {"rule": "licence", "status": "WARN", "explanation": "Licence terms could not be verified from seed metadata. Read the source licence before reuse or redistribution."}
    return {"rule": "licence", "status": "WARN",
            "explanation": f"Licence is '{dataset.get('licence')}'. Reuse/redistribution terms must be read on the source; public availability does not imply permission."}


def check_freshness(requirement: dict, dataset: dict) -> dict:
    rev = dataset.get("last_catalogue_review", "")
    health = (dataset.get("link_health") or {}).get("checked_at_utc", "")
    return {"rule": "freshness", "status": "WARN",
            "explanation": f"Catalogue review {rev or 'unknown'}; landing-page check {health or 'not run in this session'}. Re-check the source for the latest release before analysis."}


CHECKS = [check_geography, check_time, check_granularity, check_identifiers,
          check_units, check_format, check_access, check_licence, check_freshness]


def active_rules() -> set[str]:
    try:
        from .store import CompatRule, session
        rows = session().query(CompatRule).filter_by(active=True).all()
        return {r.rule for r in rows} or {fn.__name__.replace("check_", "") for fn in CHECKS}
    except Exception:  # noqa: BLE001 — table may not exist yet; all rules apply
        return {fn.__name__.replace("check_", "") for fn in CHECKS}


def evaluate(requirement: dict, dataset: dict, active: set[str] | None = None) -> dict:
    on = active if active is not None else active_rules()
    fns = [fn for fn in CHECKS if fn.__name__.replace("check_", "") in on]
    results = [fn(requirement, dataset) for fn in fns]
    skipped = [fn.__name__.replace("check_", "") for fn in CHECKS if fn.__name__.replace("check_", "") not in on]
    order = {"PASS": 0, "UNKNOWN": 1, "WARN": 2, "FAIL": 3}
    worst = max(results, key=lambda r: order[r["status"]]) if results else {"status": "UNKNOWN"}
    return {"dataset_id": dataset.get("id"), "requirement_id": requirement.get("id"),
            "overall": worst["status"], "checks": results, "skipped_rules": skipped,
            "disclaimer": DISCLAIMER,
            "provenance": {"dataset_id": dataset.get("id"), "landing_url": dataset.get("landing_url"),
                           "verification_state": dataset.get("verification_state"), "link_type": dataset.get("link_type")}}
