# CHANGELOG.md

All notable changes. Format: Keep-a-Changelog-ish. Timestamps UTC.

## [0.2.2] — 2026-09-04 — Document paths, editable abstract, custom kits, PDF exports

### Added
- **Document paths** (`/paths` + `GET /api/v1/paths[/slug]`): PhD thesis, Master's thesis, research grant, journal article, conference paper — each with section skeleton + word targets, the studio tools it leans on, and suggested ways of working. Projects store `export_path` (additive migration); abstract builder and PDF report follow the chosen path.
- **Editable abstract builder**: drafts fully editable (`PATCH /projects/{pid}/abstract/{id}`), blank-page start (`POST …/abstract/blank`), quick-add buttons for questions/aims/methods, path skeleton with suggested sentence starters, per-draft fetch (`GET …/abstract/drafts/{id}`).
- **Custom kits**: `POST /api/v1/kits` (create, auto-slug), `DELETE /api/v1/kits/{slug}` (customs only — built-ins protected); kit detail page has a CUSTOMISE mode (edit/add/remove questions, aims, methods, roles → SAVE AS MY KIT).
- **Visual PDF exports**: `/projects/[id]/report/print` — Neo-Brutalist print document (brand cover, badges, section plates, dataset inventory table with domain art, coverage statuses, Harvard citations); `SAVE AS PDF` via browser print with print-color-adjust, page-break control; EXPORT PDF buttons on project report + basket report.

### Fixed
- **Custom kits invisible in `/api/v1/kits`**: catalogue.py's static-JSON `/kits` and `/sources` routes shadowed the DB-backed routers (first-registered wins in FastAPI). Removed the shadowing routes; lists now reflect created/edited records.
- pytest 33/33 · tsc clean · build 32 routes.

## [0.2.1] — 2026-09-04 — v0.2 backend completion, full frontend wiring, home redesign, new logo/art

### Fixed
- **API deadlock**: route handlers opened sessions without teardown; under Python 3.14/SQLAlchemy the QueuePool exhausted after ~15 requests and every later request blocked forever. `store.engine()` now uses `NullPool` for SQLite (no cap, no stall). Golden journey 8/8 PASS again.
- **Citations 500**: `Citation` was not imported in `reports.py` → `NameError` on every `/citations` call.
- **9 dynamic pages crashed at runtime**: Next.js-15-style `params: Promise<...>` + React `use()` on Next 14 (params is a plain object) → `use()` throws, page renders nav-only ("buttons/pages not opening"). Fixed on studio, gaps, abstract, notes, candidates, report, datasets/[id], kits/[slug], publishers/[name].
- **No-JS content trap**: `.reveal{opacity:0}` hid content without JS. Now gated behind an `html.js` class set by an inline head script.
- **Citations endpoint returns 4 formats** (Harvard/APA/BibTeX/RIS) incl. literature citations added in studio.

### Added
- Backend test suite extended 8 → 29 tests: studio graph/methodology/steps/citations/contributions, kit instantiate (no catalogue copy), thumbnails (og:image + robots disallow + batch, network mocked), AI 14-tool provenance/no-invention, harvester CKAN mock (staging-only, idempotent), resolver exactly-1 rule, admin rules fixture, submissions never publish, basket coverage report.
- Frontend: `/basket/report` (basket × requirement coverage matrix, save-browser-basket-to-project then evaluate, access/licence readiness table, data-plan CTA), `/datasets/all`, `/projects/new` (6-step wizard), `/kits/[slug]`, `/publishers/[name]` wired; studio sections for knowledge gaps, draggable concept map (nodes/edges/positions persisted), methodology, transformations, ordered analysis steps, contributions, citations (add/remove/4 formats), AI copilot (deterministic without provider); admin rules editor + fixture test + submissions moderation + staging queue + source runs + resolver runner; map Leaflet CSS bundled + coverage panel; basket page upgraded (titles/publisher, save-to-project via drawer, report CTA).
- Design: new INQETRA logo (`assets/inqetra-logo-mark-v3-2026-09-04.png`, wire frame: Q-orbit mark, black on transparent) + 53-asset generated art library (`apps/web/public/img/`): hero, kit covers ×8, domain art ×18, banners ×13, empty-states ×3, sticker sheet; favicon/OG set; home page redesigned (process chips, highlight-block headline, ink stat band with CountUp, journey board, kit gallery, trust + sticker sheet, compact CTA). Dataset-card fallback chain: publisher og:image → domain art → deterministic SVG.

