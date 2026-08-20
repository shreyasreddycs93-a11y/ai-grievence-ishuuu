"""
Pydantic request/response schemas for GrievanceAI.

Enums are re-exported from models.py so the DB layer and the API layer
can never define the allowed values differently.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import Category, GrievanceStatus, Priority

# Re-export for convenient `from app.schemas import Category` imports elsewhere.
__all__ = [
    "Category",
    "GrievanceStatus",
    "Priority",
    "WebIntakeRequest",
    "MediaUploadResponse",
    "IntakeResponse",
    "TimelineEntry",
    "SubtaskEntry",
    "MediaItem",
    "GrievanceStatusResponse",
    "VerifyRequest",
    "VerifyResponse",
    "QueueItem",
    "DepartmentItem",
    "AdminUpdateRequest",
    "EscalateRequest",
    "EscalateResponse",
]


# ---------------------------------------------------------------------------
# Intake
# ---------------------------------------------------------------------------
class WebIntakeRequest(BaseModel):
    description: str = Field(..., min_length=1)
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    language: Optional[str] = None
    media_urls: List[str] = []
    # Set from the `description` field of a prior POST /intake/media (image)
    # response, so classification gets photo context without re-analyzing
    # the image at intake time.
    image_description: Optional[str] = None


class MediaUploadResponse(BaseModel):
    media_url: str
    kind: str
    transcript: Optional[str] = None
    description: Optional[str] = None


class IntakeResponse(BaseModel):
    tracking_id: str
    status: GrievanceStatus
    category: Category
    priority: Priority
    department: Optional[str] = None
    summary: Optional[str] = None
    merged: bool = False
    split: bool = False
    subtask_tracking_ids: List[str] = []


# ---------------------------------------------------------------------------
# Citizen-facing status lookup
# ---------------------------------------------------------------------------
class TimelineEntry(BaseModel):
    status: GrievanceStatus
    note: Optional[str] = None
    at: datetime


class SubtaskEntry(BaseModel):
    tracking_id: str
    department: Optional[str] = None
    status: GrievanceStatus


class MediaItem(BaseModel):
    type: str
    url: str


class GrievanceStatusResponse(BaseModel):
    tracking_id: str
    status: GrievanceStatus
    category: Category
    priority: Priority
    department: Optional[str] = None
    summary: Optional[str] = None
    address: Optional[str] = None
    confidence: float = 0.0
    created_at: datetime
    sla_due_at: Optional[datetime] = None
    timeline: List[TimelineEntry] = []
    subtasks: List[SubtaskEntry] = []
    media: List[MediaItem] = []


class VerifyRequest(BaseModel):
    confirmed: bool
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class VerifyResponse(BaseModel):
    tracking_id: str
    status: GrievanceStatus


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------
class QueueItem(BaseModel):
    id: int
    tracking_id: str
    status: GrievanceStatus
    category: Category
    priority: Priority
    department: Optional[str] = None
    summary: Optional[str] = None
    confidence: float = 0.0
    needs_human_review: bool
    created_at: datetime
    sla_due_at: Optional[datetime] = None
    parent_tracking_id: Optional[str] = None


class DepartmentItem(BaseModel):
    id: int
    name: str
    sla_hours: int


class AdminUpdateRequest(BaseModel):
    status: GrievanceStatus
    note: Optional[str] = None
    changed_by: Optional[str] = None


class EscalateRequest(BaseModel):
    reason: Optional[str] = None
    escalated_to: Optional[str] = None
    changed_by: Optional[str] = None


class EscalateResponse(BaseModel):
    tracking_id: str
    status: GrievanceStatus
    escalated_to: Optional[str] = None
    reason: Optional[str] = None
