# AI Research Copilot

## Principle
AI helps structure, explain and draft. Deterministic project state and authoritative metadata remain canonical.

## Context package
Project graph; RQs; aims; methods; requirements; selected datasets; variables; notes; explicit Result objects; compatibility outputs; source URLs; citations.

## Allowed actions
Improve wording while preserving meaning; detect overlap; suggest missing structural links; convert method to requirements; search internal catalogue; request external candidate search; explain warnings; draft acquisition/method text; draft abstract from project facts; summarise source documentation; propose alternatives.

## Forbidden actions
Invent dataset fields/links/licences/coverage; infer reuse permission; fabricate results; imply download occurred; overwrite official metadata; assert scientific quality from metadata; invent references.

## Evidence trace
Each factual dataset claim has `dataset_id + field + provenance source`. Each abstract sentence has a source map to Project/RQ/Aim/Method/Dataset/Result/Note objects where feasible.

## Provider architecture
`AIProvider` interface with tool calling, structured output, token budget and audit record. Local/cloud providers can be swapped. Product must degrade gracefully to deterministic UI.
