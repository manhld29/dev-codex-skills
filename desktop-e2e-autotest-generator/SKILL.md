---
name: desktop-e2e-autotest-generator
description: Generate end-to-end desktop automation tests in Python from a feature goal plus app launch target. Use when Codex needs to turn manual test ideas into concrete test cases and runnable unittest-based E2E code for Windows desktop apps launched by .exe path or python file command.
---

# Desktop E2E Autotest Generator

## Workflow

1. Collect required inputs.
- Require one feature goal sentence.
- Require one launch target string.
- Accept either `.exe` path (optionally with args) or command like `python file.py`.
- Accept optional source paths for controller/view files to improve selectors and assertions.

2. Generate test cases and initial E2E code.
- Run:
`python <skill_path>/scripts/generate_desktop_e2e.py --feature-goal "<goal>" --launch-target "<launch_target>" --repo-root <repo_root> [--source-path <path> ...]`
- Read script output to capture generated files:
  - `auto_test/testcases_<feature_slug>.md`
  - `auto_test/test_<feature_slug>_e2e.py`

3. Refine generated test code with app-specific selectors.
- Open optional source files if provided.
- Replace placeholder TODO blocks with real selectors (`title`, `auto_id`, `control_type`) and real assertions.
- Keep `unittest` style unless project already enforces another framework.

4. Run generated E2E test immediately.
- Run:
`python -m unittest <generated_test_path> -v`
- If the app or environment is unavailable, mark status as blocked with exact reason.

5. Report result with strict status.
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

- Always generate artifacts under `auto_test/` inside the current repo.
- Keep all generated files ASCII by default.
- Do not modify unrelated test files.
- Do not finish without attempting at least one test execution command.

## References

- Read selector and stability guidance in:
`references/desktop_e2e_conventions.md`
