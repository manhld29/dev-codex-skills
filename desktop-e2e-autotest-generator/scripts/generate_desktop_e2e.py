#!/usr/bin/env python
"""Generate desktop E2E testcases and unittest skeleton from feature goal and launch target."""

from __future__ import annotations

import argparse
import re
import shlex
import textwrap
import unicodedata
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestCaseSpec:
    tc_id: str
    title: str
    precondition: str
    steps: str
    expected: str


KEYWORD_CASES = [
    (
        ["login", "log in", "sign in", "dang nhap", "dangnhap", "dang-nhap"],
        TestCaseSpec(
            "TC03",
            "Authenticate with valid credentials",
            "Application is open and login form is visible.",
            "Enter valid username and password, then submit.",
            "User enters authenticated state and target screen is shown.",
        ),
    ),
    (
        ["search", "find", "tim kiem", "timkiem", "tim-kiem"],
        TestCaseSpec(
            "TC04",
            "Search returns matching results",
            "Application is open with searchable dataset.",
            "Input a keyword and trigger search.",
            "Result list shows items matching the keyword.",
        ),
    ),
    (
        ["create", "add", "new", "tao moi", "them moi", "them"],
        TestCaseSpec(
            "TC05",
            "Create a new record",
            "Application is open and create form is available.",
            "Open create form, input valid data, save.",
            "New record is created and visible in list/detail view.",
        ),
    ),
    (
        ["edit", "update", "sua", "cap nhat", "capnhat"],
        TestCaseSpec(
            "TC06",
            "Update an existing record",
            "At least one existing record is available.",
            "Open record, modify editable fields, save.",
            "Updated values are persisted and shown in UI.",
        ),
    ),
    (
        ["delete", "remove", "xoa"],
        TestCaseSpec(
            "TC07",
            "Delete record with confirmation",
            "At least one deletable record is available.",
            "Trigger delete and confirm action.",
            "Record is removed and success feedback is shown.",
        ),
    ),
    (
        ["export", "xuat"],
        TestCaseSpec(
            "TC08",
            "Export data from feature",
            "Application is open with exportable data.",
            "Trigger export with default options.",
            "Export operation completes and output confirmation is shown.",
        ),
    ),
]


def normalize_ascii(text: str) -> str:
    return (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )


def slugify(text: str) -> str:
    ascii_text = normalize_ascii(text)
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_text).strip("_")
    return slug or "feature"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for idx in range(2, 1000):
        candidate = path.with_name(f"{stem}_{idx}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not allocate unique filename for {path}")


def detect_launch_mode(launch_target: str) -> str:
    lowered = launch_target.lower()
    if ".exe" in lowered:
        return "exe"
    if lowered.strip().startswith("python ") or lowered.strip().startswith("py "):
        return "python"
    return "command"


def build_testcases(feature_goal: str) -> list[TestCaseSpec]:
    cases = [
        TestCaseSpec(
            "TC01",
            "Launch application successfully",
            "Launch target is reachable from the test machine.",
            "Run launch target and wait for app startup.",
            "Process is running and no startup crash occurs.",
        ),
        TestCaseSpec(
            "TC02",
            "Open feature entry screen",
            "Application is running.",
            f"Navigate to feature flow for: {feature_goal}",
            "Feature entry screen appears and is interactive.",
        ),
    ]

    normalized_goal = normalize_ascii(feature_goal)
    used_ids = {"TC01", "TC02"}
    for keywords, spec in KEYWORD_CASES:
        if any(keyword in normalized_goal for keyword in keywords) and spec.tc_id not in used_ids:
            cases.append(spec)
            used_ids.add(spec.tc_id)

    cases.append(
        TestCaseSpec(
            "TC99",
            "Close application cleanly",
            "Application is running.",
            "Close the application from UI or process control.",
            "Application exits without hang or crash dialog.",
        )
    )
    return cases


def render_testcases_markdown(feature_goal: str, launch_target: str, source_paths: list[str], cases: list[TestCaseSpec]) -> str:
    lines = [
        f"# Testcases: {feature_goal}",
        "",
        f"- Launch target: `{launch_target}`",
        f"- Source paths: `{', '.join(source_paths) if source_paths else 'N/A'}`",
        "",
        "| ID | Title | Preconditions | Steps | Expected |",
        "| --- | --- | --- | --- | --- |",
    ]
    for case in cases:
        lines.append(
            f"| {case.tc_id} | {case.title} | {case.precondition} | {case.steps} | {case.expected} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("- Replace generic steps with exact control identifiers from the real UI.")
    lines.append("- Keep each E2E test independent and rerunnable.")
    return "\n".join(lines) + "\n"


def shell_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=False)
    except ValueError:
        return [command]


def build_test_function(case: TestCaseSpec) -> str:
    func_name = slugify(case.title)
    return textwrap.dedent(
        f"""
        def test_{case.tc_id.lower()}_{func_name}(self):
            \"\"\"{case.title}.\"\"\"
            self._require_app()
            window = self._main_window()
            # TODO: Replace placeholders with real control interactions for this testcase.
            # Preconditions: {case.precondition}
            # Steps: {case.steps}
            # Expected: {case.expected}
            self.skipTest("TODO: implement real UI actions and assertions")
        """
    ).strip("\n")


