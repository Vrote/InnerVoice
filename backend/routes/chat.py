# backend/routes/chat.py
"""
POST /api/chat          — Send a message, run agent, return response
POST /api/chat/reply    — Answer a follow-up question
GET  /api/chat/pending  — Check if there are pending follow-up questions
"""
import uuid
import json
import logging
import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database.models import Message, FollowupTurn, User
from backend.core.security import get_current_user_id
from backend.agent.reasoning_loop import run_agent
from backend.utils.coping_utils import get_coping_suggestion

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────
class ChatMessageSchema(BaseModel):
    message: str

class ChatReplySchema(BaseModel):
    message_id: str
    reply: str

# ──────────────────────────────────────────────────────────────────────────────
# Helper: build conversation history for the agent
# ──────────────────────────────────────────────────────────────────────────────
async def _get_conversation_history(user_id: str, db: AsyncSession, limit: int = 12) -> list:
    now = datetime.datetime.utcnow()
    start_date = datetime.datetime(now.year, now.month, 1)
    q = select(Message).where(
        Message.user_id == user_id,
        Message.processing_status.in_(["done", "waiting_for_user"]),
        Message.created_at >= start_date
    ).order_by(Message.created_at.desc()).limit(limit)
    res     = await db.execute(q)
    msgs    = res.scalars().all()
    history = []
    for m in reversed(msgs):
        history.append({"role": "user",      "content": m.user_message})
        if m.ai_response:
            history.append({"role": "assistant", "content": m.ai_response})
    return history

# ──────────────────────────────────────────────────────────────────────────────
# POST /api/chat  — Main chat endpoint
# ──────────────────────────────────────────────────────────────────────────────
@router.post("")
async def send_chat_message(
    data: ChatMessageSchema,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        content_stripped = data.message.strip()
        if not content_stripped:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        # Create message record
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        db_msg = Message(
            id=message_id,
            user_id=user_id,
            user_message=content_stripped,
            word_count=len(content_stripped.split()),
            created_at=datetime.datetime.utcnow(),
            processing_status="thinking",
            session_id=message_id
        )
        db.add(db_msg)

        # Update user stats
        q_user  = select(User).where(User.id == user_id)
        res_u   = await db.execute(q_user)
        user    = res_u.scalars().first()
        if user:
            user.total_messages = (user.total_messages or 0) + 1
            # Streak logic
            now = datetime.datetime.utcnow()
            if user.last_active:
                delta = now - user.last_active
                if delta.days == 1:
                    user.streak_count = (user.streak_count or 0) + 1
                    if user.streak_count > (user.longest_streak or 0):
                        user.longest_streak = user.streak_count
                elif delta.days > 1:
                    user.streak_count = 1
            else:
                user.streak_count = 1
            user.last_active = now

        await db.commit()

        # Build agent initial state
        history = await _get_conversation_history(user_id, db)
        initial_state = {
            "user_id":             user_id,
            "message_id":          message_id,
            "user_message":        content_stripped,
            "session_id":          message_id,
            "conversation_history": history,
            "voice_profile":       {},
            "memories_retrieved":  [],
            "emotions_detected":   {},
            "patterns_detected":   [],
            "goals_active":        [],
            "orchestrator_plan":   {},
            "action_plan":         [],
            "tools_used":          [],
            "current_step":        "start",
            "iterations":          0,
            "reasoning_log":       [],
            "crisis_triggered":    False,
            "crisis_level":        "none",
            "waiting_on_user":     False,
            "followup_question":   "",
            "final_response":      "",
            "tool_results":        {},
        }

        final_state = await run_agent(initial_state)

        # Build coping suggestion from detected emotion
        emotions_detected = final_state.get("emotions_detected", {})
        primary_emotion   = emotions_detected.get("primary_emotion", "") if isinstance(emotions_detected, dict) else ""
        coping_suggestion = get_coping_suggestion(primary_emotion)

        return {
            "success": True,
            "data": {
                "message_id":        message_id,
                "response":          final_state.get("final_response", ""),
                "status":            "waiting_for_user" if final_state.get("waiting_on_user") else "done",
                "followup_question": final_state.get("followup_question", "") if final_state.get("waiting_on_user") else None,
                "emotions":          emotions_detected,
                "tools_used":        final_state.get("tools_used", []),
                "reasoning_log":     final_state.get("reasoning_log", []),
                "crisis_level":      final_state.get("crisis_level", "none"),
                "coping_suggestion": coping_suggestion,
            },
            "error": None
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"send_chat_message error: {e}", exc_info=True)
        try:
            await db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))

