# backend/routes/history.py
"""
GET /api/history  — Paginated conversation history filtered by year/month
"""
import json
import logging
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database.models import Message, EmotionRecord
from backend.core.security import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    year: int = Query(None),
    month: int = Query(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        now = datetime.datetime.utcnow()
        y = year or now.year
        m = month or now.month

        # Month boundaries
        start_date = datetime.datetime(y, m, 1)
        if m == 12:
            end_date = datetime.datetime(y + 1, 1, 1)
        else:
            end_date = datetime.datetime(y, m + 1, 1)

        offset = (page - 1) * limit
        q = select(Message).where(
            Message.user_id == user_id,
            Message.processing_status.in_(["done", "waiting_for_user"]),
            Message.created_at >= start_date,
            Message.created_at < end_date
        ).order_by(Message.created_at.desc()).offset(offset).limit(limit)

        res  = await db.execute(q)
        msgs = res.scalars().all()

        # Fetch emotions for these messages
        msg_ids = [m.id for m in msgs]
        q_em    = select(EmotionRecord).where(EmotionRecord.message_id.in_(msg_ids))
        res_em  = await db.execute(q_em)
        emotion_map = {em.message_id: em for em in res_em.scalars().all()}

        items = []
        for m in msgs:
            em = emotion_map.get(m.id)
            items.append({
                "id":               m.id,
                "user_message":     m.user_message,
                "ai_response":      m.ai_response,
                "word_count":       m.word_count,
                "created_at":       m.created_at.isoformat(),
                "followup_question": m.followup_question,
                "followup_pending": m.followup_pending,
                "tools_used":       json.loads(m.tools_used or "[]"),
                "emotion": {
                    "primary":   em.primary_emotion if em else "neutral",
                    "mood_score": em.mood_score if em else 5.0,
                    "intensity":  em.intensity if em else 0.5,
                } if em else None,
            })

        return {
            "success": True,
            "data": {
                "items": items,
                "page":  page,
                "limit": limit,
                "year":  y,
                "month": m,
                "has_more": len(msgs) == limit
            },
            "error": None
        }
    except Exception as e:
        logger.error(f"get_history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")
