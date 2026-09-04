"""AI gateway: deterministic tools return seed-backed provenance, never invention.
Provider is unset in tests → enabled=False and no LLM call is attempted."""
from fastapi.testclient import TestClient

from inqetra import app

client = TestClient(app)


def test_ai_status_lists_14_tools_and_is_optional():
    s = client.get("/api/v1/ai/status").json()
    assert len(s["tools"]) == 14
    assert s["enabled"] is False  # no provider configured in test env
    assert "without AI" in s["note"] or "fully usable" in s["note"]
    assert client.post("/api/v1/ai/draft", json={"facts": ["x"]}).json()["enabled"] is False


def test_ai_tools_search_datasets_provenance():
    r = client.post("/api/v1/ai/tools/search_datasets",
                    json={"q": "climate", "limit": 5}).json()
    assert r["items"] and r["label"].startswith("Search relevance")
    seed = client.get("/api/v1/datasets", params={"q": "climate", "limit": 5}).json()
    assert {i["id"] for i in r["items"]} == {i["id"] for i in seed["items"]}
    for i in r["items"]:
        assert i["provenance"]["dataset_id"] == i["id"]
        assert i["provenance"]["source"] == i["landing_url"]
        assert i["link_type"] and i["verification_state"]


def test_ai_tools_get_dataset_matches_seed():
    dsid = client.get("/api/v1/datasets", params={"limit": 1}).json()["items"][0]["id"]
    r = client.post("/api/v1/ai/tools/get_dataset", json={"dataset_id": dsid}).json()
    seed = next(x for x in client.get("/api/v1/datasets/views/json").json()["items"]
                if x["id"] == dsid)
    assert r["title"] == seed["title"] and r["publisher"] == seed["publisher"]
    assert r["landing_url"]["value"] == seed["landing_url"]
    assert r["licence"]["value"] == seed["licence"]


def test_ai_tools_project_gaps_no_invention():
    pid = client.post("/api/v1/projects", json={"title": "ai gaps"}).json()["id"]
    client.post(f"/api/v1/projects/{pid}/requirements",
                json={"title": "Exposure", "required_variables": ["temperature"]})
    gaps = client.post("/api/v1/ai/tools/find_data_gaps", json={"project_id": pid}).json()
    assert gaps["requirements"] and gaps["requirements"][0]["status"] in (
        "COVERED", "PARTIAL", "MISSING", "INCOMPATIBLE", "RESTRICTED", "UNKNOWN")
    proj = client.post("/api/v1/ai/tools/get_project", json={"project_id": pid}).json()
    assert proj["title"] == "ai gaps" and len(proj["requirements"]) == 1


def test_ai_tools_unknown_and_chat_routing():
    assert client.post("/api/v1/ai/tools/nope", json={}).status_code == 404
    pid = client.post("/api/v1/projects", json={"title": "ai chat"}).json()["id"]
    c = client.post("/api/v1/ai/chat",
                    json={"message": "what gaps remain?", "project_id": pid}).json()
    assert c["tool"] == "find_data_gaps"
    assert "SYSTEM" in c["system"] or "Never invent" in c["system"]
    assert "assistant" not in c  # provider unset → deterministic only
