# backend/services/mirror_me_service.py
import json
import uuid
import logging
import collections
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import MirrorMeReport, Message, EmotionRecord
from backend.services.llm_service import run_llq_call

logger = logging.getLogger(__name__)

async def get_or_generate_mirror_me_report(user_id: str, month: int, year: int, db: AsyncSession, force_regenerate: bool = False):
    try:
        # Check if already exists
        q   = select(MirrorMeReport).where(
            MirrorMeReport.user_id == user_id,
            MirrorMeReport.month   == month,
            MirrorMeReport.year    == year
        )
        res    = await db.execute(q)
        report = res.scalars().first()
        if report and not force_regenerate:
            return json.loads(report.report_data)

        # Date range
        start_date = datetime(year, month, 1)
        end_date   = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

        # Fetch messages in the month
        q_msgs = select(Message).where(
            Message.user_id    == user_id,
            Message.created_at >= start_date,
            Message.created_at <  end_date
        ).order_by(Message.created_at.asc())
        res_msgs = await db.execute(q_msgs)
        messages = res_msgs.scalars().all()

        if not messages:
            return {
                "message": f"No messages found for {month}/{year}. Start chatting to get your monthly Mirror Me report!",
                "has_data": False
            }

        # Fetch corresponding emotions
        msg_ids  = [m.id for m in messages]
        q_em     = select(EmotionRecord).where(EmotionRecord.message_id.in_(msg_ids))
        res_em   = await db.execute(q_em)
        emotions = res_em.scalars().all()

        entries_list  = [{"date": m.created_at.strftime("%Y-%m-%d"), "content": m.user_message} for m in messages]
        emotions_list = [{"primary": em.primary_emotion, "intensity": em.intensity, "mood_score": em.mood_score} for em in emotions]

        # Word frequency
        all_text = " ".join([m.user_message for m in messages])
        words    = [w.lower().strip(".,!?;:()\"'") for w in all_text.split() if len(w) > 4]
        stops    = {"about","there","their","would","could","should","myself","really","think",
                    "going","today","feeling","where","which","through","people","after","before",
                    "while","during","under","myself","these","those","every","never"}
        words    = [w for w in words if w not in stops]
        word_freq = dict(collections.Counter(words).most_common(20))

        avg_mood = sum(em.mood_score for em in emotions) / len(emotions) if emotions else 5.0

        prompt = f"""You are a senior psychologist and linguistic analyst writing a monthly reflection report called 'Mirror Me' that is designed to help the user reflect, but also serve as a structured resource for their doctor, therapist, or psychologist to analyze their mental health.
Generate a beautiful, personalized, and deep monthly analysis.

Message history for the month:
{json.dumps(entries_list)}

Emotion logs for the month:
{json.dumps(emotions_list)}

Linguistic word frequency:
{json.dumps(word_freq)}

Return ONLY valid JSON:
{{
  "month_summary": "2-3 sentences summarizing the overall monthly emotional landscape...",
  "mood_trend_description": "Analysis of how their mood changed or stabilized during the month...",
  "insights": [
    {{
      "title": "Trigger / Theme Title (e.g. Relationship boundaries)",
      "description": "Deep analytical description of what happened, referencing events and how they reacted."
    }}
  ],
  "lessons_learned": [
    "Lesson 1...",
    "Lesson 2..."
  ],
  "self_care_recommendations": [
    "Tip 1...",
    "Tip 2..."
  ],
  "clinical_insights": {{
    "practitioner_summary": "A concise, professional summary formatted for a doctor/therapist (using clinical terminology where appropriate) summarizing current presentation, main stressors, and emotional themes.",
    "cognitive_distortions_detected": [
      {{
        "distortion_type": "Name of pattern (e.g., Catastrophizing, All-or-Nothing Thinking, Mind Reading, Emotional Reasoning)",
        "evidence": "Brief explanation of where or how this manifested in their messages."
      }}
    ],
    "key_stressors": [
      "Stressor 1...",
      "Stressor 2..."
    ],
    "coping_mechanisms_observed": [
      "Observed healthy or unhealthy coping mechanism (e.g., mindfulness, cognitive reframing, avoidance, rumination)..."
    ],
    "mood_volatility": "Low / Moderate / High"
  }},
  "supportive_closing": "A warm, voice-matched closing message from their inner reflection companion."
}}"""

        res_text = await run_llq_call(prompt, orchestrator=True, json_mode=True)
        res_json = json.loads(res_text)

        res_json["avg_mood"]       = round(avg_mood, 2)
        res_json["total_messages"] = len(messages)
        res_json["word_cloud"]     = [{"text": k, "value": v} for k, v in word_freq.items()]
        res_json["has_data"]       = True

        if report:
            await db.delete(report)
            await db.flush()

        db_report = MirrorMeReport(
            id=f"rep_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            month=month,
            year=year,
            report_data=json.dumps(res_json),
            created_at=datetime.utcnow()
        )
        db.add(db_report)
        await db.commit()

        return res_json
    except Exception as e:
        logger.error(f"Mirror Me report generation error: {e}")
        await db.rollback()
        return {
            "message": "Failed to generate report due to server error.",
            "has_data": False,
            "error": str(e)
        }
