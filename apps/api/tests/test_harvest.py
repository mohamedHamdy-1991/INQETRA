"""Harvester + resolver: CKAN adapter metadata-only staging, resolver exactly-1
rule. Network mocked — catalogue is never mutated by staging (spec 10)."""
from fastapi.testclient import TestClient

import inqetra.harvest as harvest
from inqetra import app

client = TestClient(app)


class FakeResp:
    def __init__(self, payload, content_type="application/json"):
        self._p = payload
        self.headers = {"content-type": content_type}

    def raise_for_status(self):
        return None

    def json(self):
        return self._p


def _ckan_payload(n_titles):
    return {"result": {"results": [
        {"id": f"ext-{i}", "name": f"slug-{i}", "title": t,
         "notes": "synthetic", "license_title": "OGL-3.0",
         "metadata_modified": "2026-09-01T00:00:00",
         "organization": {"title": "Test Org"}}
        for i, t in enumerate(n_titles)]}}


def test_source_registry_crud_and_kill_switch():
    s = client.post("/api/v1/sources", json={
        "name": "Test CKAN", "base_url": "https://example.test/api/3/action/package_search",
        "adapter": "CKAN", "trust_level": "Tier B", "terms_notes": "OGL; metadata only"}).json()
    assert s["active"] is True and s["kill_switch"] is False
    patched = client.patch(f"/api/v1/sources/{s['id']}", json={"kill_switch": True}).json()
    assert patched["kill_switch"] is True
    run = client.post(f"/api/v1/sources/{s['id']}/run", json={"limit": 5}).json()
    assert run["status"] == "blocked" and "kill switch" in run["detail"].lower()
    runs = client.get(f"/api/v1/sources/{s['id']}/runs").json()
    assert runs["items"] and runs["items"][0]["status"] == "failed"
    client.patch(f"/api/v1/sources/{s['id']}", json={"kill_switch": False})


def test_harvest_ckan_mock(monkeypatch):
    s = client.post("/api/v1/sources", json={
        "name": "Mock CKAN run", "base_url": "https://mock.example.test/api/3/action/package_search",
        "adapter": "CKAN"}).json()
    sid = s["id"]
    total_before = client.get("/api/v1/datasets", params={"limit": 1}).json()["total"]
    monkeypatch.setattr(harvest.httpx, "get",
                        lambda *a, **k: FakeResp(_ckan_payload(["Flooding records", "Green space"])))
    run = client.post(f"/api/v1/sources/{sid}/run", json={"limit": 10}).json()
    assert run["status"] == "done" and run["added"] == 2 and run["failed"] == 0
    staging = client.get("/api/v1/staging").json()["items"]
    staged = [c for c in staging if c["source_id"] == sid]
    assert len(staged) == 2
    for c in staged:
        assert c["status"] == "staging"
        assert "Unknown" in c["licence_state"]
        assert c["provenance"]["portal"] and c["provenance"]["external_id"]
    # idempotent re-run: same fingerprints → nothing new
    run2 = client.post(f"/api/v1/sources/{sid}/run", json={"limit": 10}).json()
    assert run2["added"] == 0 and run2["changed"] == 0
    # catalogue untouched
    assert client.get("/api/v1/datasets", params={"limit": 1}).json()["total"] == total_before


def _all_records() -> list[dict]:
    return client.get("/api/v1/datasets/views/json").json()["items"]


def _collection_record() -> dict:
    for r in _all_records():
        if "data.gov.uk" in r["landing_url"] and r["link_type"] == "official_collection":
            return r
    raise AssertionError("no data.gov.uk official_collection record in seed")


def test_resolver_exactly_one(monkeypatch):
    rec = _collection_record()
    total_before = client.get("/api/v1/datasets", params={"limit": 1}).json()["total"]

    monkeypatch.setattr(harvest.httpx, "get",
                        lambda *a, **k: FakeResp(_ckan_payload([rec["title"]])))
    r1 = client.post("/api/v1/resolve", json={"dataset_id": rec["id"]}).json()
    assert r1["status"] == "staged", r1
    assert r1["candidate_id"] and r1["match"]["url"].startswith("https://data.gov.uk/dataset/")
    assert "Not published" in r1["note"] or "not published" in r1["note"]

    monkeypatch.setattr(harvest.httpx, "get",
                        lambda *a, **k: FakeResp(_ckan_payload([rec["title"], rec["title"] + " II"])))
    r2 = client.post("/api/v1/resolve", json={"dataset_id": rec["id"]}).json()
    assert r2["status"] == "unresolved" and r2["match_count"] == 2

    monkeypatch.setattr(harvest.httpx, "get",
                        lambda *a, **k: FakeResp(_ckan_payload(["Unrelated thing"])))
    r3 = client.post("/api/v1/resolve", json={"dataset_id": rec["id"]}).json()
    assert r3["status"] == "unresolved" and r3["match_count"] == 0

    # resolved candidates stay in staging; catalogue untouched
    assert client.get("/api/v1/datasets", params={"limit": 1}).json()["total"] == total_before
    staged = client.get("/api/v1/staging").json()["items"]
    assert any(c.get("provenance", {}).get("resolves") == rec["id"] for c in staged)
    # direct records don't need resolving
    direct = next(r for r in _all_records() if r["link_type"] == "direct_dataset")
    assert client.post("/api/v1/resolve", json={"dataset_id": direct["id"]}).json()["status"] \
        == "already-direct"
