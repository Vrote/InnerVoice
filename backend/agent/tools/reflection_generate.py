# backend/agent/tools/reflection_generate.py
import json
import logging
from backend.agent.state import AgentState
from backend.services.llm_service import run_llq_call

logger = logging.getLogger(__name__)

class ReflectionGenerateTool:
    async def arun(self, state: AgentState) -> dict:
        user_message   = state["user_message"]
        memories       = state.get("memories_retrieved") or []
        patterns       = state.get("patterns_detected") or []
        emotions       = state.get("emotions_detected") or {}

        primary_emotion = emotions.get("primary_emotion", "neutral")
        intensity       = emotions.get("intensity", 0.5)
        structured      = emotions.get("structured_events", {})

        prompt = f"""Generate 1-2 thoughtful reflection prompts for this user.

These should:
- Be specific to what they wrote TODAY
- Connect to their history if relevant
- Help them understand themselves (not solve their problem)
- Sound like a curious, caring friend — not a therapist
- NEVER be generic like "How does that make you feel?"

Context:
Today's Message: {user_message}
Memories: {[m.get("text","") for m in memories[:3]]}
Patterns: {patterns[:5]}
Emotion: {primary_emotion} at {intensity} intensity
Events: {structured}

Return ONLY valid JSON:
{{
  "prompts": [
    "You've mentioned your manager three times this week — what do you think that relationship is costing you emotionally?",
    "You sounded lighter when writing about drawing. When did you last make time for it?"
  ]
}}
Return [] if today's message is straightforward and doesn't need reflection."""

        try:
            res_text = await run_llq_call(prompt, orchestrator=False, json_mode=True)
            res_json = json.loads(res_text)
            return {"prompts": res_json.get("prompts", [])}
        except Exception as e:
            logger.error(f"ReflectionGenerateTool error: {e}")
            return {"prompts": []}
