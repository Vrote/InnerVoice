# backend/agent/tools/emotion_analyze.py
import uuid
import json
import logging
from datetime import datetime
from backend.agent.state import AgentState
from backend.database.connection import AsyncSessionLocal
from backend.database.models import EmotionRecord
from backend.services.llm_service import run_llq_call

logger = logging.getLogger(__name__)

class EmotionAnalyzeTool:
    async def arun(self, state: AgentState) -> dict:
        user_message = state["user_message"]
        user_id = state["user_id"]
        message_id = state["message_id"]

        prompt = f"""Analyze this message and detect the emotional state.

Return ONLY valid JSON:
{{
  "primary_emotion": "one of: happy|sad|angry|lonely|hopeful|anxious|burnout|excited|grateful|confused|motivated|fearful|disappointed|overwhelmed|nostalgic|neutral",
  "secondary_emotion": "another emotion or null",
  "intensity": 0.7,
  "mood_score": 6.5,
  "all_emotions": {{"anxious": 0.7, "hopeful": 0.3}},
  "emotional_summary": "one sentence",
  "structured_events": {{
    "important_events": [],
    "people_mentioned": [],
    "goals_expressed": [],
    "achievements": [],
    "worries": [],
    "topics": []
  }}
}}

Message: {user_message}"""

        try:
            res_text = await run_llq_call(prompt, orchestrator=False, json_mode=True)
            res_json = json.loads(res_text)

            primary = res_json.get("primary_emotion", "neutral")
            secondary = res_json.get("secondary_emotion")
            intensity = float(res_json.get("intensity", 0.5))
            mood_score = float(res_json.get("mood_score", 5.0))

            async with AsyncSessionLocal() as session:
                record = EmotionRecord(
                    id=f"em_{uuid.uuid4().hex[:12]}",
                    user_id=user_id,
                    message_id=message_id,
                    primary_emotion=primary,
                    secondary_emotion=secondary,
                    intensity=intensity,
                    mood_score=mood_score,
                    confidence=0.9,
                    raw_metadata=json.dumps(res_json),
                    created_at=datetime.utcnow()
                )
                session.add(record)
                await session.commit()

            return res_json
        except Exception as e:
            logger.error(f"EmotionAnalyzeTool error: {e}")
            fallback = {
                "primary_emotion": "neutral",
                "secondary_emotion": None,
                "intensity": 0.5,
                "mood_score": 5.0,
                "all_emotions": {"neutral": 1.0},
                "emotional_summary": "Felt neutral.",
                "structured_events": {
                    "important_events": [], "people_mentioned": [],
                    "goals_expressed": [], "achievements": [],
                    "worries": [], "topics": []
                }
            }
            try:
                async with AsyncSessionLocal() as session:
                    record = EmotionRecord(
                        id=f"em_{uuid.uuid4().hex[:12]}",
                        user_id=user_id,
                        message_id=message_id,
                        primary_emotion="neutral",
                        secondary_emotion=None,
                        intensity=0.5,
                        mood_score=5.0,
                        confidence=0.5,
                        raw_metadata=json.dumps(fallback),
                        created_at=datetime.utcnow()
                    )
                    session.add(record)
                    await session.commit()
            except Exception as dbe:
                logger.error(f"Failed to write emotion fallback to db: {dbe}")
            return fallback
