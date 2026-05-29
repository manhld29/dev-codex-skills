---
name: gitlab-mr-review
description: Review GitLab merge requests by MR ID with senior-level rigor (15+ years mindset), including coding convention checks, security checks, regression risk analysis, and cross-logic impact analysis. Use when the user asks to review a GitLab MR and wants findings with exact file/line locations in structured tables, clickable code links, and reproducible impact scenarios.
---

# GitLab MR Review

Review as a senior engineer with 15 years of experience: strict on correctness, practical on risk, and explicit on system-wide impact.

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
2. Read review criteria:
   - Load `references/review-checklist.md`.
3. Perform senior review:
   - Review changed lines first, then surrounding code paths.
   - Prioritize correctness, security, and behavioral regressions.
   - Evaluate impact on related logic/modules, API contracts, side effects, and downstream flows.
4. Report findings in Vietnamese with exact location:
   - Always include `path:line`.
   - Include severity (`high`, `medium`, `low`) and category (`security`, `correctness`, `convention`, `test-gap`, `impact`).
   - Write Vietnamese with proper diacritics (tiếng Việt có dấu).
5. For each impacted logic case:
   - Provide a reproducible scenario with step-by-step test instructions.
6. Close with risk summary:
   - Count findings by severity.
   - List affected modules/flows.
   - List required follow-up tests.

## Output Format

### 1) Bảng vấn đề chính (bắt buộc)

| STT | Mức độ | Nhóm | Vị trí | Hàm/đoạn code liên quan | Vấn đề | Logic khác bị ảnh hưởng? | Ảnh hưởng như thế nào | Bằng chứng | Khuyến nghị |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Rules:

- Viết toàn bộ nội dung bằng tiếng Việt có dấu.
- `Vị trí` phải là `path:line` và ở dạng link có thể click.
- Mọi file/hàm/đoạn code được nhắc đến đều phải có link click mở file.
- Dùng format link: `[nhãn](/đường/dẫn/tuyệt/đối/tới/file.py:line)`.
- `Logic khác bị ảnh hưởng?` chỉ nhận `Có` hoặc `Không`.
- `Ảnh hưởng như thế nào` phải mô tả cụ thể module/flow nào bị tác động và cơ chế tác động.
- `Bằng chứng` phải trỏ tới diff hoặc dòng code liên quan bằng link click.

### 2) Bảng kịch bản tái hiện ảnh hưởng logic (bắt buộc khi có `Có`)

| STT | Logic bị ảnh hưởng | Mục tiêu test | Tiền điều kiện | Các bước tái hiện | Kết quả kỳ vọng | Kết quả có thể gặp/rủi ro | Gợi ý tự động hóa test |
| --- | --- | --- | --- | --- | --- | --- | --- |

Rules:

- `Các bước tái hiện` phải là chuỗi bước rõ ràng (Bước 1, Bước 2, ...).
- Nếu có thể, thêm lệnh test cụ thể (ví dụ `pytest`, `go test`, script nội bộ).
- Mỗi logic bị ảnh hưởng trong bảng vấn đề phải có ít nhất một kịch bản tái hiện tương ứng.

### 3) Tổng kết rủi ro

- Tổng số lỗi theo mức độ (`high/medium/low`).
- Luồng có rủi ro cao nhất.
- Danh sách test bắt buộc chạy.
- Dòng bắt buộc: `Đánh giá ảnh hưởng logic liên quan: Có/Không` và giải thích ngắn gọn.

### 4) Trường hợp không có vấn đề

- Ghi rõ: `Không có phát hiện cần hành động`.
- Vẫn phải nêu rủi ro tồn dư và test cần chạy.

## Boundaries

- Do not invent file paths or line numbers.
- Do not claim a vulnerability without explaining exploitability or unsafe behavior.
- Do not block MR for style-only issues unless they affect maintainability or correctness.