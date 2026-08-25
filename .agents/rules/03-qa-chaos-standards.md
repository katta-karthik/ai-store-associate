# Rule 03: QA & Chaos Testing Standards

## 1. Test-Driven Verification
Every backend endpoint, tool function, and state graph node must be accompanied by automated unit and integration tests using `pytest` and `pytest-asyncio`.

## 2. Mandatory Test Categories
1. **Happy Path Tests**: Verify that valid user shopping requests (search, filter, add-to-cart, preference recall) succeed and produce correct state changes.
2. **Negative & Edge-Case Tests (Fuzzing)**:
   * Empty query strings, extreme character lengths, special characters/SQL injection patterns.
   * Invalid IDs, non-existent inventory items, out-of-stock items.
   * Tool execution failures simulating network dropouts.
3. **Deterministic State Machine Tests**:
   * Verify that LangGraph state routers correctly branch on all conditions.
   * Verify memory retrieval correctly ranks relevant shopper preferences using pgvector similarity thresholds.
4. **Concurrency & Load Tests**:
   * Simulate concurrent shopper sessions (using `locust` or `asyncio` test harnesses) to ensure no deadlocks or race conditions on cart mutations.

## 3. Pre-Merge Gate
* All tests must pass with 100% green status before any code is merged into `main` or deployed.
