# backend/agent/tools/memory_save.py
import uuid
import json
import logging
from datetime import datetime
from sqlalchemy.future import select
from backend.agent.state import AgentState
from backend.database.connection import AsyncSessionLocal
from backend.database.models import Memory
from backend.services.llm_service import run_llq_call
from backend.services.vector_store import add_memory_to_vector_store

logger = logging.getLogger(__name__)

class MemorySaveTool:
    async def arun(self, state: AgentState) -> dict:
        user_id = state["user_id"]
        message_id = state["message_id"]
        user_message = state["user_message"]
        emotion_data = state.get("emotions_detected") or {}

        try:
            existing_memory_texts = []
            async with AsyncSessionLocal() as session:
                q = select(Memory).where(Memory.user_id == user_id, Memory.is_active == True)
                res = await session.execute(q)
                existing = res.scalars().all()
                existing_memory_texts = [m.memory_text for m in existing]

            prompt = f"""Decide what from this message deserves permanent long-term memory.

SAVE: career goals, hobbies, relationships, fears, achievements, habits, values, preferences.
DO NOT SAVE: daily events, temporary feelings, weather, what they ate.

Existing memories (don't duplicate):
{existing_memory_texts}

Today's message:
{user_message}

Emotion / event analysis:
{json.dumps(emotion_data)}

Return ONLY valid JSON:
{{
  "memories_to_store": [
    {{
      "memory_text": "User wants to become an AI Engineer",
      "memory_type": "goal",
      "importance_score": 0.9
    }}
  ]
}}

If nothing new: {{"memories_to_store": []}}"""

            res_text = await run_llq_call(prompt, orchestrator=False, json_mode=True)
            res_json = json.loads(res_text)

            stored = []
            memories_to_store = res_json.get("memories_to_store", [])

            async with AsyncSessionLocal() as session:
                for item in memories_to_store:
                    text = item.get("memory_text", "").strip()
                    m_type = item.get("memory_type", "context")
                    score = float(item.get("importance_score", 0.5))

                    if not text or text in existing_memory_texts:
                        continue

                    memory_id = f"mem_{uuid.uuid4().hex[:12]}"
                    new_memory = Memory(
                        id=memory_id,
                        user_id=user_id,
                        memory_text=text,
                        memory_type=m_type,
                        importance_score=score,
                        source_message_id=message_id,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        last_referenced=None,
                        reference_count=0
                    )
                    session.add(new_memory)
                    await add_memory_to_vector_store(
                        user_id=user_id,
                        memory_id=memory_id,
                        memory_text=text,
                        memory_type=m_type,
                        importance=score
                    )
                    stored.append(text)

                await session.commit()

            return {"memories_stored": stored}
        except Exception as e:
            logger.error(f"MemorySaveTool error: {e}")
            return {"memories_stored": [], "error": str(e)}
