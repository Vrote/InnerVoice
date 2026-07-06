# backend/routes/mirror_me.py
import json
import logging
import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.connection import get_db
from backend.core.security import get_current_user_id
from backend.services.mirror_me_service import get_or_generate_mirror_me_report
from backend.database.models import MirrorMeReport, Message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/mirror-me", tags=["mirror_me"])

MIN_MESSAGES_REQUIRED = 5


class GenerateRequest(BaseModel):
    month: int = None
    year:  int = None


# ── Helper: count messages in a month ────────────────────────────────────────
async def _count_messages(user_id: str, m: int, y: int, db: AsyncSession) -> int:
    start_date = datetime.datetime(y, m, 1)
    end_date   = datetime.datetime(y + 1, 1, 1) if m == 12 else datetime.datetime(y, m + 1, 1)
    q          = select(Message).where(
        Message.user_id    == user_id,
        Message.created_at >= start_date,
        Message.created_at <  end_date
    )
    res = await db.execute(q)
    return len(res.scalars().all())


# ── GET /status ───────────────────────────────────────────────────────────────
@router.get("/status")
async def mirror_me_status(
    month: int = None,
    year:  int = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Returns message count, qualification status, and last report timestamp for given month/year."""
    try:
        now = datetime.datetime.utcnow()
        m   = month or now.month
        y   = year  or now.year

        message_count = await _count_messages(user_id, m, y, db)

        # Check if report already exists
        q_rep = select(MirrorMeReport).where(
            MirrorMeReport.user_id == user_id,
            MirrorMeReport.month   == m,
            MirrorMeReport.year    == y
        )
        res_rep = await db.execute(q_rep)
        existing = res_rep.scalars().first()

        return {
            "success": True,
            "data": {
                "month":              m,
                "year":               y,
                "message_count":      message_count,
                "threshold":          MIN_MESSAGES_REQUIRED,
                "qualifies":          message_count >= MIN_MESSAGES_REQUIRED,
                "has_report":         existing is not None,
                "messages_remaining": max(0, MIN_MESSAGES_REQUIRED - message_count),
                # expose when the report was last generated so the UI can show it
                "last_generated_at":  existing.created_at.isoformat() if existing else None,
            },
            "error": None
        }
    except Exception as e:
        logger.error(f"mirror_me_status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Mirror Me status")


# ── POST /generate ────────────────────────────────────────────────────────────
@router.post("/generate")
async def generate_mirror_me(
    body: GenerateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Always re-generates the report from scratch so it includes the latest conversations."""
    try:
        now   = datetime.datetime.utcnow()
        month = body.month or now.month
        year  = body.year  or now.year

        # Enforce threshold
        message_count = await _count_messages(user_id, month, year, db)
        if message_count < MIN_MESSAGES_REQUIRED:
            return {
                "success": True,
                "data": {
                    "has_data":           False,
                    "message":            f"You need at least {MIN_MESSAGES_REQUIRED} messages. You have {message_count} so far.",
                    "message_count":      message_count,
                    "messages_remaining": MIN_MESSAGES_REQUIRED - message_count,
                },
                "error": None
            }

        # force_regenerate=True → always deletes old report and re-runs analysis
        report = await get_or_generate_mirror_me_report(
            user_id, month, year, db, force_regenerate=True
        )
        return {"success": True, "data": report, "error": None}
    except Exception as e:
        logger.error(f"generate_mirror_me error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate monthly report")


# ── GET /{year}/{month} ───────────────────────────────────────────────────────
@router.get("/{year}/{month}")
async def get_mirror_me_by_date(
    year:  int,
    month: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Fetch the stored report for a specific year/month (no generation)."""
    try:
        q = select(MirrorMeReport).where(
            MirrorMeReport.user_id == user_id,
            MirrorMeReport.month   == month,
            MirrorMeReport.year    == year
        )
        res    = await db.execute(q)
        report = res.scalars().first()

        if not report:
            # Return status info so the frontend can show the progress gate
            message_count = await _count_messages(user_id, month, year, db)
            return {
                "success": True,
                "data": {
                    "has_data":           False,
                    "message_count":      message_count,
                    "messages_remaining": max(0, MIN_MESSAGES_REQUIRED - message_count),
                    "qualifies":          message_count >= MIN_MESSAGES_REQUIRED,
                },
                "error": None
            }

        return {
            "success": True,
            "data": {
                "id":               report.id,
                "month":            report.month,
                "year":             report.year,
                "last_generated_at": report.created_at.isoformat(),
                **json.loads(report.report_data)
            },
            "error": None
        }
    except Exception as e:
        logger.error(f"get_mirror_me_by_date error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch monthly report")
