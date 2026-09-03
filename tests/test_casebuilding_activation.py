import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGET_SKILLS = ["audio-forensic-core", "forensic-evidence-chain-core", "epistemic-gate"]
STUB_MARKERS = ("Status: STUB - implement per skill contract", "# TODO: Implement")


class CasebuildingActivationTests(unittest.TestCase):
    """Regression coverage for the deep-casebuilding activation package."""

    def test_pipeline_structure_and_command_paths(self):
        pipeline = json.loads((ROOT / "pipelines/deep-casebuilding.json").read_text(encoding="utf-8"))
        self.assertEqual(pipeline["schema_version"], 1)
        self.assertEqual(pipeline["id"], "deep-casebuilding")
        stages = pipeline["stages"]
        ids = [stage["id"] for stage in stages]
        self.assertEqual(len(ids), len(set(ids)))
        for stage in stages:
            for need in stage.get("needs", []):
                self.assertIn(need, ids)
            command = stage["command"]
            self.assertEqual(command[0], "{python}")
            self.assertIsInstance(stage["resume_safe"], bool)
            for token in command[1:]:
                if isinstance(token, str) and token.endswith(".py") and not token.startswith("-"):
                    self.assertTrue((ROOT / token).is_file(), f"missing command target: {token}")
            for artifact in stage.get("consumes", []) + stage.get("produces", []):
                self.assertFalse(artifact.startswith("/"))

    def test_mission_scaffold_is_valid(self):
        mission = ROOT / "missions/deep-casebuilding"
        intake = json.loads((mission / "case-intake.json").read_text(encoding="utf-8"))
        for key in ("schema_version", "case_number", "court", "evidence_roots", "bates_prefix"):
            self.assertIn(key, intake)
        events = json.loads((mission / "events.json").read_text(encoding="utf-8"))
        self.assertIsInstance(events["events"], list)
        alignment = json.loads((mission / "fixtures/alignment.sample.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(alignment["segments"]), 2)
        manifest = json.loads((mission / "pipeline-execution-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["pipeline_id"], "deep-casebuilding")

    def test_target_skill_scripts_carry_no_stub_markers(self):
        for skill_id in TARGET_SKILLS:
            scripts = ROOT / "skills" / skill_id / "scripts"
            self.assertTrue(scripts.is_dir())
            for path in scripts.glob("*.py"):
                text = path.read_text(encoding="utf-8", errors="replace")
                for marker in STUB_MARKERS:
                    self.assertNotIn(marker, text)

    def test_target_skill_behavioral_suites_pass(self):
        for skill_id in TARGET_SKILLS:
            tests_dir = ROOT / "skills" / skill_id / "tests"
            for test_file in sorted(tests_dir.glob("test_*.py")):
                proc = subprocess.run(
                    [sys.executable, str(test_file)],
                    capture_output=True, text=True, cwd=ROOT)
                self.assertEqual(proc.returncode, 0,
                                 f"{test_file.name} failed:\n{proc.stdout[-800:]}\n{proc.stderr[-800:]}")
                self.assertIn("OK", proc.stderr)

    def test_activation_dry_run_reports_ready(self):
        receipt = ROOT / "evidence/casebuilding-activation/test-dry-run-receipt.json"
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/casebuilding_activation.py"),
             "--report", str(receipt)],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(proc.returncode, 0, proc.stdout[-800:] + proc.stderr[-800:])
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertTrue(payload["activation_ready"])
        self.assertEqual(payload["mode"], "dry_run")
        self.assertEqual(payload["preflight_problems"], [])
        for skill_id in TARGET_SKILLS:
            self.assertEqual(payload["fresh_skill_verdicts"][skill_id]["state"], "behavior_verified")


if __name__ == "__main__":
    unittest.main()
