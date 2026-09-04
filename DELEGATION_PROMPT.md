# DELEGATION_PROMPT.md — Handoff for the next INQETRA implementation worker

You are the implementation worker continuing **INQETRA** (UK research-design studio + dataset hub). Work ONLY inside:

```
/Users/mohamedali/Library/CloudStorage/OneDrive-LeedsBeckettUniversity/Work/GITHUB REPO/INQETRA
```

The product contract is the build pack (`INQETRA_AI_BUILD_PACK/00_START_HERE.md` … `26_…`, `data/*`, `design/*`, `prototype/*`). Read it before changing anything. Preserve the non-negotiable data rules (below).

---

## 0. CRITICAL environment notes (read first)

1. **The repo lives on OneDrive (macOS File Provider).** File reads can stall with `ETIMEDOUT`/`errno 60`, and builds hang. Symptoms: `pytest` producing no output, `next build` failing with `errno:-60, syscall:'read'`, `head <file>` hanging.
2. **Workaround (proven):** build/run from a local SSD copy, then sync back:
   ```bash
   SRC="/Users/mohamedali/Library/CloudStorage/OneDrive-LeedsBeckettUniversity/Work/GITHUB REPO/INQETRA"
   DST="$HOME/INQETRA-run"
   rsync -a --timeout=8 --exclude='node_modules/' --exclude='.next/' \
     --exclude='INQETRA_AI_BUILD_PACK.zip' --exclude='INQETRA_AI_BUILD_PACK/reference/' \
     --exclude='INQETRA_AI_BUILD_PACK/data/INQETRA_751_DATASETS_WITH_TESTED_LINKS.csv' \
     --exclude='.DS_Store' "$SRC/" "$DST/"
   # build/run/test in $DST, then:
   rsync -a "$DST/apps" "$DST/data" "$SRC/"   # push code back
   ```
   Never `killall OneDrive` (breaks sync). Do not let `node_modules`/`.next` sync into OneDrive.
3. **Python venv with deps already installed:** `/tmp/inqvenv` (Python 3.14). If missing: `python3 -m venv /tmp/inqvenv && /tmp/inqvenv/bin/pip install -r apps/api/requirements.txt`.
4. **Ports:** API is served on **8123** in this session (`8000` is occupied by an unrelated FastAPI app; a stale `uvicorn inqetra:app --port 8123` may exist). Web uses `NEXT_PUBLIC_API_URL=http://localhost:8123`. `docker compose` maps db→5433, redis→6380.
5. **A working landing page (HTTP 200–399) does NOT prove download access, licence permission, scientific fitness, or resolved metadata.** Keep this distinction in every UI/API/report. Never invent metadata/licences/results/citations. Never silently upgrade `link_type`/`verification_state`. Never auto-publish harvester or candidate output. AI stays optional/provider-neutral.

---

## 1. Current state (as of handoff)

**Backend (FastAPI, `apps/api/inqetra/`) — RUNNING, `py_compile` clean, 8/8 pytest PASSED before the latest additions:**
- `store.py` now defines the full research model (added: `KnowledgeGap`, `Concept`, `ConceptRelationship`, `Methodology`, `VariableRequirement`, `Transformation`, `AnalysisStep`, `Contribution`, `Citation`, `ResearchKit`, `KitLink`, `Source`, `SourceRun`, `HarvestRecord`, `DatasetCandidate`, `Licence`, `LinkCheck`, `CompatRule`, `CompatResult`, `User`, `Submission`, `DatasetThumb`) on top of the original project/studio tables.
- `bootstrap.py` seeds rules/licences/sources/kits on first boot.
- `studio.py` (`/api/v1/projects/{pid}/…`) added: `kgaps`, `concepts`+`graph`+`edges`, `methodology`, `requirements/{rid}/variables`, `transformations`, `steps`, `contributions`, `citations` CRUD; plus `/api/v1/submissions`.
- `thumbs.py` (`/api/v1/datasets/{id}/thumbnail`, `POST /thumbnails`, `POST /info`): on-demand og:image/twitter:image extraction — SSRF-guarded, robots.txt-aware, rate-limited, size-capped, stores URL only (never mirrors/hosts images).
- `kits.py`: `GET /api/v1/kits`, `GET /kits/{slug}`, `POST /kits/{slug}/instantiate` (creates full project graph: questions+aims+methods+requirements+provenance note).
- `harvest.py`: source registry CRUD + `POST /sources/{sid}/run` (live CKAN adapter, metadata-only, staging-only), `POST /resolve` (CKAN portal resolver, exactly-1-match rule), `GET /staging`.
- `ai.py`: 14-tool provider-neutral gateway (`GET /api/v1/ai/status|tools`, `POST /tools/{name}`, `/draft`, `/chat`). Deterministic by default; LLM call only if `INQETRA_AI_PROVIDER`+`INQETRA_AI_API_KEY` set.
- `admin.py` added: `GET/PATCH /admin/rules`, `POST /admin/rules/test`, `GET /admin/submissions`, `POST /admin/submissions/{id}/moderate`, `GET/PATCH /admin/kits`; `link-check` now persists `LinkCheck` rows.
- `compat.py` honours `active_rules()`; `evaluate.py` persists `CompatResult`.
- `projects.py` `get_project` returns all new nested entities + 9-dimension readiness. `reports.py` citations now Harvard/APA/BibTeX/RIS.
- `__init__.py` v0.2.0 registers all routers; boots clean (verified `healthz`, `/api/v1/kits`, `/api/v1/admin/rules` on :8123).

