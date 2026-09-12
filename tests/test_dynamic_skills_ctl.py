#!/usr/bin/env python3
"""
Opt-in host-integration tests for the dynamic skill activator & governor.

These tests exercise the Operator-host runtime only when GLACIEREQ_SKILLS_BIN
explicitly names the executable under test. Generic CI must remain portable and
must not infer host capability from ~/bin/skills or any incidental local path.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Tuple
from unittest import mock

SKILLS_BIN_ENV = "GLACIEREQ_SKILLS_BIN"


def configured_skills_bin() -> Path | None:
    raw = os.environ.get(SKILLS_BIN_ENV, "").strip()
    return Path(raw).expanduser() if raw else None


class DynamicSkillsPortabilityTests(unittest.TestCase):
    def test_generic_environment_does_not_infer_host_cli(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(configured_skills_bin())

    def test_explicit_host_binding_is_preserved(self):
        target = "/operator/runtime/bin/skills"
        with mock.patch.dict(os.environ, {SKILLS_BIN_ENV: target}, clear=True):
            self.assertEqual(configured_skills_bin(), Path(target))


class DynamicSkillsControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skills_bin = configured_skills_bin()
        if cls.skills_bin is None:
            raise unittest.SkipTest(
                f"host integration is opt-in: set {SKILLS_BIN_ENV} to the Skills CLI executable"
            )
        if not cls.skills_bin.is_file():
            raise AssertionError(
                f"explicit host integration target does not exist: {cls.skills_bin}"
            )
        if not cls.skills_bin.stat().st_mode & 0o111:
            raise AssertionError(
                f"explicit host integration target is not executable: {cls.skills_bin}"
            )

    def _run_skills(self, *args: str) -> Tuple[int, Any]:
        res = subprocess.run(
            [sys.executable, str(self.skills_bin), *args],
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
