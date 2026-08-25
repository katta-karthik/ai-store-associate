---
name: qa-chaos-tester
description: Generates automated test suites, executes unit/integration tests, runs chaos fuzzing, and validates concurrency and latency under load.
---

# QA & Chaos Testing Skill

## Purpose
Use this skill to write test harnesses, execute pytest suites, fuzz edge-case inputs, test state machine transitions, and benchmark concurrency.

## Testing Protocols
1. **Unit & API Testing**:
   * `pytest tests/unit/ -v`
   * `pytest tests/integration/ -v`
   * Test all HTTP endpoints for expected status codes, envelope schemas, and database side-effects.
2. **Negative & Edge Fuzzing**:
   * Test with empty payloads, malformed JSON, out-of-range numeric values.
   * Simulate LLM returning invalid JSON or unknown tool names; verify system recovers without 500 error.
3. **Agent State Machine Testing**:
   * Mock LLM outputs to test all LangGraph conditional paths (Search node -> Filter node -> Cart node -> Memory node).
   * Verify memory extraction and recall with simulated shopper preference vectors.
4. **Load & Concurrency Testing**:
   * Simulate multiple concurrent sessions updating carts and searching products simultaneously.
   * Measure p95 and p99 response times.

## Verification Checklist
- [ ] 100% of test assertions passing.
- [ ] Zero unhandled tracebacks in test logs.
- [ ] Database state clean after test teardown.
