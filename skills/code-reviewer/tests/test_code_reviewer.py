"""Behavioural tests: execute the real scripts, assert on their output."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "scripts" / "code_quality_checker.py"
PR = ROOT / "scripts" / "pr_analyzer.py"
REPORT = ROOT / "scripts" / "review_report_generator.py"


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


class TestCodeReviewer(unittest.TestCase):
    def test_checker_flags_smells_in_known_bad_fixture(self):
        r = run(CHECKER, str(ROOT / "assets" / "sample_c_smells.c"), "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual(d["grade"], "F")
        self.assertGreater(len(d["smells"]), 0)
        self.assertIn("language", d)

    def test_checker_passes_clean_fixture(self):
        r = run(CHECKER, str(ROOT / "assets" / "sample_c_clean.c"), "--json")
        d = json.loads(r.stdout)
        self.assertNotEqual(d["grade"], "F")

    def test_checker_rejects_unsupported_type(self):
        r = run(CHECKER, str(ROOT / "SKILL.md"))
        self.assertIn("Unsupported file type", r.stderr + r.stdout)
        self.assertNotIn("grade", r.stdout)

    def test_pr_analyzer_fails_closed_outside_git(self):
        r = run(PR, str(ROOT), "--json")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not a git repository", r.stderr + r.stdout)

    def test_report_generator_emits_markdown(self):
        r = run(REPORT, str(ROOT), "--format", "markdown")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.strip())


if __name__ == "__main__":
    unittest.main()