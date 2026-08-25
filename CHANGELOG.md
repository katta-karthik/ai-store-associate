# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.6.0-alpha] - 2026-08-25

### Added - Milestone 5: Persistent Shopper Memory Across Sessions
- **Persistent Shopper Memory Graph**: Implemented `ShopperMemoryStore` with SQLite async engine in `agent-backend/agent_app/memory/shopper_memory.py`.
- **Automatic Signal Extraction**: Real-time extraction of shoe size, brand affinities, category preferences, budget limits, and ergonomic injury notes in `agent_app/memory/extractor.py`.
- **Memory-Augmented LangGraph Workflow**: Inserted `memory_loader_node` at the workflow root to load, auto-inject, and persist shopper preferences across turns and sessions.
- **SecOps Rule 05 PII Sanitization**: Integrated credit card number and email masking before memory writes.
- **Shopper Memory REST API**: `GET`, `POST`, and `DELETE /api/v1/shopper/{id}/memory` for GDPR transparency and data control.
- **Automated QA & Evaluation Suite**: 21 automated tests passing across the repository.

---

## [0.5.0-alpha] - 2026-08-25

### Added - Milestone 4: Interactive Cart & Wishlist Commerce Mutations
- **Conversational Cart & Wishlist LangGraph Node**: Added `cart_manager_node` for conversational add/remove/view cart and wishlist mutations.
- **Universal Wishlist Engine**: SQLAlchemy models, Pydantic schemas, and REST endpoints.
- **Interactive Slide-Out Drawers**: `CartDrawer.tsx` and `WishlistDrawer.tsx` in `store-frontend/`.
- **Real-Time UI Actions**: Handled `SYNC_CART`, `OPEN_CART_DRAWER`, `SYNC_WISHLIST`, `OPEN_WISHLIST_DRAWER`.

---

## [0.4.0-alpha] - 2026-08-25

### Added - Milestone 3: Dynamic Storefront UI & Real-Time SSE Filter Sync
- **Next.js 15+ App Router Storefront**: Complete modern e-commerce storefront in `store-frontend/`.
- **Embeddable AI Store Associate Widget**: Floating drawer (`components/ChatWidget.tsx`) with real-time SSE stream reader.
- **Dynamic UI Action Dispatcher**: `SET_FILTERS` and `HIGHLIGHT_PRODUCTS`.

---

## [0.3.0-alpha] - 2026-08-25

### Added - Milestone 2: LangGraph Agent Brain & Entity Extraction
- **LangGraph State Graph Engine**: State graph topology with `router`, `search_extractor`, and `salesperson_responder`.
- **Natural Language Parameter Extraction**: Price ceilings, shoe sizes, and categories.
- **REST & Real-Time SSE Streaming Endpoints**: `POST /api/v1/chat/message` and `POST /api/v1/chat/stream`.

---

## [0.2.0-alpha] - 2026-08-25

### Added - Milestone 1: Universal Commerce Engine Foundation
- **Universal Store Adapter SDK**: Implemented `UniversalStoreAdapter` ABC and DTOs.
- **Demo Store Backend Service**: FastAPI application with catalog seed dataset.

---

## [0.1.0-alpha] - 2026-08-25

### Added - Organization & Infrastructure Setup
- **Virtual Enterprise Operating System**: 14 autonomous startup departments and 10 production rules.
