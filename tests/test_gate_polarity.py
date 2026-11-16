#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


POLARITY = _load("gate_polarity", ROOT / "scripts" / "gate_polarity.py")
KERNEL = _load("operator_mission_kernel", ROOT / "scripts" / "operator_mission_kernel.py")


class GatePolarityTests(unittest.TestCase):
    def test_design_hard_gate_becomes_pitstop_not_permission(self) -> None:
        result = POLARITY.evaluate(
            {
                "skill_text": "<HARD-GATE> Do NOT write any code until the user has approved the design. MUST use before any creative work.",
                "operator_authorized": True,
                "semantic_lock": "BUILD",
            }
        )
        self.assertEqual(result["kind"], "QUALITY_PITSTOP")
        self.assertTrue(result["is_pitstop"])
        self.assertFalse(result["is_permission_gate"])
        self.assertTrue(result["continue_mission"])
        self.assertEqual(result["quality_dimension"], "design_clarity")
        self.assertIn(result["transition"], POLARITY.PITSTOP_TRANSITIONS.values())
        self.assertIn("HARD-GATE", result["stripped_labels"])

    def test_gate_denied_becomes_claim_strength_pitstop(self) -> None:
        result = POLARITY.evaluate(
            {
                "message": "GATE DENIED: target does not meet requirements. Not authorized for execution.",
                "requested_finished_deliverable": True,
            }
        )
        self.assertEqual(result["kind"], "QUALITY_PITSTOP")
        self.assertEqual(result["quality_dimension"], "claim_strength")
        self.assertEqual(result["transition"], "STRIP_PERMISSION_LABEL_LEVEL_UP")
        self.assertTrue(result["continue_mission"])

    def test_court_filing_stays_hard_boundary(self) -> None:
        result = POLARITY.evaluate(
            {
                "proposed_gate": "pause before court filing",
                "boundary": "court_filing",
                "operator_authorized": True,
            }
        )
        self.assertEqual(result["kind"], "HARD_BOUNDARY")
        self.assertFalse(result["is_pitstop"])
        self.assertEqual(result["boundary"], "court_filing")
        self.assertTrue(result["continue_independent_fronts"])

    def test_orch_gates_are_plan_and_diff_pitstops(self) -> None:
        plan = POLARITY.evaluate(
            {
                "instruction": "GATE 1 — do not write implementation code until the user approves",
                "direct_operator_request": True,
            }
        )
        commit = POLARITY.evaluate(
            {
                "instruction": "GATE 2 — do not commit until the user confirms. Between batches: just report and wait.",
                "semantic_lock": "EXECUTE",
            }
        )
        self.assertEqual(plan["quality_dimension"], "plan_coherence")
        self.assertEqual(commit["kind"], "QUALITY_PITSTOP")
        self.assertTrue(commit["continue_mission"])
        patterns = {item["pattern"] for item in commit["pitstops"]}
        self.assertTrue(patterns & {"commit_confirmation", "batch_wait_feedback"})

    def test_kernel_exposes_gate_polarity_operation(self) -> None:
        result = KERNEL.run_operator_mission_kernel(
            "gate_polarity",
            {
                "skill_text": "immutable gatekeeper printed GATE DENIED",
                "operator_authorized": True,
            },
        )
        self.assertEqual(result["operation"], "gate_polarity")
        self.assertEqual(result["invariant"], "hard_halt_is_pitstop_not_permission")
        self.assertEqual(result["kind"], "QUALITY_PITSTOP")

    def test_skill_doc_uses_pitstop_not_permission_language(self) -> None:
        text = (ROOT / "skills" / "hidden-harm-governance" / "SKILL.md").read_text(encoding="utf-8")
        folded = text.lower()
        self.assertIn("QUALITY PITSTOP", text)
        self.assertIn("HARD-PITSTOP", text)
        self.assertIn("not a permission gate", folded)
        self.assertIn("quality pitstop", folded)


if __name__ == "__main__":
    unittest.main()
