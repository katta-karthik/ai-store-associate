---
name: sre-platform-engineer
description: Manages Docker containerization, health probes, connection pooling, circuit breakers, rate limiting, and observability for ShopAgent production.
---

# SRE & Platform Reliability Skill

## Purpose
Use this skill when configuring Docker containers, setting up database connection pools, adding telemetry/health endpoints, implementing rate limiters, and verifying production readiness.

## Core Infrastructure Responsibilities
1. **Containerization & Orchestration**:
   * `docker-compose.yml` for local & staging environments (FastAPI services, PostgreSQL with `pgvector`, Redis for state caching).
   * Multi-stage Dockerfiles with non-root security users and minimal image footprints.
2. **Observability & Health Probes**:
   * Standard endpoints:
     - `/health/live`: Basic process liveness check.
     - `/health/ready`: Deep readiness check (verifies DB connection, Redis ping, LLM provider connectivity).
     - `/metrics`: Prometheus/OpenTelemetry metrics (request latency, tool error counts, active sessions).
3. **Resilience & Fault Tolerance**:
   * Connection pool management (asyncpg pool bounds, automatic recycling).
   * Circuit breaker implementation for external LLM API calls with automated fallback.
   * Rate limiting per IP/session to prevent API abuse.

## Production Readiness Checklist
- [ ] Are health check endpoints returning 200 OK under standard conditions?
- [ ] Is graceful shutdown handled properly on SIGTERM (finishing ongoing queries)?
- [ ] Are all database secrets loaded via environment variables (.env)?
- [ ] Is resource usage (CPU/Memory) bounded in Docker configurations?
