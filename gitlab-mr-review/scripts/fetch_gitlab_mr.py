#!/usr/bin/env python3
"""Fetch GitLab MR metadata and diffs, then map added lines for precise review locations."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
SCP_REMOTE_RE = re.compile(r"^(?:.+@)?([^:]+):(.+)$")


def get_env_or_arg(value: str | None, env_name: str, arg_name: str) -> str:
    if value:
        return value
    env_value = os.getenv(env_name)
    if env_value:
        return env_value
    raise ValueError(f"Missing {env_name}. Provide --{arg_name} or set env var.")


def codex_home_dir() -> pathlib.Path:
    custom = os.getenv("CODEX_HOME")
    if custom:
        return pathlib.Path(custom).expanduser()
    return pathlib.Path.home() / ".codex"


def load_env_file(env_path: pathlib.Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_path.is_file():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.lower().startswith("export "):
            line = line[7:].strip()

        if "=" not in line:
            continue

        key, raw_val = line.split("=", 1)
        key = key.strip()
        val = raw_val.strip()

        if not key:
            continue

        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]

        values[key] = val
    return values


def load_codex_env_into_process() -> None:
    env_file = codex_home_dir() / ".env"
    if not env_file.is_file():
        return

    values = load_env_file(env_file)
    for key, val in values.items():
        if key and not os.getenv(key):
            os.environ[key] = val


def run_git(args: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ValueError("git is not available in PATH, cannot auto-detect project from current repository.") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        detail = f" ({stderr})" if stderr else ""
        raise ValueError(f"Failed to run git {' '.join(args)}{detail}") from exc
    return proc.stdout.strip()


def parse_remote(remote_url: str) -> tuple[str, str] | None:
    url = remote_url.strip()
    if not url:
        return None

    if "://" in url:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https", "ssh"}:
            return None

        host = parsed.hostname
        project_path = parsed.path.lstrip("/")
        if project_path.endswith(".git"):
            project_path = project_path[:-4]
        if not host or not project_path:
            return None

        # GitLab HTTP API is typically exposed via HTTPS even when cloning over SSH.
        api_scheme = parsed.scheme if parsed.scheme in {"http", "https"} else "https"
        port = f":{parsed.port}" if parsed.port else ""
        return f"{api_scheme}://{host}{port}", project_path

    scp_match = SCP_REMOTE_RE.match(url)
    if scp_match:
        host, project_path = scp_match.groups()
        if project_path.endswith(".git"):
            project_path = project_path[:-4]
        if host and project_path:
            return f"https://{host}", project_path

    return None


def detect_project_from_git_remote() -> tuple[str, str]:
    remote_url = run_git(["remote", "get-url", "origin"])
    parsed = parse_remote(remote_url)
    if not parsed:
        raise ValueError(
            "Cannot parse git origin remote as a GitLab project. "
            "Provide --project-id and optionally --gitlab-url."
        )
    return parsed


def api_get(base_url: str, token: str, path: str, query: dict[str, Any] | None = None) -> tuple[Any, dict[str, str]]:
    base = base_url.rstrip("/")
    url = f"{base}/api/v4{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"

    req = urllib.request.Request(url)
    req.add_header("PRIVATE-TOKEN", token)
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = resp.read().decode("utf-8")
            headers = {k: v for k, v in resp.headers.items()}
            return json.loads(payload), headers
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitLab API error {exc.code} at {url}: {message}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error calling {url}: {exc}") from exc


def fetch_all_diffs(base_url: str, token: str, project_id: str, mr_iid: int) -> list[dict[str, Any]]:
    diffs: list[dict[str, Any]] = []
    page = 1
    while True:
        data, headers = api_get(
            base_url,
            token,
            f"/projects/{urllib.parse.quote(project_id, safe='')}/merge_requests/{mr_iid}/diffs",
            {"per_page": 100, "page": page},
        )
        if not isinstance(data, list):
            raise RuntimeError("Unexpected response for MR diffs endpoint.")
        diffs.extend(data)

        next_page = headers.get("X-Next-Page", "")
        if not next_page:
            break
        page = int(next_page)
    return diffs


def extract_added_lines(diff_text: str) -> list[dict[str, Any]]:
    added: list[dict[str, Any]] = []
    current_new_line: int | None = None

    for raw_line in diff_text.splitlines():
        hunk_match = HUNK_RE.match(raw_line)
        if hunk_match:
            current_new_line = int(hunk_match.group(1))
            continue

        if current_new_line is None:
            continue

        if raw_line.startswith("+++") or raw_line.startswith("---"):
            continue

        if raw_line.startswith("+"):
            added.append({"line": current_new_line, "content": raw_line[1:]})
            current_new_line += 1
            continue

        if raw_line.startswith("-"):
            continue

        if raw_line.startswith("\\"):
            continue

        current_new_line += 1

    return added


def build_context(base_url: str, token: str, project_id: str, mr_iid: int) -> dict[str, Any]:
    encoded_project = urllib.parse.quote(project_id, safe="")
    mr, _ = api_get(base_url, token, f"/projects/{encoded_project}/merge_requests/{mr_iid}")
    diffs = fetch_all_diffs(base_url, token, project_id, mr_iid)

    files: list[dict[str, Any]] = []
    total_added_lines = 0

    for diff in diffs:
        diff_text = diff.get("diff", "") or ""
        added_lines = extract_added_lines(diff_text)
        total_added_lines += len(added_lines)

        files.append(
            {
                "old_path": diff.get("old_path"),
                "new_path": diff.get("new_path"),
                "new_file": bool(diff.get("new_file")),
                "renamed_file": bool(diff.get("renamed_file")),
                "deleted_file": bool(diff.get("deleted_file")),
                "too_large": bool(diff.get("too_large")),
                "added_lines": added_lines,
                "diff": diff_text,
            }
        )

    return {
        "source": "gitlab-api-v4",
        "project_id": project_id,
        "merge_request": {
            "iid": mr.get("iid"),
            "id": mr.get("id"),
            "title": mr.get("title"),
            "description": mr.get("description"),
            "state": mr.get("state"),
            "web_url": mr.get("web_url"),
            "source_branch": mr.get("source_branch"),
            "target_branch": mr.get("target_branch"),
            "author": (mr.get("author") or {}).get("username"),
            "sha": mr.get("sha"),
        },
        "summary": {
            "changed_files": len(files),
            "added_line_entries": total_added_lines,
        },
        "files": files,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch GitLab MR context for code review.")
    parser.add_argument("mr_iid", type=int, help="GitLab merge request IID")
    parser.add_argument("--project-id", help="GitLab project id or URL-encoded path")
    parser.add_argument("--gitlab-url", help="GitLab base URL, e.g. https://gitlab.com")
    parser.add_argument("--token", help="GitLab private token")
    parser.add_argument("--output", help="Output JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    load_codex_env_into_process()

    try:
        detected_gitlab_url: str | None = None
        if args.project_id:
            project_id = args.project_id
        elif os.getenv("GITLAB_PROJECT_ID"):
            project_id = get_env_or_arg(None, "GITLAB_PROJECT_ID", "project-id")
        else:
            detected_gitlab_url, project_id = detect_project_from_git_remote()

        if args.gitlab_url:
            gitlab_url = args.gitlab_url
        elif os.getenv("GITLAB_URL"):
            gitlab_url = get_env_or_arg(None, "GITLAB_URL", "gitlab-url")
        elif detected_gitlab_url:
            gitlab_url = detected_gitlab_url
        else:
            gitlab_url = "https://gitlab.com"

        token = get_env_or_arg(args.token, "GITLAB_TOKEN", "token")
        if token in {"replace_with_your_gitlab_pat", "<your_token>", "your_token_here"}:
            raise ValueError("GITLAB_TOKEN is still a placeholder. Update ~/.codex/.env with a real token.")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    output_path = args.output or f"mr-{args.mr_iid}-context.json"

    try:
        context = build_context(gitlab_url, token, project_id, args.mr_iid)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(context, handle, ensure_ascii=False, indent=2)

    print(f"Saved MR context to: {output_path}")
    print(f"Changed files: {context['summary']['changed_files']}")
    print(f"Added-line entries: {context['summary']['added_line_entries']}")
    print(f"Project: {context['project_id']}")
    print(f"MR URL: {context['merge_request']['web_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