**Frontend (Next.js + TS, `apps/web/`) — NEW files written, NOT yet typechecked/built:**
- `lib/api.ts` extended (+15 hooks). `components/thumb.tsx` (ThumbImg + SVG placeholder), `components/reveal.tsx` (Reveal/CountUp, reduced-motion-safe), `components/chrome.tsx` now has working **BASKET drawer button** + drawer (add/remove/save-to-project). `hooks/hooks.tsx` basket now stores `{id,title}[]`, migrates v1, cross-tab events.
- `styles/motion.css` (Neo-Brutalist motion, `prefers-reduced-motion` kill-switch) imported in `layout.tsx`.
- New routes: `/datasets/all` (A–Z divided by domain, thumbnails, basket buttons), `/projects/new` (6-step wizard), `/kits/[slug]` (detail + instantiate), `/publishers/[name]` (publisher page).

**KNOWN FLAWS TO FIX (from user acceptance feedback):**
- Buttons/pages were reported "not opening" — this was partly the OneDrive build stall + one stale build; MUST re-verify every route/button after a clean build (see §3).
- Basket must fully work: drawer button, add/remove on every card, save-to-project, and a **basket data report** (per-requirement coverage) — partially built, needs finish + verify.
- User wants "a page for all datasets and divided" → `/datasets/all` exists; verify + polish.
- User wants "a page for the functions of writing / when starting a new project" → `/projects/new` wizard exists; wire the homepage hero + "START PROJECT" buttons to it, then verify.
- User wants "simple motion graphics to elements" → `motion.css` + Reveal/CountUp exist; apply + verify reduced-motion.
- User wants dataset **preview pictures** scraped from landing pages into cards → `thumbs.py` + `ThumbImg` exist; verify robots behaviour + fallback + batch warm.

---

## 2. REMAINING TODO (exact order)

1. **Backend tests (extend)** — add pytest coverage for every new endpoint (list in §5). Run green.
2. **Frontend typecheck + build** — `cd $DST/apps/web && npm install && npm run typecheck && NEXT_PUBLIC_API_URL=http://localhost:8123 npm run build` (expect 25+ pages).
3. **Fix any compile/type errors** in the 4 new pages + chrome/hooks/thumb/reveal.
4. **Wire entry points:** `/` hero "START PROJECT →" and "Start a Research Project" button → `/projects/new`; `MY PROJECTS` "New project" form → keep + add "GUIDED WIZARD" link to `/projects/new`.
5. **Studio (`/projects/[id]/studio`):** add new sections/editors for the studio.py entities — kgaps list+add, concept graph (nodes/edges + drag positions), methodology form, transformation list+add, analysis-steps pipeline (stage/order), citations list+add+delete (4 formats + download), contributions list+add. Reuse existing section pattern.
6. **Basket report:** new page `/basket/report` (or section in `/basket`) — per-project: basket items × requirements coverage table, `POST /evaluate` results, access/licence readiness, gaps per item; CTA "Generate Data Plan". Also show on `/projects/[id]/report`.
7. **Admin page polish:** rules editor (toggle active/severity, "test fixtures" button showing scoped overall), submissions moderation (accept/reject with notes → still never publishes), staging queue view, source run button + runs log, resolver runner for collection/search records.
8. **Map page:** verify Leaflet CDN CSS/JS actually load (currently `<link>` injected mid-component — move to layout or next/head), add dataset coverage summary panel; keep "map is not the only route".
9. **AI copilot (optional):** small chat panel on studio (or `/projects/[id]/copilot`) calling `POST /api/v1/ai/chat`; disabled-state copy when no provider; never fabricates.
10. **Thumbnails:** batch warm `/datasets/all` (call `POST /thumbnails` for visible set), confirm hotlinking works cross-origin (some publishers block hotlink — placeholder covers), confirm robots/responsible behaviour documented.
11. **Motion QA:** ensure no content is hidden without JS or under reduced motion; ensure 44px targets, focus-visible violet, keyboard matrix unchanged.
12. **Responsive + a11y pass:** 1440/1024/768/390; keyboard walk of studio matrix + basket drawer; print CSS.
13. **Full verification** (§3) then **update `FULL_QA_REPORT.md`, `CHANGELOG.md`, `DECISIONS.md`, `ROUTE_COMPONENT_HOOK_INVENTORY.md`** with new routes/components and final commands/timestamps.
14. **Docker compose up** (`docker compose up --build`) — verify web+api+db+redis boot; PostGIS via `DATABASE_URL`; SQLite remains dev default.
15. **Do NOT deploy or submit externally** without explicit author instruction.

