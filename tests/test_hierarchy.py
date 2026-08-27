import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HierarchyFoundationTests(unittest.TestCase):
    def test_validator_passes_for_the_initial_graph(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_hierarchy.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_layers_have_distinct_entrypoint_types(self):
        self.assertTrue((ROOT / "skills/far-away-party-core/SKILL.md").is_file())
        self.assertTrue((ROOT / "combo-skills/recon-and-map/COMBO.md").is_file())
        self.assertTrue((ROOT / "mega-skills/far-away-party/MEGA.md").is_file())

    def test_external_skills_are_metadata_only(self):
        self.assertFalse((ROOT / "skills/repository-context-onboarding").exists())
        self.assertTrue((ROOT / "registry/external-skills.json").is_file())


if __name__ == "__main__":
    unittest.main()
