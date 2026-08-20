"""
ai_service — Phase 1 of the GrievanceAI AI/ML layer.

Usage from the backend:
    from ai_service import classify_complaint, embed_text, normalize_text, transcribe_audio, describe_image
"""
from .service import (
    transcribe_audio,
    normalize_text,
    describe_image,
    classify_complaint,
    classify_from_raw_input,
    split_departments,
    embed_text,
)

__all__ = [
    "transcribe_audio",
    "normalize_text",
    "describe_image",
    "classify_complaint",
    "classify_from_raw_input",
    "split_departments",
    "embed_text",
]
