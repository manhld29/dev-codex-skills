# Red Team Critical Checklist

Use this checklist to assess severe security impact for each MR and their combined behavior.

## Priority 1: Critical/High Classes

- Broken access control / IDOR / privilege escalation.
- Injection: SQL, command, template, unsafe eval, unsafe deserialization.
- SSRF with internal network reachability.
- Path traversal and unsafe file read/write.
- Secret exposure (hardcoded keys, logs, responses, client bundles).
- Insecure crypto defaults (weak algorithm, disabled verification, static IV/key).

## Priority 2: High-Likelihood Abuse Enablers

- Missing server-side validation for trust boundaries.
- Missing ownership checks on update/delete/read endpoints.
- File upload without type/content checks and storage isolation.
- Dangerous debug/admin flags enabled by default.

## Evidence Requirements

Each finding must include:

1. Exact file and function/symbol.
2. Why the control is bypassable.
3. Realistic exploit path.
4. Expected impact (data leak, account takeover, RCE, etc.).

## Severity Calibration

- Critical: immediate severe compromise with low complexity exploit.
- High: serious compromise with realistic exploit preconditions.
- Medium: notable weakness but constrained impact or harder exploit.

## Fix Guidance Patterns

- Enforce authz at object/resource boundary.
- Parameterize queries and remove shell concatenation.
- Apply strict allowlist validation and output encoding.
- Rotate exposed secrets and remove from logs/history.
- Harden crypto and transport verification.
- Add abuse-focused tests for exploit path.

## Combined-Risk Prompts

- Does MR1 open a new surface that MR2 fails to protect?
- Does one MR remove controls while the other expands reach?
- Could merge order create a temporary vulnerable state?
