# Technical Architecture

## Frontend
Next.js App Router + TypeScript + React; TanStack Query; TanStack Table; Zod; accessible headless primitives; MapLibre GL or Leaflet; ECharts or Plotly.

## Backend
FastAPI + Pydantic v2; PostgreSQL + PostGIS; Alembic; Redis + Arq/Celery. Object storage for reports, metadata snapshots and user attachments—not third-party bulk datasets by default.

## Search
PostgreSQL FTS + pg_trgm for MVP; Meilisearch/OpenSearch only after measured need. Optional pgvector for semantic metadata search, never as the only retrieval mechanism.

## Services
Web/API; search; harvester; resolver; link health; compatibility; report/export; AI gateway; admin/curation; notifications optional.

## Deployment
Docker Compose development; environment-file template; production managed PostgreSQL + container workloads; scheduled workers. OpenTelemetry; Sentry-compatible monitoring; structured logs.

## Repository
`apps/web`, `apps/api`, `workers/*`, `packages/schema`, `packages/research-model`, `packages/compatibility`, `packages/reporting`, `packages/taxonomy`, `packages/ui`, `packages/source-adapters`, `data/seeds`, `docs`, `tests`, `infra`.
