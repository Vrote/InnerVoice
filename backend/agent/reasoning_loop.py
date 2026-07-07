# backend/agent/reasoning_loop.py
"""
InnerVoice v4.0  —  Multi-node LangGraph Reasoning Loop
=========================================================
Graph flow:
  START → crisis_node
         ├─ crisis_severe  → respond_node → END
         └─ no_crisis      → plan_node
                               └─ execute_tool_node  (runs ONE tool per pass)
                                     └─ reflect_node
                                           ├─ needs_more_tools (iterations < 5) → execute_tool_node
                                           ├─ followup_needed → respond_node → END
                                           └─ done → respond_node → END
"""

import json
import logging
from typing import Literal

from langgraph.graph import StateGraph, END

from backend.agent.state import AgentState
from backend.services.llm_service import run_llq_call
from backend.services.vector_store import add_entry_to_vector_store
from backend.database.connection import AsyncSessionLocal
from backend.database.models import Message, VoiceProfile
from sqlalchemy.future import select

# Tool imports
from backend.agent.tools.crisis_check      import CrisisCheckTool
from backend.agent.tools.voice_profile     import VoiceProfileTool
from backend.agent.tools.memory_retrieve   import MemoryRetrieveTool
from backend.agent.tools.emotion_analyze   import EmotionAnalyzeTool
from backend.agent.tools.pattern_detect    import PatternDetectTool
from backend.agent.tools.goal_tracker      import GoalTrackerTool
from backend.agent.tools.memory_save       import MemorySaveTool
from backend.agent.tools.journal_search    import JournalSearchTool
from backend.agent.tools.reflection_generate import ReflectionGenerateTool
from backend.agent.tools.followup_question import FollowupQuestionTool
from backend.agent.tools.plan_generator    import PlanGeneratorTool
from backend.agent.tools.mood_analytics    import MoodAnalyticsTool
from backend.agent.tools.summary_generate  import SummaryGenerateTool

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Tool registry
# ──────────────────────────────────────────────────────────────────────────────
TOOL_REGISTRY = {
    "voice_profile":      VoiceProfileTool(),
    "memory_retrieve":    MemoryRetrieveTool(),
    "emotion_analyze":    EmotionAnalyzeTool(),
    "pattern_detect":     PatternDetectTool(),
    "goal_tracker":       GoalTrackerTool(),
    "memory_save":        MemorySaveTool(),
    "journal_search":     JournalSearchTool(),
    "reflection_generate": ReflectionGenerateTool(),
    "followup_question":  FollowupQuestionTool(),
    "plan_generator":     PlanGeneratorTool(),
    "mood_analytics":     MoodAnalyticsTool(),
    "summary_generate":   SummaryGenerateTool(),
}

MAX_ITERATIONS = 5

# ──────────────────────────────────────────────────────────────────────────────
# Node 1: Crisis Check
# ──────────────────────────────────────────────────────────────────────────────
async def crisis_node(state: AgentState) -> AgentState:
    result = await CrisisCheckTool().arun(state)
    state["crisis_triggered"] = result.get("crisis_triggered", False)
    state["crisis_level"]     = result.get("crisis_level", "none")
    state["current_step"]     = "crisis"
    state["iterations"]       = state.get("iterations", 0)
    state["tools_used"]       = state.get("tools_used", [])
    state["tool_results"]     = state.get("tool_results", {})
    state["reasoning_log"]    = state.get("reasoning_log", [])
    state["action_plan"]      = state.get("action_plan", [])
    return state

def route_after_crisis(state: AgentState) -> Literal["plan_node", "respond_node"]:
    if state.get("crisis_triggered") and state.get("crisis_level") == "severe":
        return "respond_node"
    return "plan_node"

