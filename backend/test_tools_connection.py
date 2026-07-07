# backend/test_tools_connection.py
"""
Sanity Test Runner for InnerVoice Agentic Tools
===============================================
Imports the active TOOL_REGISTRY and runs a mock AgentState through
each tool to verify DB, Vector Store, and LLM integrations.
"""
import asyncio
import sys
import logging
from datetime import datetime

# Setup basic logging to avoid spam
logging.basicConfig(level=logging.ERROR)

from backend.database.connection import init_db, AsyncSessionLocal
from backend.database.models import User
from backend.agent.reasoning_loop import TOOL_REGISTRY
from sqlalchemy.future import select

# Mock state
mock_user_id = "test_user_999"
mock_message_id = "msg_test_999"

async def setup_test_user(db):
    # Check if test user exists
    q = select(User).where(User.id == mock_user_id)
    res = await db.execute(q)
    user = res.scalars().first()
    if not user:
        user = User(
            id=mock_user_id,
            email="test_user@example.com",
            username="test_user",
            password_hash="test",
            streak_count=1,
            longest_streak=1,
            total_messages=1,
            created_at=datetime.utcnow()
        )
        db.add(user)
        await db.commit()
    return user

async def run_diagnostics():
    print("="*60)
    print("STARTING INNERVOICE AGENTIC TOOLS SANITY CHECK")
    print("="*60)

    try:
        await init_db()
        print("[OK] SQLite database tables initialized.")
    except Exception as e:
        print(f"[FAIL] SQLite database initialization failed: {e}")
        return

    async with AsyncSessionLocal() as db:
        try:
            await setup_test_user(db)
            print(f"[OK] Test user '{mock_user_id}' established in SQLite.")
        except Exception as e:
            print(f"[FAIL] Failed to setup test user in DB: {e}")
            return

    # Formulate mock AgentState
    state = {
        "user_id":             mock_user_id,
        "message_id":          mock_message_id,
        "user_message":        "I want to finish coding my project today. I feel hopeful but also a little anxious.",
        "session_id":          "session_test_999",
        "conversation_history": [
            {"role": "user", "content": "Hi, I am starting a new coding project."},
            {"role": "assistant", "content": "That sounds exciting! What are you building?"}
        ],
        "voice_profile":       {"dominant_tone": "hopeful", "formality": 0.3},
        "memories_retrieved":  [],
        "emotions_detected":   {},
        "patterns_detected":   [],
        "goals_active":        [],
        "orchestrator_plan":   {},
        "action_plan":         [],
        "tools_used":          [],
        "current_step":        "test",
        "iterations":          0,
        "reasoning_log":       [],
        "crisis_triggered":    False,
        "crisis_level":        "none",
        "waiting_on_user":     False,
        "followup_question":   "",
        "final_response":      "",
        "tool_results":        {},
    }

    # Loop and test each tool
    success_count = 0
    total_tools = len(TOOL_REGISTRY)

    for name, tool in TOOL_REGISTRY.items():
        print(f"\nTesting Tool: '{name}' ...", end="", flush=True)
        try:
            # We wrap the execution in a timeout to prevent hanging tests
            result = await asyncio.wait_for(tool.arun(state), timeout=15.0)
            
            # Basic validation of tool output
            if isinstance(result, dict) and "error" in result:
                print(f" [FAIL] (Returned error: {result['error']})")
            else:
                print(" [OK]")
                success_count += 1
        except asyncio.TimeoutError:
            print(" [TIMEOUT] (Took longer than 15s)")
        except Exception as e:
            print(f" [CRASH] ({type(e).__name__}: {e})")

    print("\n" + "="*60)
    print(f"SUMMARY: {success_count}/{total_tools} Tools working successfully.")
    print("="*60)

    if success_count == total_tools:
        print("SUCCESS: All systems go! All agentic tools are integrated and working correctly.")
        sys.exit(0)
    else:
        print("WARNING: Some tools encountered errors. Please check configurations/keys.")
        sys.exit(1)

if __name__ == "__main__":
    # Fix event loop policy for Windows if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_diagnostics())
