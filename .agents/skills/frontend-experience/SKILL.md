---
name: frontend-experience
description: Builds Next.js/React e-commerce storefronts, real-time SSE streaming chat widgets, dynamic filter sync, and interactive state management.
---

# Frontend & UI Experience Skill

## Purpose
Use this skill when building Next.js components, store layouts, real-time chat widgets, SSE stream handlers, and interactive state synchronization.

## Technical Standards
1. **Framework**: Next.js App Router (React 19 / TypeScript).
2. **Styling**: Tailwind CSS + shadcn/ui + Framer Motion for smooth micro-animations.
3. **State Synchronization**:
   * Global state via Zustand or React Context for Store Filters, Cart, and Wishlist.
   * Event Dispatcher: Listens to incoming SSE events from the AI Associate and updates store state in real time:
     - `SET_FILTERS`: Updates active price/category/size filters visibly on the screen.
     - `HIGHLIGHT_PRODUCTS`: Visually highlights products recommended by the agent.
     - `UPDATE_CART`: Syncs cart count and items.
4. **Resilience**:
   * Auto-reconnect on SSE connection drops with exponential backoff.
   * Optimistic UI updates with rollbacks on network failure.
   * Graceful loading skeletons and error boundaries.

## Development Workflow
1. Review UI wireframes and API contracts.
2. Build responsive, mobile-first components.
3. Wire up SSE connection to the AI Associate backend.
4. Implement action dispatchers for real-time UI control.
5. Hand off to QA Department for browser and integration verification.
