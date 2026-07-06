# backend/agent/tools/pattern_detect.py
import uuid
import json
import logging
from datetime import datetime
from sqlalchemy.future import select
from backend.agent.state import AgentState
from backend.database.connection import AsyncSessionLocal
from backend.database.models import EmotionRecord, Pattern
from backend.services.llm_service import run_llq_call

logger = logging.getLogger(__name__)

class PatternDetectTool:
    async def arun(self, state: AgentState) -> dict:
        user_id  = state["user_id"]
        emotions = state.get("emotions_detected") or {}

        try:
            async with AsyncSessionLocal() as session:
                q_em = select(EmotionRecord).where(
                    EmotionRecord.user_id == user_id
                ).order_by(EmotionRecord.created_at.desc()).limit(30)
                res_em = await session.execute(q_em)
                history = res_em.scalars().all()

                if len(history) < 5:
                    return {"patterns": [], "insight_for_today": None,
                            "message": "Not enough history to detect patterns (< 5 entries)"}

                q_pat = select(Pattern).where(Pattern.user_id == user_id)
                res_pat = await session.execute(q_pat)
                existing = res_pat.scalars().all()

                history_list = [
                    {
                        "date": h.created_at.strftime("%Y-%m-%d"),
                        "primary_emotion": h.primary_emotion,
                        "intensity": h.intensity,
                        "mood_score": h.mood_score
                    }
                    for h in history
                ]
                existing_list = [
                    {"id": p.id, "description": p.pattern_description,
                     "type": p.pattern_type, "occurrence_count": p.occurrence_count}
                    for p in existing
                ]

                prompt = f"""Analyze this user's emotional history and detect recurring patterns.

Emotion history (last 30 records, newest first):
{json.dumps(history_list)}

Currently known patterns:
{json.dumps(existing_list)}

Today's emotion: {emotions.get("primary_emotion","neutral")} at {emotions.get("intensity",0.5)} intensity
Today's topics: {json.dumps(emotions.get("structured_events",{}).get("topics",[]))}

Return ONLY valid JSON:
{{
  "new_patterns": [
    {{
      "pattern_description": "Stress increases significantly before exams and deadlines",
      "pattern_type": "temporal",
      "confidence": 0.8
    }}
  ],
  "confirmed_pattern_ids": ["existing_id1"],
  "insight_for_today": "one sentence insight to mention in response, or null"
}}
Only report patterns with confidence > 0.65."""

                res_text = await run_llq_call(prompt, orchestrator=False, json_mode=True)
                res_json = json.loads(res_text)

                new_patterns   = res_json.get("new_patterns", [])
                confirmed_ids  = res_json.get("confirmed_pattern_ids", [])
                insight        = res_json.get("insight_for_today")

                if confirmed_ids:
                    q_update  = select(Pattern).where(Pattern.id.in_(confirmed_ids))
                    res_update = await session.execute(q_update)
                    for pat in res_update.scalars().all():
                        pat.occurrence_count += 1
                        pat.last_confirmed    = datetime.utcnow()

                added = []
                for np in new_patterns:
                    desc   = np.get("pattern_description", "").strip()
                    p_type = np.get("pattern_type", "behavioral")
                    conf   = float(np.get("confidence", 0.7))
                    if not desc or conf <= 0.65:
                        continue
                    pat_id = f"pat_{uuid.uuid4().hex[:12]}"
                    session.add(Pattern(
                        id=pat_id,
                        user_id=user_id,
                        pattern_description=desc,
                        pattern_type=p_type,
                        confidence=conf,
                        first_detected=datetime.utcnow(),
                        last_confirmed=datetime.utcnow(),
                        occurrence_count=1
                    ))
                    added.append(desc)

                await session.commit()

                q_all    = select(Pattern).where(Pattern.user_id == user_id)
                res_all  = await session.execute(q_all)
                all_pats = [p.pattern_description for p in res_all.scalars().all()]

                return {"patterns": all_pats, "new_patterns_detected": added, "insight_for_today": insight}
        except Exception as e:
            logger.error(f"PatternDetectTool error: {e}")
            return {"patterns": [], "insight_for_today": None, "error": str(e)}
