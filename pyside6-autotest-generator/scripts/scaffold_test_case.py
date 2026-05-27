#!/usr/bin/env python3
"""Scaffold a new unittest file for a PySide6 feature."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate test_<feature>.py inside auto_test.",
    )
    parser.add_argument("--feature", required=True, help="Feature name")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--context", default="", help="Path to context JSON from discover script")
    return parser.parse_args()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "feature"


def to_class_name(slug: str) -> str:
    return "Test" + "".join(part.capitalize() for part in slug.split("_"))


def pick_output_file(auto_test_dir: Path, slug: str) -> Path:
    base = auto_test_dir / f"test_{slug}.py"
    if not base.exists():
        return base

    idx = 2
    while True:
        candidate = auto_test_dir / f"test_{slug}_{idx}.py"
        if not candidate.exists():
            return candidate
        idx += 1


def load_context(path: str) -> dict:
    if not path:
        return {}
    context_path = Path(path).resolve()
    if not context_path.exists():
        return {}
    try:
        return json.loads(context_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def render_test(feature: str, slug: str, class_name: str, related_files: list[str], ui_keys: list[str]) -> str:
    related_block = "\n".join(f"# - {file}" for file in related_files) or "# - (not detected)"
    keys_repr = ", ".join(repr(key) for key in ui_keys[:12])
    keys_repr = f"[{keys_repr}]" if keys_repr else "[]"

    return f'''"""
Auto-generated test skeleton for feature: {feature}
Related source files detected:
{related_block}
"""

import unittest

from auto_test.base_launcher_test import (
    UDSLauncherE2EBase,
    wait_until,
)


def _find_first_control_contains(main_window, control_type: str, keyword: str):
    keyword_lower = keyword.lower()
    for control in main_window.descendants(control_type=control_type):
        automation_id = (control.element_info.automation_id or "").lower()
        title = (control.window_text() or "").strip().lower()
        if keyword_lower in automation_id or keyword_lower in title:
            return control
    return None


class {class_name}(UDSLauncherE2EBase):
    FEATURE_NAME = {feature!r}
    FEATURE_KEYS = {keys_repr}

    def test_{slug}_screen_ready(self):
        self.assertTrue(
            wait_until(
                lambda: self.main_window is not None and self.main_window.exists(timeout=1),
                timeout_sec=20,
            ),
            f"Main window is not ready for feature '{{self.FEATURE_NAME}}'.",
        )

    def test_{slug}_controls_visible(self):
        if not self.FEATURE_KEYS:
            self.skipTest("No automation key inferred. Add control keys and assertions manually.")

        detected = []
        for key in self.FEATURE_KEYS:
            control = _find_first_control_contains(self.main_window, "Button", key)
            if control is None:
                control = _find_first_control_contains(self.main_window, "Edit", key)
            if control is None:
                control = _find_first_control_contains(self.main_window, "Text", key)
            if control is not None:
                detected.append(key)

        self.assertGreater(
            len(detected),
            0,
            f"No inferred controls found for feature '{{self.FEATURE_NAME}}': {{self.FEATURE_KEYS}}",
        )

    def test_{slug}_primary_flow(self):
        self.skipTest(
            "TODO: Implement primary flow for this feature. Use click_when_ready + wait_until with deterministic assertions."
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
'''


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    auto_test_dir = repo_root / "auto_test"
    auto_test_dir.mkdir(parents=True, exist_ok=True)

    feature = args.feature.strip()
    slug = slugify(feature)
    class_name = to_class_name(slug)

    context = load_context(args.context)
    related_files = context.get("related_files", []) if isinstance(context, dict) else []
    ui_keys = context.get("ui_keys", []) if isinstance(context, dict) else []

    output_file = pick_output_file(auto_test_dir, slug)
    content = render_test(feature, slug, class_name, related_files, ui_keys)
    output_file.write_text(content, encoding="utf-8")

    print(f"Generated test file: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
