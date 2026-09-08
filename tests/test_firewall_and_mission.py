import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from firewall import FirewallViolation, guard, load_policy  # noqa: E402


class FirewallAndMissionTests(unittest.TestCase):
    def test_every_mega_has_complete_read_only_firewall(self):
        data = json.loads((ROOT / "registry" / "mega-skills.json").read_text(encoding="utf-8"))
        for entry in data["entries"]:
            policy = load_policy(ROOT, entry["id"])
            for action in ("read_repository", "run_local_tests", "write_run_artifacts", "emit_receipt"):
                guard(policy, action)
            for action in ("merge", "legal_filing", "execute_unknown_program", "network_send"):
                with self.assertRaises(FirewallViolation):
                    guard(policy, action)

    def test_buildkite_does_not_require_false_mission_completion(self):
        pipeline = (ROOT / ".buildkite" / "pipeline.yml").read_text(encoding="utf-8")
        self.assertNotIn('receipt["status"] == "COMPLETED"', pipeline)
        self.assertIn('receipt["status"] == "SUPPORT_VERIFIED"', pipeline)
        self.assertIn('receipt["completion_eligible"] is False', pipeline)
        self.assertIn('receipt["mission_state_changed"] is False', pipeline)

    def test_malformed_policy_cannot_be_used_to_bypass_guard(self):
        policy = load_policy(ROOT, "apex-autonomous-agent-foundry")
        policy["allowed_actions"].append("network_send")
        with self.assertRaises(ValueError):
            guard(policy, "network_send")

    def test_layer_copy_files_are_absent(self):
        self.assertEqual(list((ROOT / "combo-skills").glob("*/SKILL.md")), [])
        self.assertEqual(list((ROOT / "mega-skills").glob("*/SKILL.md")), [])

    def test_runtime_sync_installs_adapter_outside_source_layer(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        from sync_runtime_skills import install_contract_package
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "combo-source"
            runtime = Path(tmp) / "runtime"
            source.mkdir()
            (source / "COMBO.md").write_text("# Canonical combo contract\n", encoding="utf-8")
            install_contract_package(source, runtime, "demo", "COMBO.md", "Combo Skill")
            self.assertFalse((source / "SKILL.md").exists())
            self.assertTrue((runtime / "demo" / "SKILL.md").is_file())
            self.assertTrue((runtime / "demo" / "COMBO.md").is_symlink())

    def test_runtime_sync_does_not_recreate_source_layer_copies(self):
        source = (ROOT / "scripts" / "sync_runtime_skills.py").read_text(encoding="utf-8")
        self.assertNotIn('c / "SKILL.md"', source)
        self.assertNotIn('m / "SKILL.md"', source)
        self.assertIn('target / "SKILL.md"', source)

    def test_mission_runner_proves_support_route_without_claiming_mission_completion(self):
        with tempfile.TemporaryDirectory() as output_dir:
            result = subprocess.run(
                [sys.executable, "scripts/run_mega_mission.py", "--output-dir", output_dir],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            out = Path(output_dir)
            receipt = json.loads((out / "RUN_RECEIPT.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["status"], "SUPPORT_VERIFIED")
            self.assertFalse(receipt["mission_state_changed"])
            self.assertFalse(receipt["completion_eligible"])
            self.assertTrue(receipt["support_only"])
            self.assertTrue(receipt["mission_id"].startswith("FOUNDRY-RUN-"))
            self.assertTrue((out / "INPUT_MANIFEST.json").is_file())
            self.assertTrue((out / "FAILURE_RECORD.json").is_file())
            self.assertTrue(any(item["phase"] == "hierarchy-validation" and item["status"] == "VERIFIED" for item in receipt["phase_receipts"]))
            manifest = receipt["output_manifest"]
            actual = [{"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file() and p.name != "RUN_RECEIPT.json"]
            self.assertEqual(manifest, actual)

    def test_mission_runner_exercises_conditional_route_when_requested(self):
        with tempfile.TemporaryDirectory() as output_dir:
            result = subprocess.run(
                [sys.executable, "scripts/run_mega_mission.py", "--include-conditional", "--output-dir", output_dir],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            route = json.loads((Path(output_dir) / "ROUTE.json").read_text())
            self.assertIn("capability-readiness", route["selected_combos"])
            self.assertGreater(len(route["selected_combos"]), len(route["required_combos"]))


if __name__ == "__main__":
    unittest.main()
