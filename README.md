# 🛍️ ShopAgent — The Universal AI Store Associate

> **Transforming Static E-Commerce Websites into Intelligent, Conversational In-Store Shopping Experiences.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black.svg?logo=next.js)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/AI%20Orchestration-LangGraph-FF6F00.svg)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/Memory-PostgreSQL%20%2B%20pgvector-336791.svg?logo=postgresql)](https://github.com/pgvector/pgvector)

---

## 🌟 What is ShopAgent?

Most online shopping interfaces force customers to manually browse filter menus, categories, and keyword search bars. 

**ShopAgent** is an agentic AI Store Associate that sits on top of any e-commerce storefront (Shopify, WooCommerce, custom Next.js/React stores). It acts like an expert human salesperson in a physical store:
* **Active UI Control**: Automatically updates store filters, price sliders, and product grids in real-time as the shopper talks.
* **Intelligent Commerce Operations**: Compares products, provides honest critiques, explains technical specs, and manages cart/wishlist operations.
* **Persistent Shopper Memory**: Retains sizing preferences, brand affinity, and stylistic tastes across sessions via semantic vector memory (`pgvector`).
* **Universal Store SDK**: Completely decoupled from underlying e-commerce platforms with a standardized adapter contract.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 SHOPAGENT RUNTIME ECOSYSTEM                 │
├──────────────────────────────┬──────────────────────────────┤
│      EMBEDDABLE SDK          │      AI ASSOCIATE BRAIN      │
│  Next.js / React / Shopify   │  FastAPI + LangGraph Engine  │
│  Real-time SSE UI Sync       │  pgvector Semantic Memory    │
└──────────────┬───────────────┴──────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 UNIVERSAL COMMERCE ADAPTER                  │
│       Standardized REST / Webhook Integration Layer         │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
      ┌───────────┐      ┌───────────┐      ┌───────────┐
      │  Shopify  │      │WooCommerce│      │Custom API │
      └───────────┘      └───────────┘      └───────────┘
```

---

## 🏢 Virtual Enterprise Structure

This repository is developed and maintained by our autonomous AI virtual startup organization:
* **👑 Executive Board**: Strategy, velocity, and milestone delivery.
* **🏛️ System Architecture**: OpenAPI/AsyncAPI contracts, database schemas, and state graphs.
* **⚙️ Backend & Commerce Engine**: Async FastAPI, SQLAlchemy, pgvector, and tool handlers.
* **🎨 Frontend & UI Experience**: Next.js App Router, SSE streaming, and micro-animations.
* **🧪 QA & Chaos Testing**: 100% automated test coverage, negative input fuzzing, and load simulations.
* **🛡️ SRE & Platform Reliability**: 0-crash policy, circuit breakers, containerization, and health probes.
* **🔒 Security & Compliance (SecOps)**: Prompt injection defense, PII sanitization, and secrets management.
* **🚀 Growth & GTM Solutions**: SDK packaging, merchant integration playbooks, and demo video scripts.
* **🧬 Dynamic Org Growth Architect**: Meta-agent that auto-spawns new specialized domain roles as the codebase scales.

For full departmental operating guidelines, see [AGENTS.md](AGENTS.md).

---

## 🚦 Development Milestones

- [ ] **Milestone 1**: Universal Store Contract & Demo E-Commerce Foundation
- [ ] **Milestone 2**: Natural Language Agent Search & Product Display
- [ ] **Milestone 3**: Dynamic Agent UI & Filter Control via Real-time SSE
- [ ] **Milestone 4**: Interactive Cart & Wishlist Commerce Mutations
- [ ] **Milestone 5**: Persistent Shopper Memory across Sessions (`pgvector`)
- [ ] **Milestone 6**: In-Store Salesperson Behavior (Comparison, Critiques, Recommendations)
- [ ] **Milestone 7**: Deep Shopping Agents for Complex Autonomous Research

---

## 🛠️ Version Control & Contribution
We follow **Conventional Commits** and **Trunk-Based Feature Branching** (`feature/*`, `fix/*`). Direct commits to `main` are protected.
