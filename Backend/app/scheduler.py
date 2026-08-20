"""
APScheduler-based SLA breach checker.

Runs periodically in-process (no Celery/Redis needed at hackathon scale)
and auto-escalates any open grievance whose sla_due_at has passed:
  - status -> escalated
  - a row is written to `escalations`
  - a row is written to `status_history`
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import or_

from app import ai_client
from app.db import SessionLocal
from app.models import (
    ESCALATABLE_STATUSES,
    ComplaintVector,
    Department,
    Escalation,
    Grievance,
    GrievanceMedia,
    GrievanceStatus,
    NotificationLog,
    StatusHistory,
)
from app.notifications import send_notification
from app.routers.intake import _find_duplicate

logger = logging.getLogger("grievanceai.scheduler")

_scheduler: Optional[BackgroundScheduler] = None

# Matches the Vector(768) column size in models.py.
_EMBEDDING_DIM = 768
_ZERO_VECTOR = [0.0] * _EMBEDDING_DIM


def check_overdue_grievances() -> int:
    """
    Finds every OPEN grievance whose SLA has been breached and auto-
    escalates it. Returns the number of grievances escalated.

    Runs its own DB session since it executes outside of any HTTP request.
    """
    db = SessionLocal()
    escalated_count = 0
    try:
        now = datetime.now(timezone.utc)
        overdue = (
            db.query(Grievance)
            .filter(
                Grievance.status.in_(ESCALATABLE_STATUSES),
                Grievance.sla_due_at.isnot(None),
                Grievance.sla_due_at < now,
            )
            .all()
        )

        for grievance in overdue:
            department_name = None
            escalation_contact = None
            if grievance.department_id:
                dept = db.get(Department, grievance.department_id)
                if dept:
                    department_name = dept.name
                    escalation_contact = dept.escalation_contact

            db.add(
                Escalation(
                    grievance_id=grievance.id,
                    escalated_from=department_name,
                    escalated_to=escalation_contact or "unassigned_escalation_contact",
                    reason=f"SLA breached: was due at {grievance.sla_due_at.isoformat()}",
                )
            )
            grievance.status = GrievanceStatus.escalated
            db.add(
                StatusHistory(
                    grievance_id=grievance.id,
                    status=GrievanceStatus.escalated,
                    changed_by="system",
                    note="Auto-escalated: SLA breached",
                )
            )
            send_notification(
                db,
                grievance=grievance,
                channel="internal",
                message=(
                    f"SLA breached for {grievance.tracking_id} "
                    f"({department_name or 'unassigned'}); escalated to "
                    f"{escalation_contact or 'unassigned_escalation_contact'}."
                ),
            )
            escalated_count += 1

        db.commit()
        if escalated_count:
            logger.info("Auto-escalated %d overdue grievance(s)", escalated_count)
        return escalated_count
    except Exception:
        db.rollback()
        logger.exception("Error while checking overdue grievances")
        return 0
    finally:
        db.close()


def _merge_into(db, *, source: Grievance, target: Grievance) -> bool:
    """
    Best-effort merge of `source` into `target` (the same outcome as a
    normal /intake/web duplicate match, applied after the fact). Only
    proceeds if `source` has no dependents outside what Grievance's cascade
    relationships already cover — a split-family child (parent_id) or a
    notification log row — since those aren't safe to silently drop.
    Returns whether the merge happened.
    """
    has_children = db.query(Grievance.id).filter(Grievance.parent_id == source.id).first() is not None
    has_notifications = db.query(NotificationLog.id).filter(NotificationLog.grievance_id == source.id).first() is not None
    if has_children or has_notifications:
        logger.warning(
            "reembed_broken_vectors: %s matches %s but has dependent rows, leaving both standalone",
            source.tracking_id, target.tracking_id,
        )
        return False

    db.query(GrievanceMedia).filter(GrievanceMedia.grievance_id == source.id).update(
        {GrievanceMedia.grievance_id: target.id}
    )
    target.report_count += 1
    db.delete(source)
    logger.info(
        "reembed_broken_vectors: auto-merged %s into %s (now reported %d time(s))",
        source.tracking_id, target.tracking_id, target.report_count,
    )
    return True


def reembed_broken_vectors() -> int:
    """
    Safety net for the zero-vector fallback in ai_service.embed_text(): if a
    Gemini embedding call fails (commonly a transient per-minute rate limit
    on rapid submissions — see memory embed-zero-vector-breaks-dedup), the
    grievance is created with an all-zero embedding, which permanently
    breaks duplicate-merge detection for it (cosine distance to a zero
    vector is NaN, so it can never match anything).

    Finds every grievance with a missing or all-zero vector and retries the
    embedding call. A rate-limited /intake/web call still creates a
    standalone ticket in the moment (this job doesn't intercept that) — so
    once a vector is fixed, this also re-runs the same duplicate check
    /intake/web would have run, and merges it in if it turns out to be a
    duplicate of an existing ticket. That's the gap this closes: without it,
    a repaired vector still leaves an already-created duplicate as its own
    permanent ticket. Returns the number of vectors repaired (merged or not).
    """
    db = SessionLocal()
    repaired = 0
    merged = 0
    try:
        rows = (
            db.query(Grievance, ComplaintVector)
            .outerjoin(ComplaintVector, ComplaintVector.grievance_id == Grievance.id)
            .filter(
                or_(
                    ComplaintVector.grievance_id.is_(None),
                    ComplaintVector.embedding.l2_distance(_ZERO_VECTOR) == 0,
                )
            )
            .limit(50)
            .all()
        )

        for grievance, vector in rows:
            try:
                new_embedding = ai_client.embed_text(grievance.description)["vector"]
            except Exception:
                logger.exception("reembed_broken_vectors: embed_text raised for %s", grievance.tracking_id)
                continue

            if all(x == 0 for x in new_embedding):
                continue  # still broken (e.g. quota still exhausted) — retry next tick

            if vector is not None:
                vector.embedding = new_embedding
            else:
                db.add(ComplaintVector(grievance_id=grievance.id, embedding=new_embedding))
            db.flush()
            repaired += 1

            duplicate = _find_duplicate(db, new_embedding, exclude_grievance_id=grievance.id)
            if duplicate is not None and _merge_into(db, source=grievance, target=duplicate):
                merged += 1

        db.commit()
        if repaired:
            logger.info(
                "Re-embedded %d grievance(s) that had a broken vector (%d auto-merged into an existing duplicate)",
                repaired, merged,
            )
        return repaired
    except Exception:
        db.rollback()
        logger.exception("Error while re-embedding broken vectors")
        return 0
    finally:
        db.close()


def start_scheduler(interval_minutes: int = 5, vector_repair_interval_minutes: int = 2) -> BackgroundScheduler:
    """Idempotent: safe to call more than once (e.g. across --reload restarts)."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        check_overdue_grievances,
        "interval",
        minutes=interval_minutes,
        id="sla_breach_check",
        replace_existing=True,
    )
    _scheduler.add_job(
        reembed_broken_vectors,
        "interval",
        minutes=vector_repair_interval_minutes,
        id="vector_repair",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "Scheduler started (SLA check every %d minute(s), vector repair every %d minute(s))",
        interval_minutes, vector_repair_interval_minutes,
    )
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
