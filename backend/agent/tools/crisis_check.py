# backend/agent/tools/crisis_check.py
import logging
from backend.agent.state import AgentState

logger = logging.getLogger(__name__)

CRISIS_KEYWORDS_SEVERE = [
    "kill myself", "want to die", "end my life", "suicide", "self harm",
    "cutting myself", "don't want to live", "no reason to live",
    "can't go on", "cannot go on", "take my own life", "overdose",
]
CRISIS_KEYWORDS_MODERATE = [
    "hopeless", "worthless", "no one cares", "give up", "pointless",
    "nothing matters", "exhausted with life", "tired of everything",
    "breaking down", "falling apart",
]

class CrisisCheckTool:
    async def arun(self, state: AgentState) -> dict:
        try:
            text_lower = state["user_message"].lower()

            severe = any(kw in text_lower for kw in CRISIS_KEYWORDS_SEVERE)
            moderate = any(kw in text_lower for kw in CRISIS_KEYWORDS_MODERATE)

            if severe:
                return {"crisis_triggered": True, "crisis_level": "severe"}
            if moderate:
                return {"crisis_triggered": True, "crisis_level": "moderate"}
            return {"crisis_triggered": False, "crisis_level": "none"}
        except Exception as e:
            logger.error(f"CrisisCheckTool error: {e}")
            return {"crisis_triggered": False, "crisis_level": "none"}
