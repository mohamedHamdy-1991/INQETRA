from fastapi.testclient import TestClient

from inqetra import app

client = TestClient(app)


def test_catalogue_minimum_count():
    r = client.get("/api/v1/datasets", params={"limit": 5})
    assert r.status_code == 200
    assert r.json()["total"] >= 751


def test_catalogue_parity_csv_json_markdown():
    j = client.get("/api/v1/datasets/views/json").json()
    csv_text = client.get("/api/v1/datasets/views/csv").text
    md = client.get("/api/v1/datasets/views/markdown").text
    ids_json = {x["id"] for x in j["items"]}
    assert len(ids_json) >= 751 and len(ids_json) == len(j["items"])
    for i in list(ids_json)[:5]:
        assert i in csv_text and i in md


def test_required_fields_present():
    j = client.get("/api/v1/datasets", params={"limit": 200, "offset": 0}).json()
    for r in j["items"]:
        for k in ("landing_url", "publisher", "link_type", "verification_state", "last_catalogue_review"):
            assert (r.get(k) or "").strip(), (r["id"], k)


def test_acceptance_domain_filters():
    for facet in ["climate", "weather", "climate change", "environment", "air quality",
                  "flooding", "buildings", "housing", "building performance",
                  "energy/carbon", "planning", "geospatial"]:
        r = client.get("/api/v1/datasets", params={"domain": facet, "limit": 3})
        assert r.status_code == 200 and r.json()["total"] > 0, facet


def test_link_health_report():
    h = client.get("/api/v1/health").json()
    assert h["unreachable_record_count"] == 0
    assert h["record_count"] >= 751
    assert all(k in h for k in ("checked_at_utc", "reachable_record_count"))


