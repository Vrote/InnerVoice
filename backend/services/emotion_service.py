# backend/services/emotion_service.py
import logging
import collections
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import EmotionRecord

logger = logging.getLogger(__name__)

async def get_emotion_timeline(user_id: str, days: int, db: AsyncSession):
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        q = select(EmotionRecord).where(
            EmotionRecord.user_id == user_id,
            EmotionRecord.created_at >= cutoff
        ).order_by(EmotionRecord.created_at.asc())
        res = await db.execute(q)
        return res.scalars().all()
    except Exception as e:
        logger.error(f"Error fetching emotion timeline: {e}")
        return []

async def get_emotion_stats(user_id: str, days: int, db: AsyncSession):
    try:
        timeline = await get_emotion_timeline(user_id, days, db)
        if not timeline:
            return {
                "average_mood": 5.0,
                "most_common_emotion": "neutral",
                "emotion_counts": {},
                "total_records": 0
            }
            
        total = len(timeline)
        avg_mood = sum(r.mood_score for r in timeline) / total
        
        emotions = [r.primary_emotion for r in timeline]
        counts = dict(collections.Counter(emotions))
        most_common = collections.Counter(emotions).most_common(1)[0][0]
        
        return {
            "average_mood": round(avg_mood, 2),
            "most_common_emotion": most_common,
            "emotion_counts": counts,
            "total_records": total
        }
    except Exception as e:
        logger.error(f"Error computing emotion stats: {e}")
        return {
            "average_mood": 5.0,
            "most_common_emotion": "neutral",
            "emotion_counts": {},
            "total_records": 0
        }
