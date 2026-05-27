# Review Checklist

Use this checklist while reviewing a GitLab merge request.

## 1) Correctness and Regression

- Verify null/None handling, error paths, and timeout/retry behavior.
- Verify loop boundaries, off-by-one risks, and pagination behavior.
- Verify backward compatibility for public interfaces and payload schema.
- Verify side effects (file I/O, DB writes, external API calls) are safe and intentional.

## 2) Coding Convention

- Naming consistency: variables/functions/classes follow project conventions.
- Function size and cohesion: avoid multi-purpose functions with hidden side effects.
- Error messages and logs: clear, actionable, and no sensitive data leakage.
- Duplicated logic: suggest extraction only when duplication creates risk.
- Tests: new behavior should include or update targeted tests.

## 3) Security Checks

- Injection risks: SQL, shell, template, or command construction from untrusted input.
- Broken authz/authn: missing permission checks, weak token handling, privilege escalation.
- Secrets exposure: API keys, tokens, private keys, or credentials in code/logs.
- Insecure crypto: weak algorithms, disabled verification, custom crypto misuse.
- Path traversal / file abuse: unvalidated paths, unsafe temp files, symlink issues.
- Deserialization/SSRF/open redirect: unsafe URL fetches and trust-boundary violations.
- DoS vectors: unbounded loops, regex backtracking, large payload handling without limits.

## 4) Severity Guidance

- High: exploitable security issue, data loss/corruption, auth bypass, major outage risk.
- Medium: clear bug or security weakness with realistic impact.
- Low: maintainability issue, minor convention drift, weak test coverage.

## 5) Finding Quality Gate

Before reporting a finding, ensure:

- The finding points to a specific changed file and line.
- The reasoning ties behavior to concrete risk.
- The recommendation is minimal and implementable.
