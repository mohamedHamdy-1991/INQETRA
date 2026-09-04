"""Studio entities: concept graph, methodology/steps, citations, contributions,
submissions, and the basket coverage report chain (spec 5/16)."""
from fastapi.testclient import TestClient

from inqetra import app

client = TestClient(app)


def _project(title: str) -> str:
    return client.post("/api/v1/projects", json={"title": title}).json()["id"]


def test_studio_graph():
    pid = _project("graph test")
    c1 = client.post(f"/api/v1/projects/{pid}/concepts",
                     json={"label": "Urban form", "kind": "exposure", "x": 100, "y": 80}).json()
    c2 = client.post(f"/api/v1/projects/{pid}/concepts",
                     json={"label": "Overheating", "kind": "outcome", "x": 300, "y": 120}).json()
    e = client.post(f"/api/v1/projects/{pid}/edges",
                    json={"from_id": c1["id"], "to_id": c2["id"],
                          "relation": "influences", "rationale": "Density traps heat"}).json()
    moved = client.patch(f"/api/v1/projects/{pid}/concepts/{c1['id']}",
                         json={"x": 150, "y": 200}).json()
    assert (moved["x"], moved["y"]) == (150, 200)
    g = client.get(f"/api/v1/projects/{pid}/graph").json()
    assert len(g["nodes"]) == 2 and len(g["edges"]) == 1
    node = next(n for n in g["nodes"] if n["id"] == c1["id"])
    assert node["x"] == 150
    assert g["edges"][0]["from_id"] == c1["id"] and g["edges"][0]["relation"] == "influences"
    assert client.delete(f"/api/v1/projects/{pid}/edges/{e['id']}").json()["removed"] == e["id"]
    assert len(client.get(f"/api/v1/projects/{pid}/graph").json()["edges"]) == 0


def test_studio_methodology_steps():
    pid = _project("methodology test")
    m = client.post(f"/api/v1/projects/{pid}/methodology",
                    json={"design": "Mixed methods", "ethics": "No personal data"}).json()
    assert m["design"] == "Mixed methods"
    again = client.post(f"/api/v1/projects/{pid}/methodology", json={"design": "Convergent mixed"}).json()
    assert again["id"] == m["id"] and again["design"] == "Convergent mixed"
    s1 = client.post(f"/api/v1/projects/{pid}/steps",
                     json={"stage": "cleaning", "description": "De-duplicate records"}).json()
    s2 = client.post(f"/api/v1/projects/{pid}/steps",
                     json={"stage": "analysis", "description": "Regression"}).json()
    steps = client.get(f"/api/v1/projects/{pid}/steps").json()["items"]
    assert [s["order"] for s in steps] == sorted(s["order"] for s in steps)
    assert steps[0]["description"] == "De-duplicate records"
    patched = client.patch(f"/api/v1/projects/{pid}/steps/{s2['id']}",
                           json={"stage": "validation"}).json()
    assert patched["stage"] == "validation"
    t = client.post(f"/api/v1/projects/{pid}/transformations",
                    json={"source_dataset_id": "inq-0001", "target": "Exposure table",
                          "operation": "Spatial join LSOA", "join_strategy": "left join on code",
                          "software": "Python/geopandas"}).json()
    items = client.get(f"/api/v1/projects/{pid}/transformations").json()["items"]
    assert any(x["id"] == t["id"] and x["operation"] == "Spatial join LSOA" for x in items)
    # variables attached to a requirement
    req = client.post(f"/api/v1/projects/{pid}/requirements", json={"title": "Exposure"}).json()
    v = client.post(f"/api/v1/projects/{pid}/requirements/{req['id']}/variables",
                    json={"name": "Temperature", "unit": "degC", "role_hint": "outcome"}).json()
    assert v["requirement_id"] == req["id"] and v["unit"] == "degC"


def test_studio_citations_contributions():
    pid = _project("citations test")
    c = client.post(f"/api/v1/projects/{pid}/citations",
                    json={"ctype": "literature", "authors": "Ali, M.",
                          "year": "2024", "title": "Overheating risk", "url": "https://example.test/p"}).json()
    assert c["project_id"] == pid
    assert client.delete(f"/api/v1/projects/{pid}/citations/{c['id']}").status_code == 200
    k = client.post(f"/api/v1/projects/{pid}/contributions",
                    json={"statement": "First street-level exposure index for Leeds",
                          "kind": "empirical"}).json()
    assert k["kind"] == "empirical"


