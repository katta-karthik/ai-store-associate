---
name: org-growth-architect
description: Dynamic talent and organization meta-agent. Automatically detects new domain requirements and spawns specialized agent skills and rules as the product scales.
---

# Dynamic Organization Growth & Talent Meta-Agent Skill

## Purpose
In a rapidly scaling startup, new specialized technical and operational challenges emerge (e.g. Shopify GraphQL Connector, Stripe Billing Engine, Redis Caching Specialist, Multi-Lingual Prompt Localizer).
This meta-skill autonomously designs, scaffolds, and activates new specialized `.agents/skills/<role-name>/SKILL.md` and rules without requiring manual setup.

## Autonomous Role Spawning Trigger Conditions
1. **New Tech Domain Encountered**: When a milestone requires deep domain knowledge outside current departmental scopes (e.g., Shopify App Bridge, Stripe Webhooks, Kubernetes Helm charts).
2. **Performance Bottleneck**: When specialized optimization is needed (e.g., Vector Database Indexing Specialist, Database Sharding Engineer).
3. **Regulatory / Expansion Need**: When entering new jurisdictions or merchant formats (e.g., GDPR Compliance Agent, Accessibility A11y Reviewer).

## Role Generation Protocol
When a new role is requested or identified:
1. Determine the Role Title, Scope, and Department Assignment.
2. Create `.agents/skills/<role-name>/SKILL.md` with:
   - Clear YAML frontmatter (`name`, `description`).
   - Detailed purpose and domain-specific best practices.
   - Exact input/output expectations and verification checklists.
3. Update [AGENTS.md](file:///c:/Users/katta/Desktop/Digital%20sale%20person/AGENTS.md) to register the new department or specialist into the organization directory.
4. Notify the Executive Board (CEO/CTO) and Founder that the new specialized agent is active and ready for tasks.
