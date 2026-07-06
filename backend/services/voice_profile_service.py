# backend/services/voice_profile_service.py
import logging
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import VoiceProfile

logger = logging.getLogger(__name__)

async def get_user_voice_profile(user_id: str, db: AsyncSession):
    try:
        q = select(VoiceProfile).where(VoiceProfile.user_id == user_id)
        res = await db.execute(q)
        return res.scalars().first()
    except Exception as e:
        logger.error(f"Error fetching voice profile: {e}")
        return None

async def reset_voice_profile(user_id: str, db: AsyncSession):
    try:
        q = select(VoiceProfile).where(VoiceProfile.user_id == user_id)
        res = await db.execute(q)
        vp = res.scalars().first()
        if vp:
            await db.delete(vp)
            await db.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Error resetting voice profile: {e}")
        await db.rollback()
        return False
