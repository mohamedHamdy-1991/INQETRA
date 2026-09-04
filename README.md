# INQETRA (runnable build 0.1.0)

UK-centred research-design studio + climate/environment/buildings dataset hub. See root `INVENTORY.md`, `DECISIONS.md`, `MIGRATION_MAP.md`, `FULL_QA_REPORT.md`.

## Run locally (no Docker)

```bash
# API (SQLite file persistence at ./data/app.db; PostGIS via DATABASE_URL)
python3 -m venv .venv && . .venv/bin/activate
pip install -r apps/api/requirements.txt
INQETRA_NOCACHE=1 uvicorn inqetra:app --port 8000  # from apps/api/
# Web
cd apps/web && npm install && NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Run with Docker

```bash
docker compose up --build
# web http://localhost:3000 · api http://localhost:8000/docs
```

## Verify

```bash
cd INQETRA_AI_BUILD_PACK && python3 scripts/validate_catalogue_links.py --input data/datasets_seed.csv --output-dir data/link_health --workers 12 --timeout 20
python3 -m pytest apps/api/tests -q
cd apps/web && npm run typecheck && npm run build
```

Dataset gate truth: `unreachable_record_count` must be 0; never delete records to pass.
A working landing page does not prove download access, licence permission, scientific fitness or resolved metadata.
