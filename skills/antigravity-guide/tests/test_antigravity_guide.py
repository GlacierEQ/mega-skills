import unittest
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent

class TestAntigravityGuide(unittest.TestCase):
    def test_skill_md_manifest(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: antigravity-guide", skill_md)
        self.assertIn("description:", skill_md)

    def test_honesty_gate_no_false_offline_mandate(self):
        """Hidden-harm: do not require missing references/ as if they exist."""
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Honesty gate", skill_md)
        self.assertIn("OFFLINE_GAP", skill_md)
        self.assertIn("https://antigravity.google/docs", skill_md)
        refs = SKILL_ROOT / "references"
        if not refs.is_dir():
            self.assertNotIn("you **MUST** read the corresponding\nsubdocumentation", skill_md)

    def test_adapter_does_not_claim_cli_execution(self):
        import subprocess
        import json
        proc = subprocess.run(
            ["python3", str(SKILL_ROOT / "skill.py"), "--execute"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload.get("capability_executed"))
        self.assertEqual(payload.get("status"), "execution_unavailable")

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
