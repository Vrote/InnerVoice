# backend/agent/tools/journal_search.py
import json
import logging
from backend.agent.state import AgentState
from backend.services.llm_service import run_llq_call
from backend.services.vector_store import query_entries_vector_store

logger = logging.getLogger(__name__)

class JournalSearchTool:
    async def arun(self, state: AgentState) -> dict:
        user_id     = state["user_id"]
        user_message = state["user_message"]

        try:
            prompt = f"""Given the user's current message, extract a search query of 3-6 keywords to find relevant past messages.
Message: {user_message}
Return ONLY valid JSON:
{{"query": "argument with manager"}}"""

            res_text = await run_llq_call(prompt, orchestrator=False, json_mode=True)
            res_json = json.loads(res_text)
            query    = res_json.get("query", user_message[:50])

            results = await query_entries_vector_store(user_id, query, limit=3)
            return {"past_entries": results, "search_query": query}
        except Exception as e:
            logger.error(f"JournalSearchTool error: {e}")
            return {"past_entries": [], "error": str(e)}
