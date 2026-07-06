# backend/agent/tools/voice_profile.py
import json
import logging
from datetime import datetime
from sqlalchemy.future import select
from backend.agent.state import AgentState
from backend.database.connection import AsyncSessionLocal
from backend.database.models import VoiceProfile, Message
from backend.utils.style_analyzer import analyze_style_pure_python
from backend.services.llm_service import run_llq_call

logger = logging.getLogger(__name__)

class VoiceProfileTool:
    async def arun(self, state: AgentState) -> dict:
        try:
            user_id = state["user_id"]
            user_message = state["user_message"]

            async with AsyncSessionLocal() as session:
                q = select(VoiceProfile).where(VoiceProfile.user_id == user_id)
                res = await session.execute(q)
                vp = res.scalars().first()

                q_count = select(Message).where(Message.user_id == user_id)
                res_count = await session.execute(q_count)
                messages = res_count.scalars().all()
                entries_analyzed = len(messages)

                if not vp:
                    vp = VoiceProfile(
                        id=f"vp_{user_id}",
                        user_id=user_id,
                        avg_sentence_length=0.0,
                        avg_entry_length=0.0,
                        formality_score=0.5,
                        hinglish_ratio=0.0,
                        uses_english_only=True,
                        detected_languages="english",
                        uses_ellipsis=False,
                        uses_caps_emphasis=False,
                        uses_emoji=False,
                        exclamation_ratio=0.0,
                        question_ratio=0.0,
                        dominant_tone="neutral",
                        vocabulary_richness=0.5,
                        voice_sample_phrases="[]",
                        signature_words="[]",
                        style_summary="Writes naturally.",
                        response_style_instructions="Reply in a natural, supportive manner. Use clean language.",
                        entries_analyzed=0,
                        last_updated=datetime.utcnow(),
                        raw_style_analysis="{}"
                    )
                    session.add(vp)
                    await session.flush()

                current_analysis = analyze_style_pure_python(user_message)

                if entries_analyzed >= 3:
                    last_10 = sorted(messages, key=lambda x: x.created_at, reverse=True)[:10]
                    last_10_texts = "\n---\n".join([m.user_message for m in reversed(last_10)])

                    llm_prompt = f"""You are a linguistic analyst. Analyze this user's writing style.

Past messages (oldest to newest):
{last_10_texts}

Current message:
{user_message}

Return ONLY valid JSON:
{{
  "avg_sentence_length": 8.5,
  "formality_score": 0.2,
  "hinglish_ratio": 0.35,
  "uses_english_only": false,
  "detected_languages": ["english", "hindi"],
  "uses_ellipsis": true,
  "uses_emoji": false,
  "dominant_tone": "casual",
  "signature_words": ["yaar", "seriously", "bro", "honestly"],
  "style_summary": "Writes in casual Hinglish, short punchy sentences...",
  "response_style_instructions": "Reply in the same casual Hinglish mix. Use short sentences..."
}}"""
                    try:
                        llm_res_text = await run_llq_call(llm_prompt, orchestrator=False, json_mode=True)
                        llm_analysis = json.loads(llm_res_text)

                        for key in ["avg_sentence_length", "formality_score", "hinglish_ratio",
                                    "uses_ellipsis", "uses_caps_emphasis", "uses_emoji",
                                    "exclamation_ratio", "question_ratio", "vocabulary_richness"]:
                            if key in llm_analysis:
                                current_analysis[key] = llm_analysis[key]

                        if "detected_languages" in llm_analysis:
                            current_analysis["detected_languages"] = ", ".join(llm_analysis["detected_languages"])
                            current_analysis["uses_english_only"] = (
                                "hindi" not in llm_analysis["detected_languages"]
                                and "hinglish" not in llm_analysis["detected_languages"]
                            )
                        for k in ["dominant_tone", "signature_words", "style_summary", "response_style_instructions"]:
                            if k in llm_analysis:
                                current_analysis[k] = llm_analysis[k]
                    except Exception as ex:
                        logger.error(f"LLM Voice Profile analysis error: {ex}")

                def merge_float(old_val, new_val):
                    return (0.7 * old_val) + (0.3 * new_val) if old_val > 0 else new_val

                vp.avg_sentence_length = merge_float(vp.avg_sentence_length, current_analysis.get("avg_sentence_length", 0))
                vp.avg_entry_length    = merge_float(vp.avg_entry_length, current_analysis.get("avg_entry_length", 0))
                vp.formality_score     = merge_float(vp.formality_score, current_analysis.get("formality_score", 0.5))
                vp.hinglish_ratio      = merge_float(vp.hinglish_ratio, current_analysis.get("hinglish_ratio", 0))
                vp.exclamation_ratio   = merge_float(vp.exclamation_ratio, current_analysis.get("exclamation_ratio", 0))
                vp.question_ratio      = merge_float(vp.question_ratio, current_analysis.get("question_ratio", 0))
                vp.vocabulary_richness = merge_float(vp.vocabulary_richness, current_analysis.get("vocabulary_richness", 0.5))

                vp.uses_english_only  = current_analysis.get("uses_english_only", vp.uses_english_only)
                vp.detected_languages = current_analysis.get("detected_languages", vp.detected_languages)
                vp.uses_ellipsis      = current_analysis.get("uses_ellipsis", vp.uses_ellipsis)
                vp.uses_caps_emphasis = current_analysis.get("uses_caps_emphasis", vp.uses_caps_emphasis)
                vp.uses_emoji         = current_analysis.get("uses_emoji", vp.uses_emoji)
                vp.dominant_tone      = current_analysis.get("dominant_tone", vp.dominant_tone)

                if "signature_words" in current_analysis:
                    existing_sig = json.loads(vp.signature_words) if vp.signature_words else []
                    new_sig = list(set(existing_sig + current_analysis["signature_words"]))[:15]
                    vp.signature_words = json.dumps(new_sig)

                if current_analysis.get("style_summary"):
                    vp.style_summary = current_analysis["style_summary"]
                if current_analysis.get("response_style_instructions"):
                    vp.response_style_instructions = current_analysis["response_style_instructions"]

                vp.entries_analyzed = entries_analyzed + 1
                vp.last_updated     = datetime.utcnow()
                vp.raw_style_analysis = json.dumps(current_analysis)

                session.add(vp)
                await session.commit()

                return {
                    "avg_sentence_length": vp.avg_sentence_length,
                    "avg_entry_length": vp.avg_entry_length,
                    "formality_score": vp.formality_score,
                    "hinglish_ratio": vp.hinglish_ratio,
                    "uses_english_only": vp.uses_english_only,
                    "detected_languages": vp.detected_languages,
                    "uses_ellipsis": vp.uses_ellipsis,
                    "uses_caps_emphasis": vp.uses_caps_emphasis,
                    "uses_emoji": vp.uses_emoji,
                    "exclamation_ratio": vp.exclamation_ratio,
                    "question_ratio": vp.question_ratio,
                    "dominant_tone": vp.dominant_tone,
                    "vocabulary_richness": vp.vocabulary_richness,
                    "signature_words": json.loads(vp.signature_words) if vp.signature_words else [],
                    "style_summary": vp.style_summary,
                    "response_style_instructions": vp.response_style_instructions,
                    "entries_analyzed": vp.entries_analyzed
                }
        except Exception as e:
            logger.error(f"VoiceProfileTool error: {e}")
            return {"error": str(e), "response_style_instructions": "Be warm, supportive, and personal."}
