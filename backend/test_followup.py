import asyncio
import sys
import os
import uuid

# Add workspace directory to PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import init_db, AsyncSessionLocal
from backend.database.models import User, VoiceProfile
from backend.agent.reasoning_loop import get_reasoning_graph

async def main():
    await init_db()
    
    user_id = f"test_user_{uuid.uuid4().hex[:6]}"
    entry_id = f"ent_{uuid.uuid4().hex[:12]}"
    print(f"User: {user_id}, Entry: {entry_id}")
    
    async with AsyncSessionLocal() as db:
        user = User(
            id=user_id,
            email=f"{user_id}@example.com",
            username="TestReflector",
            password_hash="pw123",
            streak_count=0,
            longest_streak=0,
            total_entries=0
        )
        db.add(user)
        await db.commit()

    graph = await get_reasoning_graph()
    config = {"configurable": {"thread_id": entry_id}}
    
    # 1. Initial invocation (let's mock the state so it requests a followup)
    # We will mock the prompt response or simply force the state to require followup
    initial_state = {
        "user_id": user_id,
        "entry_id": entry_id,
        "journal_text": "I had a weird dream about my old school.",
        "conversation_history": [],
        "errors": [],
        "iterations": 0,
        "followup_turn": 0,
        "tool_results": {},
        "reasoning_log": [],
        "crisis_detected": False,
        "response_complete": False,
        "needs_followup": True,  # FORCE IT
        "followup_question": "What was the school like?"
    }
    
    print("\n--- STEP 1: Initial call ---")
    # We can run the graph. Since it hits routing, it should route to wait_for_user and interrupt.
    # To bypass LLM and just test the state/interrupt logic, let's execute reasoning manually or let it run.
    # Let's let it run naturally. The LLM might ask a followup or not.
    result = await graph.ainvoke(initial_state, config=config)
    print("Graph execution paused. needs_followup:", result.get("needs_followup"))
    print("Followup Question:", repr(result.get("followup_question")))
    print("Next step expected (should be wait_for_user interrupt):", (await graph.aget_state(config)).next)

    # 2. Update state with followup answer
    print("\n--- STEP 2: Updating state with answer ---")
    await graph.aupdate_state(config, {"followup_answer": "It was dark and empty.", "needs_followup": False}, as_node="wait_for_user")
    
    # 3. Resume graph
    print("\n--- STEP 3: Resuming graph ---")
    try:
        final_result = await graph.ainvoke(None, config=config)
        print("Success!")
        print("Final Response:", repr(final_result.get("final_response")))
    except Exception as e:
        print("FAIL with exception:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
