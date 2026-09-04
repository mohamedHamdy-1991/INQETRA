"""Research kits: list, detail, instantiate full project graph (spec 12)."""
from fastapi.testclient import TestClient

from inqetra import app

client = TestClient(app)


def test_kits_list_and_detail():
    items = client.get("/api/v1/kits").json()["items"]
    assert len(items) >= 8 and all(k.get("slug") and k.get("title") for k in items)
    d = client.get("/api/v1/kits/urban-heat-island").json()
    assert d["slug"] == "urban-heat-island"
    assert d["questions"] and d["aims"] and d["methods"] and d["required_roles"]
    assert client.get("/api/v1/kits/not-a-kit").status_code == 404


def test_kits_instantiate():
    total_before = client.get("/api/v1/datasets", params={"limit": 1}).json()["total"]
    r = client.post("/api/v1/kits/urban-heat-island/instantiate",
                    json={"title": "UHI kit run", "geography": "Leeds, England"}).json()
    assert r["kit"] == "urban-heat-island"
    created = r["created"]
    assert created["questions"] >= 1 and created["aims"] >= 1
    assert created["methods"] >= 1 and created["requirements"] >= 1
    p = client.get(f"/api/v1/projects/{r['project_id']}").json()
    assert p["title"] == "UHI kit run" and p["geography"] == "Leeds, England"
    assert len(p["questions"]) == created["questions"]
    assert len(p["aims"]) == created["aims"]
    assert len(p["methods"]) == created["methods"]
    assert len(p["requirements"]) == created["requirements"]
    # every requirement is linked to the kit's aims — a graph, not a basket
    for req in p["requirements"]:
        assert req.get("linked_aim_ids"), "kit requirement not linked to aims"
    note = next(n for n in p["notes"] if "Kit provenance" in n["title"])
    assert "NOT" in note["body"] and "copied" in note["body"]
    # no catalogue rows copied: total unchanged, project inventory empty
    assert client.get("/api/v1/datasets", params={"limit": 1}).json()["total"] == total_before
    assert p.get("basket", []) == []