def test_submissions_never_published():
    bad = client.post("/api/v1/submissions", json={"url": "ftp://x", "title": "no"})
    assert bad.status_code == 400
    s = client.post("/api/v1/submissions",
                    json={"url": "https://example.test/data", "title": "Community dataset",
                          "publisher": "Community group"}).json()
    assert s["status"] == "pending"
    acc = client.post(f"/api/v1/admin/submissions/{s['id']}/moderate",
                      json={"decision": "accepted", "moderator_notes": "checks out"}).json()
    assert acc["status"] == "accepted" and acc["published_to_catalogue"] is False
    assert "never direct catalogue" in acc["note"]
    rej = client.post(f"/api/v1/admin/submissions/{s['id']}/moderate",
                      json={"decision": "rejected"}).json()
    assert rej["status"] == "rejected" and rej["published_to_catalogue"] is False
    assert client.get("/api/v1/admin/submissions", params={"status": "all"}).status_code == 200


def test_basket_report():
    """Basket item × requirement coverage + factual access/licence warnings."""
    p = client.post("/api/v1/projects", json={"title": "basket report test"}).json()
    pid = p["id"]
    aim = client.post(f"/api/v1/projects/{pid}/aims",
                      json={"title": "Map exposure", "statement": "Quantify exposure"}).json()
    req = client.post(f"/api/v1/projects/{pid}/requirements",
                      json={"title": "Heat exposure", "research_role": "Climate / exposure",
                            "required_variables": ["temperature"], "geography": "Leeds, England",
                            "start_date": "2020-01-01", "end_date": "2024-12-31",
                            "desired_spatial_scale": "LSOA",
                            "preferred_identifiers": ["LSOA"], "preferred_formats": ["CSV"],
                            "linked_aim_ids": [aim["id"]]}).json()
    match = client.post(f"/api/v1/projects/{pid}/requirements/{req['id']}/match").json()
    assert match["candidates"]
    dsid = match["candidates"][0]["dataset_id"]
    b = client.post(f"/api/v1/projects/{pid}/basket",
                    json={"dataset_id": dsid, "requirement_id": req["id"],
                          "rationale": "Exposure source"}).json()
    ev = client.post(f"/api/v1/projects/{pid}/evaluate").json()
    assert ev["evaluations"], "no evaluation rows for basket"
    row = next(e for e in ev["evaluations"] if e["dataset_id"] == dsid)
    assert row["overall"] in ("PASS", "WARN", "FAIL") and "disclaimer" in ev
    gaps = client.get(f"/api/v1/projects/{pid}/gaps").json()
    grow = next(g for g in gaps["requirements"] if g["requirement_id"] == req["id"])
    assert grow["status"] in ("COVERED", "PARTIAL", "MISSING", "INCOMPATIBLE", "RESTRICTED", "UNKNOWN")
    assert grow["explanation"]
    info = client.post("/api/v1/datasets/info", json={"ids": [dsid]}).json()
    assert len(info["items"]) == 1 and info["items"][0]["id"] == dsid
    model = client.get(f"/api/v1/projects/{pid}/report-model").json()
    inv = next(i for i in model["inventory"] if i["basket"]["dataset_id"] == dsid)
    assert inv["dataset"]["landing_url"] and inv["dataset"]["verification_state"]
    cites = client.get(f"/api/v1/projects/{pid}/citations").json()
    first = next(c for c in cites["items"] if c.get("dataset_id") == dsid)
    for style in ("harvard", "apa", "bibtex", "ris"):
        assert first[style], style
    # missing requirement (no basket assignment) is reported MISSING, not invented
    client.post(f"/api/v1/projects/{pid}/requirements", json={"title": "Unassigned requirement"})
    gaps2 = client.get(f"/api/v1/projects/{pid}/gaps").json()
    statuses = {g["requirement_title"]: g["status"] for g in gaps2["requirements"]}
    assert statuses["Unassigned requirement"] in ("MISSING", "UNKNOWN")
