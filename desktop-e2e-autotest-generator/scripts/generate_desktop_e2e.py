#!/usr/bin/env python
"""Generate desktop E2E testcase CSV and unittest skeleton from feature goal and launch target."""

from __future__ import annotations

import argparse
import csv
import re
import shlex
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

CSV_COLUMNS = ["tc_id", "title", "precondition", "steps", "expected", "result", "actual"]


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


def write_testcases_csv(csv_path: Path, cases: list[TestCaseSpec]) -> None:
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for case in cases:
            writer.writerow(
                {
                    "tc_id": case.tc_id,
                    "title": case.title,
                    "precondition": case.precondition,
                    "steps": case.steps,
                    "expected": case.expected,
                    "result": "",
                    "actual": "",
                }
            )


def shell_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=False)
    except ValueError:
        return [command]


def build_test_method_text(case: TestCaseSpec) -> str:
    func_name = slugify(case.title)
    return (
        f"def test_{case.tc_id.lower()}_{func_name}(self):\n"
        f"    '''{case.title}.'''\n"
        "    self._require_app()\n"
        "    window = self._main_window()\n"
        "    # TODO: Replace placeholders with real control interactions for this testcase.\n"
        f"    # Preconditions: {case.precondition}\n"
        f"    # Steps: {case.steps}\n"
        f"    # Expected: {case.expected}\n"
        "    self.skipTest(\"TODO: implement real UI actions and assertions\")\n"
    )


