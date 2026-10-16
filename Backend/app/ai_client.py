"""
Real AI client — wraps the `ai_service` package (Gemini -> Groq -> safe
default) behind the exact function signatures / return shapes the rest of
the backend was built against, so no caller needed to change.

`ai_service` lives inside `Backend/` (not as an installed package), so it's
reached via a Backend-dir sys.path insert below. Keeping it inside Backend/
means it ships with any deploy whose root is scoped to Backend/ (e.g. a
Vercel service with `"root": "Backend"`).
"""
import sys
from pathlib import Path
from typing import List, Optional, TypedDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from ai_service import (  # noqa: E402
    classify_from_raw_input,
    describe_image as _describe_image,
    embed_text as _embed_text,
    split_departments as _split_departments,
    transcribe_audio as _transcribe_audio,
)


class ClassificationResult(TypedDict):
    category: str
    subcategory: str
    priority: str
    confidence: float
    location_text: Optional[str]
    summary: str


class EmbeddingResult(TypedDict):
    vector: List[float]


class DepartmentSplitEntry(TypedDict):
    category: str
    sub_issue: str


class DepartmentSplitResult(TypedDict):
    needs_split: bool
    departments: List[DepartmentSplitEntry]


def classify_complaint(text: str, image_description: Optional[str] = None) -> ClassificationResult:
    """Runs the real classifier via ai_service.classify_from_raw_input, which
    also handles native-script translation on the AI side when needed.
    Never raises — ai_service's own provider chain (Gemini -> Groq -> safe
    default) guarantees a same-shape result."""
    result = classify_from_raw_input(text, image_description)
    return {
        "category": result["category"],
        "subcategory": result["subcategory"],
        "priority": result["priority"],
        "confidence": result["confidence"],
        "location_text": result.get("location_text"),
        "summary": result["summary"],
    }


def embed_text(text: str) -> EmbeddingResult:
    return {"vector": _embed_text(text)["vector"]}


def transcribe_audio(path: str) -> str:
    return _transcribe_audio(path)


def describe_image(path: str) -> str:
    return _describe_image(path)


def split_departments(text: str, classification: ClassificationResult) -> DepartmentSplitResult:
    """Adapts ai_service's locked split_departments contract (`is_split`,
    per-department `excerpt`) to the shape app/routers/intake.py actually
    reads (`needs_split`, per-department `category` + `sub_issue`) —
    resolving the contract ambiguity the old mock's docstring flagged.
    `excerpt` is the AI's own quoted slice of the complaint relevant to
    that department, which is exactly what should become that child
    ticket's description, so it's used as `sub_issue` directly."""
    result = _split_departments(text, dict(classification))
    departments: List[DepartmentSplitEntry] = [
        {
            "category": entry["category"],
            "sub_issue": entry.get("excerpt") or text,
        }
        for entry in result.get("departments", [])
    ]
    return {"needs_split": result.get("is_split", False), "departments": departments}
