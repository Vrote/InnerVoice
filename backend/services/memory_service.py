# backend/services/memory_service.py
import uuid
import logging
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import Memory
from backend.services.vector_store import add_memory_to_vector_store, delete_memory_from_vector_store

logger = logging.getLogger(__name__)

async def get_all_memories(user_id: str, db: AsyncSession):
    try:
        q = select(Memory).where(Memory.user_id == user_id).order_by(Memory.created_at.desc())
        res = await db.execute(q)
        return res.scalars().all()
    except Exception as e:
        logger.error(f"Error fetching memories: {e}")
        return []

async def create_new_memory(user_id: str, text: str, memory_type: str, importance: float, source_id: str, db: AsyncSession):
    try:
        memory_id = f"mem_{uuid.uuid4().hex[:12]}"
        memory = Memory(
            id=memory_id,
            user_id=user_id,
            memory_text=text,
            memory_type=memory_type,
            importance_score=importance,
            source_entry_id=source_id,
            is_active=True,
            created_at=datetime.utcnow(),
            reference_count=0
        )
        db.add(memory)
        await db.commit()
        
        # Add to ChromaDB as well
        await add_memory_to_vector_store(
            user_id=user_id,
            memory_id=memory_id,
            memory_text=text,
            memory_type=memory_type,
            importance=importance
        )
        return memory
    except Exception as e:
        logger.error(f"Error creating memory: {e}")
        await db.rollback()
        raise e

async def delete_memory_by_id(user_id: str, memory_id: str, db: AsyncSession):
    try:
        q = select(Memory).where(Memory.user_id == user_id, Memory.id == memory_id)
        res = await db.execute(q)
        memory = res.scalars().first()
        if memory:
            await db.delete(memory)
            await db.commit()
            
            # Delete from ChromaDB
            await delete_memory_from_vector_store(user_id, memory_id)
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        await db.rollback()
        raise e

async def toggle_memory_active_status(user_id: str, memory_id: str, is_active: bool, db: AsyncSession):
    try:
        q = select(Memory).where(Memory.user_id == user_id, Memory.id == memory_id)
        res = await db.execute(q)
        memory = res.scalars().first()
        if memory:
            memory.is_active = is_active
            await db.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Error toggling memory active status: {e}")
        await db.rollback()
        raise e
