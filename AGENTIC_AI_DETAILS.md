# Dynamic Agentic AI Orchestration & Tool Execution Guide

This document explains in depth how the **Agentic AI Architecture** is implemented in **InnerVoice**. It details the LangGraph state transitions, how the agent is invoked, and how tools are dynamically chosen and executed.

---

## 🧩 1. The Core Paradigm: Why is it "Agentic"?

A standard LLM application uses **Chains**—static sequences where Prompt A goes to LLM A, which feeds into Prompt B. 
**InnerVoice** uses an **Agentic Loop**. The AI has:
1. **State Persistence**: Memory and flags are carried through a global graph state (`AgentState`).
2. **Dynamic Decision Making**: The AI decides *autonomously* which tools are relevant based on your entry.
3. **Execution & Self-Reflection Loop**: It runs a tool, evaluates the output, and can decide to run further tools or pause for user feedback.

---

## 🛠️ 2. The Global Agent State (`AgentState`)

The entire graph workflow revolves around a shared, stateful dictionary called `AgentState`. Every node reads from and writes to this state.

Defined in [`backend/agent/state.py`](file:///c:/Users/hp/Desktop/InnerVoice/backend/agent/state.py):
```python
from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    user_id: str                   # Active user identifier
    message_id: str                # Unique ID for the current chat message
    user_message: str              # The raw message typed by the user
    session_id: str                # Session thread ID for LangGraph checkpointing
    conversation_history: List[Dict[str, str]] # Last N turns of context
    voice_profile: Dict[str, Any]  # Analyzed user language characteristics
    memories_retrieved: List[Dict[str, Any]] # Semantic memories fetched from ChromaDB
    emotions_detected: Dict[str, Any]  # Primary/secondary emotion & mood score
    patterns_detected: List[str]   # Recurring themes logged from past entries
    goals_active: List[str]        # User's currently active goals
    orchestrator_plan: Dict[str, Any]  # The JSON plan output by the orchestrator
    action_plan: List[str]         # List of tools scheduled to run
    tools_used: List[str]          # List of tools already executed
    current_step: str              # Active graph node label
    iterations: int                # Counter preventing infinite execution loops
    reasoning_log: List[Dict[str, Any]] # Step-by-step reasoning details for debugging
    crisis_triggered: bool         # Safe-guard trigger flag
    crisis_level: str              # Level of distress ("none", "moderate", "severe")
    waiting_on_user: bool          # Human-in-the-loop pause flag
    followup_question: str         # AI's question text if needing clarification
    final_response: str            # Final response returned to frontend
    tool_results: Dict[str, Any]   # Raw dictionary of all tool returns
```

---

## 🔄 3. Detailed Walkthrough of the Execution Nodes

The agent executes through a compilation of **Nodes** (Python functions) and **Conditional Edges** (router functions) defined in [`backend/agent/reasoning_loop.py`](file:///c:/Users/hp/Desktop/InnerVoice/backend/agent/reasoning_loop.py).

### Node 1: Crisis Node (`crisis_node`)
* **Purpose**: Safety gatekeeping.
* **Code execution**: Runs the `CrisisCheckTool`. This does a quick LLM analysis on the user message.
* **Outcome**: Sets `crisis_triggered` (True/False) and `crisis_level` ("none", "moderate", "severe").
* **Routing**: The conditional edge `route_after_crisis` inspects this:
  * If `crisis_level == "severe"`, it skips all tool executions and routes directly to the `respond_node` to output helpline resources.
  * Otherwise, it routes to the `plan_node`.

### Node 2: Plan Node (`plan_node`)
* **Purpose**: Orchestration and tool scheduling.
* **Mechanism**: Generates a prompt containing current message, tone profile, history, and a list of 12 available tools. It queries the LLM with `json_mode=True` to output a structured planning schema:
  ```json
  {
    "reasoning": "User mentions struggles with workload. I need to query memories about their job, analyze their stress levels, and check if this relates to active goals.",
    "tools_to_run": ["memory_retrieve", "emotion_analyze", "goal_tracker", "memory_save"],
    "needs_followup": false
  }
  ```
* **State Updates**: Sets `action_plan = ["memory_retrieve", "emotion_analyze", "goal_tracker", "memory_save"]`.

### Node 3: Execute Tool Node (`execute_tool_node`)
* **Purpose**: Sequential execution of scheduled tools.
* **Loop Mechanics**:
  1. Inspects `action_plan` and compares it to `tools_used`.
  2. Identifies the first tool that hasn't run yet (e.g. `memory_retrieve`).
  3. Fetches the tool instance from the `TOOL_REGISTRY` and executes it asynchronously (`await tool.arun(state)`).
  4. Merges the tool's return dictionary into `tool_results` and saves critical fields directly to state (e.g., matching memories to `memories_retrieved`).
  5. Appends the tool name to `tools_used` and increments `iterations`.

### Node 4: Reflect Node (`reflect_node`)
* **Purpose**: Determines if the loop should continue or finish.
* **Checkpoints**:
  * If `followup_question` was scheduled and generated, it sets `waiting_on_user = True`.
* **Routing**: The conditional edge `route_after_reflect` evaluates:
  * Are there remaining tools in `action_plan` AND is `iterations < 5`?
    * **Yes**: Routes back to `execute_tool_node` to run the next tool.
    * **No**: Routes to `respond_node` to end the loop.

### Node 5: Respond Node (`respond_node`)
* **Purpose**: Formulating and saving the response.
* **Generation**: Combines conversation history, detected emotions, retrieved memories, active patterns, and style rules into a single prompt for the LLM. 
* **Writing Style**: Employs style mirroring rules (formality, punctuation, etc.) to speak like a warm friend.
* **Persistence**: Saves the AI response to the SQLite `messages` table and sends the entry to the ChromaDB vector database.

---

## 🛠️ 4. Tool Design: How a Tool Performs Actions

All tools inherit from a base `BaseTool` class. They are asynchronous and isolated.

### Example: Memory Retrieval (`MemoryRetrieveTool`)
* **Action**:
  1. Calls `query_vector_store` using the user's current message as the search text.
  2. Performs a cosine-similarity search on the **ChromaDB** database.
  3. Returns a structured list of semantic memories:
     ```python
     {
       "semantic_memories": [{"text": "User is studying computer science", "distance": 0.32}],
       "similar_entries": [...]
     }
     ```

### Example: Goal Tracker (`GoalTrackerTool`)
* **Action**:
  1. Queries the LLM to inspect the user's message against active goals.
  2. Determines if the user created a new goal (e.g., *"I want to start running"*), checked off a goal, or adjusted a deadline.
  3. Returns a JSON log updating the SQL database.

---

## 👥 5. Human-in-the-Loop (HITL) Integration

When the orchestrator identifies that a message lacks critical context (e.g. *"I'm so angry at her"* without defining who "her" is):
1. It plans the `followup_question` tool.
2. The tool generates a question: *"Who are you feeling angry at today?"*
3. The `reflect_node` catches this, sets `waiting_on_user = True`, and routes straight to `respond_node`.
4. In `respond_node`, the AI outputs a warm acknowledgment followed by the follow-up question. The database record is set to `processing_status = "waiting_for_user"`.
5. The frontend chat window intercepts this status and opens an inline chat reply box. The user's reply is posted to `/api/chat/reply`, combining the history together before resuming the full agent reasoning loop.

---

## 💾 6. Retrieval-Augmented Generation (RAG) Flow

InnerVoice utilizes a structured RAG pipeline to ensure that long-term contextual memory is retrieved and injected dynamically into conversation steps.

```
┌─────────────────┐      Vector Search      ┌──────────────────┐
│  User Message   ├────────────────────────►│  ChromaDB Store  │
└────────┬────────┘                         └────────┬─────────┘
         │                                           │
         │                                           │ Matches Fetched
         ▼                                           ▼
┌─────────────────┐      Augment Prompt     ┌──────────────────┐
│  LLM Generator  │◄────────────────────────┤ Relevant Context │
└────────┬────────┘                         └──────────────────┘
         │
         ▼
┌─────────────────┐
│ AI Reflections  │
└─────────────────┘
```

### RAG System Components:

1. **Embedding Generation (`embedding_service.py`)**:
   * Text is converted into vector representations using the `embed_text` function in [embedding_service.py](file:///c:/Users/hp/Desktop/InnerVoice/backend/services/embedding_service.py).
   * It makes calls to Groq's embedding engine (or falls back to a zero-vector baseline if offline) to produce 768-dimensional floating-point arrays.

2. **Vector Indexing & Storage (`vector_store.py`)**:
   * Leverages **ChromaDB** in [vector_store.py](file:///c:/Users/hp/Desktop/InnerVoice/backend/services/vector_store.py) to index and query user memories.
   * Every time `MemorySaveTool` extracts a permanent fact (e.g. relationship details, fears, career aspirations), it indexes it in the Chroma collection scoped to the user ID.

3. **Semantic Memory Retrieval Tool (`MemoryRetrieveTool`)**:
   * Invoked dynamically by the LangGraph orchestrator.
   * It takes the user's message, computes its vector embedding, and queries ChromaDB for the top 5 nearest-neighbor memories.

4. **Prompt Augmentation & Generation (`respond_node`)**:
   * The retrieved memory snippets are formatted and injected as a text block (`Relevant memories`) inside the final prompt.
   * This forces the LLM generator to construct a response that naturally references past events, effectively preventing conversational amnesia.

