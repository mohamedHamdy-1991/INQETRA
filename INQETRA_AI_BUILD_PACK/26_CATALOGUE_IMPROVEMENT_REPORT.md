# Catalogue Improvement Report — 4 September 2026

## Result

The INQETRA seed catalogue now contains **751 unique records**. The final reproducible health run at `2026-09-04T11:48:35+00:00` checked 447 unique landing URLs across all 751 records and reported:

| Check | Result |
|---|---:|
| Seed records | 751 |
| Unique catalogue landing URLs | 447 |
| Reachable records | 751 |
| Unreachable records | 0 |
| Reachable unique URLs | 447 |
| Unreachable unique URLs | 0 |

The record-level evidence is in `data/link_health/catalogue_link_health.csv`; the machine-readable summary is `data/link_health/catalogue_link_health_summary.json`.

For direct use outside the application, `data/INQETRA_751_DATASETS_WITH_TESTED_LINKS.csv` joins the full metadata seed to each tested landing URL, final URL, HTTP status and check timestamp.

## Changes made

- Added 14 authoritative UK entries concentrated on housing condition, building energy performance, housing vulnerability, local greenhouse-gas emissions, climate projection, extreme rainfall, climate-related ground hazard, air-quality monitoring/statistics, forest air-quality monitoring and future river-flow modelling.
- Repaired 24 dead or health-check-blocked legacy URLs by replacing them with working official collection/portal pages. These rows are explicitly labelled `collection_record_link_checked`; they still require a resolver to establish an individual current resource before production publication.
- Rebuilt `datasets_seed.json` and `DATASET_CATALOGUE.md` directly from the CSV authority and verified CSV/JSON parity and unique IDs.
- Added a reusable HTTP validation tool at `scripts/validate_catalogue_links.py` and an idempotent upgrade script at `scripts/upgrade_climate_built_environment_seed.py`.
- Corrected the Defra source-registry portal endpoint after the old `/dataset/` path returned 404.

## Interpretation boundary

“Reachable” means the specified public landing page returned HTTP 200–399 at the test time. It does not demonstrate data-download availability, rights of reuse or redistribution, metadata accuracy, scientific fitness for a study, or a completed source-specific resolver/curation pass. Those remain required before a record is published as fully verified metadata.

## Re-run

```bash
cd INQETRA_AI_BUILD_PACK
python3 scripts/validate_catalogue_links.py --input data/datasets_seed.csv --output-dir data/link_health --workers 12 --timeout 20
```
