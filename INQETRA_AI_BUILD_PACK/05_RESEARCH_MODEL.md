# Research Model

## Core entities
Project; ResearchProblem; KnowledgeGap; ResearchQuestion; Aim; Objective; Hypothesis; Concept; ConceptRelationship; Methodology; Method; VariableRequirement; DatasetRequirement; Dataset; DatasetVariable; DatasetAssignment; DatasetRelationship; Transformation; AnalysisStep; Note; Result; Contribution; Citation; AbstractDraft.

## RQ fields
`id, project_id, order, text, question_type, population_unit, exposure, outcome, geography_json, start_date, end_date, keywords, hypothesis_id, status, notes`

## Aim fields
`id, project_id, order, title, statement, expected_output, status`

## DatasetRequirement fields
`id, project_id, title, research_role, required_variables_json, geography_json, temporal_json, desired_spatial_scale, desired_resolution, desired_crs, preferred_identifiers_json, preferred_formats_json, access_preferences_json, licence_preferences_json, requirement_level`

## Relationship fields
All relationship tables must include: `relationship_type`, `rationale`, `created_by_type`, `created_by_id`, `confidence_state`, `created_at`, `updated_at`.

## Research readiness
Display independent dimensions only: question completeness, aim alignment, method coverage, dataset-role coverage, variable coverage, spatial compatibility, temporal compatibility, access/licence readiness, reproducibility. Do not collapse into a scientific-quality score.
