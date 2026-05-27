#!/usr/bin/env python3
"""Ensure auto_test directory exists and list existing tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ensure auto_test exists and return current test files.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path (default: current directory)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    auto_test_dir = repo_root / "auto_test"

    created = False
    if not auto_test_dir.exists():
        auto_test_dir.mkdir(parents=True, exist_ok=True)
        created = True

    tests = sorted(
        str(path.relative_to(repo_root)).replace("\\", "/")
        for path in auto_test_dir.glob("test_*.py")
        if path.is_file()
    )

    result = {
        "repo_root": str(repo_root),
        "auto_test_dir": str(auto_test_dir),
        "created": created,
        "existing_tests": tests,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
