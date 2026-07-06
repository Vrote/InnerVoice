import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.llm_service import run_llq_call

async def main():
    try:
        print("Testing ChatGroq orchestrator model...")
        res = await run_llq_call("Hello! Please reply in JSON mode with a greetings message.", orchestrator=True, json_mode=True)
        print("Orchestrator JSON response:", repr(res))
    except Exception as e:
        print("Orchestrator failed:", e)

    try:
        print("\nTesting ChatGroq tool model...")
        res = await run_llq_call("Hello! Please reply in text mode.", orchestrator=False, json_mode=False)
        print("Tool text response:", repr(res))
    except Exception as e:
        print("Tool failed:", e)

if __name__ == "__main__":
    asyncio.run(main())
