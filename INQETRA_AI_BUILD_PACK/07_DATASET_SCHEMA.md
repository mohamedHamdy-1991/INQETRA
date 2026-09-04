# Canonical Dataset Metadata Schema

## Identity
`id, slug, title, alternate_titles[], short_description, full_description, status`

## Publisher
`publisher_id, publisher_name, publisher_type, authoritative_flag, publisher_url`

## Classification
`domains[], topics[], keywords[], research_roles[], methods_supported[]`

## Geography
`countries[], nations[], admin_areas[], bbox, coverage_geometry, geographic_description, spatial_unit, spatial_scale`

## Time
`start_date, end_date, temporal_resolution, update_frequency, latest_release_date, reference_period`

## Variables
Each: `canonical_name, source_name, label, unit, datatype, description, vocabulary_id, role_hint`

## Spatial
`spatial_resolution_value, spatial_resolution_unit, crs, geometry_type, topology_state`

## Access
`landing_page_url, download_urls[], api_urls[], docs_urls[], access_type, registration_required, entitlement_required, access_notes`

## Formats
`format_code, mime_type, compression, api_protocol`

## Licence
`licence_id, licence_name, licence_url, reuse_allowed, commercial_reuse, redistribution, derivatives, attribution_required, verified_state, source_text`

## Provenance
`source_catalogue, source_id, source_record_id, source_first_seen, source_last_checked, source_snapshot_hash, ingestion_method, field_provenance{}`

## Quality/health
`metadata_score, broken_link_state, freshness_state, curator_status, verification_state, conflict_state`

## Citation
`authors_or_org, publication_year, release_date, version, doi_or_identifier, suggested_citation`

## Relationships
`replaces, replaced_by, derived_from, companion_to, alternative_to, overlaps_with, joinable_via`

## Important
`verification_state` is not optional. Field-level values derived by AI or inference require provenance and may not overwrite publisher metadata silently.
