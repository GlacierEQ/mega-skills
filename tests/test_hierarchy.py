import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"


class HierarchyFoundationTests(unittest.TestCase):
    def test_validator_passes_for_the_expanded_graph(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_hierarchy.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_initial_atomic_skill_set_is_independent_and_complete(self):
        skills = json.loads((REGISTRY / "skills.json").read_text(encoding="utf-8"))["entries"]
        expected = {
            "mission-contract", "roadmap-builder", "evidence-register", "context-capsule",
            "work-packet", "quality-gate", "handoff-record",
            "fleet-git-harmonizer-core", "forensic-evidence-chain-core",
            "aerospace-trajectory-core", "polyglot-rosetta-core", "omni-memory-core",
            "fork-overlay-core", "ast-repair-core", "audio-forensic-core",
        }
        self.assertEqual({entry["id"] for entry in skills}, expected)
        for entry in skills:
            self.assertTrue((ROOT / entry["entrypoint"]).is_file())

    def test_long_horizon_combo_composes_all_atomic_skills(self):
        combos = json.loads((REGISTRY / "combo-skills.json").read_text(encoding="utf-8"))["entries"]
        core = next(entry for entry in combos if entry["id"] == "long-horizon-core")
        self.assertEqual(len(core["members"]), 7)
        self.assertTrue(all(member["kind"] == "skill" for member in core["members"]))

    def test_mega_layer_requires_but_does_not_duplicate_core_contracts(self):
        mega = json.loads((REGISTRY / "mega-skills.json").read_text(encoding="utf-8"))["entries"][0]
        self.assertIn("long-horizon-core", mega["required_combos"])
        self.assertTrue((ROOT / mega["entrypoint"]).is_file())
        self.assertFalse((ROOT / "skills/far-away-party-core").exists())

    def test_external_skills_are_metadata_only(self):
        self.assertFalse((ROOT / "skills/repository-context-onboarding").exists())
        self.assertTrue((REGISTRY / "external-skills.json").is_file())


if __name__ == "__main__":
    unittest.main()
