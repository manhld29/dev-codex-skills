---
name: gitlab-mr-review
description: Review GitLab merge requests by MR ID with a structured code-review workflow that checks coding convention, security risks, and behavioral regressions. Use when the user asks to review a GitLab MR, audit a merge request for vulnerabilities, or produce findings with exact file/line locations.
---

# GitLab MR Review

Execute a consistent MR review from GitLab API data and report actionable findings.

## Inputs

- Require `MR ID` (`iid`) from user.
- Read token from `~/.codex/.env` first:
  - `GITLAB_TOKEN=<your_token>` (replace placeholder value with real PAT before review)
- Also support environment variables:
  - `GITLAB_TOKEN`: Personal Access Token with API read access.
  - `GITLAB_PROJECT_ID` (optional override): Numeric project id or URL-encoded path (`group%2Fproject`).
  - `GITLAB_URL` (optional override): GitLab base URL.
- By default, infer project from the current repository `origin` remote (the repo currently opened in Codex).

## Workflow

1. Fetch MR context and diffs:
   - In PowerShell session, load `~/.codex/.env`:
     - `. "$env:USERPROFILE\.codex\skills\gitlab-mr-review\scripts\load_codex_env.ps1"`
   - Run:
     - `python "$env:USERPROFILE\.codex\skills\gitlab-mr-review\scripts\fetch_gitlab_mr.py" <MR_ID> --output mr-<MR_ID>-context.json`
   - Script auto-detects `project_id` from `git remote get-url origin`.
   - Script also auto-loads `~/.codex/.env` as fallback when `GITLAB_TOKEN` is not already in process env.
   - If auto-detection fails, provide `--project-id` (and `--gitlab-url` for self-hosted GitLab).
   - If the script fails because a variable is missing, ask for the missing value and retry.
2. Read review criteria:
   - Load `references/review-checklist.md`.
3. Review only changed lines first, then nearby context as needed:
   - Prioritize correctness regressions and security vulnerabilities.
   - Flag convention issues only when they are concrete and actionable.
4. Produce findings with exact locations:
   - Always include `file` and `line` in `path:line` format.
   - Include severity (`high`, `medium`, `low`) and category (`security`, `correctness`, `convention`, `test-gap`).
   - Write the full review result in Vietnamese.
5. Close with risk summary:
   - Count findings by severity.
   - List required follow-up tests.

## Output Format

Return findings first in this shape:

- `[severity][category] path:line - short title`
- `Impact:` one sentence.
- `Evidence:` code-level observation from diff/context.
- `Recommendation:` concrete change.

Use Vietnamese labels in final response:

- `Tác động:` for impact.
- `Bằng chứng:` for evidence.
- `Khuyến nghị:` for recommendation.

If no issues are found, explicitly state `Không có phát hiện cần hành động` and still include residual risks (for example, missing tests or unreviewed runtime paths).

## Boundaries

- Do not invent file paths or line numbers.
- Do not claim a vulnerability without explaining exploitability or unsafe behavior.
- Do not block MR for style-only issues unless they affect maintainability or correctness.
