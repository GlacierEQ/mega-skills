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
    def test_every_mega_has_read_only_firewall(self):
        data = json.loads((ROOT / "registry" / "mega-skills.json").read_text(encoding="utf-8"))
        for entry in data["entries"]:
            policy = load_policy(ROOT, entry["id"])
            guard(policy, "read_repository")
            guard(policy, "write_run_artifacts")
            with self.assertRaises(FirewallViolation):
                guard(policy, "merge")
            with self.assertRaises(FirewallViolation):
                guard(policy, "legal_filing")

    def test_layer_copy_files_are_absent(self):
        self.assertEqual(list((ROOT / "combo-skills").glob("*/SKILL.md")), [])
        self.assertEqual(list((ROOT / "mega-skills").glob("*/SKILL.md")), [])

    def test_mission_runner_completes_contract_backed_local_run(self):
        with tempfile.TemporaryDirectory() as output_dir:
            result = subprocess.run(
                [sys.executable, "scripts/run_mega_mission.py", "--output-dir", output_dir],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            receipt = json.loads((Path(output_dir) / "RUN_RECEIPT.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["status"], "COMPLETED")
            self.assertEqual(receipt["firewall_mode"], "read_only")
            self.assertGreaterEqual(len(receipt["output_manifest"]), 9)
            self.assertTrue(any(item["phase"] == "hierarchy-validation" and item["status"] == "VERIFIED" for item in receipt["phase_receipts"]))


if __name__ == "__main__":
    unittest.main()
