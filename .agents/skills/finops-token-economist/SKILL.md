---
name: finops-token-economist
description: Monitors AI token consumption, implements model cascading (Flash vs Pro), optimizes prompt caching, and enforces unit cost economics for ShopAgent.
---

# FinOps & AI Token Cost Optimization Skill

## Purpose
Use this skill to design token-efficient prompt templates, calculate cost per shopper session, configure model cascading (routing cheap tasks to Flash and complex tasks to Pro), and enforce LLM economic viability.

## Core Responsibilities
1. **Model Cascading Strategy**:
   * Direct fast extraction (search filters, intent detection, PII masking) to lightweight models (Gemini Flash).
   * Reserve deep models (Gemini Pro, Deep Agents) for multi-product comparisons, deep research, and final recommendations.
2. **Context Window & Memory Optimization**:
   * Enforce sliding-window token truncation for active conversation turns.
   * Offload long-term shopper context into high-density semantic vector embeddings (`pgvector`) instead of stuffing raw conversation transcripts into prompt context.
3. **Unit Economics & Cost Tracking**:
   * Calculate estimated API cost per 1,000 active shoppers.
   * Enable prompt prefix caching on static system prompts and tool definitions.

## Efficiency Checklist
- [ ] Are static system prompts formatted to maximize prompt caching?
- [ ] Is conversational history bounded with a maximum turn limit?
- [ ] Are simple regex/deterministic tasks handled in Python code rather than invoking LLMs?
