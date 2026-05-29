---
name: desktop-e2e-autotest-generator
description: Generate end-to-end desktop automation tests in Python from a feature goal plus app launch target. Use when Codex needs to export generated test cases into CSV under test_case, create runnable unittest E2E code, and write execution result back to each testcase row.
---

# Desktop E2E Autotest Generator

## Workflow

1. Collect required inputs.
- Require one feature goal sentence.
- Require one launch target string.
- Accept either `.exe` path (optionally with args) or command like `python file.py`.
- Accept optional source paths for controller/view files to improve selectors and assertions.

2. Generate testcase CSV and initial E2E code.
- Run:
`python <skill_path>/scripts/generate_desktop_e2e.py --feature-goal "<goal>" --launch-target "<launch_target>" --repo-root <repo_root> [--source-path <path> ...]`
- Read script output to capture generated files:
  - `test_case/testcases_<feature_slug>.csv`
  - `auto_test/test_<feature_slug>_e2e.py`

3. Ensure generated test reads CSV and writes result per testcase row.
- Keep CSV columns: `tc_id,title,precondition,steps,expected,result,actual`.
- Keep each test method name prefixed by `test_tcXX_...` so result mapping by `tc_id` stays deterministic.
- Ensure pass/fail/error/skip status is written to the matching `tc_id` row.

4. Refine generated test code with app-specific selectors.
- Open optional source files if provided.
- Replace placeholder TODO blocks with real selectors (`title`, `auto_id`, `control_type`) and real assertions.
- Keep `unittest` style unless project already enforces another framework.

5. Run generated E2E test immediately.
- Run:
`python -m unittest <generated_test_path> -v`
- If the app or environment is unavailable, mark status as blocked with exact reason.

6. Report result with strict status.
- Always report:
  - Feature goal
  - Launch target
  - Generated files
  - Last test command
  - Status: pass, fail, skip, or blocked

## Input Contract

Use this exact input shape in user prompt whenever possible:

```text
feature_goal: <what the function should achieve>
launch_target: <C:\path\app.exe | python path\to\main.py>
source_paths: <optional comma-separated code paths>
```

## Output Rules

- Always generate testcase CSV under `test_case/` inside the current repo.
- Always generate E2E code under `auto_test/` inside the current repo.
- Keep all generated files ASCII by default.
- Do not modify unrelated test files.
- Do not finish without attempting at least one test execution command.

## References

- Read selector, stability, and testcase result tracking guidance in:
`references/desktop_e2e_conventions.md`