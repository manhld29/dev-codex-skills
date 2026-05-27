# PySide6 Autotest Conventions

## Existing Project Pattern

- Test framework: `unittest`
- Main location: `auto_test/`
- Base class pattern: inherit from `UDSLauncherE2EBase`
- Typical helpers: `wait_until`, `click_when_ready`
- Execution command:
`python -m unittest auto_test/test_<feature>.py -v`

## Generated Test Requirements

1. Import from `auto_test.base_launcher_test` when present.
2. Keep each generated file self-contained and runnable with unittest.
3. Prefer 3 default test methods:
- screen readiness
- control visibility
- primary flow placeholder (skip with TODO if behavior unclear)
4. Include metadata comment with related files used for generation.
5. Keep selectors resilient:
- first try automation id
- fallback to visible text

## Scenario Design Checklist

- Happy path with expected UI transition
- At least one negative or guard-path assertion
- Preconditions explicit (login state, list populated, etc.)
- Assertion is deterministic (avoid pure sleep)

## Safe Update Rules

- Do not edit unrelated existing test files.
- If target test file already exists, create a new indexed filename.
- Preserve manual test logic already written by users.
