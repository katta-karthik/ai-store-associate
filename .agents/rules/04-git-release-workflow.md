# Rule 04: Git, Release & Migration Safety

## 1. Branching Strategy
* `main`: Production-ready, stable branch. Direct commits to `main` are prohibited.
* `feature/<feature-name>`: Dedicated branch for specific features or milestones (e.g., `feature/demo-store-api`, `feature/langgraph-search`).
* `fix/<bug-name>`: Dedicated branch for bugfixes.
* `release/vX.Y.Z`: Release stabilization branches.

## 2. Commit Message Standards (Conventional Commits)
All commit messages must follow standard semantic format:
* `feat(be): add async cart mutation endpoints with stock validation`
* `feat(agent): implement LangGraph state router for shopper intent`
* `fix(fe): handle SSE stream disconnection gracefully`
* `test(qa): add concurrency load tests for inventory lock`
* `chore(sre): configure docker-compose for postgres pgvector`

## 3. Database Migration Safety
* Schema changes must always be managed through versioned migration scripts (Alembic).
* Destructive migrations (dropping tables/columns) must be two-phase:
  1. Deprecate and make nullable.
  2. Drop only after application code no longer queries it.
* Migrations must be verified against rollback scenarios before deployment.
