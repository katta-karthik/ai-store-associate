# 🛍️ ShopAgent — The Universal AI Store Associate

> **Transforming Static E-Commerce Websites into Intelligent, Conversational In-Store Shopping Experiences.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black.svg?logo=next.js)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/AI%20Orchestration-LangGraph-FF6F00.svg)](https://langchain-ai.github.io/langgraph/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)

---

## 🌟 What is ShopAgent?

Most online shopping interfaces force customers to manually browse filter menus, categories, and keyword search bars. 

**ShopAgent** is an agentic AI Store Sales Associate that integrates into any e-commerce storefront (Shopify, WooCommerce, custom Next.js/React stores):
* **Walkalong Retail Experience**: A personal AI associate that walks with the shopper, offering live sizing advice, charming pitch compliments, and closing deals.
* **Active UI Synchronization**: Automatically applies store filters, highlights products, triggers side-by-side comparison modals, and displays deep research biomechanics match drawers in real-time via Server-Sent Events (SSE).
* **Voice Shopping**: Web Speech API integration allows hands-free voice conversations directly with the associate.
* **Universal Commerce SDK**: Connects to any e-commerce platform via typed Store Adapters (`ShopifyStoreAdapter`, `DemoStoreAdapter`, `UniversalStoreAdapter`).
* **Persistent Shopper Memory**: Retains sizing preferences, brand affinities, and past feedback across sessions with PII sanitization.

---

## 🏛️ Modular Decoupled Architecture

The repository is organized into three distinct layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SHOPAGENT CORE PRODUCT REPO                           │
├──────────────────────────────────────┬──────────────────────────────────────┤
│     1. CLIENT WEB SDK & WIDGET       │      2. AI AGENT BRAIN ENGINE        │
│       (@shopagent/client-sdk)        │          (agent-backend/)            │
│  - <ShopAgentCompanion />            │  - LangGraph Multi-Agent Workflows   │
│  - <ComparisonModal />               │  - Sizing Fit & Biomechanics Advisor │
│  - <ResearchReportDrawer />          │  - Persistent Memory Store           │
│  - useShopAgent() React Hook         │  - Real-Time SSE Stream Endpoint     │
└──────────────────┬───────────────────┴──────────────────┬───────────────────┘
                   │                                      │
                   ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 3. UNIVERSAL STORE SDK & ADAPTERS (sdk/store-sdk/)          │
│       Standardized Data Transfer Objects (DTOs) & Typed Connector Interface │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
       ┌───────────────────────────────┼───────────────────────────────┐
       ▼                               ▼                               ▼
┌──────────────┐                ┌──────────────┐                ┌──────────────┐
│   Shopify    │                │  WooCommerce │                │ Demo Store / │
│   Storefront │                │   REST API   │                │  Custom REST │
│   GraphQL    │                │   Adapter    │                │   Adapter    │
└──────────────┘                └──────────────┘                └──────────────┘
```

### 📦 Repository Structure:
* **`agent-backend/`** — Multi-agent LangGraph AI Brain & SSE streaming API (`port 8001`).
* **`sdk/store-sdk/`** — Python Store SDK containing `UniversalStoreAdapter`, `ShopifyStoreAdapter`, `DemoStoreAdapter`, and `adapter_factory.py`.
* **`sdk/client-sdk/`** — Frontend Web SDK containing `<ShopAgentCompanion />`, comparison modal, research report drawer, and `useShopAgent` hook.
* **`tests/`** — Automated test suite covering agent brain workflows, memory, and store adapters (27/27 passing).
* **`demo-store/`** — *[Sandbox / Local Demo]* Isolated mock e-commerce store (`demo-store/backend` + `demo-store/frontend`) used exclusively for local testing, decoupled and gitignored.

---

## 🚀 Quickstart Guide

### 1. Run the AI Agent Brain
```bash
cd agent-backend
pip install -r requirements.txt
uvicorn agent_app.main:app --reload --port 8001
```

### 2. Connect Your Storefront using the Client SDK
```tsx
import { ShopAgentCompanion, useShopAgent } from '@shopagent/client-sdk';

export default function MyStorefront() {
  return (
    <div className="store-layout">
      {/* Merchant Store Content */}
      <Header />
      <ProductCatalog />

      {/* Embed the AI Sales Associate with 1 Line */}
      <ShopAgentCompanion
        config={{
          agentApiUrl: 'http://localhost:8001/api/v1',
          onFilterChange: (filters) => applyStoreFilters(filters),
          onAddToCart: (prodId, varId) => handleAddToCart(prodId, varId),
        }}
      />
    </div>
  );
}
```

### 3. Run Automated Tests
```bash
python -m pytest
```

---

## 🏢 Virtual Enterprise Structure

This repository is governed by the 14-department autonomous AI enterprise defined in [AGENTS.md](AGENTS.md).
* **Active Milestone**: [PROJECT_STATE.md](PROJECT_STATE.md)
* **API & Reliability Guardrails**: [`.agents/rules/`](.agents/rules/)
