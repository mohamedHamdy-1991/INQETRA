# INQETRA — research-design studio & UK built-environment dataset hub

<p align="center">
  <img src="assets/inqetra-logo-mark-v3-2026-09-04.png" alt="INQETRA logo" width="96"/>
</p>

**INQETRA** turns a half-formed research idea into an executable, provenance-traceable
data plan. It keeps your research logic as linked objects — problem, knowledge gap,
questions, aims, methods, dataset requirements — and connects them to a curated
catalogue of **751 authoritative UK datasets** (18 domains) with mechanical
compatibility checking, a data-gap radar, and exportable Research Data Plans.

> **Ground rule:** landing-page reachability never implies download access, licence
> permission or scientific fitness. Every dataset claim carries its publisher,
> landing URL, link type, verification state and review date.

## Features

- **Research-design graph** — questions, aims, objectives, hypotheses, methods,
  dataset requirements, basket, aim × dataset matrix, transformations, ordered
  analysis steps, contributions and citations — all linked, all stored.
- **Dataset catalogue** — 751 curated records across 18 domains with CSV/JSON/Markdown
  parity views, 12 acceptance domain filters, per-record provenance and link health.
- **Compatibility engine & gap radar** — nine rule families (geography, time,
  granularity, identifiers, units, format, access, licence, freshness) with factual,
  non-judgemental reporting: `COVERED / PARTIAL / MISSING / INCOMPATIBLE / RESTRICTED / UNKNOWN`.
- **Research kits** — eight built-in starter graphs (urban heat island, overheating,
  retrofit, flood risk…) plus full custom-kit authoring.
- **Document paths** — PhD thesis, Master's dissertation, research grant, journal and
  conference templates with section skeletons, word targets and tool emphasis.
- **Evidence-traced abstracts** — drafts draw only from project objects; results must
  be researcher-entered; every draft is editable and version-kept.
- **Responsible discovery** — robots-aware, rate-limited metadata harvester and
  thumbnail extraction; external discoveries stage in a candidate inbox, never
  auto-published.
- **Optional AI copilot** — provider-neutral, deterministic-tools-only; it can
  structure answers but cannot invent datasets, licences or results.
- **PDF exports** — project plans and basket coverage reports as print-ready
  documents in a deliberately bold visual design.

## Quickstart (local)

```bash
git clone https://github.com/mohamedHamdy-1991/INQETRA.git
cd INQETRA

# API
python3 -m venv .venv && source .venv/bin/activate
pip install -r apps/api/requirements.txt
uvicorn inqetra:app --port 8123 --app-dir apps/api

# in a second terminal — web
cd apps/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8123 npm run dev
```

Open http://localhost:3000 — API docs at http://localhost:8123/docs.
The SQLite database (`data/app.db`) is created and seeded on first boot.

## Docker

```bash
docker compose up --build   # web :3000, api :8000, PostGIS :5433, redis :6380
```

## Tests

```bash
INQETRA_NOCACHE=1 DATABASE_URL="sqlite:////tmp/inq_ci.db" \
  python -m pytest apps/api/tests -q -p no:cacheprovider    # 33 tests
cd apps/web && npx tsc --noEmit && npm run build
```

## Architecture

```
apps/api     FastAPI + SQLAlchemy (SQLite default / PostGIS via DATABASE_URL)
             catalogue · studio graph · compatibility engine · gap radar
             kits · document paths · harvester · thumbnails · AI gateway · admin
apps/web     Next.js 14 + TypeScript · Neo-Brutalist design system · mobile adaptive
data/seeds   751-record catalogue parity views (CSV/JSON/MD) + link-health report
INQETRA_AI_BUILD_PACK/   authoritative build pack: taxonomy, schemas, specs, seeds
```

## Data provenance

The catalogue curates public sources (MHCLG, ONS, Met Office, Ordnance Survey,
Environment Agency and others) with source-declared licences. Reuse conditions are
stated on each record's landing page — always read them before redistribution.

## Citation & paper

See [CITATION.cff](CITATION.cff) and [paper.md](paper.md).
Development practice, including the AI-assistance policy, is described in
[CONTRIBUTING.md](CONTRIBUTING.md) and [AI_USAGE.md](AI_USAGE.md).

## License

[MIT](LICENSE) © 2026 Mohamed Hamdy Ali
