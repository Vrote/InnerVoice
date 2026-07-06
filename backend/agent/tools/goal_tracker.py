# backend/agent/tools/goal_tracker.py
import uuid
import json
import logging
from datetime import datetime
from sqlalchemy.future import select
from backend.agent.state import AgentState
from backend.database.connection import AsyncSessionLocal
from backend.database.models import Goal
from backend.services.llm_service import run_llq_call

logger = logging.getLogger(__name__)

class GoalTrackerTool:
    async def arun(self, state: AgentState) -> dict:
        user_id      = state["user_id"]
        message_id   = state["message_id"]
        user_message = state["user_message"]
        emotions     = state.get("emotions_detected") or {}

        try:
            async with AsyncSessionLocal() as session:
                q = select(Goal).where(Goal.user_id == user_id, Goal.status == "active")
                res = await session.execute(q)
                active = res.scalars().all()

                active_list = [
                    {
                        "id": g.id,
                        "title": g.title,
                        "description": g.description,
                        "goal_type": g.goal_type,
                        "created_at": g.created_at.strftime("%Y-%m-%d")
                    }
                    for g in active
                ]

                prompt = f"""Manage goals based on this message.

Existing active goals:
{json.dumps(active_list)}

Today's message:
{user_message}
Events/Topics/Achievements: {json.dumps(emotions.get("structured_events", {}))}

Decide:
1. Should a NEW goal be created from something mentioned today?
2. Has any existing goal made PROGRESS based on today's message?
3. Has any goal been COMPLETED?

Return ONLY valid JSON:
{{
  "new_goals": [
    {{
      "title": "Prepare for AI placement interviews",
      "description": "User has expressed desire to break into AI roles",
      "goal_type": "career",
      "ai_suggested": true
    }}
  ],
  "progress_updates": [
    {{
      "goal_id": "...",
      "note": "User solved 2 LeetCode problems today"
    }}
  ],
  "completed_goals": ["goal_id_if_completed"]
}}
If nothing to do: {{"new_goals": [], "progress_updates": [], "completed_goals": []}}"""

                res_text = await run_llq_call(prompt, orchestrator=False, json_mode=True)
                res_json = json.loads(res_text)

                new_goals        = res_json.get("new_goals", [])
                progress_updates = res_json.get("progress_updates", [])
                completed_goals  = res_json.get("completed_goals", [])

                added_goals = []
                for ng in new_goals:
                    title  = ng.get("title", "").strip()
                    desc   = ng.get("description", "")
                    g_type = ng.get("goal_type", "personal")
                    if not title:
                        continue
                    goal_id = f"goal_{uuid.uuid4().hex[:12]}"
                    db_goal = Goal(
                        id=goal_id,
                        user_id=user_id,
                        title=title,
                        description=desc,
                        goal_type=g_type,
                        status="active",
                        progress_notes="[]",
                        created_at=datetime.utcnow(),
                        target_date=None,
                        completed_at=None,
                        source_message_id=message_id,
                        ai_suggested=True
                    )
                    session.add(db_goal)
                    added_goals.append(title)

                updated_goals = []
                for pu in progress_updates:
                    gid  = pu.get("goal_id")
                    note = pu.get("note", "").strip()
                    if not gid or not note:
                        continue
                    q_g   = select(Goal).where(Goal.id == gid)
                    res_g = await session.execute(q_g)
                    g_obj = res_g.scalars().first()
                    if g_obj:
                        notes_list = json.loads(g_obj.progress_notes or "[]")
                        notes_list.append({"date": datetime.utcnow().strftime("%Y-%m-%d"), "note": note, "message_id": message_id})
                        g_obj.progress_notes = json.dumps(notes_list)
                        updated_goals.append(g_obj.title)

                completed_titles = []
                for cg in completed_goals:
                    if not cg:
                        continue
                    q_g   = select(Goal).where(Goal.id == cg)
                    res_g = await session.execute(q_g)
                    g_obj = res_g.scalars().first()
                    if g_obj:
                        g_obj.status       = "completed"
                        g_obj.completed_at = datetime.utcnow()
                        completed_titles.append(g_obj.title)

                await session.commit()

                return {
                    "new_goals_created": added_goals,
                    "goals_progressed":  updated_goals,
                    "goals_completed":   completed_titles
                }
        except Exception as e:
            logger.error(f"GoalTrackerTool error: {e}")
            return {"error": str(e)}
