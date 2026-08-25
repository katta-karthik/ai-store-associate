# Rule 08: FinOps & AI Token Cost Optimization Standards

## 1. Token Budget Constraints
* AI SaaS economics require strict unit cost controls. A single shopping session must not exceed an average token budget of 15,000 total tokens (input + output).
* Sliding window memory or context summarization must prevent unbounded history accumulation.

## 2. Model Cascading Architecture
* Use the right model for the right task:
  - **Tier 1 (Fast & Economical - e.g. Gemini 3.7 Flash / Mini)**: Intent routing, filter parameter extraction, simple FAQ answering, and PII masking.
  - **Tier 2 (Deep Reasoning - e.g. Gemini Pro / Deep Agents)**: Multi-product comparison, complex styling critiques, and deep shopping research.
* Never use expensive frontier reasoning models for simple deterministic regex or classification tasks.

## 3. Prompt Caching & Embeddings Efficiency
* Leverage prompt prefix caching for static system instructions and product catalog schemas.
* Batch vector embeddings generation during catalog sync rather than generating per-item embeddings on runtime shopper requests.