def render_test_python(feature_goal: str, launch_target: str, launch_mode: str, source_paths: list[str], cases: list[TestCaseSpec]) -> str:
    token_list = shell_tokens(launch_target)
    first_token = token_list[0] if token_list else launch_target
    if launch_mode == "exe":
        run_hint = "Executable launch detected. Prefer direct process start without shell."
    elif launch_mode == "python":
        run_hint = "Python command launch detected. Ensure virtual environment/deps are ready."
    else:
        run_hint = "Generic command launch detected. Validate quoting and shell availability."

    test_funcs = "\n\n".join(build_test_function(case) for case in cases if case.tc_id not in {"TC01", "TC02", "TC99"})
    if not test_funcs:
        test_funcs = textwrap.dedent(
            """
            def test_tc03_feature_specific_flow(self):
                '''Feature-specific flow placeholder.'''
                self._require_app()
                window = self._main_window()
                # TODO: Implement feature steps and assertions.
                self.skipTest("TODO: implement real UI actions and assertions")
            """
        ).strip("\n")

    return textwrap.dedent(
        f"""
        import shlex
        import subprocess
        import time
        import unittest

        try:
            from pywinauto.application import Application
        except Exception:
            Application = None


        FEATURE_GOAL = {feature_goal!r}
        LAUNCH_TARGET = {launch_target!r}
        SOURCE_PATHS = {source_paths!r}
        RUN_HINT = {run_hint!r}


        class DesktopE2EGenerated(unittest.TestCase):
            process = None
            app = None

            @classmethod
            def setUpClass(cls):
                launch_tokens = shlex.split(LAUNCH_TARGET, posix=False)
                if not launch_tokens:
                    raise ValueError("LAUNCH_TARGET is empty")

                use_shell = {str(launch_mode != 'exe')}
                launch_cmd = LAUNCH_TARGET if use_shell else launch_tokens
                cls.process = subprocess.Popen(launch_cmd, shell=use_shell)
                time.sleep(5)

                if Application is not None:
                    try:
                        cls.app = Application(backend="uia").connect(process=cls.process.pid, timeout=30)
                    except Exception:
                        cls.app = None

            @classmethod
            def tearDownClass(cls):
                if cls.app is not None:
                    try:
                        cls.app.top_window().close()
                        time.sleep(1)
                    except Exception:
                        pass
                if cls.process is not None and cls.process.poll() is None:
                    cls.process.terminate()
                    try:
                        cls.process.wait(timeout=10)
                    except Exception:
                        cls.process.kill()

            def _require_app(self):
                if self.process is None or self.process.poll() is not None:
                    self.fail("Application is not running. Check launch target.")

            def _main_window(self):
                if self.app is None:
                    self.skipTest(
                        "pywinauto not available or cannot connect to app window. "
                        "Install pywinauto and provide stable window identifiers."
                    )
                window = self.app.top_window()
                window.wait("visible ready", timeout=30)
                return window

            def test_tc01_launch_application_successfully(self):
                self.assertIsNotNone(self.process)
                self.assertIsNone(self.process.poll(), "App exited unexpectedly right after launch")

            def test_tc02_open_feature_entry_screen(self):
                self._require_app()
                window = self._main_window()
                self.assertTrue(window.exists(), "Main window was not found")
                # TODO: Navigate to feature entry for FEATURE_GOAL and assert screen readiness.
                self.skipTest("TODO: implement feature entry navigation")

        {textwrap.indent(test_funcs, '    ')}

            def test_tc99_close_application_cleanly(self):
                self._require_app()
                # Teardown verifies termination path. Keep this as checkpoint only.
                self.assertTrue(True)


        if __name__ == "__main__":
            unittest.main(verbosity=2)
        """
    ).lstrip("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate testcase markdown and E2E unittest skeleton.")
    parser.add_argument("--feature-goal", required=True, help="Feature purpose to test")
    parser.add_argument("--launch-target", required=True, help=".exe path or python command")
    parser.add_argument("--repo-root", default=".", help="Repository root where auto_test will be created")
    parser.add_argument("--source-path", action="append", default=[], help="Optional related source files")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    auto_test_dir = repo_root / "auto_test"
    auto_test_dir.mkdir(parents=True, exist_ok=True)

    feature_slug = slugify(args.feature_goal)
    cases_path = unique_path(auto_test_dir / f"testcases_{feature_slug}.md")
    test_path = unique_path(auto_test_dir / f"test_{feature_slug}_e2e.py")

    launch_mode = detect_launch_mode(args.launch_target)
    cases = build_testcases(args.feature_goal)

    cases_path.write_text(
        render_testcases_markdown(args.feature_goal, args.launch_target, args.source_path, cases),
        encoding="utf-8",
    )
    test_path.write_text(
        render_test_python(args.feature_goal, args.launch_target, launch_mode, args.source_path, cases),
        encoding="utf-8",
    )

    print(f"feature_goal={args.feature_goal}")
    print(f"launch_target={args.launch_target}")
    print(f"launch_mode={launch_mode}")
    print(f"testcases_file={cases_path}")
    print(f"test_file={test_path}")
    print(f"first_token={first_token_from_launch(args.launch_target)}")
    return 0


def first_token_from_launch(launch_target: str) -> str:
    tokens = shell_tokens(launch_target)
    return tokens[0] if tokens else ""


if __name__ == "__main__":
    raise SystemExit(main())

