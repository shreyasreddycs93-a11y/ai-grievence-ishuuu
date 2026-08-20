"""
Media upload endpoint: stores a citizen-submitted photo or voice note and
runs it through the AI layer (audio -> transcript, image -> description)
before the grievance itself is created via POST /intake/web.

Storage is local disk (Backend/uploads/), served back via the /media
static mount in app/main.py. That's fine for a local/demo deployment but
is ephemeral on most PaaS hosts (e.g. Railway's filesystem doesn't
persist across deploys) — swap for real object storage (S3, Cloudinary,
Supabase Storage) before relying on this in production.
"""
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile

from app import ai_client
from app.schemas import MediaUploadResponse

logger = logging.getLogger("grievanceai.media")

router = APIRouter(tags=["intake"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"}
_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/webm", "audio/mp4", "audio/x-m4a", "audio/aac"}

# Keeps demo uploads from filling the disk / taking too long to process.
# Capped near Groq Whisper's ~25MB fallback limit (Gemini's own File API
# handles much larger files, so Groq is the real ceiling here).
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


@router.post("/intake/media", response_model=MediaUploadResponse)
async def upload_media(request: Request, file: UploadFile):
    # Browsers report MediaRecorder blobs with a codec suffix, e.g.
    # "audio/webm;codecs=opus" — strip it before matching, or every real
    # in-browser voice recording gets rejected as "unsupported".
    content_type = (file.content_type or "").split(";", 1)[0].strip().lower()
    if content_type in _IMAGE_TYPES:
        kind = "image"
    elif content_type in _AUDIO_TYPES:
        kind = "audio"
    else:
        raise HTTPException(status_code=422, detail=f"Unsupported content type: {content_type}")

    body = await file.read()
    if len(body) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 15MB)")

    ext = Path(file.filename or "").suffix or (".jpg" if kind == "image" else ".webm")
    filename = f"{uuid.uuid4().hex}{ext}"
    local_path = UPLOAD_DIR / filename
    local_path.write_bytes(body)

    media_url = f"{str(request.base_url).rstrip('/')}/media/{filename}"

    transcript = None
    description = None
    if kind == "audio":
        try:
            transcript = ai_client.transcribe_audio(str(local_path))
        except Exception:
            logger.exception("transcribe_audio failed for upload %s", filename)
    elif kind == "image":
        try:
            description = ai_client.describe_image(str(local_path)) or None
        except Exception:
            logger.exception("describe_image failed for upload %s", filename)

    return MediaUploadResponse(media_url=media_url, kind=kind, transcript=transcript, description=description)
