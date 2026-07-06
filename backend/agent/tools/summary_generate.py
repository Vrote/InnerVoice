# backend/agent/tools/summary_generate.py
import json
import logging
from sqlalchemy.future import select
from backend.agent.state import AgentState
from backend.database.connection import AsyncSessionLocal
from backend.database.models import Message, EmotionRecord
from backend.services.llm_service import run_llq_call

logger = logging.getLogger(__name__)

class SummaryGenerateTool:
    async def arun(self, state: AgentState) -> dict:
        user_id      = state["user_id"]
        voice_profile = state.get("voice_profile") or {}

        try:
            async with AsyncSessionLocal() as session:
                q = select(Message).where(Message.user_id == user_id).order_by(
                    Message.created_at.desc()
                ).limit(10)
                res = await session.execute(q)
                messages = res.scalars().all()

                msg_ids = [m.id for m in messages]
                q_em    = select(EmotionRecord).where(EmotionRecord.message_id.in_(msg_ids))
                res_em  = await session.execute(q_em)
                emotions = res_em.scalars().all()

            if not messages:
                return {"summary": "You haven't sent any messages yet. Start a conversation to get your summary!"}

            entries_list = [
                {"date": m.created_at.strftime("%Y-%m-%d"), "content": m.user_message}
                for m in reversed(messages)
            ]
            emotions_list = [
                {"message_id": em.message_id, "primary_emotion": em.primary_emotion, "mood_score": em.mood_score}
                for em in emotions
            ]

            prompt = f"""Summarize this user's conversation history.

Messages in period:
{json.dumps(entries_list)}

Emotions logged:
{json.dumps(emotions_list)}

User Voice Profile styling guidelines:
{voice_profile.get("response_style_instructions", "Be warm, casual, and supportive.")}

Return ONLY valid JSON:
{{
  "summary": "a narrative summary of 2-3 paragraphs written in the user's voice style reflecting on their recent conversations."
}}"""

            res_text = await run_llq_call(prompt, orchestrator=False, json_mode=True)
            res_json = json.loads(res_text)
            return {"summary": res_json.get("summary", "")}
        except Exception as e:
            logger.error(f"SummaryGenerateTool error: {e}")
            return {"summary": "Failed to generate summary.", "error": str(e)}
