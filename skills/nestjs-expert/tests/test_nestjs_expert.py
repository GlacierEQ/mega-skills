import unittest
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent

class TestNestjsExpert(unittest.TestCase):
    def test_skill_md_manifest(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: nestjs-expert", skill_md)
        self.assertIn("description:", skill_md)

    def test_skill_entry_point_exists_and_executable(self):
        skill_py = SKILL_ROOT / "skill.py"
        self.assertTrue(skill_py.exists())
        self.assertTrue(bool(skill_py.stat().st_mode & 0o111))

    def test_scripts_executable(self):
        for script_name in ("run.py", "this_skill.py"):
            p = SKILL_ROOT / "scripts" / script_name
            self.assertTrue(p.exists())
            self.assertTrue(bool(p.stat().st_mode & 0o111))

if __name__ == "__main__":
    unittest.main()
