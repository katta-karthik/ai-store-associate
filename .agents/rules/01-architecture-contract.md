# Rule 01: Architecture & API Contract Standard

## 1. System Decoupling Principle
* The **E-commerce Platform** (Store Frontend & Backend) and the **AI Store Associate** (Agent Brain) MUST be built as two strictly decoupled systems.
* They communicate exclusively via well-defined REST APIs and Server-Sent Events (SSE) / WebSockets.
* The AI Associate must NEVER access the store's database directly. All commerce operations (search, filter, cart, wishlist) must occur through typed Store API endpoints.

## 2. API Contract First
* Every new feature must define its request, response, and error schemas using **Pydantic (Backend)** and **Zod/TypeScript (Frontend)** before implementation.
* All endpoints must return standard JSON envelope formats:
  ```json
  {
    "success": true,
    "data": { ... },
    "error": null,
    "metadata": { "timestamp": "...", "version": "v1" }
  }
  ```

## 3. Asynchronous Non-Blocking Execution
* All backend I/O operations (database queries, network calls, embedding generation, LLM invocations) must be 100% asynchronous (`async`/`await`).
* Synchronous blocking calls (`time.sleep()`, synchronous `requests`, heavy CPU loops) are strictly forbidden on main event loops.

## 4. State Management (LangGraph)
* The agent conversation and shopping state must use deterministic state transitions in LangGraph.
* State checkpointing must be backed by persistent storage (PostgreSQL/Redis) to allow seamless session recovery across restarts.
