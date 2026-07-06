# backend/agent/tools/followup_question.py
import json
import logging
from backend.agent.state import AgentState
from backend.services.llm_service import run_llq_call

logger = logging.getLogger(__name__)

class FollowupQuestionTool:
    async def arun(self, state: AgentState) -> dict:
        user_message = state["user_message"]
        voice_profile = state.get("voice_profile") or {}

        prompt = f"""Generate a single, specific question to ask the user to go deeper.

The user wrote: {user_message}

What ONE question would most help you understand their situation better?
The question should be:
- Specific, not generic
- Show you've been listening closely
- Easy to answer
- In their communication style (style guidelines: {voice_profile.get("response_style_instructions", "natural casual")})

Return ONLY valid JSON:
{{
  "question": "When you say you're upset — is it more about what happened, or how people reacted to it?"
}}"""

        try:
            res_text = await run_llq_call(prompt, orchestrator=False, json_mode=True)
            res_json = json.loads(res_text)
            return {"question": res_json.get("question", "Can you tell me more about how you are feeling?")}
        except Exception as e:
            logger.error(f"FollowupQuestionTool error: {e}")
            return {"question": "Can you tell me more about how you are feeling?"}
