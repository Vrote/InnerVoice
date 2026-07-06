# backend/routes/voice_profile.py
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.core.security import get_current_user_id
from backend.services.voice_profile_service import get_user_voice_profile, reset_voice_profile

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice-profile", tags=["voice_profile"])

@router.get("")
async def get_profile(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        vp = await get_user_voice_profile(user_id, db)
        if not vp:
            return {
                "has_profile": False,
                "message": "Start writing entries! We need at least 1 entry to establish a baseline voice profile."
            }
            
        return {
            "id": vp.id,
            "avg_sentence_length": round(vp.avg_sentence_length or 0, 1),
            "avg_entry_length": round(vp.avg_entry_length or 0, 1),
            "formality_score": round(vp.formality_score or 0.5, 2),
            "hinglish_ratio": round(vp.hinglish_ratio or 0.0, 2),
            "uses_english_only": vp.uses_english_only,
            "detected_languages": vp.detected_languages,
            "uses_ellipsis": vp.uses_ellipsis,
            "uses_caps_emphasis": vp.uses_caps_emphasis,
            "uses_emoji": vp.uses_emoji,
            "exclamation_ratio": round(vp.exclamation_ratio or 0, 2),
            "question_ratio": round(vp.question_ratio or 0, 2),
            "dominant_tone": vp.dominant_tone,
            "vocabulary_richness": round(vp.vocabulary_richness or 0.5, 2),
            "signature_words": json.loads(vp.signature_words or "[]"),
            "style_summary": vp.style_summary,
            "response_style_instructions": vp.response_style_instructions,
            "entries_analyzed": vp.entries_analyzed,
            "has_profile": True
        }
    except Exception as e:
        logger.error(f"Error fetching voice profile in route: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch voice profile")

@router.post("/reset")
async def reset_profile(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        success = await reset_voice_profile(user_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="No voice profile found to reset")
        return {"success": True, "message": "Voice profile reset successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error resetting voice profile in route: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset voice profile")
