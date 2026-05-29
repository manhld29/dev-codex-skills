---
name: gitlab-dual-mr-impact-security-review
description: Compare exactly two GitLab merge requests to detect cross-MR logic impact, behavior conflicts, and critical security risks from a red-team perspective. Use when a user provides two MR IDs and asks whether the MRs affect each other, what resolution to apply, and what severe security issues exist across both changes. By default, fetch MR code from the current repository's GitLab origin remote.
---

# GitLab Dual MR Impact Security Review

## Overview

Execute a structured dual-MR review that answers two questions: (1) do the two MRs impact each other's logic, and (2) do they introduce critical or high security risk. Return findings as clear markdown tables with evidence and concrete resolution guidance.

## Required Inputs

Collect these inputs before analysis:

1. MR ID #1.
2. MR ID #2.
3. Optional risk context: deployment environment, protected assets, auth model.

Authentication and source resolution:

- Read token from `~/.codex/.env` first: `GITLAB_TOKEN=<your_token>`.
- Also support environment variables: `GITLAB_TOKEN`, `GITLAB_PROJECT_ID` (optional override), `GITLAB_URL` (optional override).
- By default, infer project from the current repository `origin` remote (the repo currently opened in Codex).

If either MR cannot be loaded, stop and report the blocker.

## Workflow

1. Fetch both MRs from current project's GitLab.
2. Build a change inventory for each MR.
3. Compare logic impact between MR1 and MR2.
4. Run red-team security analysis on each MR and on combined behavior.
5. Produce final result in the exact output structure below.

## Step 1: Fetch Both MRs (Same Mechanism as gitlab-mr-review)

In PowerShell session:

1. Load Codex env file:
   - `. "$env:USERPROFILE\.codex\skills\gitlab-dual-mr-impact-security-review\scripts\load_codex_env.ps1"`
2. Fetch MR1 context:
   - `python "$env:USERPROFILE\.codex\skills\gitlab-dual-mr-impact-security-review\scripts\fetch_gitlab_mr.py" <MR1_ID> --output mr-<MR1_ID>-context.json`
3. Fetch MR2 context:
   - `python "$env:USERPROFILE\.codex\skills\gitlab-dual-mr-impact-security-review\scripts\fetch_gitlab_mr.py" <MR2_ID> --output mr-<MR2_ID>-context.json`

Behavior requirements:

- Script must auto-detect `project_id` from `git remote get-url origin`.
- Script must auto-load `~/.codex/.env` if `GITLAB_TOKEN` is not already in process env.
- If auto-detection fails, rerun with `--project-id` (and `--gitlab-url` for self-hosted GitLab).

For each MR context, gather:

- Title, author, source branch, target branch, state.
- Full changed file list.
- Unified diffs / patch hunks.

Do not rely only on title/description. Base all findings on code-level evidence.

## Step 2: Build Change Inventory

Map each MR into these buckets:

- Business rules and decision logic.
- Data contracts (request/response schema, DTOs, event payloads).
- Persistence logic (schema migrations, query logic, transaction behavior).
- Security controls (authn/authz, validation, sanitization, secret handling).
- Runtime behavior (feature flags, config, cache, concurrency, retries, timeout).

Use [logic-impact-checklist.md](references/logic-impact-checklist.md) for overlap heuristics.

## Step 3: Analyze Cross-MR Logic Impact

Identify direct and indirect interaction:

- Direct overlap: same file, same symbol, same code path.
- Behavioral overlap: different files but same workflow or invariant.
- Contract overlap: one MR changes producer, the other changes consumer.
- Order-dependent behavior: merge order changes runtime result.

Classify each row:

- `No impact`: independent changes.
- `Soft impact`: compatible but requires coordination.
- `Conflict`: inconsistent logic or likely regression.

For every `Soft impact` or `Conflict`, provide one concrete mitigation:

- Rebase and align implementation.
- Add/adjust guard conditions.
- Update contracts and adapters.
- Add regression tests covering both MR paths.
- Change merge order or split risky commit.

## Step 4: Run Red-Team Security Review

Focus on severe outcomes (Critical/High first):

- Authorization bypass / IDOR.
- Injection risks (SQL/command/template/deserialization).
- SSRF, path traversal, unsafe file handling.
- Secret leakage and sensitive data exposure.
- Broken crypto or insecure defaults.
- Missing validation that enables privilege escalation or code execution.

Also evaluate combined-risk scenarios:

- MR1 introduces new entry point and MR2 weakens validation.
- One MR expands permissions while the other removes checks.

Use [redteam-critical-checklist.md](references/redteam-critical-checklist.md) for severity and exploit framing.

## Output Format (Mandatory)

Return exactly 3 sections in this order.

Language rule (mandatory): Write all findings, tables, summaries, and recommendations in Vietnamese with full diacritics (tiếng Việt có dấu). Keep code, commands, file paths, and identifiers unchanged.

### 1) Cross-MR Logic Impact Table

| Area/Flow | MR1 Change | MR2 Change | Impact Type | Risk | Evidence | Resolution |
|---|---|---|---|---|---|---|

Rules:

- `Impact Type` must be one of: `No impact`, `Soft impact`, `Conflict`.
- `Evidence` must include file path and symbol/function (line number when available).
- `Resolution` must be actionable, not generic.

### 2) Security Findings Table (Red Team)

| Issue | Severity | Affected MR | Evidence | Exploit Scenario | Fix Guidance |
|---|---|---|---|---|---|

Rules:

- Include only validated findings. Do not invent vulnerabilities.
- Prioritize `Critical` and `High`; include `Medium` only if no severe issues found.
- `Fix Guidance` must include specific control changes (validation, authz, encoding, secret rotation, etc.).

### 3) Merge Decision Summary

Provide:

- `Overall verdict`: `Safe to merge`, `Merge with conditions`, or `Block merge`.
- `Blocking items`: bullet list of unresolved `Conflict` or `Critical/High` findings.
- `Suggested merge order`: MR1 -> MR2, MR2 -> MR1, or either.
- `Minimum regression tests`: exact scenarios that must pass before merge.

## Quality Bar

- Write the entire response in Vietnamese with full diacritics (except code/paths/identifiers).
- Cite evidence for every non-trivial claim.
- Separate confirmed finding vs assumption.
- Prefer smallest safe fix that preserves intent.
- If information is insufficient, state `Insufficient evidence` and list what is missing.