# ──────────────────────────────────────────────────────────────────────────────
# Node 2: Plan
# ──────────────────────────────────────────────────────────────────────────────
async def plan_node(state: AgentState) -> AgentState:
    user_message = state["user_message"]
    voice_profile = state.get("voice_profile") or {}
    memories     = state.get("memories_retrieved") or []
    history      = state.get("conversation_history") or []

    history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history[-6:]])
    memories_text = "\n".join([f"- {m.get('text','')}" for m in memories[:5]])

    prompt = f"""You are the orchestrator for InnerVoice, a psychological AI companion.

Decide which tools to run for this user's message.

Available tools:
- voice_profile: Analyze and update the user's writing style
- memory_retrieve: Fetch relevant memories from vector store
- emotion_analyze: Detect emotions in current message
- pattern_detect: Find recurring emotional/behavioral patterns (only if 5+ prior records)
- goal_tracker: Track progress on goals or create new ones
- memory_save: Save important long-term information to memory
- journal_search: Search past messages for context
- reflection_generate: Create reflective prompts about patterns
- followup_question: Generate a follow-up question when needed
- plan_generator: Build an action plan based on goals/events
- mood_analytics: Compute mood trends over last 7/30 days
- summary_generate: Summarize the user's recent message history

Conversation history (last 6 turns):
{history_text}

Current message: "{user_message}"
Crisis level: {state.get("crisis_level","none")}
User style hint: {voice_profile.get("dominant_tone","neutral")}
Relevant memories: {memories_text}

Return ONLY valid JSON:
{{
  "reasoning": "Brief explanation of your plan",
  "tools_to_run": ["voice_profile", "memory_retrieve", "emotion_analyze"],
  "needs_followup": false
}}

Rules:
- Always run voice_profile, memory_retrieve, emotion_analyze.
- Run memory_save to persist important new factual revelations (e.g. details about relationships, preferences, job, etc.).
- Run goal_tracker if user mentions achievements, goals, or setbacks.
- Run pattern_detect only if user seems to repeat a theme.
- CRITICAL: Run followup_question and set "needs_followup" to true when the user's message is vague, contains unresolved emotional issues, or uses context-free pronouns (like "they", "them", "she", "he", "him", "her", "that", "this", "it") without a clear referent in the immediate message or conversation history.
- Run plan_generator only when user asks "what should I do" or expresses a clear desire to act.
- Never run more than 7 tools total.
- Do NOT assume, invent, or hallucinate facts about the user's past if no memories are retrieved and conversation history is empty."""

    try:
        res_text = await run_llq_call(prompt, orchestrator=True, json_mode=True)
        res_json = json.loads(res_text)
    except Exception as e:
        logger.error(f"plan_node LLM error: {e}")
        res_json = {
            "reasoning": "Fallback plan due to LLM error.",
            "tools_to_run": ["voice_profile", "memory_retrieve", "emotion_analyze"],
            "needs_followup": False
        }

    valid_tools = [t for t in res_json.get("tools_to_run", []) if t in TOOL_REGISTRY]
    
    # Programmatic bridge to guarantee followup_question tool runs if flagged
    if res_json.get("needs_followup") is True:
        if "followup_question" not in valid_tools:
            valid_tools.append("followup_question")

    state["orchestrator_plan"] = res_json
    state["action_plan"]       = valid_tools
    state["current_step"]      = "plan"
    state["reasoning_log"].append({"step": "plan", "reasoning": res_json.get("reasoning","")})
    return state

# ──────────────────────────────────────────────────────────────────────────────
# Node 3: Execute Tool (one tool per pass)
# ──────────────────────────────────────────────────────────────────────────────
async def execute_tool_node(state: AgentState) -> AgentState:
    action_plan = state.get("action_plan", [])
    tools_used  = state.get("tools_used", [])

    # Find first tool not yet run
    next_tool = None
    for t in action_plan:
        if t not in tools_used:
            next_tool = t
            break

    if not next_tool:
        state["current_step"] = "execute_tool"
        return state

    logger.info(f"Executing tool: {next_tool} for message {state['message_id']}")
    tool = TOOL_REGISTRY[next_tool]
    try:
        result = await tool.arun(state)
    except Exception as e:
        logger.error(f"Tool {next_tool} crashed: {e}")
        result = {"error": str(e)}

    # Merge results into state
    tool_results = state.get("tool_results", {})
    tool_results[next_tool] = result
    state["tool_results"] = tool_results

    # Populate state fields from well-known tools
    if next_tool == "voice_profile":
        state["voice_profile"] = result
    elif next_tool == "memory_retrieve":
        state["memories_retrieved"] = result.get("semantic_memories", []) + result.get("similar_entries", [])
    elif next_tool == "emotion_analyze":
        state["emotions_detected"] = result
    elif next_tool == "pattern_detect":
        state["patterns_detected"] = result.get("patterns", [])

    tools_used.append(next_tool)
    state["tools_used"]  = tools_used
    state["iterations"]  = state.get("iterations", 0) + 1
    state["current_step"] = "execute_tool"
    state["reasoning_log"].append({"step": "execute_tool", "tool": next_tool, "result_summary": str(result)[:200]})
    return state

