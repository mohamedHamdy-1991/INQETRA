# Page-by-Page Specification

Every page must implement loading, empty, partial, error, stale-data and success states; keyboard navigation; responsive layouts; analytics hooks; provenance where relevant.

## 1. Home `/`
**Purpose:** explain INQETRA and immediately start research or dataset discovery.
**Hero:** INQETRA wordmark, statement "Turn research questions into executable data plans", large research-question/search field, `Start a Research Project`, `Explore Datasets`.
**Secondary:** workflow strip Problem→Question→Aim→Method→Data→Plan→Abstract; live catalogue statistics; domain grid; featured Research Kits; three verified dataset cards; UK source ecosystem strip; trust/provenance explanation; CTA/footer.
**Interaction:** search suggestions switch between Research Question / Dataset / Variable / Publisher. `Start project` opens project starter modal.

## 2. Explore Datasets `/datasets`
Filter rail + result toolbar + card/table toggle. Query persists in URL. Filters: domain/topic/geography/time/scale/variable/format/access/licence/publisher/authority/method/role/freshness/API. Every result shows title, publisher, authority, one-line use, coverage, years, resolution, access, licence, freshness, metadata state, `Add to Basket`, `Compare`, `View`.

## 3. Dataset Detail `/datasets/[slug]`
Header; authority/source badges; provenance strip; Add/Compare/Favourite. Tabs: Overview, Variables, Geography, Time, Access, Licence, API, Documentation, Research Uses, Related, Compatibility, Versions, Provenance. Variable browser has search and `Add variable requirement`. Include Python/R/QGIS/API examples where source supports them. Citation export.

## 4. Data Map `/map`
Full-height map + left search/filter panel + right results drawer. Geography selection by place/postcode/UPRN/admin boundary, viewport, drawn polygon, buffer, GeoJSON upload. Display dataset coverage and resolution; never make map the only discovery route.

## 5. Compare `/compare`
2–4 dataset columns. Compare: authority, purpose, coverage, bbox, spatial unit/resolution/CRS, temporal extent/resolution, variables, identifiers, formats, API, bulk access, authentication, licence, reuse, update frequency, freshness, limitations, Aim coverage, join burden. Explain recommendation and differences with explicit rules.

## 6. Basket `/basket`
Persistent global drawer + full page. Group by requirement/aim/role. Dataset rationale; assignment; required/recommended/optional; compare; replace; duplicate warning. KPI: aim coverage, role coverage, spatial compatibility, temporal compatibility, licence readiness. CTA `Create/Update Project Data Plan`.

## 7. Projects `/projects`
Cards: title, research problem excerpt, last edit, RQ count, aim count, dataset count, readiness dimensions, unresolved gaps, export, duplicate, archive.

## 8. Research Studio shell `/projects/[id]/studio`
240px project subrail. Top strip with project title, geography, dates, readiness summary, save state, export. Central panel is section-specific; right Context Inspector shows linked objects and warnings.

## 9. Research Problem
Fields: background, problem statement, gap, significance, population/unit, geography, time, domain, key concepts, assumptions. AI actions: structure—not invent—problem/gap from notes.

## 10. Research Questions
Cards with question type, unit/population, exposure, outcome, geography, time, keywords, hypothesis, linked aims/methods/datasets. Duplicate/overlap warnings. Drag ordering. `Create aim from question`.

## 11. Aims & Objectives
Aim cards with objectives, required evidence, variables, methods, dataset roles, selected datasets, expected output, completion. Include editable RQ×Aim matrix.

## 12. Hypotheses
Hypothesis statement; null/alternative; linked RQ; variables; direction; test strategy; dataset requirements; status.

## 13. Conceptual Framework
Interactive node/edge graph using project concepts, exposures, mediators, outcomes, controls, datasets and methods. Nodes remain editable forms—not decorative diagram only.

## 14. Methodology
Research design selector; method library; per-method purpose, inputs, variables, data requirements, operations, software, validation, sensitivity, uncertainty, ethics, limitations, expected outputs. Editable Aim×Method matrix.

## 15. Dataset Requirements
Requirements-first table. Role, variables, geography, time, scale, resolution, CRS, identifiers, preferred formats, access/licence preference, linked aim/method. Match button shows candidate datasets and reasons.

## 16. Aim × Dataset Matrix
Rows=datasets, columns=aims. Cell relationship: Primary, Supporting, Validation, Context, Not used. Cell editor selects variables, rationale, transformations, join strategy, caveat and priority.

## 17. Analysis Plan
Ordered pipeline: acquisition → cleaning → transformation → joining → derived variables → analysis/model → validation → sensitivity → output. Each step links inputs/outputs, software and reproducibility notes.

## 18. Notes
Notebook with typed notes: General, Idea, Method decision, Dataset caveat, Supervisor comment, Meeting, Result, Limitation, Future work, Quotation, Task. Link note to RQ/Aim/Method/Dataset/Variable/Result. Markdown, tables, equations, URLs, attachments.

## 19. Citations
Dataset citations and literature links. Formats: Harvard, APA, Chicago, BibTeX, RIS. Dataset citation always carries authoritative URL, version/date and retrieval date when needed.

## 20. Data Gap Radar
Aim accordion plus requirement matrix. Status: Covered/Partial/Missing/Incompatible/Restricted/Unknown. Explain why. `Find Data` searches internal catalogue then approved external sources. External discoveries enter Candidate Inbox.

## 21. Candidate Inbox
Candidate URL, discovered source, search query, match rationale, extraction evidence, licence state, duplicate check. Actions: resolve, reject, curate, attach to requirement. Never auto-publish.

## 22. Abstract Builder
Modes: proposal/thesis/journal/conference/grant/extended/plain language. Controls: target, word limit, structure, tense, style. Sections draw from explicit project objects. Results require researcher-entered Result objects. Sentence evidence trace opens provenance inspector.

## 23. Research Data Plan
Cover; problem/gap; RQs; aims/objectives; RQ×Aim; methodology; Aim×Method; Aim×Dataset; inventory; variable coverage; spatial/temporal coverage; access/licence; transformations/joins; acquisition order; gaps/alternatives; limitations; reproducibility manifest; citations; abstract; notes appendix.

## 24. Research Kits `/kits`
Browse/filter templates. Card: purpose, questions, typical methods, roles, geography, difficulty, required/recommended/optional requirements. Kit detail creates a project graph, not just a basket.

## 25. Sources `/sources`
Source registry cards; trust tier; adapter; cadence; dataset count; last harvest; legal/access notes; health. Public transparency view.

## 26. Publisher `/publishers/[slug]`
Publisher metadata; verification; datasets; access/licence patterns; source health; official homepage.

## 27. Methodology Library `/methodology`
Explain method families, typical evidence requirements, common dataset roles, examples and limitations. Educational guide, not prescriptive methodology selection.

## 28. Developer API `/developers`
OpenAPI docs, schemas, auth/rates, examples, dataset search, project export and source provenance fields.

## 29. Admin — Sources
Enable/disable, schedule, rate limit, trust, legal notes, adapter config, last run, failures, kill switch.

## 30. Admin — Curation
Candidate queue, duplicate merge, metadata diff, licence uncertainty, broken links, publisher verification, correction/takedown requests, audit log/rollback.

## 31. Admin — Research Kits & Rules
Visual kit editor and deterministic compatibility-rule editor with fixture tests.
