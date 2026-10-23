"""Regression tests for false-positive completion and forged readback."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "gate_integrity", Path(__file__).resolve().parents[1] / "scripts" / "completion_gate.py"
)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def ostensibly_verified():
    revision = "a" * 40
    return {
        "state": "VERIFIED",
        "revision": revision,
        "ci": "passed",
        "criteria": {
            key: {"status": "passed", "revision": revision,
                  "evidence": "receipt://" + key, "kind": "runtime"}
            for key in gate.REQUIRED
        },
        "outstanding_actions": [],
        "unresolved_defects": [],
    }


class GateIntegrityTests(unittest.TestCase):
    def test_open_cannot_claim_complete_even_with_passing_criteria(self):
        mission = ostensibly_verified()
        mission["state"] = "OPEN"
        self.assertFalse(gate.decide(mission)["accepted"])

    def test_failed_cannot_claim_complete_even_with_passing_criteria(self):
        mission = ostensibly_verified()
        mission["state"] = "FAILED"
        self.assertFalse(gate.decide(mission)["accepted"])

    def test_boolean_provider_readback_is_not_receipt(self):
        mission = ostensibly_verified()
        mission.update(provider_mutation=True, provider_readback=True)
        self.assertFalse(gate.decide(mission)["accepted"])

    def test_boolean_deployment_readback_is_not_receipt(self):
        mission = ostensibly_verified()
        mission.update(deployed=True, deployment_readback=True)
        self.assertFalse(gate.decide(mission)["accepted"])


if __name__ == "__main__":
    unittest.main()
