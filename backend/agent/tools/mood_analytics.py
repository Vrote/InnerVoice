# backend/agent/tools/mood_analytics.py
import logging
import collections
from datetime import datetime, timedelta
from sqlalchemy.future import select
from backend.agent.state import AgentState
from backend.database.connection import AsyncSessionLocal
from backend.database.models import EmotionRecord

logger = logging.getLogger(__name__)

class MoodAnalyticsTool:
    async def arun(self, state: AgentState) -> dict:
        user_id = state["user_id"]
        
        try:
            now = datetime.utcnow()
            date_7d = now - timedelta(days=7)
            date_30d = now - timedelta(days=30)
            
            async with AsyncSessionLocal() as session:
                q = select(EmotionRecord).where(
                    EmotionRecord.user_id == user_id,
                    EmotionRecord.created_at >= date_30d
                ).order_by(EmotionRecord.created_at.desc())
                res = await session.execute(q)
                records = res.scalars().all()
                
            if not records:
                return {
                    "avg_mood_7d": 5.0,
                    "avg_mood_30d": 5.0,
                    "most_common_emotion": "neutral",
                    "best_day_week": None,
                    "hardest_day_week": None,
                    "mood_trend": "stable",
                    "record_count_30d": 0
                }
                
            records_7d = [r for r in records if r.created_at >= date_7d]
            records_prev_23d = [r for r in records if r.created_at < date_7d]
            
            avg_mood_30d = sum(r.mood_score for r in records) / len(records)
            avg_mood_7d = sum(r.mood_score for r in records_7d) / len(records_7d) if records_7d else avg_mood_30d
            
            emotions = [r.primary_emotion for r in records]
            most_common_emotion = collections.Counter(emotions).most_common(1)[0][0] if emotions else "neutral"
            
            if records_prev_23d:
                avg_prev = sum(r.mood_score for r in records_prev_23d) / len(records_prev_23d)
                diff = avg_mood_7d - avg_prev
                if diff >= 0.5:
                    trend = "up"
                elif diff <= -0.5:
                    trend = "down"
                else:
                    trend = "stable"
            else:
                trend = "stable"
                
            best_day = None
            hardest_day = None
            if records_7d:
                best = max(records_7d, key=lambda x: x.mood_score)
                hardest = min(records_7d, key=lambda x: x.mood_score)
                best_day = {
                    "date": best.created_at.strftime("%A, %b %d"),
                    "mood_score": best.mood_score,
                    "emotion": best.primary_emotion
                }
                hardest_day = {
                    "date": hardest.created_at.strftime("%A, %b %d"),
                    "mood_score": hardest.mood_score,
                    "emotion": hardest.primary_emotion
                }
                
            return {
                "avg_mood_7d": round(avg_mood_7d, 2),
                "avg_mood_30d": round(avg_mood_30d, 2),
                "most_common_emotion": most_common_emotion,
                "best_day_week": best_day,
                "hardest_day_week": hardest_day,
                "mood_trend": trend,
                "record_count_30d": len(records)
            }
        except Exception as e:
            logger.error(f"Error in MoodAnalyticsTool: {e}")
            return {
                "avg_mood_7d": 5.0,
                "avg_mood_30d": 5.0,
                "most_common_emotion": "neutral",
                "best_day_week": None,
                "hardest_day_week": None,
                "mood_trend": "stable",
                "error": str(e)
            }
