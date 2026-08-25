---
name: ai-evaluation-engineer
description: Implements quantitative LLM benchmarks, hallucination detection, prompt quality tracking, and LangGraph accuracy evaluation.
---

# AI Evaluation & Prompt Engineering Skill

## Purpose
Use this skill to benchmark LLM outputs, measure tool-calling accuracy, track semantic memory retrieval recall, and prevent prompt regressions.

## Evaluation Framework
1. **Benchmark Test Harness**:
   * Maintain a curated suite of diverse shopping queries (ambiguous queries, multi-constraint queries, brand comparisons, memory tests).
   * Automatically run evaluation datasets against the LangGraph pipeline.
2. **Scoring Dimensions**:
   * **Intent Classification Accuracy**: Did the router direct to search vs general chat vs cart?
   * **Parameter Extraction Accuracy**: Did the LLM extract accurate price ceilings, categories, and attributes?
   * **Hallucination Check**: Cross-reference recommended product IDs against the real database catalog.
3. **Observability Integration**:
   * Format spans and trace logs compatible with LangSmith / Langfuse / OpenTelemetry.

## Deliverables
* Evaluation benchmark scripts (`tests/evals/test_agent_benchmarks.py`).
* Accuracy reports comparing prompt versions.
