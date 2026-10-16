# Deploying

This repo is a **single-origin app**: the FastAPI backend serves the three
built frontends (`/` landing, `/citizen/`, `/officer/`) and the API. Deploy it
as **one Docker service** — do not split the frontends onto Vercel.

## Recommended: Render (uses `render.yaml` + `Dockerfile`)

1. Render dashboard → New → **Blueprint** → select this repo.
2. It creates the web service and a Postgres database (`civicsahayak-db`) and
   wires `DATABASE_URL` automatically. The backend runs
   `CREATE EXTENSION vector` on startup.
3. Fill the secrets it prompts for: `GEMINI_API_KEY`, `GROQ_API_KEY` (optional),
   `WHATSAPP_TOKEN` (optional), `DEPARTMENT_INVITE_CODE`.
4. Open the service URL.

Railway also works (`Backend/railway.json`) but needs the frontends built into
the image, so prefer the root `Dockerfile`.

## Why not Vercel?

The root `requirements.txt` makes Vercel detect a Python project, and there is
no root `package.json`, so `vite build` fails with `vite: command not found`.
If you still want a frontend on Vercel, create a separate project with Root
Directory = `Frontend` (Vite preset), set `VITE_API_BASE_URL` to the backend
URL, and note `base: '/citizen/'` in `Frontend/vite.config.ts`.

## Local development

Backend: `cd Backend && uvicorn app.main:app --reload` (needs `.env`).
Frontend: `cd Frontend && npm run dev` (port 5180). Officer UI and Landing
similarly via `npm run dev`.
