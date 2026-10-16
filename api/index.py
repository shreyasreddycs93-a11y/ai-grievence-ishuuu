"""Vercel serverless entrypoint: exposes the FastAPI app from Backend/app."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "Backend", ROOT):  # Backend -> `app`, root -> `ai_service`
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from app.main import app  # noqa: E402,F401
