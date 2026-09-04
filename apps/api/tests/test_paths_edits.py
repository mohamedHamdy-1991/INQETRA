"""Document paths, abstract editing, custom kits (v0.2.2 features)."""
from fastapi.testclient import TestClient

from inqetra import app

client = TestClient(app)


def test_paths_list_and_detail():
    items = client.get("/api/v1/paths").json()["items"]
    slugs = {x["slug"] for x in items}
    assert {"phd-thesis", "masters-thesis", "research-grant", "journal-article", "conference-paper"} <= slugs
    d = client.get("/api/v1/paths/phd-thesis").json()
    assert len(d["sections"]) >= 5 and d["tools"] and all(s["starters"] for s in d["sections"])
    assert client.get("/api/v1/paths/nope").status_code == 404


def test_project_export_path():
    pid = client.post("/api/v1/projects", json={"title": "path project"}).json()["id"]
    assert client.get(f"/api/v1/projects/{pid}").json()["export_path"] == ""
    client.patch(f"/api/v1/projects/{pid}", json={"export_path": "research-grant"})
    assert client.get(f"/api/v1/projects/{pid}").json()["export_path"] == "research-grant"


def test_abstract_blank_and_edit():
    pid = client.post("/api/v1/projects", json={"title": "abstract edit"}).json()["id"]
    blank = client.post(f"/api/v1/projects/{pid}/abstract/blank", json={}).json()
    assert blank["text"] == "" and blank["mode"] == "custom"
    edited = client.patch(f"/api/v1/projects/{pid}/abstract/{blank['id']}",
                          json={"text": "  My own abstract.  ", "word_limit": 400}).json()
    assert edited["text"] == "My own abstract." and edited["edited"] is True
    got = client.get(f"/api/v1/projects/{pid}/abstract/drafts/{blank['id']}").json()
    assert got["text"] == "My own abstract."
    assert client.patch(f"/api/v1/projects/{pid}/abstract/missing-id", json={"text": "x"}).status_code == 404


def test_custom_kit_lifecycle():
    made = client.post("/api/v1/kits", json={
        "title": "My Overheating Kit",
        "graph": {"questions": ["Q1?"], "aims": ["A1"], "methods": ["GIS"],
                  "required_roles": ["Climate / exposure"]}}).json()
    slug = made["slug"]
    assert slug.startswith("my-overheating-kit") and made["graph"]["custom"] is True
    assert slug in {x["slug"] for x in client.get("/api/v1/kits").json()["items"]}
    # custom kit instantiates like a built-in
    r = client.post(f"/api/v1/kits/{slug}/instantiate", json={"title": "from my kit"}).json()
    assert r["created"]["questions"] == 1 and r["created"]["requirements"] == 1
    # cannot delete built-ins, can delete customs
    assert client.delete("/api/v1/kits/urban-heat-island").status_code == 400
    assert client.delete(f"/api/v1/kits/{slug}").json()["removed"] == slug
    assert client.get(f"/api/v1/kits/{slug}").status_code == 404
