# backend/routes/goals.py
import uuid
import json
import logging
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.database.models import Goal
from backend.core.security import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/goals", tags=["goals"])

class GoalCreateSchema(BaseModel):
    title: str
    description: Optional[str] = ""
    goal_type: Optional[str] = "personal"
    target_date: Optional[str] = None

class GoalUpdateSchema(BaseModel):
    status: Optional[str] = None  # active|completed|paused|abandoned
    progress_note: Optional[str] = None

@router.get("")
async def get_goals(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        q = select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc())
        res = await db.execute(q)
        goals = res.scalars().all()
        
        return [
            {
                "id": g.id,
                "title": g.title,
                "description": g.description,
                "goal_type": g.goal_type,
                "status": g.status,
                "progress_notes": json.loads(g.progress_notes or "[]"),
                "created_at": g.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "target_date": g.target_date,
                "completed_at": g.completed_at.strftime("%Y-%m-%d %H:%M:%S") if g.completed_at else None,
                "ai_suggested": g.ai_suggested
            }
            for g in goals
        ]
    except Exception as e:
        logger.error(f"Error fetching goals: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch goals")

@router.post("", status_code=210)
async def create_goal(data: GoalCreateSchema, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        title_stripped = data.title.strip()
        if not title_stripped:
            raise HTTPException(status_code=400, detail="Goal title cannot be empty")
            
        goal_id = f"goal_{uuid.uuid4().hex[:12]}"
        db_goal = Goal(
            id=goal_id,
            user_id=user_id,
            title=title_stripped,
            description=data.description,
            goal_type=data.goal_type,
            status="active",
            progress_notes="[]",
            created_at=datetime.datetime.utcnow(),
            target_date=data.target_date,
            completed_at=None,
            source_entry_id=None,
            ai_suggested=False
        )
        db.add(db_goal)
        await db.commit()
        
        return {
            "id": db_goal.id,
            "title": db_goal.title,
            "description": db_goal.description,
            "goal_type": db_goal.goal_type,
            "status": db_goal.status,
            "created_at": db_goal.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "ai_suggested": db_goal.ai_suggested
        }
    except Exception as e:
        logger.error(f"Error creating goal: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create goal")

@router.put("/{goal_id}")
async def update_goal(goal_id: str, data: GoalUpdateSchema, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        q = select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        res = await db.execute(q)
        g = res.scalars().first()
        if not g:
            raise HTTPException(status_code=404, detail="Goal not found")
            
        if data.status:
            g.status = data.status
            if data.status == "completed":
                g.completed_at = datetime.datetime.utcnow()
            else:
                g.completed_at = None
                
        if data.progress_note:
            notes_list = json.loads(g.progress_notes or "[]")
            notes_list.append({
                "date": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                "note": data.progress_note.strip()
            })
            g.progress_notes = json.dumps(notes_list)
            
        await db.commit()
        return {
            "id": g.id,
            "title": g.title,
            "status": g.status,
            "progress_notes": json.loads(g.progress_notes or "[]"),
            "completed_at": g.completed_at.strftime("%Y-%m-%d %H:%M:%S") if g.completed_at else None
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating goal: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update goal")

@router.delete("/{goal_id}")
async def delete_goal(goal_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        q = select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        res = await db.execute(q)
        g = res.scalars().first()
        if not g:
            raise HTTPException(status_code=404, detail="Goal not found")
            
        await db.delete(g)
        await db.commit()
        return {"success": True, "message": "Goal deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting goal: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete goal")
