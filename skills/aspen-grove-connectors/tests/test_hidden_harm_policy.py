#!/usr/bin/env python3
"""Regression tests for hidden-harm counter-engineering in connector routing."""

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC = importlib.util.spec_from_file_location(
    "worker_policy", ROOT / "worker_policy.py"
)
policy = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(policy)


class HiddenHarmTests(unittest.TestCase):
    def test_operator_report_is_preserved_without_provider_verification(self):
        result = policy.WorkerPolicy.authority_aware_reconcile(
            prior={
                "value": "locator last ping Sep 1",
                "authority": "OPERATOR_REPORTED",
                "evidence": "SOURCE_BOUND",
            },
            incoming={
                "value": None,
                "authority": "PROVIDER",
                "evidence": "UNVERIFIED",
                "reason": "not recovered",
            },
        )
        self.assertEqual(
            result["state"],
            "PRESERVE_DISTINCT_AUTHORITY",
        )
        self.assertEqual(
            result["selected"]["authority"],
            "OPERATOR_REPORTED",
        )

    def test_retrieval_failure_is_not_absence(self):
        result = policy.WorkerPolicy.interpret_negative_result(
            query_completed=False,
            source_complete=False,
            matches=0,
        )
        self.assertEqual(result["state"], "RETRIEVAL_GAP")
        self.assertFalse(result["proves_absence"])

    def test_empty_search_without_complete_coverage_is_not_absence(self):
        result = policy.WorkerPolicy.interpret_negative_result(
            query_completed=True,
            source_complete=False,
            matches=0,
        )
        self.assertEqual(
            result["state"],
            "NO_MATCH_IN_PARTIAL_COVERAGE",
        )
        self.assertFalse(result["proves_absence"])

    def test_weaker_fallback_is_not_silently_equivalent(self):
        result = policy.WorkerPolicy.fallback_gate(
            required_capabilities={
                "read",
                "write",
                "readback",
                "provenance",
            },
            fallback_capabilities={
                "read",
                "provenance",
            },
        )
        self.assertFalse(result["equivalent"])
        self.assertEqual(
            set(result["lost_capabilities"]),
            {"write", "readback"},
        )
        self.assertEqual(
            result["state"],
            "DEGRADED_FALLBACK",
        )

    def test_projection_loss_blocks_protected_field_loss(self):
        result = policy.WorkerPolicy.projection_loss_gate(
            source_fields={
                "value",
                "authority",
                "provenance",
                "contradictions",
            },
            projected_fields={
                "value",
                "provenance",
            },
            protected_fields={
                "authority",
                "provenance",
                "contradictions",
            },
        )
        self.assertFalse(result["runnable"])
        self.assertEqual(
            set(result["lost_protected_fields"]),
            {"authority", "contradictions"},
        )

    def test_reversible_mutation_requires_prestate(self):
        result = policy.WorkerPolicy.mutation_reversibility_gate(
            reversible_surface=True,
            pre_state_captured=False,
            rollback_route_known=True,
            idempotency_key_present=True,
        )
        self.assertFalse(result["runnable"])
        self.assertIn(
            "pre_state_captured",
            result["missing"],
        )

    def test_demotion_requires_disconfirming_evidence(self):
        result = policy.WorkerPolicy.demotion_gate(
            current_state="VERIFIED_READ_WRITE",
            proposed_state="UNVERIFIED",
            disconfirming_provider_evidence=False,
            provider_scope_changed=False,
        )
        self.assertFalse(result["allowed"])
        self.assertEqual(
            result["state"],
            "BLOCKED_HIDDEN_HARM_DEMOTION",
        )


if __name__ == "__main__":
    unittest.main()
