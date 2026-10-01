#!/usr/bin/env python3
"""Behavior tests for beneficial plugin-worker routing rules."""

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


class WorkerRuleTests(unittest.TestCase):
    def test_stale_projection_cannot_demote_verified_provider_evidence(self):
        self.assertEqual(
            policy.WorkerPolicy.reconcile_evidence(
                "VERIFIED_READ_WRITE", "UNVERIFIED"
            ),
            "VERIFIED_READ_WRITE",
        )

    def test_verified_core_is_skipped_without_regression_signal(self):
        self.assertFalse(
            policy.WorkerPolicy.should_probe_verified_core(
                "VERIFIED_READ_WRITE"
            )
        )
        self.assertTrue(
            policy.WorkerPolicy.should_probe_verified_core(
                "VERIFIED_READ_WRITE",
                regression_signal=True,
            )
        )

    def test_transient_blocker_does_not_retry_same_route_without_change(self):
        self.assertFalse(
            policy.WorkerPolicy.should_retry_same_route("quota")
        )
        self.assertTrue(
            policy.WorkerPolicy.should_retry_same_route(
                "quota",
                materially_different_route=True,
            )
        )

    def test_multiple_provider_accounts_are_not_guessed(self):
        decision = policy.WorkerPolicy.account_binding_decision(
            2,
            explicit_binding=False,
        )
        self.assertFalse(decision["runnable"])
        self.assertEqual(
            decision["state"],
            "BLOCKED_ACCOUNT_DISAMBIGUATION",
        )

    def test_write_promotion_requires_acceptance_readback_and_scope(self):
        self.assertFalse(
            policy.WorkerPolicy.can_promote_write(
                True,
                False,
                "folder-create",
            )["verified"]
        )
        promoted = policy.WorkerPolicy.can_promote_write(
            True,
            True,
            "folder-create",
        )
        self.assertTrue(promoted["verified"])
        self.assertEqual(promoted["scope"], "folder-create")

    def test_security_mutation_requires_access_path_preservation(self):
        blocked = policy.WorkerPolicy.security_mutation_gate(
            True,
            False,
            True,
            True,
        )
        self.assertFalse(blocked["runnable"])
        self.assertIn(
            "legitimate_access_paths_recovered",
            blocked["missing"],
        )
        ready = policy.WorkerPolicy.security_mutation_gate(
            True,
            True,
            True,
            True,
        )
        self.assertTrue(ready["runnable"])

    def test_stale_failed_deployment_is_not_used_to_repair_current_source(self):
        result = policy.WorkerPolicy.deployment_repair_gate(
            False,
            True,
        )
        self.assertFalse(result["runnable"])
        self.assertEqual(
            result["state"],
            "STALE_FAILURE_DO_NOT_REPAIR_CURRENT_SOURCE",
        )

    def test_run_requires_material_delta(self):
        self.assertFalse(policy.WorkerPolicy.material_delta())
        self.assertTrue(
            policy.WorkerPolicy.material_delta(
                coalition_strengthened=True
            )
        )


if __name__ == "__main__":
    unittest.main()
