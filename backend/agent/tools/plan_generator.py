# backend/agent/tools/plan_generator.py
import json
import logging
from backend.agent.state import AgentState
from backend.services.llm_service import run_llq_call

logger = logging.getLogger(__name__)

class PlanGeneratorTool:
    async def arun(self, state: AgentState) -> dict:
        user_message = state["user_message"]
        memories_retrieved = state.get("memories_retrieved") or []
        emotions_detected = state.get("emotions_detected") or {}

        primary_emotion = emotions_detected.get("primary_emotion", "neutral")
        goals_expressed = emotions_detected.get("structured_events", {}).get("goals_expressed", [])

        prompt = f"""Create a small, realistic action plan for this user based on what they shared.

User Message: {user_message}
Goals/desires expressed today: {goals_expressed}
User's long-term memories: {[m.get("text","") for m in memories_retrieved[:5]]}
Emotional state: {primary_emotion}

Rules:
- Max 3 steps
- Each step completable in 1-7 days
- SPECIFIC, not vague
- If user is overwhelmed (anxious or burnout), suggest only 1 gentle step

Return ONLY valid JSON:
{{
  "has_plan": true,
  "plan_title": "Starting your AI learning journey",
  "steps": [
    {{"step": "Create a LeetCode account and solve 1 easy problem today", "timeframe": "Today"}},
    {{"step": "List 5 AI companies you want to work at", "timeframe": "This week"}}
  ],
  "encouragement": "one warm, specific sentence"
}}"""

        try:
            res_text = await run_llq_call(prompt, orchestrator=False, json_mode=True)
            return json.loads(res_text)
        except Exception as e:
            logger.error(f"PlanGeneratorTool error: {e}")
            return {
                "has_plan": False,
                "plan_title": "Take it easy",
                "steps": [{"step": "Take a deep breath and rest today", "timeframe": "Today"}],
                "encouragement": "You are doing your best, and that is enough."
            }
