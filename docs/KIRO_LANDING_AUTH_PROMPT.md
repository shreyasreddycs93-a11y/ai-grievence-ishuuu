# Kiro prompt: unified landing page with citizen/officer auth

Paste everything below the line into Kiro as the initial feature prompt.

---

## Context

Monorepo with three independent apps + no auth anywhere yet:

- `Backend/` — FastAPI + SQLAlchemy + Postgres (pgvector). Routers in `Backend/app/routers/*.py`, each `APIRouter(tags=[...])` with **no path prefix**, included in `Backend/app/main.py`. Every error response is `{"error": "..."}` (see the exception handlers in `main.py`). No Alembic — `Backend/app/db.py::init_db()` just does `Base.metadata.create_all`. Settings are a pydantic `Settings` class in `Backend/app/config.py` reading `.env`.
- `Frontend/` — citizen app. React 18 + Vite 5 + Tailwind 3 + TS, path alias `@/`. `App.tsx` does manual screen-state routing (`Screen` union in `src/types.ts`), no react-router. `src/lib/api.ts` calls the backend via `VITE_API_BASE_URL`. No auth.
- `OfficerFrontend/` — officer dashboard. React 19 + Vite + Tailwind 4 + react-router-dom v7 (`BrowserRouter` in `App.tsx`, `DashboardLayout` wraps `Overview`/`Queue`/`GrievanceDetail`/`Intake`). `src/api/client.ts` calls backend via `VITE_API_URL`, with a mock-data fallback when the backend is unreachable. No auth.
- The existing `User` model in `Backend/app/models.py` is a WhatsApp-contact profile tied to grievances — **do not** repurpose it for login credentials; it's a different concept.

## Goal

A new `Landing/` app (same stack as `Frontend/`: Vite + React + TS + Tailwind) that is the single entry point at `/`. Flow: pick **Citizen** or **Officer** → **Log in** or **Create account** → authenticate against a new backend auth API → redirect into the matching existing app. All three apps + the API must be reachable from **one local origin/port**, in dev and prod.

## Requirements

### 1. Backend auth — `Backend/app/routers/auth.py` + model additions
- New `accounts` table (SQLAlchemy model in `models.py`): `id`, `name`, `email` (unique), `phone` (nullable), `password_hash`, `role` (`citizen`|`officer` enum, mirror the existing `str, enum.Enum` style), `department_id` (nullable FK to `departments`, officers only), `created_at`.
- `POST /auth/signup` — `{name, email, password, role, department_id?, invite_code?}` → account + JWT.
- `POST /auth/login` — `{email, password}` → JWT.
- `GET /auth/me` — Bearer JWT → account profile.
- Bcrypt hashing (`passlib[bcrypt]`) and JWT (`python-jose` or `pyjwt`) — add both to `Backend/requirements.txt`, neither is present yet. JWT secret via new `Settings.JWT_SECRET`, default only for local dev.
- Officer signup gating: require a `DEPARTMENT_INVITE_CODE` env var checked against `invite_code`; reject with `{"error": "..."}` if it doesn't match. (Simplest viable gate — revisit later if a real officer-onboarding flow is needed.)
- Match existing conventions exactly: same error envelope, `tags=["auth"]`, router included in `main.py` the same way as the other four.
- No Alembic in this repo — just add the model and let `create_all` pick it up.

### 2. `Landing/` app
- Screen 1: two cards, "I'm a Citizen" / "I'm an Officer".
- Screen 2: Login/Create-account tabs, form scoped to the chosen role (officer adds department select + invite code field).
- On success: store the JWT (`localStorage`), then redirect to the citizen or officer app's mount path.
- Reuse `Frontend`'s visual language (Tailwind utility classes, header/footer layout) — no new design system, no component library.

### 3. Single-origin integration
- Path-based mounts: `/` = Landing, `/citizen/*` = `Frontend`, `/officer/*` = `OfficerFrontend`. Backend API keeps its current unprefixed paths.
- Each Vite app sets `base` to its mount path; `OfficerFrontend`'s `BrowserRouter` needs `basename="/officer"`.
- Prod (and default dev): FastAPI serves each app's built `dist/` via `StaticFiles` mounted at its path — simplest, and one port covers everything including the API.
- Only add dev-mode HMR proxying (Vite `server.proxy` across the three dev servers) if the static-mount rebuild-on-save loop actually proves too slow to iterate with — don't build it preemptively.

### 4. Officer app gate
- `OfficerFrontend` should require a valid JWT with `role: officer`; redirect to `/` if missing/invalid.
- `Frontend` (citizen) stays anonymous-capable — JWT is optional there for now.

## Out of scope
Password reset, email verification, social login, per-department RBAC beyond "logged in as officer."

## Ask before assuming
- If `department_id` officer selection needs a `GET /departments` list endpoint (none exists today — `OfficerFrontend/src/api/client.ts` hardcodes 5 departments) — add one rather than hardcoding further.
- Anything about JWT expiry/refresh strategy beyond a single long-lived token, if it comes up.
