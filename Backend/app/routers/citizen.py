"""
Citizen-facing endpoints: check status, confirm/reopen resolution.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_account
from app.db import get_db
from app.models import Account, Department, Grievance, GrievanceStatus, StatusHistory
from app.schemas import (
    GrievanceStatusResponse,
    MediaItem,
    MyGrievanceItem,
    SubtaskEntry,
    TimelineEntry,
    VerifyRequest,
    VerifyResponse,
)

router = APIRouter(tags=["citizen"])


@router.get("/citizen/my-grievances", response_model=List[MyGrievanceItem])
def get_my_grievances(db: Session = Depends(get_db), account: Account = Depends(get_current_account)):
    """Grievances the logged-in citizen has submitted while logged in —
    anonymous submissions made before/without logging in aren't linked to
    any account, so they can't appear here. Only top-level tickets (not
    split-family sub-tickets) are listed; parent's status/timeline already
    reflects the sub-tickets."""
    grievances = (
        db.query(Grievance)
        .filter(Grievance.account_id == account.id, Grievance.parent_id.is_(None))
        .order_by(Grievance.created_at.desc())
        .all()
    )

    department_ids = {g.department_id for g in grievances if g.department_id}
    departments = {}
    if department_ids:
        for dept in db.query(Department).filter(Department.id.in_(department_ids)).all():
            departments[dept.id] = dept.name

    return [
        MyGrievanceItem(
            tracking_id=g.tracking_id,
            status=g.status,
            category=g.category,
            priority=g.priority,
            department=departments.get(g.department_id),
            summary=g.description[:140],
            created_at=g.created_at,
        )
        for g in grievances
    ]


def _get_grievance_or_404(db: Session, tracking_id: str) -> Grievance:
    grievance = db.query(Grievance).filter(Grievance.tracking_id == tracking_id).first()
    if grievance is None:
        raise HTTPException(status_code=404, detail="Grievance not found")
    return grievance


@router.get("/grievance/{tracking_id}/status", response_model=GrievanceStatusResponse)
def get_status(tracking_id: str, db: Session = Depends(get_db)):
    grievance = _get_grievance_or_404(db, tracking_id)

    department_name = None
    if grievance.department_id:
        dept = db.get(Department, grievance.department_id)
        department_name = dept.name if dept else None

    timeline = [
        TimelineEntry(status=h.status, note=h.note, at=h.changed_at)
        for h in grievance.status_history
    ]

    subtasks = []
    for child in grievance.subtasks:  # backref from Grievance.parent (self-referencing FK)
        child_dept_name = None
        if child.department_id:
            child_dept = db.get(Department, child.department_id)
            child_dept_name = child_dept.name if child_dept else None
        subtasks.append(
            SubtaskEntry(tracking_id=child.tracking_id, department=child_dept_name, status=child.status)
        )

    media = [MediaItem(type=m.type, url=m.storage_url) for m in grievance.media]

    return GrievanceStatusResponse(
        tracking_id=grievance.tracking_id,
        status=grievance.status,
        category=grievance.category,
        priority=grievance.priority,
        department=department_name,
        # Full text, not a 140-char preview: this is the detail view, and the
        # truncation was cutting off the tail of longer complaints — including
        # the English rendering appended to non-English ones. The list
        # endpoint above still previews.
        summary=grievance.description,
        address=grievance.address,
        confidence=grievance.confidence,
        created_at=grievance.created_at,
        sla_due_at=grievance.sla_due_at,
        report_count=grievance.report_count,
        timeline=timeline,
        subtasks=subtasks,
        media=media,
    )


@router.post("/grievance/{tracking_id}/verify", response_model=VerifyResponse)
def verify_grievance(tracking_id: str, payload: VerifyRequest, db: Session = Depends(get_db)):
    grievance = _get_grievance_or_404(db, tracking_id)

    if payload.confirmed:
        grievance.status = GrievanceStatus.closed
        note = "Citizen confirmed resolution"
        if payload.rating is not None:
            note += f" (rating: {payload.rating})"
    else:
        grievance.status = GrievanceStatus.reopened
        note = "Citizen rejected resolution; grievance reopened"

    db.add(
        StatusHistory(
            grievance_id=grievance.id,
            status=grievance.status,
            changed_by="citizen",
            note=note,
        )
    )
    db.commit()
    db.refresh(grievance)

    return VerifyResponse(tracking_id=grievance.tracking_id, status=grievance.status)