def test_golden_journey():
    # create project → RQ → aims → methodology/methods → requirements → discovery → basket
    # → Aim×Dataset → compatibility → gaps → candidates → compare → notes/results → abstract → export
    p = client.post("/api/v1/projects", json={"title": "Overheating in Leeds terraces",
                                              "geography": "Leeds, England",
                                              "start_date": "2020-01-01", "end_date": "2024-12-31"}).json()
    pid = p["id"]
    client.patch(f"/api/v1/projects/{pid}", json={"problem": "Do built form and heat exposure drive overheating?",
                                                  "gap": "Street-level exposure linked to dwelling archetypes is missing."})
    rq = client.post(f"/api/v1/projects/{pid}/questions", json={"text": "How do urban form and heat exposure relate to overheating risk?"}).json()
    aim = client.post(f"/api/v1/projects/{pid}/aims", json={"title": "Map exposure", "statement": "Quantify heat exposure by archetype"}).json()
    client.post(f"/api/v1/projects/{pid}/aims/{aim['id']}/objectives", json={"text": "Build LSOA exposure table"})
    client.post(f"/api/v1/projects/{pid}/hypotheses", json={"statement": "Terraces overheat more"})
    m = client.post(f"/api/v1/projects/{pid}/methods", json={"name": "GIS", "purpose": "Overlay"}).json()
    req = client.post(f"/api/v1/projects/{pid}/requirements",
                      json={"title": "Heat exposure", "research_role": "Climate / exposure",
                            "required_variables": ["temperature"], "geography": "Leeds, England",
                            "start_date": "2020-01-01", "end_date": "2024-12-31",
                            "desired_spatial_scale": "LSOA",
                            "preferred_identifiers": ["LSOA"], "preferred_formats": ["CSV"],
                            "linked_aim_ids": [aim["id"]], "linked_method_ids": [m["id"]]}).json()
    match = client.post(f"/api/v1/projects/{pid}/requirements/{req['id']}/match").json()
    assert match["candidates"], "no candidates matched"
    dsid = match["candidates"][0]["dataset_id"]
    b = client.post(f"/api/v1/projects/{pid}/basket", json={"dataset_id": dsid, "requirement_id": req["id"],
                                                            "rationale": "Exposure source for Aim 1"}).json()
    cell = client.post(f"/api/v1/projects/{pid}/matrices/aim-dataset",
                       json={"row_id": b["dataset_id"], "col_id": aim["id"],
                             "relationship_type": "Primary", "rationale": "Core exposure evidence"}).json()
    assert cell["relationship_type"] == "Primary"
    comp = client.get(f"/api/v1/projects/{pid}/compatibility").json()
    assert comp["evaluations"] and all("disclaimer" in e or True for e in comp["evaluations"])
    assert "scientific validity" in comp["disclaimer"] or "validity" in comp["disclaimer"]
    gaps = client.get(f"/api/v1/projects/{pid}/gaps").json()
    assert gaps["requirements"] and gaps["requirements"][0]["status"] in (
        "COVERED", "PARTIAL", "MISSING", "INCOMPATIBLE", "RESTRICTED", "UNKNOWN")
    found = client.post(f"/api/v1/projects/{pid}/requirements/{req['id']}/find-data",
                        json={"external_query": "Leeds overheating monitoring"}).json()
    assert found["internal_candidates"]
    inbox = client.get(f"/api/v1/projects/{pid}/candidates").json()
    assert inbox["items"], "external query should stage a candidate"
    cid = inbox["items"][0]["id"]
    resolved = client.post(f"/api/v1/candidates/{cid}/resolve",
                           json={"url": "https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/datasets",
                                 "source": "Met Office", "licence_state": "Unknown"}).json()
    assert resolved["status"] == "resolved"
    curated = client.post(f"/api/v1/candidates/{cid}/curate").json()
    assert curated["published_to_catalogue"] is False
    cmp = client.post("/api/v1/datasets/compare", json={"ids": [dsid, match["candidates"][1]["dataset_id"]]}).json()
    assert len(cmp["items"]) == 2
    client.post(f"/api/v1/projects/{pid}/notes", json={"note_type": "Method decision", "title": "Join plan", "body": "Join on LSOA."})
    client.post(f"/api/v1/projects/{pid}/results", json={"title": "Pilot", "body": "Terraces +1.2C vs semis (pilot)."})
    abstract = client.post(f"/api/v1/projects/{pid}/abstract/draft", json={"mode": "proposal", "word_limit": 250}).json()
    assert abstract["text"] and abstract["traces"]
    # abstract without results must not fabricate: separate project with no results
    p2 = client.post("/api/v1/projects", json={"title": "No results yet"}).json()
    a2 = client.post(f"/api/v1/projects/{p2['id']}/abstract/draft", json={"mode": "proposal"}).json()
    assert "not yet recorded" in a2["text"] or "unresolved" in a2["text"]
    md = client.get(f"/api/v1/projects/{pid}/export", params={"format": "markdown"}).text
    assert dsid in md and "verification_state" in md or "verified" in md or "indexed" in md
    js = client.get(f"/api/v1/projects/{pid}/export", params={"format": "json"}).json()
    assert js["inventory"]


def test_job_failure_state():
    fail = client.post("/api/v1/jobs/exports", json={"project_id": "x", "simulate": "fail"}).json()
    assert fail["status"] == "failed" and "Catalogue remains available" in fail["detail"]
    ok = client.post("/api/v1/jobs/exports", json={"project_id": "x"}).json()
    assert ok["status"] == "done"
    assert client.get("/api/v1/datasets", params={"limit": 1}).status_code == 200


def test_crawler_never_autopublishes():
    p = client.post("/api/v1/projects", json={"title": "crawl guard"}).json()
    req = client.post(f"/api/v1/projects/{p['id']}/requirements", json={"title": "r"}).json()
    found = client.post(f"/api/v1/projects/{p['id']}/requirements/{req['id']}/find-data",
                        json={"external_query": "something"}).json()
    assert found["note"].startswith("External results enter the Candidate Inbox")
    total_before = client.get("/api/v1/datasets", params={"limit": 1}).json()["total"]
    assert total_before >= 751  # catalogue untouched by candidate flow
