#!/usr/bin/env python3
"""
Host-integration tests for the dynamic skill activator & governor (~/bin/skills).

These tests exercise the Operator-host runtime when the CLI is installed. Repository
CI must remain portable: a generic Buildkite/GitHub runner is not evidence that the
host-only CLI is broken merely because ~/bin/skills is absent there.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Tuple

SKILLS_BIN = Path(os.environ.get("GLACIEREQ_SKILLS_BIN", str(Path.home() / "bin" / "skills")))


class DynamicSkillsControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SKILLS_BIN.is_file():
            raise unittest.SkipTest(
                f"host integration unavailable: Skills CLI not found at {SKILLS_BIN}"
            )
        if not SKILLS_BIN.stat().st_mode & 0o111:
            raise unittest.SkipTest(
                f"host integration unavailable: Skills CLI is not executable at {SKILLS_BIN}"
            )

    def _run_skills(self, *args: str) -> Tuple[int, Any]:
        res = subprocess.run(
            [sys.executable, str(SKILLS_BIN), *args],
            capture_output=True,
            text=True,
        )
        try:
            parsed = json.loads(res.stdout)
            return res.returncode, parsed
        except Exception:
            return res.returncode, res.stdout + res.stderr

    def test_skills_status_optimal(self):
        code, data = self._run_skills("status")
        self.assertEqual(code, 0)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["status"], "OPTIMAL")
        self.assertGreater(data["available_count"], 700)
        self.assertLessEqual(data["live_count"], 150)
        self.assertIn("token_savings_pct", data)

    def test_skills_search(self):
        code, results = self._run_skills("search", "supabase", "--limit", "5")
        self.assertEqual(code, 0)
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1)
        names = [r["name"] for r in results]
        self.assertTrue(any("supabase" in n for n in names))

    def test_skills_recommend_enforces_two_skill_limit(self):
        code, recs = self._run_skills("recommend", "build a fastapi postgres microservice")
        self.assertEqual(code, 0)
        self.assertIsInstance(recs, list)
        self.assertLessEqual(len(recs), 2)
        self.assertGreaterEqual(len(recs), 1)

    def test_skills_activate_and_deactivate_lifecycle(self):
        test_skill = "playwright-skill"

        code_act, res_act = self._run_skills("activate", test_skill)
        self.assertEqual(code_act, 0)
        self.assertEqual(res_act[0]["name"], test_skill)
        self.assertTrue(res_act[0]["success"])

        code_st, status = self._run_skills("status")
        self.assertEqual(code_st, 0)
        self.assertIn(test_skill, status["dynamic_active_skills"])

        code_deact, res_deact = self._run_skills("deactivate", test_skill)
        self.assertEqual(code_deact, 0)
        self.assertEqual(res_deact[0]["name"], test_skill)
        self.assertTrue(res_deact[0]["success"])

        code_st2, status2 = self._run_skills("status")
        self.assertEqual(code_st2, 0)
        self.assertNotIn(test_skill, status2["dynamic_active_skills"])


if __name__ == "__main__":
    unittest.main()
