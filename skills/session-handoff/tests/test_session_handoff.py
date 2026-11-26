"""Behavioural tests: execute the real redaction and fidelity checkers."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINTER = ROOT / "scripts" / "redaction_linter.py"
SELFCHECK = ROOT / "scripts" / "handoff_self_check.py"


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


class TestSessionHandoff(unittest.TestCase):
    def test_linter_catches_planted_secret_in_strict_mode(self):
        r = run(LINTER, "--mode", "strict", "--sample")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("aws_access_key", r.stdout + r.stderr)

    def test_linter_warn_mode_exits_zero(self):
        r = run(LINTER, "--mode", "warn", "--sample")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_linter_off_mode_skips(self):
        r = run(LINTER, "--mode", "off", "--sample")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_selfcheck_runs_on_sample(self):
        r = run(SELFCHECK, "--sample")
        self.assertIn(r.returncode, {0, 1})

    def test_selfcheck_emits_json(self):
        r = run(SELFCHECK, "--sample", "--json")
        d = json.loads(r.stdout)
        self.assertIsInstance(d, dict)


if __name__ == "__main__":
    unittest.main()