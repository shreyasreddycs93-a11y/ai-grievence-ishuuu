# Deploying on Vercel (one project, multiple services)

`vercel.json` defines four services in a single Vercel project / one domain:

| Service | Root | Framework | Public path |
|---|---|---|---|
| `backend` | `Backend` | FastAPI | `/auth`, `/admin`, `/intake`, `/grievance`, `/departments`, `/media`, `/health`, `/cron`, `/citizen/my-grievances` |
| `citizen` | `Frontend` | Vite | `/citizen` |
| `officer` | `OfficerFrontend` | Vite | `/officer` |
| `landing` | `Landing` | Vite | `/` (everything else) |

No service calls another server-side (the browsers call the API on the same
origin), so there are no `bindings`.

## Steps
1. Import the repo in Vercel; leave Root Directory empty. The services are read from `vercel.json`.
2. Create a Postgres DB with pgvector (Neon via Vercel Storage) -> `DATABASE_URL`.
3. Env vars: `DATABASE_URL`, `GEMINI_API_KEY`, `JWT_SECRET`, `DEPARTMENT_INVITE_CODE`, `CRON_SECRET`; optional `GROQ_API_KEY`, `WHATSAPP_TOKEN`. Don't set `VITE_*`.

## Notes
- `ai_service/` now lives in `Backend/ai_service/` so it ships with the backend service.
- Frontends run `scripts/mirror-base.mjs` after build (copies `dist/` into `dist/<prefix>/`) so assets resolve whether or not Vercel strips the route prefix. Remove once confirmed.
- APScheduler is off on Vercel; `/cron/maintenance` (Vercel Cron) does SLA escalation + vector repair.
- Uploads are stored in Postgres (`media_blobs`); Vercel limits bodies to 4.5 MB.
- Docker/Render still work (`Dockerfile`, `render.yaml`).