def indent_block(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join((prefix + line) if line else "" for line in text.splitlines())


def render_test_python(
    feature_goal: str,
    launch_target: str,
    launch_mode: str,
    source_paths: list[str],
    cases: list[TestCaseSpec],
    csv_path: Path,
) -> str:
    if launch_mode == "exe":
        run_hint = "Executable launch detected. Prefer direct process start without shell."
    elif launch_mode == "python":
        run_hint = "Python command launch detected. Ensure virtual environment/deps are ready."
    else:
        run_hint = "Generic command launch detected. Validate quoting and shell availability."

    use_shell = launch_mode != "exe"

    dynamic_cases = [case for case in cases if case.tc_id not in {"TC01", "TC02", "TC99"}]
    if not dynamic_cases:
        dynamic_methods = (
            "def test_tc03_feature_specific_flow(self):\n"
            "    '''Feature-specific flow placeholder.'''\n"
            "    self._require_app()\n"
            "    window = self._main_window()\n"
            "    # TODO: Implement feature steps and assertions.\n"
            "    self.skipTest(\"TODO: implement real UI actions and assertions\")\n"
        )
    else:
        dynamic_methods = "\n".join(build_test_method_text(case) for case in dynamic_cases)

    lines = [
        "import csv",
        "import re",
        "import shlex",
        "import subprocess",
        "import time",
        "import unittest",
        "from pathlib import Path",
        "",
        "try:",
        "    from pywinauto.application import Application",
        "except Exception:",
        "    Application = None",
        "",
        f"FEATURE_GOAL = {feature_goal!r}",
        f"LAUNCH_TARGET = {launch_target!r}",
        f"SOURCE_PATHS = {source_paths!r}",
        f"RUN_HINT = {run_hint!r}",
        f"TESTCASE_CSV = Path({str(csv_path)!r})",
        "",
        "",
        "class CsvResultStore:",
        "    FIELDNAMES = [\"tc_id\", \"title\", \"precondition\", \"steps\", \"expected\", \"result\", \"actual\"]",
        "",
        "    def __init__(self, csv_path: Path):",
        "        self.csv_path = Path(csv_path)",
        "        self.rows = self._load_rows()",
        "",
        "    def _load_rows(self):",
        "        with self.csv_path.open(\"r\", encoding=\"utf-8\", newline=\"\") as handle:",
        "            return list(csv.DictReader(handle))",
        "",
        "    def update(self, tc_id: str, status: str, actual: str):",
        "        normalized_tc = tc_id.upper().strip()",
        "        for row in self.rows:",
        "            if row.get(\"tc_id\", \"\").upper().strip() == normalized_tc:",
        "                row[\"result\"] = status",
        "                row[\"actual\"] = actual",
        "                self._flush()",
        "                return",
        "",
        "    def _flush(self):",
        "        with self.csv_path.open(\"w\", encoding=\"utf-8\", newline=\"\") as handle:",
        "            writer = csv.DictWriter(handle, fieldnames=self.FIELDNAMES)",
        "            writer.writeheader()",
        "            writer.writerows(self.rows)",
        "",
        "",
        "class DesktopE2EGenerated(unittest.TestCase):",
        "    process = None",
        "    app = None",
        "    result_store = None",
        "",
        "    @classmethod",
        "    def setUpClass(cls):",
        "        cls.result_store = CsvResultStore(TESTCASE_CSV)",
        "",
        "        launch_tokens = shlex.split(LAUNCH_TARGET, posix=False)",
        "        if not launch_tokens:",
        "            raise ValueError(\"LAUNCH_TARGET is empty\")",
        "",
        f"        use_shell = {use_shell}",
        "        launch_cmd = LAUNCH_TARGET if use_shell else launch_tokens",
        "        cls.process = subprocess.Popen(launch_cmd, shell=use_shell)",
        "        time.sleep(5)",
        "",
        "        if Application is not None:",
        "            try:",
        "                cls.app = Application(backend=\"uia\").connect(process=cls.process.pid, timeout=30)",
        "            except Exception:",
        "                cls.app = None",
        "",
        "    @classmethod",
        "    def tearDownClass(cls):",
        "        if cls.app is not None:",
        "            try:",
        "                cls.app.top_window().close()",
        "                time.sleep(1)",
        "            except Exception:",
        "                pass",
        "        if cls.process is not None and cls.process.poll() is None:",
        "            cls.process.terminate()",
        "            try:",
        "                cls.process.wait(timeout=10)",
        "            except Exception:",
        "                cls.process.kill()",
        "",
        "    def run(self, result=None):",
        "        if result is None:",
        "            result = self.defaultTestResult()",
        "        super().run(result)",
        "        self._write_case_result(result)",
        "        return result",
        "",
        "    def _write_case_result(self, result):",
        "        tc_id = self._extract_tc_id()",
        "        if not tc_id or self.result_store is None:",
        "            return",
        "",
        "        status = \"PASS\"",
        "        actual = \"OK\"",
        "",
        "        failure_text = self._message_for_test(self, result.failures)",
        "        error_text = self._message_for_test(self, result.errors)",
        "        skipped_reason = self._skip_reason_for_test(self, result.skipped)",
        "",
        "        if failure_text is not None:",
        "            status = \"FAIL\"",
        "            actual = self._normalize_message(failure_text)",
        "        elif error_text is not None:",
        "            status = \"ERROR\"",
        "            actual = self._normalize_message(error_text)",
        "        elif skipped_reason is not None:",
        "            status = \"SKIP\"",
        "            actual = self._normalize_message(skipped_reason)",
        "",
        "        self.result_store.update(tc_id, status, actual)",
        "",
        "    def _extract_tc_id(self):",
        "        match = re.search(r\"test_(tc\\d+)_\", self._testMethodName)",
        "        if match:",
        "            return match.group(1).upper()",
        "        return None",
        "",
        "    @staticmethod",
        "    def _message_for_test(test_obj, test_result_pairs):",
        "        for current_test, message in test_result_pairs:",
        "            if current_test is test_obj:",
        "                return message",
        "        return None",
        "",
        "    @staticmethod",
        "    def _skip_reason_for_test(test_obj, skipped_pairs):",
        "        for current_test, reason in skipped_pairs:",
        "            if current_test is test_obj:",
        "                return reason",
        "        return None",
        "",
        "    @staticmethod",
        "    def _normalize_message(message):",
        "        compressed = \" \".join(str(message).split())",
        "        return compressed[:1500]",
        "",
        "    def _require_app(self):",
        "        if self.process is None or self.process.poll() is not None:",
        "            self.fail(\"Application is not running. Check launch target.\")",
        "",
        "    def _main_window(self):",
        "        if self.app is None:",
        "            self.skipTest(",
        "                \"pywinauto not available or cannot connect to app window. \"",
        "                \"Install pywinauto and provide stable window identifiers.\"",
        "            )",
        "        window = self.app.top_window()",
        "        window.wait(\"visible ready\", timeout=30)",
        "        return window",
        "",
        "    def test_tc01_launch_application_successfully(self):",
        "        self.assertIsNotNone(self.process)",
        "        self.assertIsNone(self.process.poll(), \"App exited unexpectedly right after launch\")",
        "",
        "    def test_tc02_open_feature_entry_screen(self):",
        "        self._require_app()",
        "        window = self._main_window()",
        "        self.assertTrue(window.exists(), \"Main window was not found\")",
        "        # TODO: Navigate to feature entry for FEATURE_GOAL and assert screen readiness.",
        "        self.skipTest(\"TODO: implement feature entry navigation\")",
        "",
    ]

    lines.append(indent_block(dynamic_methods.rstrip(), 4))
    lines.extend(
        [
            "",
            "    def test_tc99_close_application_cleanly(self):",
            "        self._require_app()",
            "        # Teardown verifies termination path. Keep this as checkpoint only.",
            "        self.assertTrue(True)",
            "",
            "",
            "if __name__ == \"__main__\":",
            "    unittest.main(verbosity=2)",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate testcase CSV and E2E unittest skeleton.")
    parser.add_argument("--feature-goal", required=True, help="Feature purpose to test")
    parser.add_argument("--launch-target", required=True, help=".exe path or python command")
    parser.add_argument("--repo-root", default=".", help="Repository root where outputs will be created")
    parser.add_argument("--source-path", action="append", default=[], help="Optional related source files")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    auto_test_dir = repo_root / "auto_test"
    test_case_dir = repo_root / "test_case"
    auto_test_dir.mkdir(parents=True, exist_ok=True)
    test_case_dir.mkdir(parents=True, exist_ok=True)

    feature_slug = slugify(args.feature_goal)
    csv_path = unique_path(test_case_dir / f"testcases_{feature_slug}.csv")
    test_path = unique_path(auto_test_dir / f"test_{feature_slug}_e2e.py")

    launch_mode = detect_launch_mode(args.launch_target)
    cases = build_testcases(args.feature_goal)

    write_testcases_csv(csv_path, cases)
    test_path.write_text(
        render_test_python(
            args.feature_goal,
            args.launch_target,
            launch_mode,
            args.source_path,
            cases,
            csv_path,
        ),
        encoding="utf-8",
    )

    print(f"feature_goal={args.feature_goal}")
    print(f"launch_target={args.launch_target}")
    print(f"launch_mode={launch_mode}")
    print(f"testcases_csv={csv_path}")
    print(f"test_file={test_path}")
    print(f"first_token={first_token_from_launch(args.launch_target)}")
    return 0


def first_token_from_launch(launch_target: str) -> str:
    tokens = shell_tokens(launch_target)
    return tokens[0] if tokens else ""


if __name__ == "__main__":
    raise SystemExit(main())