# ──────────────────────────────────────────────────────────────────────────────
# POST /api/chat/reply  — Answer a follow-up question
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/reply")
async def reply_to_followup(
    data: ChatReplySchema,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        message_id = data.message_id
        reply_text = data.reply.strip()

        if not reply_text:
            raise HTTPException(status_code=400, detail="Reply cannot be empty.")

        # Fetch original message
        q   = select(Message).where(Message.id == message_id, Message.user_id == user_id)
        res = await db.execute(q)
        msg = res.scalars().first()
        if not msg:
            raise HTTPException(status_code=404, detail="Message not found.")

        # Save the followup answer to FollowupTurn
        turn_count = 1
        q_turns = select(FollowupTurn).where(FollowupTurn.message_id == message_id)
        res_t   = await db.execute(q_turns)
        turns   = res_t.scalars().all()
        turn_count = len(turns) + 1

        turn = FollowupTurn(
            id=f"ft_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            message_id=message_id,
            question=msg.followup_question or "",
            answer=reply_text,
            turn_number=turn_count,
            created_at=datetime.datetime.utcnow(),
            answered_at=datetime.datetime.utcnow()
        )
        db.add(turn)

        # Update original message
        msg.followup_answer  = reply_text
        msg.followup_pending = False
        await db.commit()

        # Run agent again with enriched context
        combined_message = f"{msg.user_message}\n\n[Follow-up answer]: {reply_text}"
        history = await _get_conversation_history(user_id, db)

        initial_state = {
            "user_id":              user_id,
            "message_id":           message_id,
            "user_message":         combined_message,
            "session_id":           message_id,
            "conversation_history": history,
            "voice_profile":        {},
            "memories_retrieved":   [],
            "emotions_detected":    {},
            "patterns_detected":    [],
            "goals_active":         [],
            "orchestrator_plan":    {},
            "action_plan":          [],
            "tools_used":           [],
            "current_step":         "start",
            "iterations":           0,
            "reasoning_log":        [],
            "crisis_triggered":     False,
            "crisis_level":         "none",
            "waiting_on_user":      False,
            "followup_question":    "",
            "final_response":       "",
            "tool_results":         {},
        }

        final_state = await run_agent(initial_state)

        # Build coping suggestion from detected emotion
        emotions_detected = final_state.get("emotions_detected", {})
        primary_emotion   = emotions_detected.get("primary_emotion", "") if isinstance(emotions_detected, dict) else ""
        coping_suggestion = get_coping_suggestion(primary_emotion)

        return {
            "success": True,
            "data": {
                "message_id":    message_id,
                "response":      final_state.get("final_response", ""),
                "status":        "done",
                "emotions":      emotions_detected,
                "tools_used":    final_state.get("tools_used", []),
                "crisis_level":  final_state.get("crisis_level", "none"),
                "coping_suggestion": coping_suggestion,
            },
            "error": None
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"reply_to_followup error: {e}", exc_info=True)
        try:
            await db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))

# ──────────────────────────────────────────────────────────────────────────────
# GET /api/chat/pending  — Check for pending follow-up questions
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/pending")
async def get_pending_followups(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        q = select(Message).where(
            Message.user_id == user_id,
            Message.followup_pending == True
        ).order_by(Message.created_at.desc())
        res  = await db.execute(q)
        msgs = res.scalars().all()

        return {
            "success": True,
            "data": [
                {
                    "message_id":       m.id,
                    "user_message":     m.user_message,
                    "followup_question": m.followup_question,
                    "created_at":       m.created_at.isoformat()
                }
                for m in msgs
            ],
            "error": None
        }
    except Exception as e:
        logger.error(f"get_pending_followups error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
