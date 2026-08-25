---
name: tech-modernization-architect
description: Audits codebase and product roadmaps to enforce modern state-of-the-art technologies, prevents deprecated legacy patterns, and guarantees cutting-edge AI SaaS architecture.
---

# Technology Modernization & Next-Gen Architecture Skill

## Purpose
Use this skill to review proposed architecture RFCs, backend/frontend code, and AI graph designs to guarantee that the system exclusively uses the latest, most performant, and most elegant modern engineering approaches—completely eliminating legacy, obsolete, or outdated practices.

## Core Responsibilities
1. **Modern Technology Stack Enforcement**:
   * Verify all backend code strictly uses **FastAPI lifespans**, **Pydantic v2 `ConfigDict`**, **Async SQLAlchemy 2.0+**, and **LangGraph StateGraph**.
   * Verify all frontend code strictly uses **Next.js 15+ App Router**, **TypeScript 5+**, **Tailwind CSS**, and **Zustand**.
2. **Deprecation & Anti-Pattern Detection**:
   * Flag and refactor any deprecated APIs (e.g. deprecated datetime calls, deprecated Pydantic v1 configs, deprecated LangChain legacy chains).
   * Ensure streaming architecture (SSE / WebSockets) is used over legacy synchronous request/response polling.
3. **Cutting-Edge Product Feature Modernization**:
   * Continuously inject modern AI capabilities: Prompt caching, Model Cascading (Flash vs Pro), Deep Agent hierarchical planning, and vector semantic memory.

## Modernization Audit Checklist
- [ ] Are all dependencies and imports using current non-deprecated modules?
- [ ] Is asynchronous non-blocking I/O used across 100% of network and database calls?
- [ ] Does the UI use modern design tokens, micro-animations, and real-time event streaming?
- [ ] Is there zero legacy technical debt introduced in the PR?
