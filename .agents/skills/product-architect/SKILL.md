---
name: product-architect
description: Designs system RFCs, OpenAPI REST/SSE contracts, database schemas, and LangGraph state graphs for ShopAgent.
---

# Product & System Architecture Skill

## Purpose
Use this skill when defining or modifying system boundaries, designing database tables, writing API contracts, or structuring LangGraph state machines.

## Key Deliverables
1. **RFC & System Design**: Explaining the exact data flow, decoupled layers, and latency budgets.
2. **API Contracts**: Defining standard REST request/response schemas (OpenAPI specification) and SSE stream event payloads (`message`, `action`, `filter_change`, `cart_update`).
3. **Database & Vector Schema**: Designing PostgreSQL relational tables (products, inventory, carts, sessions) and pgvector semantic memory schemas (shopper_preferences, embeddings).
4. **LangGraph Graph Topology**: Defining nodes (Router, Search, ShoppingAction, MemoryExtractor, Reviewer), state schema (`ShopAgentState`), and conditional edges.

## Checklist Before Handoff to Backend/Frontend
- [ ] Are all fields strictly typed with types and descriptions?
- [ ] Is the API contract backward compatible?
- [ ] Are error response codes (400, 404, 422, 429, 500) explicitly documented?
- [ ] Is there zero direct database dependency between Store and Agent?
