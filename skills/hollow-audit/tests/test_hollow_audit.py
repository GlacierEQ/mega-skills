"""Behavioural tests: run the real scanner against real packages."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCANNER = ROOT / "scripts" / "hollow_scan.py"
SKILLS = ROOT.parent


def scan(target):
    r = subprocess.run(
        [sys.executable, str(SCANNER), str(target)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return r, json.loads(r.stdout)


class TestHollowAudit(unittest.TestCase):
    def test_real_skill_passes(self):
        r, d = scan(SKILLS / "repomix")
        self.assertEqual(d["verdict"], "PASS", d)
        self.assertGreater(d["real_scripts"], 0)
        self.assertEqual(d["documented_scripts_missing"], [])

    def test_adapter_stub_fails(self):
        stub = SKILLS / "_arc" / "create-skill"
        if not stub.is_dir():
            self.skipTest("archived stub not present")
        r, d = scan(stub)
        self.assertEqual(d["verdict"], "FAIL", d)
        self.assertTrue(d["stub_template_signature"])
        self.assertEqual(d["real_scripts"], 0)

    def test_exit_code_matches_verdict(self):
        r, d = scan(SKILLS / "repomix")
        self.assertEqual(r.returncode, 0)
        stub = SKILLS / "_arc" / "create-skill"
        if stub.is_dir():
            r2, _ = scan(stub)
            self.assertNotEqual(r2.returncode, 0)

    def test_missing_skill_dir_reports_error(self):
        r, d = scan(SKILLS / "does-not-exist")
        self.assertIn("error", d)


if __name__ == "__main__":
    unittest.main()