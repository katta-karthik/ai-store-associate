# Rule 11: Continual Self-Improvement & Recursive Delegation Standards (Prime Agent Architecture)

## 1. The Recursive Language Model (RLM) Principle
* **Context as Variables**: Never dump raw 50k+ token dumps into a single monolithic LLM prompt. Store long-range context, product specs, customer purchase histories, and transcripts in persistent variables, runtime scratch storage, or vector/graph databases.
* **Programmatic Sub-Agent Spawning**: When a problem requires multi-faceted analysis (e.g. biomechanical evaluation + price benchmarking + style alignment), parent agents MUST programmatically decompose the task into isolated child sub-agents.
* **Zero Context Contamination**: Each spawned sub-agent receives ONLY its dedicated prompt and scoped context slice. Sub-agents must never suffer from context rot or cross-task prompt leakage.

## 2. Dynamic Hierarchy & Nuclear Family Communication
* **Hierarchical Tree Delegation**: Sub-agents can recursively spawn leaf sub-agents when tasks require deeper sub-specialization (e.g. Deep Biomechanics Critic $\rightarrow$ Sole Durability Analyzer).
* **Scoped Messaging**: Communication flows within the nuclear family (Parent $\leftrightarrow$ Sibling $\leftrightarrow$ Child). Results are asynchronously aggregated and returned to the parent coordinator.
* **Non-Blocking Asynchronous Execution**: All child agent invocations must run concurrently via `asyncio.gather()` or background task queues to maintain user responsiveness (<1.5s total latency target).

## 3. The Continual Harness & Self-Refinement Protocol (`/refine`)
* **Harness as Mutable State**: All `.agents/skills/`, prompt templates, tool definitions, and system rules are treated as mutable state on disk.
* **Trajectory Retrospective Loop**:
  1. After completing complex reasoning tasks or resolving test/runtime failures, the agent reviews its trajectory.
  2. The agent identifies reasoning bottlenecks, hallucination risks, or outdated rules.
  3. The agent generates precision patches to `.agents/skills/` and system instructions permanently on disk.
* **Continuous Playbook Evolution**: Operational playbooks improve monotonically across runs without requiring human prompt re-engineering.

## 4. On-The-Fly Digital Hiring & Org Growth
* **Dynamic Role Generation**: When an unhandled domain emerges (e.g., 3D shoe rendering, regional tax compliance, bespoke loyalty program), the `org-growth-architect` must autonomously write a new `.agents/skills/<new-role>/SKILL.md` and register it in `AGENTS.md`.