# ──────────────────────────────────────────────────────────────────────────────
# Node 4: Reflect
# ──────────────────────────────────────────────────────────────────────────────
async def reflect_node(state: AgentState) -> AgentState:
    action_plan = state.get("action_plan", [])
    tools_used  = state.get("tools_used", [])
    remaining   = [t for t in action_plan if t not in tools_used]

    state["current_step"]    = "reflect"
    state["waiting_on_user"] = False

    # Check if followup was requested
    if "followup_question" in tools_used:
        fq = state.get("tool_results", {}).get("followup_question", {})
        q  = fq.get("question", "")
        if q:
            state["followup_question"] = q
            state["waiting_on_user"]   = True

    return state

def route_after_reflect(
    state: AgentState
) -> Literal["execute_tool_node", "respond_node"]:
    action_plan = state.get("action_plan", [])
    tools_used  = state.get("tools_used", [])
    remaining   = [t for t in action_plan if t not in tools_used]
    iterations  = state.get("iterations", 0)

    if remaining and iterations < MAX_ITERATIONS:
        return "execute_tool_node"
    return "respond_node"

# ──────────────────────────────────────────────────────────────────────────────
# Node 5: Respond
# ──────────────────────────────────────────────────────────────────────────────
async def respond_node(state: AgentState) -> AgentState:
    user_message   = state["user_message"]
    user_id        = state["user_id"]
    message_id     = state["message_id"]
    crisis_level   = state.get("crisis_level", "none")
    voice_profile  = state.get("voice_profile") or {}
    memories       = state.get("memories_retrieved") or []
    emotions       = state.get("emotions_detected") or {}
    patterns       = state.get("patterns_detected") or []
    tool_results   = state.get("tool_results") or {}
    history        = state.get("conversation_history") or []
    waiting        = state.get("waiting_on_user", False)
    followup_q     = state.get("followup_question", "")

    # Build history context
    history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history[-8:]])

    # Gather supplemental context
    plan_data       = tool_results.get("plan_generator", {})
    reflection_data = tool_results.get("reflection_generate", {})
    mood_data       = tool_results.get("mood_analytics", {})
    pattern_insight = tool_results.get("pattern_detect", {}).get("insight_for_today")
    goals_result    = tool_results.get("goal_tracker", {})

    # CRISIS response
    if crisis_level in ("severe", "moderate") and state.get("crisis_triggered"):
        crisis_response = f"""I hear you, and I want you to know I'm fully present with you right now.

What you're feeling is real, and it makes sense that things feel this heavy.

Please know that you don't have to carry this alone. There are people whose only job is to listen:
- **iCall (India):** 9152987821
- **Vandrevala Foundation:** 1860-2662-345 (24/7)
- **International:** https://findahelpline.com

I'm here. Tell me what's happening — one small piece at a time. 💙"""
        state["final_response"] = crisis_response
    elif waiting and followup_q:
        # Partial response + followup question
        prompt = f"""You are InnerVoice — the user's deeply personal AI companion. Think like an empathetic, skilled psychologist/counselor, but communicate with the warmth, casualness, and intimacy of a close friend or the user's own inner self-reflection. Your goal is to guide the user to explore and resolve their struggles without sounding clinical or robotic.

Your response style (CRITICAL — mirror this exactly):
{voice_profile.get("response_style_instructions", "Be warm, personal, and casual.")}

Conversation history:
{history_text}

User's current message: "{user_message}"
Detected emotion: {emotions.get("primary_emotion","neutral")} (intensity: {emotions.get("intensity",0.5)})
Relevant memories: {[m.get("text","") for m in memories[:3]]}

Write a SHORT (2-4 sentence) warm acknowledgment of their message.
Then naturally transition to asking them this follow-up: "{followup_q}"
Do NOT number anything or use bullet points. Write like a human friend or their own supportive inner voice."""

        try:
            response = await run_llq_call(prompt, orchestrator=True, json_mode=False)
        except Exception as e:
            logger.error(f"respond_node LLM error: {e}")
            response = f"I hear you. {followup_q}"
        state["final_response"] = response
    else:
        # Full synthesized response
        extras = []
        if pattern_insight:
            extras.append(f"Pattern insight: {pattern_insight}")
        if plan_data.get("has_plan"):
            extras.append(f"Suggested plan: {plan_data.get('plan_title')} — {plan_data.get('encouragement')}")
        if goals_result.get("new_goals_created"):
            extras.append(f"New goals noted: {', '.join(goals_result['new_goals_created'])}")
        if goals_result.get("goals_completed"):
            extras.append(f"Celebrated completed goals: {', '.join(goals_result['goals_completed'])}")
        if reflection_data.get("prompts"):
            extras.append(f"Reflections: {'; '.join(reflection_data['prompts'][:2])}")

        prompt = f"""You are InnerVoice — the user's deeply personal AI companion. You have known them for a while. Think like an empathetic, skilled psychologist/counselor to validate their experiences and help them address their root problems, but express yourself with the warmth, comfort, and directness of a close friend or their own supportive inner self-talk. The user should feel like they are talking to a trusted companion or reflecting inward, not talking to a clinical therapist or AI assistant.

Your response style (CRITICAL — mirror this exactly):
{voice_profile.get("response_style_instructions", "Be warm, personal, and conversational.")}

Conversation history (last 8 turns):
{history_text}

User's current message: "{user_message}"

Context you've gathered:
- Detected emotion: {emotions.get("primary_emotion","neutral")} (intensity: {emotions.get("intensity",0.5)})
- Emotional summary: {emotions.get("emotional_summary","")}
- Relevant memories about this person: {[m.get("text","") for m in memories[:5]]}
- Patterns: {patterns[:3]}
- Mood trend: {mood_data.get("mood_trend","stable")} (7d avg: {mood_data.get("avg_mood_7d",5.0)})
- Additional context: {'; '.join(extras) if extras else "None"}

Write a response that:
1. Acknowledges what they said with genuine warmth and validation (reference their specific words).
2. Connects to what you know about them from memory (CRITICAL: if 'Relevant memories' list above is empty, do NOT make up or assume any facts about their past, family, or relationships; behave as if this is your very first conversation).
3. Offers a psychological insight, emotional validation, or gentle reframing of their problem. Help them unpack the root issue.
4. Ends naturally and comfortably (can ask one soft, self-reflective question if helpful).

Length: 3-6 sentences. No headers. No lists. Write like you truly know them and want to support them as a friend.
Do NOT start with "I" — vary your openings and focus the conversation on them."""

        try:
            response = await run_llq_call(prompt, orchestrator=True, json_mode=False)
        except Exception as e:
            logger.error(f"respond_node LLM error (full): {e}")
            response = "I'm here with you. Thank you for sharing that with me."

        state["final_response"] = response

    # Persist to DB
    try:
        async with AsyncSessionLocal() as session:
            q   = select(Message).where(Message.id == message_id)
            res = await session.execute(q)
            msg = res.scalars().first()
            if msg:
                msg.ai_response        = state["final_response"]
                msg.tools_used         = json.dumps(state.get("tools_used", []))
                msg.agent_plan         = json.dumps(state.get("orchestrator_plan", {}))
                msg.followup_question  = state.get("followup_question", "")
                msg.followup_pending   = state.get("waiting_on_user", False)
                msg.processing_status  = "waiting_for_user" if state.get("waiting_on_user") else "done"
                await session.commit()

        # Add to vector store for future retrieval
        emotion_tag = emotions.get("primary_emotion", "neutral") if emotions else "neutral"
        from datetime import datetime
        await add_entry_to_vector_store(
            user_id    = user_id,
            entry_id   = message_id,
            entry_text = user_message,
            date_str   = datetime.utcnow().strftime("%Y-%m-%d"),
            emotion    = emotion_tag
        )
    except Exception as e:
        logger.error(f"respond_node DB persist error: {e}")

    state["current_step"] = "respond"
    return state

