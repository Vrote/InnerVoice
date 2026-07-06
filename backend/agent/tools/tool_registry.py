# backend/agent/tools/tool_registry.py
from backend.agent.tools.crisis_check import CrisisCheckTool
from backend.agent.tools.voice_profile import VoiceProfileTool
from backend.agent.tools.emotion_analyze import EmotionAnalyzeTool
from backend.agent.tools.memory_retrieve import MemoryRetrieveTool
from backend.agent.tools.memory_save import MemorySaveTool
from backend.agent.tools.journal_search import JournalSearchTool
from backend.agent.tools.pattern_detect import PatternDetectTool
from backend.agent.tools.mood_analytics import MoodAnalyticsTool
from backend.agent.tools.reflection_generate import ReflectionGenerateTool
from backend.agent.tools.goal_tracker import GoalTrackerTool
from backend.agent.tools.plan_generator import PlanGeneratorTool
from backend.agent.tools.summary_generate import SummaryGenerateTool
from backend.agent.tools.followup_question import FollowupQuestionTool

AVAILABLE_TOOLS = {
    "crisis_check":          CrisisCheckTool(),
    "voice_profile":         VoiceProfileTool(),
    "emotion_analyze":       EmotionAnalyzeTool(),
    "memory_retrieve":       MemoryRetrieveTool(),
    "memory_save":           MemorySaveTool(),
    "journal_search":        JournalSearchTool(),
    "pattern_detect":        PatternDetectTool(),
    "mood_analytics":        MoodAnalyticsTool(),
    "reflection_generate":   ReflectionGenerateTool(),
    "goal_tracker":          GoalTrackerTool(),
    "plan_generator":        PlanGeneratorTool(),
    "summary_generate":      SummaryGenerateTool(),
    "followup_question":     FollowupQuestionTool(),
}

TOOL_DESCRIPTIONS = {
    "crisis_check":        "ALWAYS run this first. Detects self-harm or crisis signals in the entry.",
    "voice_profile":       "Retrieve and update the user's writing style fingerprint. Run early to shape the final response style.",
    "emotion_analyze":     "Detect the user's emotional state (type + intensity + mood score) from the entry.",
    "memory_retrieve":     "Semantic search of long-term memories relevant to today's entry. Use when context from the past would help.",
    "memory_save":         "Decide what new memories to store from this entry. Run near the end after understanding the full picture.",
    "journal_search":      "Full-text search across past journal entries. Use when user references past events or patterns need confirmation.",
    "pattern_detect":      "Analyze emotional history to find recurring patterns. Use when user seems to be in a recurring situation.",
    "mood_analytics":      "Compute mood trends, averages, and statistics. Use when user asks about their overall emotional state.",
    "reflection_generate": "Generate thoughtful, personalized reflection questions. Use when the user would benefit from self-examination.",
    "goal_tracker":        "Create, update, or review the user's long-term goals. Use when goals are mentioned or progress is notable.",
    "plan_generator":      "Generate small, actionable next steps. Use when user expresses desire for change or asks what to do.",
    "summary_generate":    "Summarize a period of journal history. Use when user asks about patterns over time.",
    "followup_question":   "Ask the user a clarifying question when critical information is missing. Sets needs_followup=True.",
}
