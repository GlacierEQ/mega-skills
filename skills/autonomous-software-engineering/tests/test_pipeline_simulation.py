import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills" / "autonomous-software-engineering" / "scripts" / "run_pipeline_simulation.py"


def scenario(name):
    proc = subprocess.run([sys.executable, str(SCRIPT), "--scenario", name], check=True, capture_output=True, text=True)
    return json.loads(proc.stdout)


class PipelineSimulationTests(unittest.TestCase):
    def test_happy_path_routes_all_core_specialists_and_releases(self):
        result = scenario("happy")
        self.assertEqual(result["state"], "VERIFIED")
        self.assertTrue(result["approval_granted"])
        for key in ("architecture", "implementation", "tests", "security", "performance", "quality_gate", "review", "release"):
            self.assertIn(key, result["evidence"])
        receivers = {handoff["receiver"] for handoff in result["handoffs"]}
        self.assertTrue({"automated-architecture-analysis", "automated-code-refactoring", "automated-test-generation", "automated-security-scanning", "automated-performance-profiling", "quality-gate"} <= receivers)

    def test_security_block_prevents_quality_gate_and_release(self):
        result = scenario("security-block")
        self.assertEqual(result["state"], "BLOCKED")
        self.assertIn("vulnerability", result["blocked_reason"])
        self.assertNotIn("release", result["evidence"])
        self.assertNotIn("quality_gate", result["evidence"])

    def test_approval_boundary_escalates_without_release(self):
        result = scenario("approval-required")
        self.assertEqual(result["state"], "ESCALATED")
        self.assertTrue(result["approval_requested"])
        self.assertFalse(result["approval_granted"])
        self.assertNotIn("release", result["evidence"])

    def test_tower_route_preserves_mandated_order(self):
        result = scenario("tower-route")
        self.assertEqual(result["state"], "VERIFIED")
        tower_events = [event["detail"] for event in result["events"] if event["kind"] == "tower"]
        self.assertEqual(tower_events, ["preflight", "source_of_truth", "exhibits_proof", "validate", "generate", "tests", "build", "integrity", "receipt"])

    def test_failed_handoff_has_recovery_evidence(self):
        result = scenario("handoff-recovery")
        self.assertEqual(result["state"], "VERIFIED")
        self.assertTrue(result["recovered"])
        statuses = [handoff["status"] for handoff in result["handoffs"]]
        self.assertIn("BLOCKED", statuses)
        self.assertIn("VERIFIED", statuses)
        self.assertTrue(any(event["kind"] == "recovery" for event in result["events"]))

    def test_unknown_scenario_fails_closed(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "--scenario", "not-a-scenario"], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
