# backend/agent/tools/memory_retrieve.py
import logging
from backend.agent.state import AgentState
from backend.services.vector_store import query_memories_vector_store, query_entries_vector_store

logger = logging.getLogger(__name__)

class MemoryRetrieveTool:
    async def arun(self, state: AgentState) -> dict:
        user_id = state["user_id"]
        user_message = state["user_message"]

        try:
            semantic_memories = await query_memories_vector_store(user_id, user_message, limit=5)
            similar_entries   = await query_entries_vector_store(user_id, user_message, limit=3)

            return {
                "semantic_memories": semantic_memories,
                "similar_entries": similar_entries,
                "total_retrieved": len(semantic_memories) + len(similar_entries)
            }
        except Exception as e:
            logger.error(f"MemoryRetrieveTool error: {e}")
            return {"semantic_memories": [], "similar_entries": [], "total_retrieved": 0}
