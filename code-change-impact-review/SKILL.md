---
name: code-change-impact-review
description: Enforce mandatory rationale and impact analysis whenever Codex changes code. Use when requests involve bug fixes, refactors, feature changes, optimizations, or any source edits where the user needs explicit reasons for each change and clear analysis of effects on related logic.
---

# Code Change Impact Review

## Objective

Enforce explanation discipline for all code edits.

Always explain:
1. Why each change is required.
2. How each change affects related logic and behavior.

## Required Workflow

1. Confirm scope and list files that will be changed.
2. Identify related logic before editing.
3. Implement the smallest safe set of edits.
4. Verify behavior with tests or targeted checks when feasible.
5. Report results using the mandatory output structure.

## Impact Scan Checklist

Review these areas for every non-trivial code edit:
- Data flow and state transitions.
- Function/class contracts (inputs, outputs, side effects).
- Call sites and dependent modules.
- Error handling and failure paths.
- Backward compatibility and config assumptions.
- Performance, security, and concurrency risk where relevant.
- Test coverage impact and missing test scenarios.

## Mandatory Output Structure

When code is changed, output must contain all sections below in this order:

### 1. Change Summary
- List each modified file.
- State what changed in one sentence per file.

### 2. Why This Change
- For each file, explain the root reason.
- Tie the reason to the user request, bug cause, or design constraint.

### 3. Impact Analysis
- For each file, describe affected logic/components.
- State expected behavior changes.
- State potential side effects and mitigations.

### 4. Risk and Compatibility
- Note regression risks.
- Note compatibility concerns (API, schema, config, version behavior).

### 5. Validation
- List tests/checks run and outcomes.
- If checks were not run, state why and what remains unverified.

## Guardrails

Never present code edits without rationale and impact analysis.
Never claim "no impact" without checking dependent logic.
Flag assumptions explicitly when repository context is incomplete.
Prefer concise explanations, but do not omit required sections.

## If No Code Was Changed

State explicitly that no source edits were made.
Provide a short explanation-only response without the full mandatory structure.
