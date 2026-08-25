---
name: security-compliance-officer
description: Enforces SecOps, prompt injection defenses, PII sanitization in memory, token safety, and API security.
---

# Security & Compliance Officer (SecOps) Skill

## Purpose
Use this skill to audit endpoints, validate prompt injection barriers, enforce PII redaction before vector persistence, and verify safe token handling.

## Security Audit Protocol
1. **Prompt Injection Testing**:
   * Attempt jailbreaks on conversational inputs (e.g. asking the agent to disclose developer instructions or simulate admin commands).
   * Verify that system prompt defense boundaries contain rogue user inputs.
2. **PII Redaction Audit**:
   * Feed mock shopper profiles containing fake credit cards, phone numbers, and addresses.
   * Verify that the memory extractor sanitizes PII before writing to `pgvector`.
3. **API & Secret Scans**:
   * Ensure no hardcoded tokens exist in client-side bundles or git history.
   * Verify rate limiting headers and CORS headers are properly restricted.

## Verification Checklist
- [ ] No un-sanitized user strings passed directly into raw execution contexts.
- [ ] PII filter tested with regex patterns for credit cards, phone numbers, and emails.
- [ ] All environment secrets mapped via `pydantic_settings`.
