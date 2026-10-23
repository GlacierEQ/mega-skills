"""Behavioral tests for the RE safety gate implementation."""
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import gate


class GateBehaviorTests(unittest.TestCase):
    def test_owned_inspection_admitted(self):
        result = gate.evaluate_gate({
            "authority_basis": "owned_software",
            "purpose": "interoperability",
            "operations": ["inspect_binary_layout", "inspect_sqlite_database"],
            "environment": {"throwaway": False},
        })
        self.assertTrue(result["admitted"])
        self.assertEqual(result["refusal_reasons"], [])
        self.assertEqual(len(result["decision_digest"]), 64)

    def test_excluded_purpose_refused(self):
        result = gate.evaluate_gate({
            "authority_basis": "owned_software",
            "purpose": "drm_circumvention",
            "operations": ["inspect_binary_layout"],
            "environment": {"throwaway": True},
        })
        self.assertFalse(result["admitted"])
        self.assertTrue(any("exclusion list" in r for r in result["refusal_reasons"]))

    def test_execution_requires_throwaway_and_separate_authority(self):
        result = gate.evaluate_gate({
            "authority_basis": "authorized_security_research",
            "purpose": "vulnerability_research",
            "operations": ["instrument_with_frida"],
            "environment": {"throwaway": False},
            "execute": True,
            "execution_authorized": False,
        })
        self.assertFalse(result["admitted"])
        self.assertEqual(len(result["refusal_reasons"]), 2)
        admitted = gate.evaluate_gate({
            "authority_basis": "authorized_security_research",
            "purpose": "vulnerability_research",
            "operations": ["instrument_with_frida"],
            "environment": {"throwaway": True},
            "execute": True,
            "execution_authorized": True,
        })
        self.assertTrue(admitted["admitted"])
        effect = admitted["operation_effects"][0]
        self.assertTrue(effect["executes_foreign_code"])

    def test_missing_basis_refused(self):
        result = gate.evaluate_gate({"operations": [], "environment": {}})
        self.assertFalse(result["admitted"])

    def test_cli_round_trip(self):
        payload = {"authority_basis": "ctf_education", "purpose": "ctf_education",
                   "operations": ["inspect_wasm_artifact"], "environment": {"throwaway": False}}
        proc = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "..", "scripts", "gate.py")],
            input=json.dumps(payload), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        output = json.loads(proc.stdout)
        self.assertTrue(output["admitted"])


if __name__ == "__main__":
    unittest.main()
