# Crawler & Harvester Specification

## Adapter priority
1 CKAN; 2 DCAT; 3 ArcGIS Hub/REST; 4 OGC API/WFS/WMS; 5 STAC; 6 Socrata; 7 JSON/XML/CSV index; 8 repository API; 9 sitemap; 10 permitted HTML parser.

## Pipeline
Source Registry trigger → fetch metadata only → raw immutable snapshot → canonical parse → licence/date/geography/format/publisher normalisation → source fingerprint → duplicate detection → URL health → field-level provenance → validation → staging → trusted auto-publish or moderation → audit event.

## Candidate search
Project `Find Data` can query external approved sources on demand. Candidate results never enter production catalogue directly.

## Legal/technical safeguards
Robots/terms compliance; per-domain rate limits; exponential backoff; descriptive user-agent/contact; no auth bypass; no bulk data mirroring by default; SSRF allowlist/denylist; maximum response size; content-type validation; source kill switch; idempotent jobs; retry quarantine; immutable audit log.

## Resolver
`official_search_query` seed records require a resolver that searches the same authoritative portal and stores the unique current item URL/ID. If 0 or >1 matches, remain unresolved and enter curation queue.
