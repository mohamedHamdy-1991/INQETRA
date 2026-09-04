# INQETRA — Master Autonomous Build Prompt

You are the lead product architect, senior full-stack engineer, data-platform engineer, GIS engineer, UX designer and QA owner for **INQETRA**.

Your task is to implement the complete application described by this repository. Do not treat these documents as inspiration. Treat them as a product contract.

## 1. Product purpose
Build a production-quality, open-source research-design and UK dataset-discovery platform. The platform must help researchers transform an initial research problem into a defensible research architecture and executable data plan.

Canonical workflow:

**Research Problem → Knowledge Gap → Research Questions → Aims → Objectives → Hypotheses → Methodology → Methods → Dataset Requirements → Dataset Discovery → Project Basket → Dataset Assignment → Compatibility → Analysis Plan → Notes/Results → Abstract → Research Data Plan.**

## 2. Hard constraints
1. INQETRA must remain useful without a generative-AI provider.
2. Deterministic metadata, compatibility, provenance, ranking and project-state logic are canonical.
3. AI is optional, provider-neutral and tool-driven.
4. Never invent dataset properties, licences, coverage, variables, source URLs, methods, results or citations.
5. Never treat a public download as permission to redistribute.
6. Do not mirror third-party datasets by default. Store metadata, provenance and authoritative links.
7. Never bypass login, paywall, institutional subscription, CAPTCHA, robots or rate limits.
8. PostgreSQL + PostGIS is canonical storage.
9. Every published dataset must have source provenance and `last_checked_at`.
10. Every AI-derived metadata field must be labelled `AI_SUGGESTED` until evidence is attached and validation occurs.
11. Aim/RQ/method/dataset relationships must be real database relations, not generated text only.
12. No abstract generator may fabricate results. If results are absent, use proposal/future tense or leave the results section explicitly unresolved.
13. WCAG 2.2 AA is a release requirement.
14. All interaction must work on desktop, tablet and mobile.

## 3. Research model
Implement first-class entities for Project, ResearchProblem, KnowledgeGap, ResearchQuestion, Aim, Objective, Hypothesis, Methodology, Method, VariableRequirement, DatasetRequirement, Dataset, DatasetVariable, DatasetAssignment, Transformation, AnalysisStep, Note, Result, Contribution, Citation and AbstractDraft.

Implement many-to-many matrices:
- RQ × Aim
- Aim × Objective
- Aim × Method
- Method × Dataset Requirement
- Aim × Dataset
- Dataset × Variable Requirement

Every matrix cell has `relationship_type`, `rationale`, `status`, `created_by` and timestamps.

## 4. Research Design Studio
Create a persistent project rail:
01 Research Problem
02 Research Questions
03 Aims & Objectives
04 Hypotheses
05 Conceptual Framework
06 Methodology
07 Dataset Requirements
08 Dataset Basket
09 Aim × Dataset Matrix
10 Analysis Plan
11 Notes
12 Literature / Citations
13 Data Gaps
14 Abstract Builder
15 Research Data Plan
16 Export

Show Research Readiness as component coverage, never as scientific quality.

## 5. Dataset requirement logic
A dataset requirement is defined before a dataset is chosen. Capture role, variables, geography, date range, desired scale, resolution, CRS, identifiers, formats, licence/access preferences, linked aims and methods. Match catalogue candidates against requirements using explicit explainable scores.

## 6. Dataset hub
Use the canonical schema in `07_DATASET_SCHEMA.md` and taxonomy in `06_DATASET_TAXONOMY.md`.

Search facets must include domain, topic, geography, time, spatial scale, temporal resolution, variable, format, access, licence, publisher, authority, method, research role, update frequency, open-only, API, registration and metadata completeness.

Search ranking label = **Search relevance**, never "best dataset".

## 7. Basket
Persistent across catalogue, map and project views. Support add/remove, project role, aim assignment, requirement assignment, rationale, notes, required/recommended/optional status, compare, alternative and replacement.