---

## 3. VALIDATION GATES (all must pass before you declare done)

```bash
# 1. Dataset gate (751 records, 0 unreachable) — rerun, keep output
cd INQETRA_AI_BUILD_PACK
python3 scripts/validate_catalogue_links.py --input data/datasets_seed.csv --output-dir data/link_health --workers 12 --timeout 20
# → unreachable_record_count MUST be 0. Never delete records to pass.

# 2. Backend tests
INQETRA_NOCACHE=1 DATABASE_URL="sqlite:////tmp/inq_ci.db" /tmp/inqvenv/bin/python -m pytest apps/api/tests -q -p no:cacheprovider
# → all pass (extended suite, §5). Run inside $DST if OneDrive stalls.

# 3. Frontend
cd $DST/apps/web && npm run typecheck && NEXT_PUBLIC_API_URL=http://localhost:8123 npm run build   # 0 errors, 25+ routes

# 4. Live smoke (API on :8123, web `npm run start` on :3000)
curl -s localhost:8123/healthz && curl -s "localhost:8123/api/v1/datasets?limit=1"   # total:751
curl -s localhost:8123/api/v1/health                                                # unreachable_record_count:0
# For EVERY route in ROUTE_COMPONENT_HOOK_INVENTORY.md: HTTP 200 and meaningful content:
for r in / /datasets /datasets/all /map /compare /basket /basket/report /projects /projects/new \
  /kits /kits/urban-heat-island /sources /publishers /publishers/Met%20Office /methodology /about \
  /developers /settings /admin; do echo -n "$r → "; curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:3000$r"; done
# Then exercise the GOLDEN JOURNEY end-to-end (create project → … → export) via curl + browser.

# 5. Parity + data-acceptance (pytest covers; spot check)
# CSV/JSON/MD parity, every record has landing_url/publisher/link_type/verification_state/review date,
# filters climate/weather/climate-change/environment/air-quality/flooding/buildings/housing/
# building-performance/energy-carbon/planning/geospatial each return >0.

# 6. A11y / responsive manual pass + job-failure state (`POST /api/v1/jobs/exports {"simulate":"fail"}` → status failed, catalogue still 200).
```

---

## 4. FILE MAP (paths to touch)

**Backend `apps/api/`**
- `inqetra/store.py` — schema (do not drop tables; additive migrations only)
- `inqetra/bootstrap.py` — defaults seeding
- `inqetra/catalogue.py`, `domain_filter.py` — catalogue/search (stable)
- `inqetra/projects.py`, `studio.py` — project CRUD + new entities
- `inqetra/evaluate.py`, `compat.py` — compatibility/gaps
- `inqetra/inbox.py`, `harvest.py` — candidates + harvester/resolver
- `inqetra/reports.py`, `jobs.py` — abstracts/exports/citations/jobs
- `inqetra/ai.py` — 14-tool gateway
- `inqetra/admin.py` — rules/submissions/kits/link-check
- `inqetra/thumbs.py` — thumbnail extraction
- `inqetra/kits.py` — kit instantiate
- `inqetra/seed.py` — CSV loader + parity views
- `inqetra/__init__.py` — app assembly
- `tests/test_inqetra.py` — extend here or add `tests/test_studio.py`, `test_harvest.py`, `test_ai.py`, `test_thumbs.py` (mock `httpx`), `test_kits.py`
- `requirements.txt`, `Dockerfile`