### Verified
- pytest 29/29 PASS (7.1 s); `tsc --noEmit` clean; `next build` 30 routes; live route matrix 19/19 → 200; browser audit: wizard end-to-end, kit instantiate, basket save+evaluate (2 combinations), studio 20 sections, map tiles (15 loaded), admin fixture, static pages content.

## [0.1.0] — 2026-09-04 — Initial runnable INQETRA studio + dataset hub

### Added
- Dataset gate re-run: 751/751 reachable, 447/447 URLs, `unreachable_record_count=0` (see INVENTORY.md). No records added/removed/edited.
- Audit artefacts: `INVENTORY.md`, `DECISIONS.md`, `CHANGELOG.md`, `MIGRATION_MAP.md`, `ROUTE_COMPONENT_HOOK_INVENTORY.md`.
- Stack: `apps/api` (FastAPI, SQLAlchemy, SQLite-file default / PostGIS via `DATABASE_URL`), `apps/web` (Next.js 14 + TypeScript App Router, token-exact Neo-Brutalist CSS), `docker-compose.yml` (web/api/db-PostGIS-16/redis-7), `data/seeds/` (751 CSV+JSON+MD parity views + link-health summary copy).
- Catalogue API: `GET /api/v1/datasets` (q + 12 acceptance domain filters + topic/geography/time/scale/variable/format/access/licence/publisher/authority/method/role/open-only/API + pagination), `GET /datasets/{id}`, `GET /datasets/views/{csv,json,markdown}`, `GET /publishers|sources|taxonomy|kits|health`, `POST /datasets/compare`.
- Research-studio API: projects CRUD + problem/gap + questions + aims/objectives + hypotheses + methods + requirements + basket (`project_datasets`) + Aim×Dataset matrix + notes + results + candidates + gaps + compatibility + abstract draft (evidence-traced, no fabricated results) + report-model + exports (MD/JSON) + jobs with failure simulation + AI stub (disabled without provider).
- Deterministic compatibility engine (9 rule families, factual language, no validity claims) + Data Gap Radar (`COVERED/PARTIAL/MISSING/INCOMPATIBLE/RESTRICTED/UNKNOWN`) + Candidate Inbox (never auto-publishes).
- Web: `/`, `/datasets`, `/datasets/[id]`, `/map`, `/compare`, `/basket`, `/projects`, `/projects/[id]/studio`, `/projects/[id]/notes`, `/projects/[id]/abstract`, `/projects/[id]/report`, `/projects/[id]/gaps`, `/projects/[id]/candidates`, `/kits`, `/sources`, `/publishers`, `/methodology`, `/about`, `/developers`, `/settings`, `/admin` — Neo-Brutalist, keyboard-operable, responsive 1440/1024/768/390, reduced-motion, print CSS.
- Tests: `pytest` API suite (catalogue count/parity/filters/golden journey/compatibility/exports/job-failure/link-health) + `tsc` + `next build`. See `FULL_QA_REPORT.md`.

### Preserved
- `INQETRA_AI_BUILD_PACK/` untouched except regenerated `data/link_health/*` (gate output). Loose root files untouched.

### Known limitations
- SQLite default stores bbox as JSON (PostGIS geometry only under `DATABASE_URL`). Map is discovery aid, not sole route. Auth is single-user header (D-13). AI is stub (D-08). PDF via print CSS (D-11).
