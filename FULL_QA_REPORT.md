# FULL_QA_REPORT.md — INQETRA v0.2.1
Rewritten: 2026-09-04T16:17:37Z · Worker session: full backend completion + frontend wiring + redesign + art pack.

## Verdict: PASS (all gates green; nothing deployed externally)

## Gates and evidence (all run from ~/INQETRA-run local-SSD mirror, OneDrive untouched during work)

1. **Dataset gate / link health** — `GET /api/v1/health` → `record_count: 751`, `unreachable_record_count: 0`, 447 unique URLs. Catalogue never edited to pass.
2. **Backend tests** — `INQETRA_NOCACHE=1 DATABASE_URL="sqlite:////tmp/inq_ci.db" /tmp/inqvenv/bin/python -m pytest apps/api/tests -q -p no:cacheprovider` → **29/29 PASSED (7.1 s)**. Suite extended 8 → 29 (studio graph/methodology/steps, kits instantiate, thumbnails incl. robots-disallow (mocked network), AI 14-tool no-invention, harvester CKAN mock + kill switch, resolver exactly-1, rules fixture, submissions never publish, basket coverage report, citations 4 formats).
3. **Frontend** — `tsc --noEmit` clean; `NEXT_PUBLIC_API_URL=http://localhost:8123 npm run build` → **30 routes, 0 errors**.
4. **Live route matrix** — 19/19 routes → HTTP 200 on http://localhost:3100 (`/`, `/datasets`, `/datasets/all`, `/map`, `/compare`, `/basket`, `/basket/report`, `/projects`, `/projects/new`, `/kits`, `/kits/urban-heat-island`, `/sources`, `/publishers`, `/publishers/Met Office`, `/methodology`, `/about`, `/developers`, `/settings`, `/admin`). Image assets 200.
5. **Browser golden journey (IAB, 1440×900)** — wizard 6 steps → CREATE PROJECT → studio redirect with content; kit instantiate → project with 4 requirements + provenance note; basket add → header count; basket report save-to-project + evaluate → "Evaluated 2 basket × requirement combinations", coverage matrix rendered; studio all 20 anchored sections present; map Leaflet tiles loaded (15 tiles); admin rules fixture returns scoped engine output; static pages carry real content.
6. **Thumbnails** — live batch warm of 10 records: robots.txt respected, rate-limited, size-capped; honest notes when no og:image (cards fall back to domain art → SVG). No third-party image mirrored or re-hosted.
7. **Parity/required fields/filters** — covered by suite (`test_catalogue_parity_csv_json_markdown`, `test_required_fields_present`, `test_acceptance_domain_filters`): 751 unique ids across CSV/JSON/MD, landing_url/publisher/link_type/verification_state/review date present, 12 acceptance filters > 0.
8. **Job failure state** — `POST /api/v1/jobs/exports {"simulate":"fail"}` → status failed, catalogue still 200 (suite).

## Fixed this session (were user-visible flaws)
- API deadlock for any UI after ~15 requests (QueuePool exhaustion; sessions never closed) → NullPool for SQLite.
- 9 dynamic pages rendered nav-only ("nothing in the page / buttons dead"): Next 14 `params` is not a Promise; `use(params)` threw. All converted.
- `/citations` 500 (missing `Citation` import).
- No-JS users got invisible `.reveal` content → now visible without JS.
- Basket report now saves the browser basket into the project before evaluating.

## Known limitations / notes
- Playwright locator clicks time out on some wizard buttons inside the IAB harness while programmatic/real clicks work — automation-environment quirk, app handlers verified attached and functioning (wizard completes end-to-end).
- Docker: engine 29.5.2 + compose v5.5.0 present; `docker compose config` valid. Full `up --build` deferred (colima holds host :3000; compose maps web 3000 — use `COMPOSE_FILE` override or stop colima to boot the full stack).
- Ports this session: API :8123, web :3100 (compose file unchanged: 8000/3000).
- Nothing deployed or submitted externally.

## Mobile pass — 2026-09-04T16:29:18Z
- 390×844 (and 768) verified: 18/18 routes **zero horizontal overflow** (scrollWidth − innerWidth ≤ 0).
- Shell: sidebar hides ≤768px; new ☰ MENU panel (all 14 routes, active state, closes on navigate); fixed bottom quick nav (HOME/DATA/PROJECTS/BASKET); topbar stacks (search row → actions row).
- Content safety: `.grid` single-track clamp `minmax(0,1fr)` (kills max-content blowouts app-wide), card grid `minmax(min(300px,100%),1fr)`, tables/pre scroll or wrap, URLs `overflow-wrap:anywhere`, studio sub-nav horizontal scroll chips, CTA overlay stacks under art ≤768px, touch targets ≥44px, focus-visible preserved, reduced-motion respected.
