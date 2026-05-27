---
name: pyside6-autotest-generator
description: Generate or extend automation tests for Python PySide6 desktop applications. Use when Codex needs to create test cases for an existing feature by scanning related source code, ensuring the auto_test folder exists, reviewing existing tests, generating a new unittest-based test file, and immediately executing that generated test during implementation.
---

# PySide6 Autotest Generator

## Workflow

1. Identify feature scope.
- Ask for or infer one concrete feature name.
- Convert the feature to a slug for filenames (`test_<feature>.py`).

2. Ensure test workspace exists.
- Run `scripts/ensure_auto_test_dir.py --repo-root <repo_root>`.
- If `auto_test` does not exist, create it.
- If it exists, list existing `test_*.py` files.

3. Discover related code.
- Run `scripts/discover_feature_context.py --feature "<feature>" --repo-root <repo_root>`.
- Read output JSON context.
- Prioritize controller/view/dialog modules and UI automation identifiers.

4. Read existing tests before writing new ones.
- Open the test files listed by `ensure_auto_test_dir.py`.
- Reuse the same setup style and helper imports.
- Avoid duplicating already-covered scenarios.

5. Generate new test skeleton.
- Run `scripts/scaffold_test_case.py --feature "<feature>" --repo-root <repo_root> --context <context_json>`.
- Capture the exact generated file path from script output.
- Keep `unittest` style unless project clearly uses another framework.
- Base class should match project convention (for this repo: `UDSLauncherE2EBase` in `auto_test/base_launcher_test.py`).

6. Mandatory test-run loop while writing.
- After every meaningful edit to the generated test file, run:
`python -m unittest <generated_test_path> -v`
- If test fails due to code/assertion issues, fix the test and rerun immediately.
- Continue loop until either:
  - the test reaches expected state (pass or intentional `skip` with clear TODO), or
  - blocker is external (missing app runtime, credentials, environment dependency).

7. Report execution status.
- Always include the last test command executed.
- Always include result summary: pass, fail, skip, or blocked.
- If blocked, include concrete blocker reason and the exact next command to retry.

## Output Rules

- Always create or update tests under `auto_test/`.
- Name files as `test_<feature_slug>.py` (or indexed suffix when file exists).
- Keep generated code ASCII by default.
- Add short comments only where logic is non-obvious.
- Do not modify unrelated existing tests.
- Do not finish the task without attempting to run the generated test at least once.

## References

- For project-level conventions and review checklist, read:
`references/pyside6_autotest_conventions.md`
