# backend/routes/emotions.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.core.security import get_current_user_id
from backend.services.emotion_service import get_emotion_timeline, get_emotion_stats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/emotions", tags=["emotions"])

@router.get("/timeline")
async def get_timeline(days: int = 30, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        timeline = await get_emotion_timeline(user_id, days, db)
        return [
            {
                "id": r.id,
                "entry_id": r.entry_id,
                "primary_emotion": r.primary_emotion,
                "secondary_emotion": r.secondary_emotion,
                "intensity": r.intensity,
                "mood_score": r.mood_score,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for r in timeline
        ]
    except Exception as e:
        logger.error(f"Error in emotions/timeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch emotion timeline")

@router.get("/stats")
async def get_stats(days: int = 30, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        stats = await get_emotion_stats(user_id, days, db)
        return stats
    except Exception as e:
        logger.error(f"Error in emotions/stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch emotion stats")
