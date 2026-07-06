# backend/test_agent.py
import asyncio
import uuid
import sys
import os
import json
import logging

# Add workspace directory to PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import init_db, AsyncSessionLocal
from backend.database.models import User, VoiceProfile, JournalEntry
from backend.agent.tools.crisis_check import CrisisCheckTool
from backend.utils.style_analyzer import analyze_style_pure_python
from backend.agent.reasoning_loop import build_reasoning_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_agent")

async def test_crisis_check():
    logger.info("--- Testing Crisis Check Tool ---")
    tool = CrisisCheckTool()
    
    # Test safe text
    safe_state = {"journal_text": "I had a great day today, finished my homework!"}
    res_safe = await tool.arun(safe_state)
    logger.info(f"Safe text result: {res_safe}")
    assert res_safe["crisis_detected"] == False, "Safe text false positive!"
    
    # Test unsafe text
    unsafe_state = {"journal_text": "I want to kill myself, I cannot go on anymore..."}
    res_unsafe = await tool.arun(unsafe_state)
    logger.info(f"Unsafe text result: {res_unsafe}")
    assert res_unsafe["crisis_detected"] == True, "Unsafe text was not flagged!"
    
    logger.info("Crisis Check Tool passed!")

async def test_style_analyzer():
    logger.info("--- Testing Style Analyzer Utility ---")
    text = "yaar aaj bohot stress ho gaya... seriously! I feel quite lost. literally WTF."
    analysis = analyze_style_pure_python(text)
    logger.info(f"Analysis: {json.dumps(analysis, indent=2)}")
    
    assert analysis["uses_english_only"] == False, "Hinglish was not detected!"
    assert analysis["uses_ellipsis"] == True, "Ellipsis was not detected!"
    assert analysis["uses_caps_emphasis"] == True, "CAPS emphasis was not detected!"
    assert analysis["exclamation_ratio"] > 0, "Exclamation was not counted!"
    
    logger.info("Style Analyzer Utility passed!")

async def test_database_and_user_creation():
    logger.info("--- Testing DB & User Creation ---")
    await init_db()
    
    user_id = f"test_{uuid.uuid4().hex[:6]}"
    async with AsyncSessionLocal() as session:
        # Create user
        user = User(
            id=user_id,
            email=f"{user_id}@example.com",
            username="TestUser",
            password_hash="mock_hash",
            streak_count=1,
            longest_streak=1,
            total_entries=0
        )
        session.add(user)
        
        # Create voice profile
        vp = VoiceProfile(
            id=f"vp_{user_id}",
            user_id=user_id,
            avg_sentence_length=5.0,
            avg_entry_length=15.0,
            dominant_tone="casual",
            signature_words='["yaar"]'
        )
        session.add(vp)
        await session.commit()
        logger.info(f"Created test user with ID: {user_id}")
        
    logger.info("DB and User Creation passed!")

async def test_langgraph_loop_compilation():
    logger.info("--- Testing LangGraph Loop Compilation ---")
    try:
        graph = build_reasoning_graph()
        logger.info("LangGraph compiled and loaded checkpoint databases successfully.")
    except Exception as e:
        logger.error(f"LangGraph compile failed: {e}")
        raise e
        
    logger.info("LangGraph Loop compilation passed!")

async def main():
    try:
        await test_crisis_check()
        await test_style_analyzer()
        await test_database_and_user_creation()
        await test_langgraph_loop_compilation()
        logger.info("==========================================")
        logger.info("ALL AGENT VERIFICATION TESTS PASSED!")
        logger.info("==========================================")
    except Exception as e:
        logger.error(f"TEST RUN ENCOUNTERED A FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
