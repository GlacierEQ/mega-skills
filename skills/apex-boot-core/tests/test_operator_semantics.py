#!/usr/bin/env python3
"""Regression tests for Operator semantic binding and enrichment-transition law."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from boot_watchdog import ApexBootCore
from operator_semantics import (
    DEFAULT_CONTRACT_PATH,
    detect_inversions,
    load_operator_semantics,
    project_operator_semantics,
    transition_for_status,
    validate_contract,
)


class TestOperatorSemanticsContract(unittest.TestCase):
    def test_durable_contract_binds_operator_authority(self):
        binding = load_operator_semantics()
        self.assertEqual(binding["status"], "BOUND_DURABLE_CONTRACT")
        projection = project_operator_semantics(binding)
        self.assertEqual(projection["authority_holder"], "OPERATOR")
        self.assertTrue(projection["exclusive_project_direction_authority"])
        self.assertFalse(projection["machine_project_direction_authority"])

    def test_mesh_never_collapses_to_machine_root(self):
        contract = json.loads(DEFAULT_CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["topology"]["model"], "HOLOGRAPHIC_POLYCENTRIC_MESH")
        self.assertFalse(contract["topology"]["single_root"])
        self.assertFalse(contract["topology"]["machine_sovereignty"])

    def test_gates_are_literal_level_up_enrichment_transitions(self):
        binding = load_operator_semantics()
        contract = binding["contract"]
        self.assertEqual(contract["gates"]["semantic"], "ENRICHMENT_TRANSITION")
        self.assertEqual(contract["gates"]["literal_model"], "LEVEL_UP")
        self.assertFalse(contract["gates"]["may_stop_mission"])
        self.assertEqual(transition_for_status("FAIL", binding), "LOCALIZE_REPAIR_REROUTE_LEVEL_UP")
        self.assertEqual(transition_for_status("WARN", binding), "ENRICH_WITH_UNCERTAINTY")
        self.assertEqual(transition_for_status("PASS", binding), "VALIDATED_LEVEL_UP")

    def test_local_block_changes_route_not_objective(self):
        contract = load_operator_semantics()["contract"]
        self.assertTrue(contract["routing"]["local_block_changes_route"])
        self.assertFalse(contract["routing"]["local_block_changes_objective"])
        self.assertEqual(contract["routing"]["mission_changes_only_by"], "OPERATOR")

    def test_contract_validator_rejects_machine_authority_inversion(self):
        contract = json.loads(DEFAULT_CONTRACT_PATH.read_text(encoding="utf-8"))
        contract["authority"]["machine_project_direction_authority"] = True
        issues = validate_contract(contract)
        self.assertTrue(any("machine_project_direction_authority" in issue for issue in issues))


class TestOntologyInversionDetector(unittest.TestCase):
    def test_detects_non_operator_sole_authority(self):
        findings = detect_inversions("APEX Boot Core becomes the sole authority for the estate.")
        self.assertIn("NON_OPERATOR_SOLE_AUTHORITY", {f["rule"] for f in findings})

    def test_detects_gate_as_veto(self):
        findings = detect_inversions("A failed gate blocks the mission from continuing.")
        self.assertIn("GATE_AS_MISSION_VETO", {f["rule"] for f in findings})

    def test_does_not_flag_correct_gate_semantics(self):
        findings = detect_inversions("A failed gate does not stop the mission; it enriches state and changes the route.")
        self.assertFalse(any(f["rule"] == "GATE_AS_MISSION_VETO" for f in findings))

    def test_detects_single_root_collapse(self):
        findings = detect_inversions("The runtime is the canonical root of the estate.")
        self.assertIn("MESH_COLLAPSED_TO_SINGLE_ROOT", {f["rule"] for f in findings})


class TestBootProjection(unittest.TestCase):
    def test_every_gate_result_is_non_veto_enrichment(self):
        receipt = ApexBootCore().boot()
        self.assertTrue(receipt.pre_reasoning_binding["mission_continues"])
        self.assertFalse(receipt.pre_reasoning_binding["gate_may_stop_mission"])
        for gate in receipt.gates:
            self.assertTrue(gate["level_up"])
            self.assertFalse(gate["mission_stop"])
            self.assertTrue(gate["transition"])

    def test_fail_telemetry_cannot_change_operator_authority(self):
        receipt = ApexBootCore().boot()
        binding = receipt.pre_reasoning_binding
        self.assertEqual(binding["authority_holder"], "OPERATOR")
        self.assertFalse(binding["machine_project_direction_authority"])
        self.assertEqual(binding["mission_changes_only_by"], "OPERATOR")


class TestEntrypointAndDocsParity(unittest.TestCase):
    def test_legacy_this_skill_no_longer_contains_v1_watchdog(self):
        text = (SKILL_ROOT / "scripts" / "this_skill.py").read_text(encoding="utf-8")
        self.assertNotIn("class ApexBootWatchdog", text)
        self.assertIn("from boot_watchdog import main", text)

    def test_skill_docs_use_real_v2_cli(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("--check", text)
        self.assertIn("python scripts/boot_watchdog.py --json", text)
        self.assertIn("enrichment transition", text.lower())


if __name__ == "__main__":
    unittest.main()
