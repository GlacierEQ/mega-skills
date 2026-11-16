#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
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

    def test_unprompted_court_filing_stays_hard_boundary(self) -> None:
        result = POLARITY.evaluate(
            {
                "proposed_gate": "pause before court filing",
                "boundary": "court_filing",
            }
        )
        self.assertEqual(result["kind"], "HARD_BOUNDARY")
        self.assertFalse(result["is_pitstop"])
        self.assertEqual(result["boundary"], "court_filing")
        self.assertFalse(result["continue_mission"])
        self.assertTrue(result["continue_independent_fronts"])

    def test_operator_authorized_reserved_boundary_discharges(self) -> None:
        result = POLARITY.evaluate(
            {
                "boundary": "production_deploy",
                "direct_operator_request": True,
            }
        )
        self.assertEqual(result["kind"], "AUTHORIZED_BOUNDARY")
        self.assertTrue(result["continue_mission"])
        self.assertTrue(result["require_receipt"])
        self.assertEqual(result["boundary"], "production_deploy")

    def test_context_force_push_prohibition_does_not_block_push_pitstop(self) -> None:
        result = POLARITY.evaluate(
            {
                "proposed_gate": "ask before push",
                "skill_text": "Never force-push history. Do not rewrite protected branches.",
                "operator_authorized": True,
            }
        )
        self.assertEqual(result["kind"], "QUALITY_PITSTOP")
        self.assertEqual(result["quality_dimension"], "remote_readback")
        self.assertTrue(result["continue_mission"])

    def test_reserved_boundary_match_is_deterministic(self) -> None:
        first = POLARITY.evaluate({"proposed_gate": "court filing and production deploy"})
        second = POLARITY.evaluate({"proposed_gate": "court filing and production deploy"})
        self.assertEqual(first["kind"], "HARD_BOUNDARY")
        self.assertEqual(first["boundary"], second["boundary"])
        self.assertEqual(first["boundary"], "court_filing")

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
        self.assertEqual(result["calibrator"], "hidden-harm-governance")

    def test_casey_entrypoint_accepts_gate_polarity(self) -> None:
        payload = {
            "skill_text": "GATE DENIED theater",
            "operator_authorized": True,
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(payload, handle)
            path = handle.name
        proc = subprocess.run(
            [sys.executable, str(ROOT / "skills" / "casey-operator-execution-kernel" / "skill.py"), "gate_polarity", "--input", path],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        body = json.loads(proc.stdout)
        self.assertEqual(body["kind"], "QUALITY_PITSTOP")

    def test_governance_calibrator_entrypoint(self) -> None:
        payload = {"proposed_gate": "ask before push", "semantic_lock": "CONTINUE"}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(payload, handle)
            path = handle.name
        proc = subprocess.run(
            [sys.executable, str(ROOT / "skills" / "hidden-harm-governance" / "skill.py"), "calibrate", "--input", path],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        body = json.loads(proc.stdout)
        self.assertEqual(body["kind"], "QUALITY_PITSTOP")
        self.assertEqual(body["quality_dimension"], "remote_readback")

    def test_skill_doc_uses_pitstop_not_permission_language(self) -> None:
        text = (ROOT / "skills" / "hidden-harm-governance" / "SKILL.md").read_text(encoding="utf-8")
        folded = text.lower()
        self.assertIn("QUALITY PITSTOP", text)
        self.assertIn("HARD-PITSTOP", text)
        self.assertIn("not a permission gate", folded)
        self.assertIn("calibrator", folded)

    def test_governance_is_registered(self) -> None:
        skills = json.loads((ROOT / "registry" / "skills.json").read_text(encoding="utf-8"))
        ids = {entry["id"] for entry in skills["entries"]}
        self.assertIn("hidden-harm-governance", ids)
        readiness = json.loads((ROOT / "registry" / "skill-readiness.json").read_text(encoding="utf-8"))
        ready_ids = {entry["id"] for entry in readiness["skills"]}
        self.assertIn("hidden-harm-governance", ready_ids)


if __name__ == "__main__":
    unittest.main()
