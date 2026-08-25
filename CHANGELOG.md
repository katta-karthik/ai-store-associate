# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0-alpha] - 2026-08-25

### Added - Milestone 2: LangGraph Agent Brain & Entity Extraction
- **LangGraph State Graph Engine**: Implemented `ShopAgentState` and state graph topology with `router`, `search_extractor`, and `salesperson_responder` nodes in `agent-backend/agent_app/graph/`.
- **Natural Language Parameter Extraction**:
  - Regex and semantic extraction of price ceilings (e.g. "under ₹8000", "below 8k").
  - Size extraction (e.g. "size 10", "uk 9").
  - Brand and category classification (Road Running, Trail & Outdoor, Sneakers).
- **Universal Store Tool Client**: `StoreAPIClient` connecting to `/api/v1/products` endpoints.
- **Consultative Salesperson Responder**: Explains why products match shopper needs and dispatches `SET_FILTERS` and `HIGHLIGHT_PRODUCTS` UI actions.
- **REST & Real-Time SSE Streaming Endpoints**:
  - `POST /api/v1/chat/message`: Standard REST turn processing.
  - `POST /api/v1/chat/stream`: Real-time Server-Sent Events stream yielding `ui_action`, `token`, and `done` frames.
- **Automated QA Test Harness**: 14 automated tests passing across the repository with clean namespace separation (`agent_app` vs `store_app`).
- **Multi-Service Containerization**: Updated `docker-compose.yml` to orchestrate both `shopagent-demo-store` (port 8000) and `shopagent-brain` (port 8001).

---

## [0.2.0-alpha] - 2026-08-25

### Added - Milestone 1: Universal Commerce Engine Foundation
- **Universal Store Adapter SDK**: Implemented `UniversalStoreAdapter` ABC and DTOs in `sdk/store-sdk/universal_adapter.py`.
- **System Architecture RFC**: Published decoupling boundaries and latency SLAs in `docs/architecture.md`.
- **Universal Commerce API Contract**: Published OpenAPI REST & SSE stream specification in `docs/api-contract.md`.
- **Demo Store Backend Service**: FastAPI application with catalog seed dataset, multi-dimensional search/filter, and atomic cart endpoints.
- **QA Automated Test Suite**: 11 automated pytest suites covering health probes and cart mutations.

---

## [0.1.0-alpha] - 2026-08-25

### Added - Organization & Infrastructure Setup
- **Virtual Enterprise Operating System**: Initialized 12 autonomous startup departments in `.agents/skills/` and `.agents/rules/`.
- **Master Corporate Charter**: Established C-Suite leadership matrix (CEO, CTO, CPO) and 6-gate delivery lifecycle in `AGENTS.md`.
- **Production Guardrails & Policies**: 8 production rules for architecture, SRE, QA, SecOps, and FinOps.
- **Dynamic Organization Spawner**: Meta-agent (`org-growth-architect`) for on-demand role creation.
