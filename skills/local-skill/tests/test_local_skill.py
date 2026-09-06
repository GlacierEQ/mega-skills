#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate.py"

class TestLocalSkill(unittest.TestCase):
    def test_skill_dispatcher_preserves_child_script_runtime_context(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "skill.py"), "inspect"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Found ", result.stdout)
        self.assertNotIn("NameError", result.stderr)

    def test_skill_entry_point_exists(self):
        skill_py = ROOT / "skill.py"
        self.assertTrue(skill_py.exists())
        self.assertTrue(bool(skill_py.stat().st_mode & 0o111))

    def test_scripts_exist(self):
        for script in ["inspect_skill.py","extract.py","generate.py","validate.py","pattern_catalog.py","this_skill.py"]:
            path = ROOT / "scripts" / script
            self.assertTrue(path.exists(), f"Missing script: {script}")
            self.assertTrue(bool(path.stat().st_mode & 0o111), f"Not executable: {script}")

    def test_resources_exist(self):
        for resource in ["local_skill_config.yaml","local_skill_schema.json","SKILL.md.template","skill.py.template"]:
            self.assertTrue((ROOT / "resources" / resource).exists())

    def test_skill_md_front_matter(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.lstrip().startswith("---"))
        self.assertIn("name: local-skill", text)

    def test_generator_emits_truthful_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(GENERATOR), "swarm-proof-demo", "Demonstrate a generated candidate skill.", "--output-root", tmp],
                text=True, capture_output=True, check=False
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            root = Path(tmp) / "swarm-proof-demo"
            self_check = subprocess.run([sys.executable, str(root / "scripts" / "this_skill.py")], text=True, capture_output=True, check=False)
            payload = json.loads(self_check.stdout)
            self.assertEqual(payload["status"], "candidate")
            self.assertEqual(payload["epistemic_tier"], "L1")
            self.assertFalse(payload["capability_executed"])

            run = subprocess.run([sys.executable, str(root / "scripts" / "run.py")], text=True, capture_output=True, check=False)
            run_payload = json.loads(run.stdout)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run_payload["status"], "execution_unavailable")
            self.assertFalse(run_payload["capability_executed"])

    def test_generator_never_embeds_false_ready_claims(self):
        text = GENERATOR.read_text(encoding="utf-8")
        self.assertNotIn('"status": "ready"', text)
        self.assertNotIn('"execution": "completed"', text)

if __name__ == "__main__":
    unittest.main()
