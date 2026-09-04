# Contributing to INQETRA

Thank you for considering a contribution. INQETRA is an open-source research-design
studio for the UK built-environment community, and contributions of code, catalogue
curation, documentation and bug reports are all welcome.

## Development setup

Prerequisites: Python 3.12+ (3.13/3.14 tested), Node.js 18+.

```bash
git clone https://github.com/mohamedHamdy-1991/INQETRA.git
cd INQETRA

# API
python3 -m venv .venv && source .venv/bin/activate
pip install -r apps/api/requirements.txt
uvicorn inqetra:app --port 8123 --app-dir apps/api     # http://localhost:8123/healthz

# Web
cd apps/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8123 npm run dev   # http://localhost:3000
```

The API defaults to a SQLite database at `data/app.db` (created on first boot and
seeded with compatibility rules, licences, sources and research kits). Set
`DATABASE_URL` to a PostGIS/PostgreSQL connection string for a shared deployment.

## Running the tests

```bash
INQETRA_NOCACHE=1 DATABASE_URL="sqlite:////tmp/inq_ci.db" python -m pytest apps/api/tests -q -p no:cacheprovider
cd apps/web && npx tsc --noEmit && npm run build
```

## Ground rules

1. **Provenance is non-negotiable.** Every dataset claim must carry publisher,
   landing URL, link type, verification state and review date. Landing-page
   reachability never implies licence permission or scientific fitness.
2. **No auto-publishing.** Harvester and external results enter the candidate
   inbox and require curator review. Catalogue rows are never created silently.
3. **AI is optional and provider-neutral.** AI features may only structure
   deterministic tool outputs; they must not invent datasets, licences or results.
4. **Additive migrations only.** Never drop tables or columns; extend the model
   with additive changes so existing project databases keep working.
5. **Tests with every change.** New endpoints need tests; the suite must stay
   green before merging.

## Submitting changes

Open an issue describing the change first if it is large. Pull requests should
pass the test suite and include a clear description. Commit messages should
explain *why*, not only *what*.

## Reporting bugs

Open an issue with: what you did, what you expected, what happened, and the
smallest reproduction (a curl command or screenshot helps). Include your
Python/Node versions for environment problems.

## AI-assistance disclosure

Contributions may be prepared with AI coding assistants; contributors remain
responsible for verifying correctness, tests and licence compliance of anything
they submit, and significant AI assistance should be noted in the pull request.
