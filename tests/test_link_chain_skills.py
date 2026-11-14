#!/usr/bin/env python3
"""Run the link-chain atomic Skill behavior suites from the root test gate."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ["link-admission", "machine-binding", "staleness-assess", "library-quality-audit"]


class LinkChainSkillTests(unittest.TestCase):
    def test_all_four_behavior_suites(self):
        for skill in SKILLS:
            path = ROOT / "skills" / skill / "tests" / ("test_" + skill.replace("-", "_") + ".py")
            with self.subTest(skill=skill):
                result = subprocess.run(
                    [sys.executable, str(path), "-v"],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
