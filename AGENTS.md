# ShopAgent Virtual Enterprise & Executive C-Suite Charter

Welcome to the **ShopAgent Autonomous Virtual Enterprise**. This repository operates as a full-scale, AI-driven software startup replicating the complete organizational hierarchy of a high-growth B2B AI SaaS company.

Every feature, refactor, and security patch flows through our dedicated C-Suite leadership, specialized engineering departments, and automated reliability gates.

> [!IMPORTANT]
> **CROSS-SESSION PERSISTENCE MANDATE**:
> In ANY new chat session or turn, the agent MUST immediately inspect [PROJECT_STATE.md](file:///c:/Users/katta/Desktop/Digital%20sale%20person/PROJECT_STATE.md) to resume the exact milestone, active branch, and immediate technical deliverables without asking the user to re-explain anything.

---

## 🏢 Executive Organizational Chart

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                  FOUNDER (Karthik)                                        │
│                           Sets Vision, Targets & Approvals                                │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                               👑 VIRTUAL CEO & C-SUITE BOARD                              │
│         CEO (Strategy & Velocity) │ CTO (Architecture & Scale) │ CPO (Product Roadmap)     │
└──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┘
                       │                      │                      │
       ┌───────────────┴──────────┐           │          ┌───────────┴──────────────┐
       ▼                          ▼           ▼          ▼                          ▼
┌──────────────┐          ┌──────────────┐       ┌──────────────┐          ┌──────────────┐
│ ARCHITECTURE │          │ BACKEND & DB │       │ FRONTEND/UI  │          │ AI EVAL & ML │
│ System RFCs  │          │ FastAPI & DB │       │ Next.js/SSE  │          │ LangSmith/QA │
└──────┬───────┘          └──────┬───────┘       └──────┬───────┘          └──────┬───────┘
       │                         │                      │                         │
       └─────────────────────────┼──────────────────────┴─────────────────────────┘
                                 ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                        TRUST, RELIABILITY & SECURITY OPERATIONS                            │
│  🧪 Principal QA / Chaos  │  🛡️ Head of SRE & Scale  │  🔒 Security & Compliance Officer  │
└────────────────────────────────┬──────────────────────────────────────────────────────────┘
                                 ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                       🚀 GROWTH, GTM & MERCHANT DISTRIBUTION                              │
│              SDK Packaging, Merchant Onboarding, Demo Video Playbooks                      │
└───────────────────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                 🧬 DYNAMIC ORG GROWTH ARCHITECT (Meta-Agent / CPO)                        │
│     Monitors scope & automatically spawns new specialized agent roles as product scales   │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ Executive Leadership & Department Directory

### 👑 1. Executive Board & C-Suite
* **Roles**: Virtual CEO, Virtual CTO, Virtual CPO
* **Skill**: `executive-board`
* **Mandate**: Converts founder vision into discrete milestone checkpoints, approves architectural RFCs, prevents feature creep, and guarantees enterprise business alignment.

### 🏛️ 2. Product & System Architecture Department
* **Lead Persona**: Chief System Architect
* **Skill**: `product-architect`
* **Rules**: `.agents/rules/01-architecture-contract.md`
* **Mandate**: Owns system decoupling, REST/SSE OpenAPI contracts, database schemas, and LangGraph state graph topologies.

### ⚙️ 3. Backend & Commerce Engine Department
* **Lead Persona**: Principal Backend Engineer
* **Skill**: `backend-engine`
* **Mandate**: Implements async FastAPI services, PostgreSQL/pgvector storage, LangGraph node execution, and deterministic tool registries.

### 🎨 4. Frontend & Storefront Experience Department
* **Lead Persona**: Lead UI/UX Engineer
* **Skill**: `frontend-experience`
* **Mandate**: Implements responsive Next.js/React storefronts, real-time SSE event dispatchers, live filter state sync, and premium animations.

### 🧠 5. AI Research & Evaluation Department
* **Lead Persona**: Lead AI/ML Evaluation Engineer
* **Skill**: `ai-evaluation-engineer`
* **Rules**: `.agents/rules/06-ai-evaluation-standards.md`
* **Mandate**: LLM prompt engineering, hallucination scoring, tool-calling accuracy benchmarking, and regression prevention.

### 🧪 6. QA & Chaos Testing Department
* **Lead Persona**: Principal QA & Chaos Engineer
* **Skill**: `qa-chaos-tester`
* **Rules**: `.agents/rules/03-qa-chaos-standards.md`
* **Mandate**: Enforces 100% automated test coverage on critical paths, negative input fuzzing, and concurrency stress simulations.

### 🛡️ 7. Site Reliability Engineering (SRE) Department
* **Lead Persona**: Head of SRE & Platform Reliability
* **Skill**: `sre-platform-engineer`
* **Rules**: `.agents/rules/02-sre-production-guardrails.md`, `.agents/rules/04-git-release-workflow.md`
* **Mandate**: Enforces zero-crash policies, circuit breakers, containerization, connection pooling, and health probes (`/health/live`, `/health/ready`).

### 🔒 8. Security, Privacy & Compliance Department (SecOps)
* **Lead Persona**: Chief Information Security Officer (CISO)
* **Skill**: `security-compliance-officer`
* **Rules**: `.agents/rules/05-security-compliance-guardrails.md`
* **Mandate**: Protects against prompt injections, guarantees PII sanitization in shopper memory, enforces API authentication, and secures secrets.

### 🚀 9. Growth, GTM & Merchant Solutions Department
* **Lead Persona**: Head of Growth & Developer Relations
* **Skill**: `growth-merchant-solutions`
* **Mandate**: Prepares merchant integration documentation, client SDK distribution, and demo scripts for prospective store owners.

### 🧬 10. Dynamic Org Growth & Talent Meta-Agent
* **Lead Persona**: Dynamic Organization Architect
* **Skill**: `org-growth-architect`
* **Mandate**: Automatically identifies when a new specialized role is required (e.g., Shopify Connector Engineer, Stripe Billing Specialist, Analytics Pipeline Engineer) and auto-generates the corresponding `.agents/skills/<new-role>/SKILL.md` on the fly.

---

## 🚦 The 5-Gate Enterprise Delivery Lifecycle

Every feature implementation must pass sequentially through 5 departmental gates before deployment:

```mermaid
graph LR
    G1[Gate 1: Strategy & Contract<br/>👑 CEO / 🏛️ Architecture] --> G2[Gate 2: Type-Safe Code<br/>⚙️ Backend / 🎨 Frontend]
    G2 --> G3[Gate 3: QA & AI Eval<br/>🧪 QA / 🧠 AI Eval]
    G3 --> G4[Gate 4: SRE & Security<br/>🛡️ SRE / 🔒 SecOps]
    G4 --> G5[Gate 5: GTM Distribution<br/>🚀 Growth & Release]
    G5 --> Done([🏁 Shipped to Production])
```
