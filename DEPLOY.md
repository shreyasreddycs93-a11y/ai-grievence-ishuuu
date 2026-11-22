# Deploying on Render

`render.yaml` is a Blueprint that creates:
- a Docker web service `civicsahayak` (builds the 3 frontends + FastAPI backend, served from one URL)
- a Postgres database `civicsahayak-db` (Render Postgres supports pgvector; the app runs `CREATE EXTENSION vector` on boot)

## Steps
1. Render dashboard -> New -> Blueprint -> pick this GitHub repo.
2. Fill in the prompted env vars:
   - `GEMINI_API_KEY` (new key from https://aistudio.google.com/)
   - `DEPARTMENT_INVITE_CODE` (any code; officers enter it at signup)
   - `GROQ_API_KEY`, `WHATSAPP_TOKEN`: optional, leave blank
   - `DATABASE_URL` and `JWT_SECRET` are filled in automatically.
3. Deploy. Departments are seeded automatically on every start (idempotent).
4. Check `https://<service>.onrender.com/health` -> `{"ok":true}`.

## Notes
- Free plan: the service sleeps when idle (first request ~1 min); free Postgres expires after 30 days.
- Uploaded photos/audio are stored on the container disk and are lost on redeploy/restart.
  Add a persistent disk (paid plan) or move uploads to object storage for production.
