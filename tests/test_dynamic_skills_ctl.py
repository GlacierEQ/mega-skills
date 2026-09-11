#!/usr/bin/env python3
"""
Tests for dynamic skill activator & governor (~/bin/skills).
Run with: python3 -m pytest tests/test_dynamic_skills_ctl.py -v
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

SKILLS_BIN = Path.home() / "bin" / "skills"


class DynamicSkillsControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert SKILLS_BIN.is_file(), f"Skills CLI binary not found at {SKILLS_BIN}"
        assert SKILLS_BIN.stat().st_mode & 0o111, f"Skills CLI binary is not executable"

    def _run_skills(self, *args) -> tuple[int, dict | list | str]:
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

        # Activate
        code_act, res_act = self._run_skills("activate", test_skill)
        self.assertEqual(code_act, 0)
        self.assertEqual(res_act[0]["name"], test_skill)
        self.assertTrue(res_act[0]["success"])

        # Verify active in status
        code_st, status = self._run_skills("status")
        self.assertEqual(code_st, 0)
        self.assertIn(test_skill, status["dynamic_active_skills"])

        # Deactivate
        code_deact, res_deact = self._run_skills("deactivate", test_skill)
        self.assertEqual(code_deact, 0)
        self.assertEqual(res_deact[0]["name"], test_skill)
        self.assertTrue(res_deact[0]["success"])

        # Verify inactive in status
        code_st2, status2 = self._run_skills("status")
        self.assertEqual(code_st2, 0)
        self.assertNotIn(test_skill, status2["dynamic_active_skills"])


if __name__ == "__main__":
    unittest.main()
