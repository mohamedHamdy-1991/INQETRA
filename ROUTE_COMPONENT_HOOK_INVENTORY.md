# Route / Component / Data-hook inventory (planned → implemented)

## Routes (Next.js App Router) ↔ spec 03/04

| Route | Spec | Data hooks |
|---|---|---|
| `/` | 04§1 Home | `useCatalogueStats`, `useKits`, `useSearchSuggest` |
| `/datasets` | 04§2 Explore | `useDatasets(query→URL params)`, `useBasket` |
| `/datasets/[id]` | 04§3 Detail | `useDataset(id)`, `useDatasetRelated`, `useBasket` |
| `/map` | 04§4 Data Map | `useDatasets`, Leaflet CDN, `useBasket` |
| `/compare?ids=a,b,c` | 04§5 Compare | `useCompare(ids)` |
| `/basket` | 04§6 Basket | `useBasket` (localStorage mirror + project basket via API) |
| `/projects` | 04§7 Projects | `useProjects` |
| `/projects/[id]/studio` | 04§8–18 Studio shell + Problem→Export (16 anchored sections) | `useProject(id)`, `useStudioSection` (questions/aims/methods/requirements/matrix/analysis/notes/citations/gaps/abstract/report) |
| `/projects/[id]/notes` | 04§18 Notes | `useNotes(projectId)` |
| `/projects/[id]/abstract` | 04§22 Abstract | `useAbstract(projectId)` |
| `/projects/[id]/report` | 04§23 Data Plan | `useReportModel(projectId)` |
| `/projects/[id]/gaps` | 04§20 Gap Radar | `useGaps(projectId)` |
| `/projects/[id]/candidates` | 04§21 Inbox | `useCandidates(projectId)` |
| `/kits` | 04§24 Kits | `useKits` |
| `/sources` | 04§25 Sources | `useSources` |
| `/publishers` | 04§26 Publishers | `usePublishers` |
| `/methodology` | 04§27 Method library | static + `useTaxonomy` |
| `/about` | Trust/method | static |
| `/developers` | 04§28 API docs | OpenAPI link (`/api/docs`) |
| `/settings` | System | `useSettings` (provider-neutral AI opt-in, local only) |
| `/admin` | 04§29–31 Admin | `useAdminSources`, `useJobs`, `useAuditLog` |

## Components ↔ spec 14

Shell: `Sidebar`, `TopBar`, `ProjectRail`, `ContextInspector`, `MobileNav`, `SkipLink`, `Toast`.
Primitives: `Button`, `Input`, `Textarea`, `Select`, `Tabs`, `Chip`, `StatusBadge`, `Card`, `Panel`, `KPI`, `Drawer`, `Modal`, `DataTable`, `EmptyState`, `ProvenanceStrip`.
Research: `QuestionCard`, `AimCard`, `MethodCard`, `RequirementCard`, `Matrix` (keyboard grid: arrows+Enter), `ReadinessPanel`, `GapRadar`, `AnalysisPipeline`, `EvidenceTrace`, `NoteEditor`, `AbstractComposer`.
Dataset: `DatasetCard`, `DatasetRow`, `AuthorityBadge`, `AccessBadge`, `LicenceBadge`, `CoverageSummary`, `CompareGrid`, `BasketDrawer`, `CandidateCard`, `SourceHealthCard`.

All components live under `apps/web/components/`. All hooks under `apps/web/hooks/` (fetch wrappers over `NEXT_PUBLIC_API_URL`, default `http://localhost:8000`).

## API ↔ spec 17 (FastAPI `apps/api/inqetra/`)

`catalogue.py` (`GET /api/v1/datasets`, `/{id}`, `/views/csv|json|markdown`, `/publishers`, `/taxonomy`, `/kits`, `/sources`, `/health`, `POST /compare`), `projects.py` (projects + all nested CRUD + matrices), `evaluate.py` (compatibility/gaps/find-data), `inbox.py` (candidates resolve/reject), `reports.py` (abstract/draft+traces, report-model, exports, citations), `jobs.py` (exports jobs + failure sim), `ai.py` (provider-neutral stub), `admin.py` (sources CRUD, link-check, audit log), `compat.py` + `domain_filter.py` (deterministic rules), `store.py` (SQLAlchemy models: all 05 entities + matrices + provenance), `seed.py` (CSV loader + parity builder).


## Added 2026-09-04 (v0.2.1)

| Route | Notes | Data hooks |
|---|---|---|
| `/basket/report` | Coverage matrix (browser basket × project requirements), save-basket-to-project, access/licence table, data-plan CTA | `api.project`, `api.info`, `api.post(evaluate)`, `api.get(gaps)`, `useBasket` |
| `/datasets/all` | A–Z catalogue divided by domain, paginated 200/page | `api.datasets` (paged), `useBasket`, `ThumbImg` |
| `/projects/new` | 6-step wizard incl. kit templates | `api.kits`, `api.createProject`, `api.post(...)` per entity |
| `/kits/[slug]` | Kit detail + instantiate full graph | `api.kit`, `api.instantiate` |
| `/publishers/[name]` | Publisher page with cards | `api.datasets({publisher})`, `useBasket`, `ThumbImg` |

Components: `Reveal`/`CountUp` (scroll/count motion, reduced-motion safe, `.js`-gated), `ThumbImg` (publisher og:image → domain art `/img/domains/…` → deterministic SVG), `ConceptBoard`/`EdgeForm` (studio concept map), `MethodologyForm`, `Copilot` (deterministic AI panel), admin `RulesEditor`/`SubmissionsModeration`/`StagingQueue`/`SourceRuns`/`ResolverRunner`.
