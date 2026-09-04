"""Dataset preview pictures without mirroring (spec 10/18).

On demand, fetch the catalogue landing page (robots-aware, rate-limited,
size-capped, SSRF-guarded) and extract an OpenGraph/Twitter <meta> preview
image. Only the image URL is stored — INQETRA never downloads, hosts or
re-serves third-party images. Cards hotlink the publisher's own image with a
local deterministic SVG placeholder fallback.
"""
from __future__ import annotations

import ipaddress
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, build_opener
from urllib import robotparser

import httpx
from fastapi import APIRouter, HTTPException

from .store import DatasetThumb, session

router = APIRouter(prefix="/api/v1/datasets", tags=["thumbnails"])

UA = "INQETRA-thumbnail/1.0 (+link health; respects robots.txt)"
MAX_BYTES = 600_000
MIN_INTERVAL = 1.5
_last_host_hit: dict[str, float] = {}
_robots_cache: dict[str, object] = {}


def _guard(url: str) -> str:
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise HTTPException(400, "Only http(s) landing URLs")
    try:
        ip = ipaddress.ip_address(u.hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise HTTPException(400, "Private-network URLs are not allowed")
    except ValueError:
        pass
    return url


class _Meta(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.found: dict[str, str] = {}
        self.done = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.done or tag not in ("meta", "link"):
            return
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta":
            prop = (a.get("property") or a.get("name") or "").lower()
            if prop in ("og:image", "twitter:image") and a.get("content"):
                self.found.setdefault(prop, a["content"])
        elif tag == "link" and a.get("rel", "").lower() == "image_src" and a.get("href"):
            self.found.setdefault("link:image_src", a["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self.done = True


def _robots_allows(landing: str) -> tuple[bool, str]:
    u = urlparse(landing)
    base = f"{u.scheme}://{u.netloc}"
    if base not in _robots_cache:
        try:
            req = Request(base + "/robots.txt", headers={"User-Agent": UA})
            with build_opener().open(req, timeout=5) as r:
                body = r.read(100_000).decode("utf-8", "ignore").splitlines()
            rp = robotparser.RobotFileParser()
            rp.parse(body)
            _robots_cache[base] = rp
        except Exception:  # noqa: BLE001 — unfetchable robots: proceed with a minimal single GET (validator precedent)
            _robots_cache[base] = None
    rp = _robots_cache[base]
    if rp is None:
        return True, "robots.txt unfetchable; single minimal GET performed"
    ok = rp.can_fetch(UA, landing)
    return ok, "robots.txt allows preview fetch" if ok else "robots.txt disallows fetching this page"


def _extract(landing: str) -> dict:
    _guard(landing)
    allowed, why = _robots_allows(landing)
    if not allowed:
        return {"image_url": "", "source": "", "note": why}
    host = urlparse(landing).hostname or ""
    wait = MIN_INTERVAL - (time.monotonic() - _last_host_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    try:
        with httpx.stream("GET", landing, headers={"User-Agent": UA}, timeout=8, follow_redirects=True) as r:
            if r.status_code not in range(200, 400):
                return {"image_url": "", "source": "", "note": f"landing page returned HTTP {r.status_code}"}
            buf = b""
            for chunk in r.iter_bytes(32_768):
                buf += chunk
                if len(buf) >= MAX_BYTES or b"</head>" in buf.lower():
                    break
        _last_host_hit[host] = time.monotonic()
        if len(buf) >= MAX_BYTES and b"</head>" not in buf.lower():
            return {"image_url": "", "source": "", "note": "page head too large; skipped"}
        p = _Meta()
        p.feed(buf.decode("utf-8", "ignore"))
        for key in ("og:image", "twitter:image", "link:image_src"):
            if p.found.get(key):
                abs_url = urljoin(landing, p.found[key])
                try:
                    _guard(abs_url)
                except HTTPException:
                    continue
                return {"image_url": abs_url, "source": key,
                        "note": f"Preview image advertised by the publisher page ({key}); hotlinked, not hosted by INQETRA. {why}."}
        return {"image_url": "", "source": "", "note": "No publisher preview image (og:image/twitter:image) found on the landing page."}
    except Exception as e:  # noqa: BLE001 — evidence, not a badge
        return {"image_url": "", "source": "", "note": f"Preview fetch failed: {str(e)[:160]}"}


def _dump_thumb(t: DatasetThumb) -> dict:
    return {"dataset_id": t.dataset_id, "image_url": t.image_url,
            "source": t.source, "note": t.note,
            "checked_at": t.updated_at.isoformat() if hasattr(t.updated_at, "isoformat") else ""}


@router.get("/{dataset_id}/thumbnail")
def thumbnail(dataset_id: str, refresh: bool = False):
    from . import catalogue as cat
    known = {r["id"]: r for r in cat._project_subset()}
    if dataset_id not in known:
        raise HTTPException(404, "Unknown dataset")
    db = session()
    t = db.query(DatasetThumb).filter_by(dataset_id=dataset_id).first()
    if t and t.image_url and not refresh:
        return _dump_thumb(t)
    if t is None:
        t = DatasetThumb(dataset_id=dataset_id)
        db.add(t)
    res = _extract(known[dataset_id]["landing_url"])
    t.image_url, t.source, t.note = res["image_url"], res["source"], res["note"]
    db.commit()
    db.refresh(t)
    return _dump_thumb(t)


@router.post("/thumbnails")
def thumbnails_batch(payload: dict):
    ids = (payload.get("ids") or [])[:24]
    return {"items": [thumbnail(i) if _known(i) else {"dataset_id": i, "image_url": "", "note": "Unknown dataset"} for i in ids]}


def _known(dataset_id: str) -> bool:
    from . import catalogue as cat
    return any(r["id"] == dataset_id for r in cat._project_subset())


@router.post("/info")
def info(payload: dict):
    """Full rows for a basket/report id list (no invention — straight from the seed)."""
    from . import catalogue as cat
    ids = payload.get("ids") or []
    known = {r["id"]: r for r in cat._project_subset()}
    return {"items": [known[i] for i in ids if i in known]}
