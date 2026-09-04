"""Thumbnail extraction: og:image found, robots disallow, 404 unknown id.
Network is fully mocked/short-circuited — no live fetches in tests."""
from urllib.parse import urlparse

from fastapi.testclient import TestClient

import inqetra.thumbs as thumbs
from inqetra import app

client = TestClient(app)

OG_HTML = """<html><head>
<meta property="og:title" content="Dataset">
<meta property="og:image" content="https://cdn.publisher.example.test/preview.jpg">
<meta name="twitter:image" content="https://cdn.publisher.example.test/t.jpg">
</head><body>landing</body></html>"""


class FakeStream:
    status_code = 200

    def __init__(self, body: bytes):
        self._b = body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def iter_bytes(self, n):
        yield self._b


def _robots(lines: list[str]):
    from urllib import robotparser
    rp = robotparser.RobotFileParser()
    rp.parse(lines)
    return rp


def _first_item() -> dict:
    return client.get("/api/v1/datasets", params={"limit": 1}).json()["items"][0]


def test_thumbs_mock(monkeypatch):
    item = _first_item()
    did, landing = item["id"], item["landing_url"]
    u = urlparse(landing)
    thumbs._robots_cache[f"{u.scheme}://{u.netloc}"] = _robots([])
    thumbs._last_host_hit.clear()
    monkeypatch.setattr(thumbs.httpx, "stream",
                        lambda *a, **k: FakeStream(OG_HTML.encode()))
    r = client.get(f"/api/v1/datasets/{did}/thumbnail", params={"refresh": True})
    assert r.status_code == 200
    body = r.json()
    assert body["image_url"] == "https://cdn.publisher.example.test/preview.jpg"
    assert body["source"] == "og:image"
    assert "hotlink" in body["note"].lower()
    # cached second read is served from the store — never refetches
    def _no_refetch(*a, **k):
        raise AssertionError("must not refetch a cached thumbnail")
    monkeypatch.setattr(thumbs.httpx, "stream", _no_refetch)
    r2 = client.get(f"/api/v1/datasets/{did}/thumbnail").json()
    assert r2["image_url"] == "https://cdn.publisher.example.test/preview.jpg"


def test_thumbs_robots_disallow(monkeypatch):
    item = _first_item()
    did = item["id"]
    base = "https://blocked.example.test"
    thumbs._robots_cache[base] = _robots(["User-agent: *", "Disallow: /"])
    thumbs._last_host_hit.clear()
    from inqetra import catalogue as cat
    monkeypatch.setattr(cat, "_project_subset",
                        lambda: [{"id": did, "landing_url": f"{base}/dataset/{did}"}])
    r = client.get(f"/api/v1/datasets/{did}/thumbnail", params={"refresh": True}).json()
    assert r["image_url"] == ""
    assert "disallow" in r["note"].lower()


def test_thumbs_unknown_dataset():
    assert client.get("/api/v1/datasets/definitely-not-real/thumbnail").status_code == 404


def test_thumbs_batch_shape(monkeypatch):
    ids = [x["id"] for x in client.get("/api/v1/datasets", params={"limit": 3}).json()["items"]]

    def _stub(landing: str) -> dict:
        assert landing.startswith("http")
        return {"image_url": "", "source": "", "note": "unit-test stub"}
    monkeypatch.setattr(thumbs, "_extract", _stub)
    r = client.post("/api/v1/datasets/thumbnails", json={"ids": ids}).json()
    assert len(r["items"]) == 3 and all("note" in i for i in r["items"])
    info = client.post("/api/v1/datasets/info", json={"ids": ids[:2]}).json()
    assert [i["id"] for i in info["items"]] == ids[:2]
