# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.5.0-alpha] - 2026-08-25

### Added - Milestone 4: Interactive Cart & Wishlist Commerce Mutations
- **Conversational Cart & Wishlist LangGraph Node**: Added `cart_manager_node` in `agent-backend/agent_app/graph/nodes/cart_manager.py` capable of extracting target shoe models, specific sizes, and executing add/remove/view cart and wishlist mutations.
- **Universal Wishlist Engine**:
  - SQLAlchemy models `Wishlist` and `WishlistItem` in `demo-store/backend/store_app/models/catalog.py`.
  - Pydantic schemas in `demo-store/backend/store_app/schemas/catalog.py`.
  - REST endpoints (`GET /api/v1/wishlist/{id}`, `POST /items`, `DELETE /items/{id}`) in `demo-store/backend/store_app/api/wishlist.py`.
  - Universal Store SDK methods in `sdk/store-sdk/universal_adapter.py`.
- **Interactive Slide-Out Drawers**:
  - `store-frontend/components/CartDrawer.tsx`: Line items with thumbnails, size badges, quantity indicators, subtotal calculations, and checkout CTA.
  - `store-frontend/components/WishlistDrawer.tsx`: Saved-for-later items with one-click "Move to Bag" action.
- **Real-Time UI Actions**:
  - Emits and consumes `SYNC_CART`, `OPEN_CART_DRAWER`, `SYNC_WISHLIST`, `OPEN_WISHLIST_DRAWER`.
- **QA Automated Test Suites**: 19 automated tests passing across catalog, cart, wishlist, and agent brain graph.

---

## [0.4.0-alpha] - 2026-08-25

### Added - Milestone 3: Dynamic Storefront UI & Real-Time SSE Filter Sync
- **Next.js 15+ App Router Storefront**: Complete modern e-commerce storefront in `store-frontend/` with React Server Components, TypeScript, Tailwind CSS, and Lucide icons.
- **Glassmorphism Design System**: Custom dark-mode UI with sleek glass panels, neon glows, and micro-animations.
- **Embeddable AI Store Associate Widget**: Floating drawer (`components/ChatWidget.tsx`) with real-time SSE stream reader.
- **Dynamic UI Action Dispatcher**: `SET_FILTERS` (adjusts filters in real-time) and `HIGHLIGHT_PRODUCTS` (glowing animation on recommended cards).
- **Zustand State Store**: Synchronizes catalog, filters, cart, and streaming.

---

## [0.3.0-alpha] - 2026-08-25

### Added - Milestone 2: LangGraph Agent Brain & Entity Extraction
- **LangGraph State Graph Engine**: Implemented `ShopAgentState` and state graph topology with `router`, `search_extractor`, and `salesperson_responder` nodes.
- **Natural Language Parameter Extraction**: Extraction of price ceilings, shoe sizes, and categories.
- **Universal Store Tool Client**: `StoreAPIClient` connecting to `/api/v1/products` endpoints.
- **Consultative Salesperson Responder**: Explains product benefits and dispatches `SET_FILTERS` and `HIGHLIGHT_PRODUCTS`.
- **REST & Real-Time SSE Streaming Endpoints**: `POST /api/v1/chat/message` and `POST /api/v1/chat/stream`.

---

## [0.2.0-alpha] - 2026-08-25

### Added - Milestone 1: Universal Commerce Engine Foundation
- **Universal Store Adapter SDK**: Implemented `UniversalStoreAdapter` ABC and DTOs.
- **System Architecture RFC & API Contract**: Decoupling boundaries, latency SLAs, and OpenAPI REST & SSE stream specification.
- **Demo Store Backend Service**: FastAPI application with catalog seed dataset and atomic cart endpoints.

---

## [0.1.0-alpha] - 2026-08-25

### Added - Organization & Infrastructure Setup
- **Virtual Enterprise Operating System**: 14 autonomous startup departments and 10 production rules.
- **Master Corporate Charter**: C-Suite leadership matrix and 6-gate delivery lifecycle.
