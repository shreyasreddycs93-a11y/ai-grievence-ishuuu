# Frontend-only deploy on Vercel (current setup)

`vercel.json` + `.vercelignore` deploy **only the three static frontends**
(no Python, no database): `/` Landing, `/citizen/` Citizen app, `/officer/` Officer app.

1. Vercel → Add New Project → import this repo. Root Directory **empty**, Framework Preset **Other**.
2. Deploy. No environment variables are needed.
3. Because there is no backend yet, API calls (login, report, queue) will fail.
   To demo the citizen app with built-in fixtures, set `VITE_USE_MOCK=true`
   in Vercel env vars and redeploy (citizen app only). Or point the apps at a
   backend hosted elsewhere via `VITE_API_BASE_URL` (Landing + Citizen) and
   `VITE_API_URL` (Officer) — but note the API must allow CORS (it currently allows all).

## Adding the backend later (full stack on Vercel)

1. Replace `vercel.json` with `vercel.fullstack.json` (`cp vercel.fullstack.json vercel.json`).
2. Empty `.vercelignore` of `Backend`, `ai_service`, `api`, `requirements.txt`, `.python-version`.
3. Follow the "Full stack" section below.

---

# Deploying on Vercel (single project)

One Vercel project serves everything:

| URL | What | Source |
|---|---|---|
| `/` | Landing + login | `Landing` (static) |
| `/citizen/` | Citizen app | `Frontend` (static) |
| `/officer/` | Officer dashboard | `OfficerFrontend` (static) |
| `/auth`, `/admin`, `/intake`, `/grievance`, `/citizen/my-grievances`, `/media`, `/health` | API | FastAPI in `Backend/`, run as a Python function via `api/index.py` |

`vercel.json` wires the build (`npm run build:all` builds all three Vite apps into `dist/`) and rewrites the API paths to the function.

## Steps

1. **Create a Postgres DB with pgvector** (Vercel can't host one). Neon (free) is easiest — Vercel Marketplace → Neon, or neon.tech. Use the *pooled* connection string.
2. Vercel → **Add New Project** → import this repo. Leave **Root Directory empty** (repo root) and Framework Preset **Other** — `vercel.json` sets everything.
3. Add **Environment Variables**:
   - `DATABASE_URL` — Neon connection string (required)
   - `GEMINI_API_KEY` — required for AI classification
   - `JWT_SECRET` — any long random string
   - `DEPARTMENT_INVITE_CODE` — officer signup code
   - `CRON_SECRET` — any random string (protects `/cron/maintenance`)
   - `GROQ_API_KEY`, `WHATSAPP_TOKEN` — optional
   - Do **not** set `VITE_*` vars; the apps call the API on the same origin.
4. Deploy. Tables and the `vector` extension are created on the first request.

## What changed vs. the Docker/Render setup

- **Scheduler:** APScheduler can't run on serverless. SLA escalation + vector repair now run via Vercel Cron → `GET /cron/maintenance` (daily on the Hobby plan; change the schedule in `vercel.json` to `*/5 * * * *` on Pro).
- **Uploads:** photos/voice notes are stored in the DB (`media_blobs`) instead of local disk, and served from `/media/{file}`. Vercel caps request bodies at 4.5 MB, so uploads are limited to 4 MB there.
- **DB connections:** no pooling in the function (`NullPool`); use the provider's pooled URL.

The `Dockerfile` / `render.yaml` still work for non-Vercel hosting.

## Local development

Backend: `cd Backend && uvicorn app.main:app --reload` (needs `.env` with `DATABASE_URL`).
Frontends: `npm run dev` inside `Frontend` (5180), `OfficerFrontend` (5175), `Landing` (5173).
