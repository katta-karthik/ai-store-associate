# Rule 06: AI Evaluation & Prompt Quality Standards

## 1. Quantitative Evaluation Over Guesswork
* Never evaluate LLM prompts or agent behavior through casual manual inspection alone.
* Maintain a golden dataset of realistic shopper conversations with expected outputs (intent classification, filter payloads, tool call arguments).

## 2. Core Evaluation Metrics
1. **Tool-Calling Precision & Recall**:
   * Does the agent call `search_products` with the exact intended filters when given a complex query? Target: >95% precision.
2. **Hallucination Rate**:
   * Does the agent recommend products that do not exist in the store catalog or quote incorrect prices? Target: 0% tolerance.
3. **Memory Retrieval Relevance**:
   * Does the cosine similarity search over `pgvector` accurately retrieve relevant past preferences (e.g. shoe size, brand affinity)?
4. **Latency SLA**:
   * Time to First Token (TTFT) in SSE streams must remain under 800ms.
   * Total response generation under 2.5 seconds.

## 3. Prompt Versioning & Regression Tracking
* Prompt templates must be modular, versioned in source control, and tracked with evaluation runs.
* A prompt update must not degrade accuracy on older benchmark test cases.
