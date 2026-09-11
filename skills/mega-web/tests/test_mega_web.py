import unittest
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent

class TestMegaWeb(unittest.TestCase):
    def test_skill_md_manifest(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: mega-web", skill_md)
        self.assertIn("description:", skill_md)

    def test_skill_entry_point_exists_and_executable(self):
        skill_py = SKILL_ROOT / "skill.py"
        self.assertTrue(skill_py.exists())
        self.assertTrue(bool(skill_py.stat().st_mode & 0o111))

    def test_run_behavioral(self):
        import subprocess
        import sys
        run_py = SKILL_ROOT / "scripts" / "run.py"
        cmd = [sys.executable, str(run_py)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output.get("skill"), "mega-web")
        self.assertEqual(output.get("status"), "ready")
        self.assertTrue(output.get("firewall_active"))


if __name__ == "__main__":
    unittest.main()

