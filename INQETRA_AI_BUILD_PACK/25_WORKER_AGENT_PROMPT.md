# INQETRA — Worker-Agent Implementation Prompt

You are the implementation worker for INQETRA. Work only inside:

`/Users/mohamedali/Library/CloudStorage/OneDrive-LeedsBeckettUniversity/Work/GITHUB REPO/INQETRA`

## Your authority and objective

Implement a runnable, testable INQETRA application: a UK-centred research-design studio and a climate, environment, buildings and built-environment dataset hub. The authoritative product contract is this build pack. Do not reinterpret it as a generic catalogue or an AI writing app.

Read, in order:

1. `00_START_HERE.md`
2. `01_MASTER_BUILD_PROMPT.md`
3. `02_PRODUCT_SPECIFICATION.md` through `22_CONTENT_MODEL_COPY.md`
4. `25_WORKER_AGENT_PROMPT.md` (this instruction)
5. `data/datasets_seed.csv`, `data/source_registry.csv`, and `data/link_health/catalogue_link_health_summary.json`

## Dataset gate — do this before app work

The supplied seed is a staging catalogue of **751** records. It is weighted toward climate, environmental exposure, air quality, flood risk, building stock, housing condition, energy/carbon, planning and spatial analysis. It contains direct dataset records as well as explicitly labelled official collection/search/family records. Do not silently upgrade a collection record into a direct dataset.

Run:

```bash
cd INQETRA_AI_BUILD_PACK
python3 scripts/validate_catalogue_links.py --input data/datasets_seed.csv --output-dir data/link_health --workers 12 --timeout 20
```

Required result: `unreachable_record_count` must be `0`. If it is non-zero, repair only by locating an authoritative working replacement and preserve the truthful `link_type`, `verification_state`, evidence note and check date. Re-run the checker. Do not delete records to make the check pass. A 200–399 landing-page response does **not** prove the resource, licence, coverage or methodology; retain that distinction in the UI and data model.

Before first deployment, use a source-specific resolver to convert any `official_collection`, `official_search_query`, `official_product_catalogue`, `collection_record_link_checked`, or `indexed_family_from_official_portal` record into a resolved candidate with immutable source snapshot and field-level provenance. Ambiguous results go to curation, never direct publish.

## Build requirements

1. Audit the existing repository first. Create `DECISIONS.md`, `CHANGELOG.md`, a route/component/data-hook inventory, and an old-to-new mapping before changing code. Preserve unknown files.
2. Keep the app runnable after every vertical slice. Use the canonical stack: Next.js/TypeScript frontend, FastAPI backend, PostgreSQL/PostGIS, and a local Docker Compose path. Do not substitute mock-only local state for persistent project state.
3. Implement the complete golden journey: create project → research problem → RQs → aims/objectives → methodology → dataset requirements → catalogue discovery → basket → Aim×Dataset assignment → compatibility → data gaps → candidates → comparison → notes/results → evidence-traced abstract → research data-plan export.
4. Use the supplied Neo-Brutalist design system exactly. No generic rounded SaaS dashboard, gradients or glass effects. Ensure keyboard access, responsive 1440/1024/768/390 layouts, reduced motion and WCAG 2.2 AA.
5. Make requirements first-class before matching datasets. Build deterministic, explainable compatibility/coverage logic for geography, spatial and temporal resolution, identifiers, units, formats, access and licence. Never label mechanical compatibility as methodological validity.
6. Keep AI optional and provider-neutral. It may structure or draft from project state but must never invent datasets, licences, results, methods, citations or source facts. Every dataset claim needs dataset ID, field and source provenance.
7. Do not mirror third-party bulk data. Store official metadata, links, source snapshots/provenance and health checks only, unless explicit reuse terms permit otherwise.

## Non-negotiable data acceptance tests

- CSV, JSON and Markdown catalogue views remain in parity; IDs are unique.
- Catalogue count is never below 751.
- Every seed has a non-empty authoritative landing URL, `link_type`, `verification_state`, publisher and last review/check date.
- The checked landing URL response is 200–399 at validation time. Record the check timestamp, final URL, status and error when a check fails; do not replace evidence with a green badge.
- Licence/access is source-declared or `Unknown`; never inferred from public accessibility.
- Search and filters expose climate, weather, climate change, environment, air quality, flooding/hazards, buildings/housing, building performance, energy/carbon, planning and geospatial domains.
- Catalogue records cannot be published from raw crawler output without provenance, link health and validation.

## Required verification and handoff

Run type checking, unit tests, API tests, end-to-end golden-journey tests, link-health validation and an accessibility pass. Test the database writes, background-job failure state, exports, keyboard navigation and the four target widths. Write `FULL_QA_REPORT.md` with exact commands, timestamps, test results, known limitations and the source of every PASS claim.

Stop and report `BLOCKER` rather than inventing data if a licence, source identity, credentials, deployment destination, API key or migration decision is missing. Never submit or deploy externally without explicit author instruction.
