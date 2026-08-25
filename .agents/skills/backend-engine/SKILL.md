---
name: backend-engine
description: Implements high-performance async FastAPI backend services, PostgreSQL/pgvector database interactions, tool handlers, and LangGraph agent execution.
---

# Backend & Engine Engineering Skill

## Purpose
Use this skill when implementing FastAPI endpoints, database models, SQLAlchemy async sessions, pgvector search queries, and LangGraph agent logic.

## Technical Standards
1. **Framework**: FastAPI with Python 3.11+.
2. **Database Access**: SQLAlchemy async engine (`asyncpg`) with connection pooling.
3. **Validation**: 100% Pydantic v2 data models with field constraints.
4. **Agent Brain**:
   * LangGraph state graph with asynchronous node execution.
   * Deterministic tool definitions with clear type annotations and docstrings for LLM parameter extraction.
   * Semantic memory retrieval using pgvector cosine distance (`<=>`).
5. **Streaming**: Server-Sent Events (SSE) using `EventSourceResponse` with typed event frames:
   ```json
   data: {"event": "token", "content": "..."}
   data: {"event": "ui_action", "action": "SET_FILTERS", "payload": {...}}
   ```

## Development Workflow
1. Read the API contract from the Architecture Department.
2. Implement data models & migrations.
3. Write repository/service layer with async DB queries.
4. Implement API route with dependency injection (`Depends(get_db)`).
5. Hand off to QA Department for test suite verification.
