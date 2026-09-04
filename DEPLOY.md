# Deploying INQETRA

INQETRA has two parts that must be hosted separately:

| Part | Path | Hosting |
|---|---|---|
| Website (Next.js 14) | `apps/web` | **Vercel** (free) |
| API (FastAPI + SQLite/PostGIS) | `apps/api` | Render / Koyeb / Fly.io / any small server — **not Vercel** (serverless has an ephemeral disk: the SQLite database would reset) |

## 1. Website on Vercel (free)

The repo root has no `package.json` — the app is in `apps/web`. When importing on
vercel.com/new, set **Root Directory = `apps/web`** (Vercel detects Next.js there).

Required environment variable (Project → Settings → Environment Variables):

```
NEXT_PUBLIC_API_URL = https://<your-api-host>   e.g. https://inqetra-api.onrender.com
```

Without it the site builds but every page calls `localhost` and shows no data.

CLI alternative (one-time `npx vercel login` first):

```bash
cd apps/web
npx vercel --prod
```

## 2. API on Render (free tier)

- New → Web Service → connect this repo → **Root Directory `apps/api`**
- Runtime: Python 3 · Build: `pip install -r requirements.txt`
- Start: `uvicorn inqetra:app --host 0.0.0.0 --port $PORT`
- The free tier uses SQLite at `/app/data/app.db` (persists while the service exists;
  wakes with cold starts). Set `DATABASE_URL` if you point it at PostGIS instead.

Free tiers sleep after ~15 min idle — first page load takes ~30 s to wake.
