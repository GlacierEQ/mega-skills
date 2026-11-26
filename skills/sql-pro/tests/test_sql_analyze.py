"""Behavioural tests: run the analyzer, assert on findings."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYZER = ROOT / "scripts" / "sql_analyze.py"


def run(text):
    return subprocess.run(
        [sys.executable, str(ANALYZER), "--json"],
        input=text, capture_output=True, text=True, timeout=60,
    )


BAD = "SELECT * FROM users WHERE lower(email) LIKE '%x' AND id NOT IN (SELECT id FROM t);"
GOOD = "SELECT id, email FROM users WHERE email = 'a@b.c' LIMIT 10;"


class TestSqlAnalyze(unittest.TestCase):
    def test_flags_select_star_and_leading_wildcard(self):
        r = run(BAD)
        d = json.loads(r.stdout)
        rules = {f["rule"] for f in d["files"]["<stdin>"]}
        self.assertIn("select_star", rules)
        self.assertIn("leading_wildcard_like", rules)
        self.assertGreater(d["total_findings"], 2)

    def test_clean_query_has_no_findings(self):
        r = run(GOOD)
        d = json.loads(r.stdout)
        self.assertEqual(d["total_findings"], 0)

    def test_finding_names_line_and_fix(self):
        r = run(BAD)
        d = json.loads(r.stdout)
        for f in d["files"]["<stdin>"]:
            self.assertIn("line", f)
            self.assertTrue(f["fix"])

    def test_exit_zero_on_success(self):
        self.assertEqual(run(GOOD).returncode, 0)


if __name__ == "__main__":
    unittest.main()