# ──────────────────────────────────────────────────────────────────────────────
# Graph builder
# ──────────────────────────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("crisis_node",       crisis_node)
    graph.add_node("plan_node",         plan_node)
    graph.add_node("execute_tool_node", execute_tool_node)
    graph.add_node("reflect_node",      reflect_node)
    graph.add_node("respond_node",      respond_node)

    graph.set_entry_point("crisis_node")

    graph.add_conditional_edges(
        "crisis_node",
        route_after_crisis,
        {
            "plan_node":    "plan_node",
            "respond_node": "respond_node"
        }
    )
    graph.add_edge("plan_node",         "execute_tool_node")
    graph.add_edge("execute_tool_node", "reflect_node")
    graph.add_conditional_edges(
        "reflect_node",
        route_after_reflect,
        {
            "execute_tool_node": "execute_tool_node",
            "respond_node":      "respond_node"
        }
    )
    graph.add_edge("respond_node", END)

    return graph.compile()

# Singleton compiled graph
_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph

async def run_agent(initial_state: AgentState) -> AgentState:
    """Run the full agent reasoning loop and return the final state."""
    graph = get_graph()
    config = {"configurable": {"thread_id": initial_state["session_id"]}}
    result = await graph.ainvoke(initial_state, config=config)
    return result