## 8. Compatibility engine
Deterministic rules for:
- geography overlap;
- spatial granularity;
- CRS transformability;
- temporal overlap;
- temporal resolution;
- join identifiers;
- units;
- formats;
- access constraints;
- licence/reuse constraints;
- freshness/version mismatch;
- missing variables;
- research-role coverage.

Warnings never imply methodological validity; they explain mechanical/data compatibility.

## 9. Data Gap Radar
For every Aim and Method, evaluate required roles and variables against selected datasets. Classify each requirement: `COVERED`, `PARTIAL`, `MISSING`, `INCOMPATIBLE`, `RESTRICTED`, `UNKNOWN`. Every non-covered item has a `Find Data` action.

External search results go to Candidate Data Inbox and require resolution/validation before becoming catalogue records.

## 10. AI Copilot
Implement a provider-neutral gateway. Minimum tool contract:
`search_datasets`, `get_dataset`, `search_variables`, `compare_datasets`, `get_project`, `get_rq_alignment`, `get_aim_coverage`, `find_data_gaps`, `search_external_sources`, `explain_compatibility`, `generate_acquisition_plan`, `draft_methods`, `draft_abstract`, `trace_statement`.

AI responses must cite internal dataset IDs/source URLs for factual dataset claims.

## 11. Notes and abstract
Notes are typed and linkable to RQ/Aim/Method/Dataset/Variable/Result. Support Markdown, tables, URLs, equations and attachments.

Abstract modes: proposal, thesis, journal, conference, grant, extended abstract, plain-language summary. Controls: word limit, target venue, tense, structured/unstructured style. Sentence-level evidence trace where possible.

## 12. Crawler
Follow `10_CRAWLER_HARVESTER_SPEC.md`. Adapter priority:
CKAN → DCAT → ArcGIS REST → OGC API/WFS/WMS → STAC → Socrata → publisher JSON/XML/CSV → repository APIs → sitemap → permitted HTML.

A source registry controls cadence, trust, egress, legal notes and kill switch.

## 13. UK seed data
Import `data/datasets_seed.csv` into staging only. Preserve `verification_state` and `link_type`. Resolve `official_search_query` and `official_collection` records before elevating them to direct verified dataset records. Never silently upgrade confidence.

## 14. Design
Apply the supplied warm editorial Neo-Brutalist system everywhere. Use the exact tokens and component rules in `/design`. No gradients, glassmorphism, blurred shadows, generic soft SaaS cards or uncontrolled pill UI.

Semantic accents:
- Yellow = primary / attention
- Orange = operation / crawler / action
- Cyan = data / GIS / measurement
- Violet = research relationship / AI / selection
- Pink = warning / missing / exception
- Green = verified / compatible / success

Desktop uses ~240px left rail plus utility/search bar. Mobile uses drawer/bottom navigation. Minimum tap target 44px.

## 15. Required pages
Implement every route in `04_PAGE_BY_PAGE_SPECIFICATION.md`; do not stop at the landing page.

## 16. Stack
Next.js + TypeScript + React; FastAPI; PostgreSQL/PostGIS; Redis + Celery/Arq; PostgreSQL FTS first; MapLibre/Leaflet; ECharts/Plotly; S3-compatible object storage for metadata snapshots/reports only. Docker Compose local dev.

## 17. Definition of done
The following journey must work end-to-end with persistent state:
**create project → write question → create aims → choose methodology → derive dataset requirements → discover datasets → add to basket → assign datasets to aims → detect data gap → search candidates → compare → resolve compatibility → add notes/results → generate evidence-traced abstract → export research plan.**

Do not declare completion because pages render. Test routes, forms, keyboard use, mobile layouts, database writes, background jobs, exports and failure states.

## 18. Local target
When operating on Mohamed's Mac, project root is:
`/Users/mohamedali/Library/CloudStorage/OneDrive-LeedsBeckettUniversity/Work/GITHUB REPO/INQETRA`

Never delete unrelated repository files. Audit first, create a migration map, work in vertical slices, keep the repository runnable after each milestone, and maintain `CHANGELOG.md` + `FULL_QA_REPORT.md`.