**Frontend `apps/web/`**
- `app/layout.tsx`, `app/page.tsx` (wire wizard), `app/datasets/page.tsx`, `app/datasets/all/page.tsx`, `app/datasets/[id]/page.tsx`, `app/compare/page.tsx`, `app/map/page.tsx`, `app/basket/page.tsx` (+ `/basket/report`), `app/projects/page.tsx`, `app/projects/new/page.tsx`, `app/projects/[id]/studio/page.tsx`, `app/projects/[id]/{notes,abstract,report,gaps,candidates}/page.tsx`, `app/kits/page.tsx`, `app/kits/[slug]/page.tsx`, `app/sources/page.tsx`, `app/publishers/page.tsx`, `app/publishers/[name]/page.tsx`, `app/methodology/page.tsx`, `app/about/page.tsx`, `app/developers/page.tsx`, `app/settings/page.tsx`, `app/admin/page.tsx`
- `components/chrome.tsx`, `components/thumb.tsx`, `components/reveal.tsx`
- `hooks/hooks.tsx`, `lib/api.ts`
- `styles/{tokens,components,maps,charts,motion,app}.css`
- `public/logo.png`, `package.json`, `tsconfig.json`, `next.config.js`, `Dockerfile`

**Root**
- `docker-compose.yml`, `README.md`, `INVENTORY.md`, `DECISIONS.md`, `CHANGELOG.md`, `FULL_QA_REPORT.md`, `MIGRATION_MAP.md`, `ROUTE_COMPONENT_HOOK_INVENTORY.md`, `data/seeds/*` (751 parity copies), `assets/inqetra-logo-mark-v2.png`

---

## 5. REQUIRED NEW TESTS (add to `apps/api/tests/`)

| Test | Endpoint | Assert |
|---|---|---|
| `test_studio_graph` | POST kgaps/concepts/edges, GET graph, PATCH move | nodes+edges persisted, move applies |
| `test_studio_methodology_steps` | POST methodology, steps (order), transformations | ordered list returned |
| `test_kits_instantiate` | POST /kits/{slug}/instantiate | project created with ≥1 question/aim/method/requirement + provenance note; **no catalogue copy** |
| `test_thumbs_mock` | GET /datasets/{id}/thumbnail (mock httpx to return og:image html) | image_url stored, hotlink note, robots-aware |
| `test_ai_tools` | POST /ai/tools/search_datasets, get_project, find_data_gaps | provenance fields present; no invention (compare against seed) |
| `test_harvest_ckan_mock` | POST /sources (CKAN) + run (mock httpx JSON) | HarvestRecord + DatasetCandidate staged, status done, catalogue total unchanged (751) |
| `test_resolver` | POST /resolve on a collection record | exactly-1 match → staged; 0/>1 → unresolved; never published |
| `test_rules_fixture` | POST /admin/rules/test + PATCH toggle | overall changes reflect active_rules; fixture deterministic |
| `test_submissions` | POST /submissions, moderate accepted/rejected | never `published_to_catalogue=True` |
| `test_basket_report` | evaluate + report-model after basket add | coverage rows present; access/licence warnings factual |

Also keep green: `test_catalogue_minimum_count`, parity, required-fields, 12 filters, golden journey, job-failure, crawler-guard.

---

## 6. DEFINITION OF DONE (do not claim done early)

- [ ] All §2 todos complete; §3 gates green with recorded outputs/timestamps.
- [ ] Every route in the inventory deep-links and every primary button works (browser-verified).
- [ ] Golden journey works end-to-end with **persistent DB state** (SQLite file, PostGIS via `DATABASE_URL`).
- [ ] 751 datasets remain; CSV/JSON/MD parity; link-health report current; `unreachable_record_count=0`.
- [ ] Basket drawer + add/remove/save-to-project + basket data report all verified.
- [ ] Wizard `/projects/new` reachable from home and creates a working project.
- [ ] Dataset preview pictures show (publisher og:image hotlink OR deterministic placeholder) with robots/SSRF notes; never mirrors data.
- [ ] Motion is additive and fully disabled under `prefers-reduced-motion`; no content hidden without JS.
- [ ] `FULL_QA_REPORT.md` rewritten with exact commands, timestamps, PASS sources, failures and any `BLOCKER`.
- [ ] Nothing deployed/submitted externally without explicit author instruction.