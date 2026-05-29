# Logic Impact Checklist

Use this checklist to detect whether MR1 and MR2 affect each other.

## 1) Direct Code Overlap

- Same file edited by both MRs.
- Same class/function edited by both MRs.
- Same condition branch changed in both MRs.

## 2) Data/Contract Overlap

- API request or response field renamed/removed/required.
- Event payload shape changed.
- DB schema changed while dependent query/service remains old.

## 3) Behavioral Overlap

- Validation rules differ for same user flow.
- State machine transitions changed differently.
- Error handling changed in one MR but caller assumptions unchanged.

## 4) Operational Overlap

- Feature flag default differs.
- Cache key/TTL semantics diverge.
- Retry/timeout policy mismatch causes hidden failures.

## 5) Merge-Order Risk

- MR1 merged first breaks MR2 branch assumptions.
- MR2 merged first creates temporary production regression.

## Classification Guide

- No impact: no shared flow, no contract dependency, no order risk.
- Soft impact: compatible but coordination and tests are required.
- Conflict: inconsistent logic/contract or likely regression without fix.

## Resolution Patterns

- Rebase and reconcile overlapping hunks.
- Add compatibility layer (adapter, fallback field, dual-write/read).
- Update test coverage for both execution paths.
- Sequence merges with temporary safeguards.
