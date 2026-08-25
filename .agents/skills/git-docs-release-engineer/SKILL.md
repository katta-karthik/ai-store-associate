---
name: git-docs-release-engineer
description: Manages Git version control, branch hygiene, conventional commits, remote GitHub syncing, CHANGELOG maintenance, and complete documentation integrity.
---

# Git Release & Documentation Engineering Skill

## Purpose
Use this skill to maintain Git repository health, enforce conventional commit standards, synchronize remote GitHub branches, update `CHANGELOG.md`, keep `PROJECT_STATE.md` synchronized with live progress, and ensure 100% documentation coverage across the codebase.

## Core Responsibilities
1. **Git Lifecycle & Branch Protection**:
   * Create and manage feature branches (`feature/<milestone-name>`).
   * Structure conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).
   * Push and track all local branches to the remote GitHub repository (`git push -u origin <branch>`).
2. **Continuous Documentation Synchronization**:
   * Ensure any architectural modification is immediately updated in `docs/architecture.md` and `docs/api-contract.md`.
   * Update `PROJECT_STATE.md` with active tasks, milestone completion percentages, and next steps.
   * Keep `CHANGELOG.md` updated under the active semantic version (`v0.1.0-alpha`).
   * Verify all functions and API routes have complete Google-style docstrings.
3. **Cross-Session Memory Assurance**:
   * Guarantee that any developer or agent starting in a new chat session can inspect `PROJECT_STATE.md` and git logs to instantly understand repository context.

## Pre-Commit & Pre-Push Checklist
- [ ] Are all new files staged and tracked in git?
- [ ] Is `.gitignore` protecting secrets, `.env` files, and local build caches?
- [ ] Has `PROJECT_STATE.md` been updated to reflect the latest progress?
- [ ] Is the commit message clear, descriptive, and using Conventional Commit syntax?
- [ ] Has the branch been pushed to `origin`?
