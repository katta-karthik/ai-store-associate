# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.0-alpha] - 2026-08-25

### Added - Milestone 3: Dynamic Storefront UI & Real-Time SSE Filter Sync
- **Next.js 15+ App Router Storefront**: Complete modern e-commerce storefront in `store-frontend/` with React Server Components, TypeScript, Tailwind CSS, and Lucide icons.
- **Glassmorphism Design System**: Custom dark-mode UI with sleek glass panels, neon glows, and micro-animations in `app/globals.css`.
- **Embeddable AI Store Associate Widget**: Floating drawer (`components/ChatWidget.tsx`) with real-time SSE stream reader, markdown rendering, and quick prompt suggestions.
- **Dynamic UI Action Dispatcher**:
  - `SET_FILTERS`: Visibly updates category tabs, price slider, brand toggles, and size pills on screen in real time.
  - `HIGHLIGHT_PRODUCTS`: Applies animated glowing highlights (`agent-highlight`) around recommended product cards.
- **Zustand State Store**: Integrated state store (`store/useStore.ts`) synchronizing catalog fetching, cart items, filter state, and chat streaming.
- **Production Build & Multi-Service Compose**:
  - Validated with `npm run build` (0 TypeScript / lint errors).
  - Multi-stage `store-frontend/Dockerfile`.
  - Updated `docker-compose.yml` orchestrating demo store backend (8000), agent brain (8001), and storefront (3000).

---

## [0.3.0-alpha] - 2026-08-25

### Added - Milestone 2: LangGraph Agent Brain & Entity Extraction
- **LangGraph State Graph Engine**: Implemented `ShopAgentState` and state graph topology with `router`, `search_extractor`, and `salesperson_responder` nodes in `agent-backend/agent_app/graph/`.
- **Natural Language Parameter Extraction**: Regex and semantic extraction of price ceilings, shoe sizes, and categories.
- **Universal Store Tool Client**: `StoreAPIClient` connecting to `/api/v1/products` endpoints.
- **Consultative Salesperson Responder**: Explains product benefits and dispatches `SET_FILTERS` and `HIGHLIGHT_PRODUCTS` UI actions.
- **REST & Real-Time SSE Streaming Endpoints**: `POST /api/v1/chat/message` and `POST /api/v1/chat/stream`.
- **Automated QA Test Harness**: 14 automated tests passing across the repository.

---

## [0.2.0-alpha] - 2026-08-25

### Added - Milestone 1: Universal Commerce Engine Foundation
- **Universal Store Adapter SDK**: Implemented `UniversalStoreAdapter` ABC and DTOs in `sdk/store-sdk/universal_adapter.py`.
- **System Architecture RFC**: Published decoupling boundaries and latency SLAs in `docs/architecture.md`.
- **Universal Commerce API Contract**: Published OpenAPI REST & SSE stream specification in `docs/api-contract.md`.
- **Demo Store Backend Service**: FastAPI application with catalog seed dataset and atomic cart endpoints.
- **QA Automated Test Suite**: 11 automated pytest suites.

---

## [0.1.0-alpha] - 2026-08-25

### Added - Organization & Infrastructure Setup
- **Virtual Enterprise Operating System**: Initialized 14 autonomous startup departments and 10 production rules.
- **Master Corporate Charter**: Established C-Suite leadership matrix and 6-gate delivery lifecycle in `AGENTS.md`.
- **Dynamic Organization Spawner**: Meta-agent (`org-growth-architect`) for on-demand role creation.
