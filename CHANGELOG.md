# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0-alpha] - 2026-08-25

### Added
- **Virtual Enterprise Operating System**: Initialized 10 autonomous startup departments in `.agents/skills/` and `.agents/rules/`.
- **Master Corporate Charter**: Established C-Suite leadership matrix (CEO, CTO, CPO) and 5-gate delivery lifecycle in `AGENTS.md`.
- **Production Guardrails & Policies**:
  - `01-architecture-contract.md`: Decoupled architecture and REST/SSE boundary.
  - `02-sre-production-guardrails.md`: Zero-crash, circuit breakers, and connection pool limits.
  - `03-qa-chaos-standards.md`: Automated test standards and fuzzing policies.
  - `04-git-release-workflow.md`: Branch protection and semantic versioning rules.
  - `05-security-compliance-guardrails.md`: Prompt injection defenses and PII sanitization.
  - `06-ai-evaluation-standards.md`: Quantitative LLM benchmark SLAs.
- **Dynamic Organization Spawner**: Meta-agent (`org-growth-architect`) for on-demand role creation.
