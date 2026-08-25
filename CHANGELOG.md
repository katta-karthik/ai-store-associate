# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0-alpha] - 2026-08-25

### Added - Milestone 1: Universal Commerce Engine Foundation
- **Universal Store Adapter SDK**: Implemented `UniversalStoreAdapter` ABC and DTOs in `sdk/store-sdk/universal_adapter.py`.
- **System Architecture RFC**: Published decoupling boundaries and latency SLAs in `docs/architecture.md`.
- **Universal Commerce API Contract**: Published OpenAPI REST & SSE stream specification in `docs/api-contract.md`.
- **Demo Store Backend Service**:
  - FastAPI application with CORS and async SQLAlchemy session management.
  - Relational database models for Products, Categories, Variants, and Carts.
  - Seed catalog dataset with realistic footwear (Nike Pegasus, Adidas Ultraboost, Puma Velocity, Salomon Speedcross).
  - Search, multi-dimensional filter, and product detail endpoints (`/api/v1/products`).
  - Atomic cart mutation and stock validation endpoints (`/api/v1/cart`).
- **QA Automated Test Suite**: 11 automated pytest suites covering health probes, catalog search, price range filtering, out-of-stock validation, and cart mutations.
- **SRE & Containerization**: Added multi-stage `Dockerfile`, root `docker-compose.yml`, and `/health/live`, `/health/ready` probes.

---

## [0.1.0-alpha] - 2026-08-25

### Added - Organization & Infrastructure Setup
- **Virtual Enterprise Operating System**: Initialized 12 autonomous startup departments in `.agents/skills/` and `.agents/rules/`.
- **Master Corporate Charter**: Established C-Suite leadership matrix (CEO, CTO, CPO) and 6-gate delivery lifecycle in `AGENTS.md`.
- **Production Guardrails & Policies**:
  - `01-architecture-contract.md`: Decoupled architecture and REST/SSE boundary.
  - `02-sre-production-guardrails.md`: Zero-crash, circuit breakers, and connection pool limits.
  - `03-qa-chaos-standards.md`: Automated test standards and fuzzing policies.
  - `04-git-release-workflow.md`: Branch protection and semantic versioning rules.
  - `05-security-compliance-guardrails.md`: Prompt injection defenses and PII sanitization.
  - `06-ai-evaluation-standards.md`: Quantitative LLM benchmark SLAs.
  - `07-documentation-git-standards.md`: Zero undocumented code and live sync.
  - `08-finops-token-budgeting.md`: Token budgets and model cascading.
- **Dynamic Organization Spawner**: Meta-agent (`org-growth-architect`) for on-demand role creation.
