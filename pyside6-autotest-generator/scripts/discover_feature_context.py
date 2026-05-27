#!/usr/bin/env python3
"""Discover source context related to a feature for PySide6 UI tests."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

CODE_SUFFIXES = {".py", ".ui", ".qss", ".json"}
STOPWORDS = {
    "a",
    "an",
    "and",
    "app",
    "button",
    "click",
    "dialog",
    "feature",
    "for",
    "from",
    "in",
    "list",
    "menu",
    "on",
    "or",
    "screen",
    "the",
    "to",
    "ui",
    "view",
}
EXCLUDED_PATH_PARTS = {
    "__pycache__",
    ".git",
    "build",
    "dist",
    "venv",
    "site-packages",
    "exe.win-amd64-3.12",
}
KEYWORD_HINTS = (
    "btn",
    "button",
    "action",
    "input",
    "edit",
    "dialog",
    "window",
    "menu",
    "card",
    "table",
    "list",
)
KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
LITERAL_RE = re.compile(r"['\"]([A-Za-z0-9_.:-]{3,48})['\"]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find related source files and UI keys for a feature.",
    )
    parser.add_argument("--feature", required=True, help="Feature name to analyze")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--src-dir", default="src", help="Source directory relative to repo root")
    parser.add_argument("--max-files", type=int, default=12, help="Max related files in output")
    parser.add_argument(
        "--output",
        default="",
        help="Optional output JSON path. Default: auto_test/generated_<feature>_context.json",
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "feature"


def tokenize(feature: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", feature.lower())
    return [tok for tok in tokens if tok not in STOPWORDS and len(tok) >= 2]


def is_excluded(path: Path) -> bool:
    lowered = {part.lower() for part in path.parts}
    return any(part in lowered for part in EXCLUDED_PATH_PARTS)


def iter_source_files(src_root: Path) -> Iterable[Path]:
    if not src_root.exists():
        return []
    files = []
    for path in src_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in CODE_SUFFIXES:
            continue
        if is_excluded(path):
            continue
        files.append(path)
    return files


def score_file(path: Path, text: str, feature: str, tokens: list[str]) -> int:
    score = 0
    feature_lower = feature.lower()
    text_lower = text.lower()
    path_lower = str(path).lower()

    if feature_lower in path_lower:
        score += 10
    if feature_lower in text_lower:
        score += 8

    for tok in tokens:
        if tok in path_lower:
            score += 4
        count = text_lower.count(tok)
        if count:
            score += min(6, count)

    for marker in ("controller", "dialog", "views", "pyside6", "btn", "action"):
        if marker in path_lower:
            score += 1

    return score


def _is_probable_ui_key(candidate: str) -> bool:
    lower = candidate.lower()
    if len(candidate) > 48:
        return False
    if candidate.isupper() and len(candidate) > 8:
        return False
    return any(hint in lower for hint in KEYWORD_HINTS)


def extract_keys(text: str) -> list[str]:
    keys = set()
    for token in KEY_RE.findall(text):
        if _is_probable_ui_key(token):
            keys.add(token)
    for literal in LITERAL_RE.findall(text):
        if _is_probable_ui_key(literal):
            keys.add(literal)

    filtered = sorted(key for key in keys if key.lower() not in STOPWORDS)
    return filtered[:40]


def existing_tests(repo_root: Path, tokens: list[str]) -> list[str]:
    auto_test_dir = repo_root / "auto_test"
    if not auto_test_dir.exists():
        return []

    tests = []
    for test_file in auto_test_dir.glob("test_*.py"):
        test_name = test_file.name.lower()
        if not tokens or any(tok in test_name for tok in tokens):
            tests.append(str(test_file.relative_to(repo_root)).replace("\\", "/"))
    return sorted(tests)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    src_root = (repo_root / args.src_dir).resolve()
    feature = args.feature.strip()
    tokens = tokenize(feature)

    scored = []
    all_keys = set()
    for src_file in iter_source_files(src_root):
        text = read_text(src_file)
        if not text:
            continue
        score = score_file(src_file, text, feature, tokens)
        if score <= 0:
            continue

        file_keys = extract_keys(text)
        for key in file_keys[:16]:
            all_keys.add(key)

        scored.append((score, src_file))

    scored.sort(key=lambda item: item[0], reverse=True)
    related_files = [
        str(path.relative_to(repo_root)).replace("\\", "/")
        for _, path in scored[: max(1, args.max_files)]
    ]

    context = {
        "feature": feature,
        "feature_slug": slugify(feature),
        "tokens": tokens,
        "related_files": related_files,
        "ui_keys": sorted(all_keys)[:40],
        "existing_tests": existing_tests(repo_root, tokens),
    }

    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_dir = repo_root / "auto_test"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"generated_{context['feature_slug']}_context.json"

    output_path.write_text(json.dumps(context, indent=2), encoding="utf-8")

    print(json.dumps(context, indent=2))
    print(f"\nContext written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
