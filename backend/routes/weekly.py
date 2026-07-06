# backend/routes/weekly.py
import json
import uuid
import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.database.models import WeeklySummary, Message, EmotionRecord
from backend.core.security import get_current_user_id
from backend.services.llm_service import run_llq_call

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weekly", tags=["weekly"])


async def generate_weekly_summary_data(user_id: str, db: AsyncSession):
    now        = datetime.datetime.utcnow()
    week_start = now - datetime.timedelta(days=7)

    q_msgs = select(Message).where(
        Message.user_id    == user_id,
        Message.created_at >= week_start,
        Message.processing_status.in_(["done", "waiting_for_user"])
    ).order_by(Message.created_at.asc())
    res_msgs = await db.execute(q_msgs)
    messages = res_msgs.scalars().all()

    if not messages:
        return None

    msg_ids = [m.id for m in messages]
    q_em    = select(EmotionRecord).where(EmotionRecord.message_id.in_(msg_ids))
    res_em  = await db.execute(q_em)
    emotions = res_em.scalars().all()

    entries_list  = [{"date": m.created_at.strftime("%A, %b %d"), "content": m.user_message} for m in messages]
    emotions_list = [{"primary": em.primary_emotion, "intensity": em.intensity, "mood_score": em.mood_score} for em in emotions]
    avg_mood      = sum(em.mood_score for em in emotions) / len(emotions) if emotions else 5.0

    prompt = f"""You are a reflective journal companion. Summarize this user's last 7 days.

Messages:
{json.dumps(entries_list)}

Emotions logged:
{json.dumps(emotions_list)}

Return ONLY valid JSON:
{{
  "summary_text": "2-3 paragraphs synthesizing their week, highlighting their main thoughts and feelings...",
  "most_common_emotion": "happy|sad|anxious|etc.",
  "most_positive_day": "DayName (e.g. Wednesday)",
  "most_stressful_day": "DayName or None",
  "biggest_achievement": "one brief sentence description or None"
}}"""

    try:
        res_text = await run_llq_call(prompt, orchestrator=False, json_mode=True)
        res_json = json.loads(res_text)

        summary = WeeklySummary(
            id=f"ws_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            week_start=week_start,
            week_end=now,
            summary_text=res_json.get("summary_text", "Reflecting on your week."),
            most_common_emotion=res_json.get("most_common_emotion", "neutral"),
            most_positive_day=res_json.get("most_positive_day", "Sunday"),
            most_stressful_day=res_json.get("most_stressful_day"),
            biggest_achievement=res_json.get("biggest_achievement"),
            average_mood_score=round(avg_mood, 2),
            entries_count=len(messages),
            created_at=datetime.datetime.utcnow()
        )
        db.add(summary)
        await db.commit()
        return summary
    except Exception as e:
        logger.error(f"Weekly summary generation error: {e}")
        await db.rollback()
        return None


@router.get("")
async def get_weekly_summary(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        recent_threshold = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        q = select(WeeklySummary).where(
            WeeklySummary.user_id    == user_id,
            WeeklySummary.created_at >= recent_threshold
        ).order_by(WeeklySummary.created_at.desc())

        res     = await db.execute(q)
        summary = res.scalars().first()

        if not summary:
            summary = await generate_weekly_summary_data(user_id, db)

        if not summary:
            return {
                "success": True,
                "data": {"summary_text": "Write some messages this week to get your weekly summary!", "has_data": False},
                "error": None
            }

        return {
            "success": True,
            "data": {
                "id":                 summary.id,
                "week_start":         summary.week_start.strftime("%Y-%m-%d"),
                "week_end":           summary.week_end.strftime("%Y-%m-%d"),
                "summary_text":       summary.summary_text,
                "most_common_emotion": summary.most_common_emotion,
                "most_positive_day":  summary.most_positive_day,
                "most_stressful_day": summary.most_stressful_day,
                "biggest_achievement": summary.biggest_achievement,
                "average_mood_score": summary.average_mood_score,
                "entries_count":      summary.entries_count,
                "has_data":           True
            },
            "error": None
        }
    except Exception as e:
        logger.error(f"get_weekly_summary error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weekly summary")
