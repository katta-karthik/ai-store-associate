# Rule 07: Git Release Management & Documentation Synchronization Standards

## 1. Zero Undocumented Code Policy
* Every code addition, API modification, or schema change MUST be documented simultaneously in:
  1. `PROJECT_STATE.md`: Update milestone progress, active tasks, and recent changes.
  2. `CHANGELOG.md`: Record semantic changes under the active release version.
  3. `docs/api-contract.md` or relevant architecture doc: If an endpoint, parameter, or event schema changes.
  4. Code Docstrings: All public functions, classes, Pydantic schemas, and endpoints must have Google-style docstrings.

## 2. Git Branch & Commit Hygiene
* **Trunk-Based Feature Branching**: Work exclusively on `feature/<name>` or `fix/<name>`.
* **Conventional Commits**: Every commit message must use standard prefixes:
  - `feat(...)`: A new feature
  - `fix(...)`: A bug fix
  - `docs(...)`: Documentation changes only
  - `test(...)`: Adding or updating tests
  - `refactor(...)`: Code refactoring without changing behavior
  - `chore(...)`: Tooling, build config, or dependency updates
* **Clean Working Tree**: Before any handoff or chat session pause, the working directory must be committed and pushed to the remote GitHub repository.
