#!/usr/bin/env python3
"""
L2 Behavioral tests for apex-ast-sentinel.
"""

import sys
import json
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestApexAstSentinel(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent

    def test_skill_entry_point_exists_and_executable(self):
        skill_py = self.root / "skill.py"
        self.assertTrue(skill_py.exists())
        self.assertTrue(bool(skill_py.stat().st_mode & 0o111))

    def test_scripts_exist_and_executable(self):
        scripts_dir = self.root / "scripts"
        for script in ['this_skill.py', 'run.py']:
            p = scripts_dir / script
            self.assertTrue(p.exists(), f"Missing script: {script}")
            self.assertTrue(bool(p.stat().st_mode & 0o111), f"Script not executable: {script}")

    def test_resources_exist(self):
        resources_dir = self.root / "resources"
        self.assertTrue((resources_dir / "apex-ast-sentinel_config.yaml").exists() or (resources_dir / "config.yaml").exists())
        self.assertTrue((resources_dir / "apex-ast-sentinel_schema.json").exists() or (resources_dir / "schema.json").exists())

    def test_requirements_exist(self):
        self.assertTrue((self.root / "requirements.txt").exists())

    def test_skill_md_contract(self):
        skill_md = self.root / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---"))
        self.assertIn("name: apex-ast-sentinel", text)
        self.assertIn("Cognitive Firewall", text)
        self.assertIn("Epistemic Tier", text)

if __name__ == "__main__":
    unittest.main()
