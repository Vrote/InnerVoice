# backend/routes/memories.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.core.security import get_current_user_id
from backend.services.memory_service import get_all_memories, delete_memory_by_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/memories", tags=["memories"])

@router.get("")
async def get_memories(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        memories = await get_all_memories(user_id, db)
        return [
            {
                "id": m.id,
                "memory_text": m.memory_text,
                "memory_type": m.memory_type,
                "importance_score": m.importance_score,
                "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "reference_count": m.reference_count or 0,
                "is_active": m.is_active
            }
            for m in memories
        ]
    except Exception as e:
        logger.error(f"Error fetching memories in route: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch memories")

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        deleted = await delete_memory_by_id(user_id, memory_id, db)
        if not deleted:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"success": True, "message": "Memory deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting memory in route: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete memory")
