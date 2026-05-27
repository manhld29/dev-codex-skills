# Desktop E2E Conventions

## Selector Strategy

1. Prefer stable selectors in this order:
- `auto_id`
- `title`
- `control_type`
- index-based fallback only when unavoidable

2. Keep selectors centralized.
- Store repeated selectors as constants near the top of the generated test file.
- Use helper methods for repeated navigation flows.

## Assertion Strategy

1. Cover at least these baseline checks:
- App process starts.
- Main window becomes visible and ready.
- Feature entry flow is reachable.
- Feature action returns expected UI state.
- App can close cleanly.

2. Make assertions observable.
- Assert on visible UI text/state changes.
- Avoid only asserting no exception.

## Flakiness Control

1. Replace fixed sleeps with waits when possible.
- Use `window.wait("visible ready", timeout=...)`.
- Use retry loops for delayed controls.

2. Keep teardown safe.
- Try graceful close first.
- Fallback to process terminate.

## Blocking Conditions

Report `blocked` if any of the following is true:
- Launch target is invalid.
- Runtime dependencies for the desktop app are missing.
- Test machine cannot display GUI session.
- Automation library is unavailable and cannot be installed in this run.
