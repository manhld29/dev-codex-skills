# Review Checklist

Use this checklist while reviewing a GitLab merge request.

Review posture: act as a senior engineer with 15 years of practical delivery and incident-response experience.

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

## 5) Cross-Logic Impact Analysis

- Identify upstream inputs that can alter behavior in the changed code paths.
- Identify downstream consumers that depend on changed outputs, events, or side effects.
- Check contract compatibility for function signatures, API payload keys, and return semantics.
- Check lifecycle impacts: retries, rollback, state transitions, and cleanup behavior.
- Check concurrent/runtime impacts: locks, races, shared state, and timeout cascades.
- Explicitly map each finding to at least one impacted module/flow when applicable.

## 6) Clickable Evidence Requirement

- Every mentioned file must have a clickable link.
- Every mentioned function or code block must include a clickable link to its nearest definition/use line.
- Use format: `[label](/absolute/path/to/file.ext:line)`.
- Do not report findings without at least one clickable evidence link.

## 7) Reproduction Scenario Requirement

For each finding where `Logic khác bị ảnh hưởng? = Có`:

- Provide at least one step-by-step reproduction scenario.
- Include preconditions, test steps, expected result, and likely actual/risk result.
- Provide executable test command when possible (`pytest`, `go test`, local script, curl, etc.).

## 8) Finding Quality Gate

Before reporting a finding, ensure:

- The finding points to a specific changed file and line.
- The reasoning ties behavior to concrete risk.
- The impact on related logic/flows is clearly explained.
- State explicitly whether related project logic is impacted (`Có`/`Không`) and explain why.
- The recommendation is minimal and implementable.
- Use Vietnamese with proper diacritics in the final review output.