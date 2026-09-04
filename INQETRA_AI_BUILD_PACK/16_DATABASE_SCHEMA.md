# Database Schema Blueprint

Core tables:
`users, publishers, sources, source_runs, harvest_records, dataset_candidates, datasets, dataset_versions, dataset_access, licences, dataset_licences, dataset_geographies, dataset_temporal, dataset_formats, variables, dataset_variables, tags, dataset_tags, dataset_relationships, link_checks, projects, research_problems, knowledge_gaps, research_questions, aims, objectives, hypotheses, concepts, concept_relationships, methodologies, methods, variable_requirements, dataset_requirements, rq_aim_links, aim_objective_links, aim_method_links, method_requirement_links, aim_dataset_links, requirement_dataset_matches, project_datasets, transformations, analysis_steps, notes, results, contributions, citations, abstract_drafts, compatibility_rules, compatibility_results, research_kits, kit_nodes, kit_links, submissions, audit_log`.

Use UUID primary keys, `created_at/updated_at`, soft-delete/status where needed. PostGIS geometries use explicit SRID. Raw source metadata stored in version/snapshot tables, not flattened away.

Field provenance table recommended:
`metadata_field_provenance(id,dataset_version_id,field_path,value_hash,source_type,source_url,evidence_text,retrieved_at,confidence_state)`.
