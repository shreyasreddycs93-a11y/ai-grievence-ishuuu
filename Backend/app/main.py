"""
CivicSahayak FastAPI application entrypoint.
"""
import logging
import os
import threading

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db import init_db
from app.scheduler import check_overdue_grievances, reembed_broken_vectors, start_scheduler, stop_scheduler

IS_SERVERLESS = bool(os.environ.get("VERCEL"))

REPO_ROOT = Path(__file__).resolve().parents[2]
CITIZEN_DIST = REPO_ROOT / "Frontend" / "dist"
OFFICER_DIST = REPO_ROOT / "OfficerFrontend" / "dist"
LANDING_DIST = REPO_ROOT / "Landing" / "dist"

logger = logging.getLogger("grievanceai")


class SPAStaticFiles(StaticFiles):
    """StaticFiles that falls back to index.html for any unmatched path,
    so client-side routes (e.g. /officer/queue) work on direct load/refresh.

    Also sets Cache-Control, which StaticFiles omits entirely. Without it
    browsers fall back to heuristic caching and can serve a stale index.html
    for hours after a deploy — which is how citizens kept seeing the old
    mock-data bundle long after the fix shipped. Vite fingerprints everything
    under assets/, so those are safe to cache forever; index.html points at
    those hashes and must be revalidated on every load."""

    async def get_response(self, path: str, scope):
        try:
            response = await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404:
                raise
            response = await super().get_response("index.html", scope)
            path = "index.html"

        # StaticFiles hands us an OS-normalized path, so this is
        # "assets\app.js" on Windows and "assets/app.js" on Linux.
        if path.replace("\\", "/").startswith("assets/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        else:
            response.headers["Cache-Control"] = "no-cache"
        return response

app = FastAPI(title="CivicSahayak", version="0.1.0")

# CORS: allow all origins for now (SIH prototype). Tighten before production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Every HTTPException (404, 400, 409, etc.) must return {"error": "..."}"""
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic/body validation failures (422) also follow {"error": "..."}"""
    first = exc.errors()[0] if exc.errors() else None
    message = f"{'.'.join(str(p) for p in first['loc'])}: {first['msg']}" if first else "Invalid request"
    return JSONResponse(status_code=422, content={"error": message})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all so every unhandled error still returns {"error": "..."}"""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


_db_ready = False
_db_lock = threading.Lock()


def _ensure_db_ready() -> None:
    """Serverless has no reliable startup hook, so create the extension/tables
    lazily on the first request of each instance. Retries until it succeeds."""
    global _db_ready
    if _db_ready:
        return
    with _db_lock:
        if not _db_ready:
            init_db()
            _db_ready = True


if IS_SERVERLESS:
    @app.middleware("http")
    async def lazy_init_db(request: Request, call_next):
        if request.url.path != "/health":
            await run_in_threadpool(_ensure_db_ready)
        return await call_next(request)
else:
    @app.on_event("startup")
    def on_startup():
        init_db()
        start_scheduler(interval_minutes=5)

    @app.on_event("shutdown")
    def on_shutdown():
        stop_scheduler()


@app.get("/cron/maintenance")
def cron_maintenance(request: Request):
    """Replaces the in-process APScheduler on Vercel: Vercel Cron calls this with
    `Authorization: Bearer $CRON_SECRET`. Runs the SLA-breach check and vector repair."""
    secret = os.environ.get("CRON_SECRET", "")
    if not secret or request.headers.get("authorization") != f"Bearer {secret}":
        raise StarletteHTTPException(status_code=401, detail="Unauthorized")
    return {"escalated": check_overdue_grievances(), "reembedded": reembed_broken_vectors()}


@app.get("/health")
def health():
    return {"ok": True}


from app.routers import admin, auth, citizen, intake, media  # noqa: E402

app.include_router(intake.router)
app.include_router(media.router)
app.include_router(citizen.router)
app.include_router(admin.router)
app.include_router(auth.router)

# Serve the three built frontend apps off this same port. Order matters:
# API routes/mounts above always win on an exact prefix match; "/" is
# mounted last so it only catches whatever nothing else claimed.
for path, dist in (("/citizen", CITIZEN_DIST), ("/officer", OFFICER_DIST)):
    if dist.is_dir():
        app.mount(path, SPAStaticFiles(directory=str(dist), html=True), name=path.strip("/"))
    else:
        logger.warning("%s not built yet — run `npm run build` there, then restart. Skipping mount for %s.", dist, path)

if LANDING_DIST.is_dir():
    app.mount("/", SPAStaticFiles(directory=str(LANDING_DIST), html=True), name="landing")
else:
    logger.warning("%s not built yet — run `npm run build` there, then restart. Skipping mount for /.", LANDING_DIST)
