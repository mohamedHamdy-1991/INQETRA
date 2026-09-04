# Source Registry

The crawler must never "scrape the internet" indiscriminately. All scheduled harvesting originates from a controlled Source Registry.

## Required source fields
`id, name, base_url, source_type, adapter, trust_level, active, cadence, rate_limit, robots_policy, terms_notes, authentication_mode, licence_notes, geographic_scope, owner, contact, last_run_at, next_run_at, kill_switch, config_json`

## Priority order
Tier A: government/statutory publisher structured API/feed. Tier B: authoritative institutional/catalogue source with access conditions. Tier C: academic repositories. Tier D: community submissions pending review.

## Initial registry
See `data/source_registry.csv`.

## Key rules
- data.gov.uk: CKAN metadata index; do not assume directory licence equals resource licence.
- Planning Data: structured England planning/housing source; preserve source/provider information.
- ONS Open Geography: resolve ArcGIS item IDs, keep generalisation/version/coverage explicit.
- OS: separate OpenData from premium/licensed products.
- Digimap: metadata/deep link only for subscription resources unless explicit licence enables more.
- Environment Agency/Defra: resolve current resource UUIDs from the working portal before publishing; prefer OGC/API/full download metadata and capture CRS/bbox.
- CEDA/Met Office: preserve dataset version and citation.
