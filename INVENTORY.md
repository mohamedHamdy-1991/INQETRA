# INQETRA — Repository Audit (2026-09-04)

Target root: `/Users/mohamedali/Library/CloudStorage/OneDrive-LeedsBeckettUniversity/Work/GITHUB REPO/INQETRA`

## What exists at root (pre-implementation)

| Path | Type | Verdict |
|---|---|---|
| `INQETRA_AI_BUILD_PACK/` | spec + seed pack (35 entries: 00–26 specs, `data/`, `design/`, `prototype/`, `scripts/`, `assets/`, `reference/`) | AUTHORITATIVE INPUT. Do not edit. App copies derived artefacts out; pack stays read-only. |
| `INQETRA_AI_BUILD_PACK.zip` | zipped duplicate of pack | Preserve. Not used by build. |
| `neo_brutalism_tokens.css` | loose token CSS (root) | Superseded by `INQETRA_AI_BUILD_PACK/design/inqetra_tokens.css`. Preserved; new app uses `apps/web/styles/tokens.css` copied from pack. |
| `neo_brutalist_ai_migration_prompt.txt` | loose migration note | Preserve. Informational only. |
| `neo_brutalist_web_design_system.html` / `.pdf` | loose reference design system | Preserve. Reference only; canonical tokens are pack `13_DESIGN_SYSTEM.md` + `design/*`. |
| `assets/inqetra-logo-mark-v2.png` (required by brief) | lives at `INQETRA_AI_BUILD_PACK/assets/inqetra-logo-mark-v2.png` (1254×1254, SHA-256 `d2abca05…`), NOT at root `assets/` | Copied to `assets/inqetra-logo-mark-v2.png` + `apps/web/public/logo.png` without alteration. |
| `data/*.csv` (required by brief as `data/...`) | lives at `INQETRA_AI_BUILD_PACK/data/` only; root has NO `data/` dir | Canonical seed stays in pack; app consumes via `data/seeds/` copies with provenance header. Root `data/` NOT created to avoid forked truth — see DECISIONS.md D-03. |
| App code (`apps/web`, `apps/api`, `docker-compose.yml`, DB) | ABSENT | Greenfield build (this worker). |
| `DECISIONS.md`, `CHANGELOG.md`, `FULL_QA_REPORT.md` | ABSENT | Created by this worker at root. |

## Dataset gate — 2026-09-04 ~12:59 UTC (re-run by worker)

Command:

```bash
cd INQETRA_AI_BUILD_PACK
python3 scripts/validate_catalogue_links.py --input data/datasets_seed.csv --output-dir data/link_health --workers 12 --timeout 20
```

Result (fresh run, overwrote `data/link_health/*` inside pack):

```json
{
  "checked_at_utc": "2026-09-04T11:59:36+00:00",
  "record_count": 751,
  "unique_url_count": 447,
  "reachable_record_count": 751,
  "unreachable_record_count": 0,
  "reachable_unique_url_count": 447,
  "unreachable_unique_url_count": 0
}
```

Gate: **PASS — `unreachable_record_count` is 0. Implementation authorised. No records deleted or edited.**

## Seed shape (measured, not assumed)

- 751 rows, 751 unique `id`s (`inq-0001…`), 447 unique `landing_url`s.
- Columns: `id,title,publisher,source_portal,country,uk_nation,domain,subdomain,research_roles,methods_supported,spatial_scale,temporal_resolution,coverage,formats,access_type,licence,authority_level,landing_url,link_type,verification_state,variables,notes,last_catalogue_review`.
- No empty `id/title/publisher/landing_url/link_type/verification_state/access_type/licence/last_catalogue_review`. `variables` mostly empty (expected — variable browser is a project-level requirement feature, not seed truth).
- `link_type`: official_collection 311, official_search_query 270, direct_dataset 139, + product_catalogue/profile/api/service long tail. Collection/search records MUST NOT be silently upgraded — UI labels them as such.
- `verification_state`: 14 distinct states, truthfully mixed (indexed/partition/verified/collection). App preserves verbatim.
- `domain` top values: Geospatial/GIS 312, Weather & Climate 180, Planning & Development 105. Required acceptance filters (climate, weather, climate change, environment, air quality, flooding, buildings, housing, building performance, energy/carbon, planning, geospatial) are covered by `domain`+`subdomain`+`title` keyword mapping in the API (`packages: domain_filter.py`), because the seed's single `domain` column under-represents multi-domain records — the mapping is explicit, tested, and never rewrites stored metadata.
- Prior health report (`26_CATALOGUE_IMPROVEMENT_REPORT.md`, 2026-09-04T11:48Z) claimed 751/0; worker re-run confirms 751/0 at 11:59Z.

## Interpretation boundary (carried into UI + data model)

HTTP 200–399 on a landing page ≠ download access, licence permission, scientific fitness, or resolved metadata. Every dataset view carries this caveat; `verification_state`/`link_type` are shown verbatim with `last_catalogue_review` + link-health `checked_at/final_url/status`.
