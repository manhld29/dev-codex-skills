# GitLab Dual MR Impact & Security Review

## Muc tieu

Skill nay review dong thoi 2 Merge Request (MR) tren GitLab theo 2 huong:

1. So sanh anh huong logic cheo giua 2 MR.
2. Phat hien van de security nghiem trong theo goc nhin red team.

Dau ra bat buoc la cac bang ket qua ro rang, co bang chung va huong xu ly cu the.

## Duong dan skill

`C:\Users\ManhLD31\.codex\skills\gitlab-dual-mr-impact-security-review`

## Co che lay code MR (da dong bo voi gitlab-mr-review)

Skill lay thong tin MR tu GitLab cua project hien tai (repo dang mo trong Codex):

- Tu dong suy ra project tu `git remote get-url origin`.
- Doc token tu `~/.codex/.env` (bien `GITLAB_TOKEN`) hoac tu environment variable.
- Ho tro override bang `GITLAB_PROJECT_ID` va `GITLAB_URL` khi can.

## Input bat buoc

- MR ID thu nhat.
- MR ID thu hai.

Khuyen nghi them:

- Moi truong deploy (dev/staging/prod).
- Tai san can bao ve (PII, token, payment data...).
- Mo hinh authn/authz hien tai.

## Chuan bi token

Them vao file `~/.codex/.env`:

```text
GITLAB_TOKEN=<your_real_pat>
```

Co the them khi can:

```text
GITLAB_PROJECT_ID=<project_id_or_group%2Frepo>
GITLAB_URL=https://gitlab.example.com
```

## Lenh fetch 2 MR

Trong PowerShell:

```powershell
. "$env:USERPROFILE\.codex\skills\gitlab-dual-mr-impact-security-review\scripts\load_codex_env.ps1"
python "$env:USERPROFILE\.codex\skills\gitlab-dual-mr-impact-security-review\scripts\fetch_gitlab_mr.py" <MR1_ID> --output mr-<MR1_ID>-context.json
python "$env:USERPROFILE\.codex\skills\gitlab-dual-mr-impact-security-review\scripts\fetch_gitlab_mr.py" <MR2_ID> --output mr-<MR2_ID>-context.json
```

Neu auto-detect project that bai, chay lai voi override:

```powershell
python "$env:USERPROFILE\.codex\skills\gitlab-dual-mr-impact-security-review\scripts\fetch_gitlab_mr.py" <MR_ID> --project-id <project> --gitlab-url <url>
```

## Cach goi skill

Vi du prompt:

```text
Dung skill gitlab-dual-mr-impact-security-review de review 2 MR sau:
MR1: 125
MR2: 131
Yeu cau: kiem tra anh huong logic cheo + security nghiem trong, tra ket qua dang bang.
```

## Dinh dang output bat buoc

**Yêu cầu ngôn ngữ (bắt buộc):** Tất cả kết quả phải trả về bằng tiếng Việt có dấu, bao gồm toàn bộ nội dung trong bảng và phần tổng kết.

### 1) Cross-MR Logic Impact Table

| Area/Flow | MR1 Change | MR2 Change | Impact Type | Risk | Evidence | Resolution |
|---|---|---|---|---|---|---|

### 2) Security Findings Table (Red Team)

| Issue | Severity | Affected MR | Evidence | Exploit Scenario | Fix Guidance |
|---|---|---|---|---|---|

### 3) Merge Decision Summary

Gom:

- `Overall verdict`: `Safe to merge` / `Merge with conditions` / `Block merge`
- `Blocking items`
- `Suggested merge order`
- `Minimum regression tests`

## Tai lieu tham chieu kem theo

- `references/logic-impact-checklist.md`
- `references/redteam-critical-checklist.md`

