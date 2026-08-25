# Rule 09: Modern Technology & Anti-Legacy Engineering Standards

## 1. Zero-Legacy Policy
* Outdated programming paradigms, deprecated library syntax, and obsolete architecture patterns are strictly prohibited in this codebase.
* If a modern, more performant, or more resilient pattern exists in the contemporary ecosystem, it MUST be used over legacy practices.

## 2. Up-To-Date Technology Stack Mandates

### 2.1 AI & Agentic Orchestration
* **NO** legacy sequential chains or monolithic LLM calls.
* **MANDATORY**: Use **LangGraph (v0.2+) StateGraph** with explicit state schemas, conditional edges, checkpointing, and Deep Agents.
* **MANDATORY**: Use real-time Server-Sent Events (SSE) streaming with typed event envelopes (`ui_action`, `token`, `done`) rather than synchronous waiting.

### 2.2 Backend & Data Layer
* **NO** deprecated FastAPI `@app.on_event("startup")` / `@app.on_event("shutdown")`.
* **MANDATORY**: Use modern async lifespan context managers (`@asynccontextmanager`).
* **NO** deprecated Pydantic v1 `class Config:`.
* **MANDATORY**: Use **Pydantic v2 `model_config = ConfigDict(...)`** and `pydantic-settings`.
* **NO** synchronous database drivers (`sqlite3`, `psycopg2`).
* **MANDATORY**: Use **Async SQLAlchemy 2.0+** (`asyncpg` / `aiosqlite`) with async session makers.

### 2.3 Frontend & Storefront Experience
* **NO** legacy React Pages Router (`pages/`) or class components.
* **MANDATORY**: Use **Next.js 15+ App Router (`app/`)**, React Server Components, Tailwind CSS, and shadcn/ui.
* **MANDATORY**: Reactive state dispatching (Zustand) listening to streaming SSE backend events.

## 3. Continuous Modernization Auditing
* Before any milestone is approved at Gate 1 or Gate 4, the **Technology Modernization Department** audits all proposed designs and code against current state-of-the-art standards.
