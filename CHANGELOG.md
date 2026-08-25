# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-25

### Added - Milestone 7: Deep Shopping Research Agent & General Availability Release
- **Multi-Constraint Deep Research Engine**: Implemented `deep_research_node` in `agent-backend/agent_app/graph/nodes/deep_research.py` to synthesize complex queries (biomechanics, marathon training, flat feet, hybrid gravel/road terrain, price ceilings).
- **Match Confidence & Critic Scorer**: Quantitative match scoring algorithm evaluating candidates on impact cushioning, durability, and outsole grip with transparent trade-off analysis.
- **Deep Research UI Drawer**: Built `store-frontend/components/ResearchReportDrawer.tsx` displaying match percentage badges, biomechanical fit tags, pros list, and one-click recommendation selection.
- **Dynamic UI Actions**: Emitted `SHOW_RESEARCH_REPORT` via real-time SSE stream.
- **Full System QA Verification**: 24 automated tests passing across the entire repository.
- **Production Build Validated**: Next.js 15 App Router production bundle compiled with 0 TypeScript/lint errors.

---

## [0.7.0-alpha] - 2026-08-25

### Added - Milestone 6: Salesperson Behavior (Comparison, Critiques & Fit Recommendations)
- **Side-by-Side Product Comparison Engine**: Implemented `product_comparator_node` comparing shoe cushioning, weight, heel-to-toe drop, terrain, and price.
- **Interactive Visual Comparison Modal**: Built `store-frontend/components/ComparisonModal.tsx` displaying structured spec tables and direct "Add to Bag" buttons.
- **Sizing & Fit Advisory Intelligence**: Heuristic rules providing half-size recommendations for athletic fits (e.g. Salomon trail footwear).
- **Dynamic UI Actions**: Dispatched `OPEN_COMPARISON_MODAL` with real-time SSE stream events.

---

## [0.6.0-alpha] - 2026-08-25

### Added - Milestone 5: Persistent Shopper Memory Across Sessions
- **Persistent Shopper Memory Graph**: Implemented `ShopperMemoryStore` with SQLite async engine in `agent-backend/agent_app/memory/shopper_memory.py`.
- **Automatic Signal Extraction**: Real-time extraction of shoe size, brand affinities, category preferences, budget limits, and ergonomic injury notes.
- **Memory-Augmented LangGraph Workflow**: Inserted `memory_loader_node` at the workflow root to load, auto-inject, and persist shopper preferences across turns and sessions.
- **SecOps Rule 05 PII Sanitization**: Integrated credit card number and email masking before memory writes.
- **Shopper Memory REST API**: `GET`, `POST`, and `DELETE /api/v1/shopper/{id}/memory`.

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

---

## [0.2.0-alpha] - 2026-08-25

### Added - Milestone 1: Universal Commerce Engine Foundation
- **Universal Store Adapter SDK**: Implemented `UniversalStoreAdapter` ABC and DTOs.
- **Demo Store Backend Service**: FastAPI application with catalog seed dataset.

---

## [0.1.0-alpha] - 2026-08-25

### Added - Organization & Infrastructure Setup
- **Virtual Enterprise Operating System**: 14 autonomous startup departments and 10 production rules.
