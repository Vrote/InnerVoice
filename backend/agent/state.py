# backend/agent/state.py
from typing import TypedDict, List, Dict, Optional, Any

class AgentState(TypedDict):
    # --- Core Identity ---
    user_id: str
    message_id: str          # maps to Message.id in `messages` table
    user_message: str        # the text the user sent
    session_id: str          # same as message_id, used for LangGraph thread

    # --- Context ---
    conversation_history: List[Dict]   # last N turns: [{role, content}]
    voice_profile: Dict                # latest VoiceProfile snapshot
    memories_retrieved: List[Dict]     # semantic + recency memories
    emotions_detected: Dict            # output of EmotionAnalyzeTool
    patterns_detected: List[Dict]      # output of PatternDetectTool
    goals_active: List[Dict]           # active goals for this user

    # --- Planning ---
    orchestrator_plan: Dict            # planner LLM output
    action_plan: List[str]             # ordered list of tool names to run
    tools_used: List[str]              # tools executed so far this cycle

    # --- Execution Control ---
    current_step: str                  # node name currently executing
    iterations: int                    # loop counter (cap at 5)
    reasoning_log: List[Dict]          # [{step, tool, result_summary}] for transparency

    # --- Crisis ---
    crisis_triggered: bool
    crisis_level: str                  # none|moderate|severe

    # --- Followup ---
    waiting_on_user: bool
    followup_question: str

    # --- Output ---
    final_response: str
    tool_results: Dict[str, Any]       # raw tool outputs keyed by tool name
