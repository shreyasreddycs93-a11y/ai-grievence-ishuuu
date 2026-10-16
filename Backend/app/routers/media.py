"""
Media upload endpoint: stores a citizen-submitted photo or voice note and
runs it through the AI layer (audio -> transcript, image -> description)
before the grievance itself is created via POST /intake/web.

Uploaded bytes are stored in the database (media_blobs table) and served
back via GET /media/{filename}. This works on serverless hosts such as
Vercel where the filesystem is read-only/ephemeral. The AI layer needs a
file path, so the bytes are also written to a temp file just for that call.
"""
import logging
import os
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile
from sqlalchemy.orm import Session

from app import ai_client
from app.db import get_db
from app.models import MediaBlob
from app.schemas import MediaUploadResponse

logger = logging.getLogger("grievanceai.media")

router = APIRouter(tags=["intake"])

_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"}
_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/webm", "audio/mp4", "audio/x-m4a", "audio/aac"}

# Capped near Groq Whisper's ~25MB fallback limit locally. Vercel rejects
# request bodies over 4.5MB before they reach the function, so cap lower there.
MAX_UPLOAD_BYTES = (4 if os.environ.get("VERCEL") else 25) * 1024 * 1024


@router.post("/intake/media", response_model=MediaUploadResponse)
async def upload_media(request: Request, file: UploadFile, db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=413, detail=f"File too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)}MB)")

    ext = Path(file.filename or "").suffix or (".jpg" if kind == "image" else ".webm")
    filename = f"{uuid.uuid4().hex}{ext}"
    db.add(MediaBlob(filename=filename, content_type=content_type, data=body))
    db.commit()

    media_url = f"{str(request.base_url).rstrip('/')}/media/{filename}"

    # The AI layer works on file paths, so hand it a throwaway temp file.
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(body)
        local_path = Path(tmp.name)

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

    local_path.unlink(missing_ok=True)
    return MediaUploadResponse(media_url=media_url, kind=kind, transcript=transcript, description=description)


@router.get("/media/{filename}")
def get_media(filename: str, db: Session = Depends(get_db)):
    blob = db.get(MediaBlob, filename)
    if blob is None:
        raise HTTPException(status_code=404, detail="Media not found")
    return Response(
        content=blob.data,
        media_type=blob.content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
