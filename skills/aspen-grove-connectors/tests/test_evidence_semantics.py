#!/usr/bin/env python3
"""Behavior tests for evidence-safe Aspen Grove connector semantics."""

import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC = importlib.util.spec_from_file_location("aspen_mesh", ROOT / "skill.py")
mesh = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mesh)


class EvidenceSemanticsTests(unittest.TestCase):
    def test_credential_presence_is_not_provider_verification(self):
        with patch.dict(os.environ, {"GITHUB_API_KEY": "present"}, clear=False):
            connector = mesh.BaseConnector("github")
            result = connector.health_check()
        self.assertEqual(result["status"], "configured_unverified")
        self.assertEqual(result["evidence_state"], "UNVERIFIED")
        self.assertFalse(result["verified"])

    def test_mock_health_is_simulated(self):
        result = mesh.BaseConnector("github", mock_mode=True).health_check()
        self.assertEqual(result["evidence_state"], "SIMULATED")
        self.assertFalse(result["verified"])

    def test_probe_must_explicitly_verify(self):
        connector = mesh.BaseConnector("github", health_probe=lambda: {"status": "ok"})
        result = connector.health_check()
        self.assertEqual(result["evidence_state"], "SOURCE_BOUND")
        self.assertFalse(result["verified"])

    def test_verified_probe_is_promoted(self):
        connector = mesh.BaseConnector(
            "github",
            health_probe=lambda: {"verified": True, "provider": "github"},
        )
        result = connector.health_check()
        self.assertEqual(result["status"], "verified_live")
        self.assertEqual(result["evidence_state"], "VERIFIED")
        self.assertTrue(result["verified"])

    def test_unbound_live_transport_blocks_instead_of_faking_success(self):
        connector = mesh.BaseConnector("github")
        result = connector.execute_request("/repos/example")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "live_transport_unbound")
        self.assertFalse(result["verified"])

    def test_mock_dispatch_is_not_verified(self):
        connector = mesh.BaseConnector("github", mock_mode=True)
        result = connector.execute_request("/repos/example")
        self.assertEqual(result["evidence_state"], "SIMULATED")
        self.assertFalse(result["verified"])

    def test_handler_without_verified_receipt_stays_source_bound(self):
        connector = mesh.BaseConnector(
            "github",
            request_handler=lambda endpoint, payload: {"status": "ok"},
        )
        result = connector.execute_request("/repos/example")
        self.assertEqual(result["status"], "completed_unverified")
        self.assertEqual(result["evidence_state"], "SOURCE_BOUND")
        self.assertFalse(result["verified"])

    def test_verified_handler_receipt_is_promoted(self):
        connector = mesh.BaseConnector(
            "github",
            request_handler=lambda endpoint, payload: {
                "verified": True,
                "provider": "github",
                "resource": endpoint,
            },
        )
        result = connector.execute_request("/repos/example")
        self.assertEqual(result["status"], "verified_success")
        self.assertEqual(result["evidence_state"], "VERIFIED")
        self.assertTrue(result["verified"])

    def test_pipeline_blocks_required_unverified_stage(self):
        connector = mesh.BaseConnector("github")
        grove = mesh.AspenGroveMesh(
            services=["github"],
            connectors={"github": connector},
        )
        plan = grove.plan_pipeline([{"service": "github"}])
        self.assertFalse(plan["runnable"])
        self.assertEqual(plan["blocked"][0]["reason"], "provider_not_verified")

    def test_pipeline_accepts_verified_stage(self):
        connector = mesh.BaseConnector(
            "github",
            health_probe=lambda: {"verified": True, "provider": "github"},
        )
        grove = mesh.AspenGroveMesh(
            services=["github"],
            connectors={"github": connector},
        )
        plan = grove.plan_pipeline([{"service": "github"}])
        self.assertTrue(plan["runnable"])
        self.assertEqual(plan["status"], "ready")

    def test_dynamic_service_expansion(self):
        grove = mesh.AspenGroveMesh(services=["gmail", "memoryplugin"])
        self.assertEqual(set(grove.connectors), {"gmail", "memoryplugin"})

    def test_default_surface_contains_new_high_leverage_connectors(self):
        expected = {"gmail", "google_drive", "slack", "memoryplugin", "mem0", "e2b"}
        self.assertTrue(expected.issubset(set(mesh.AspenGroveMesh.SERVICES)))

    def test_mirrored_entrypoints_match_canonical_source(self):
        canonical = (ROOT / "skill.py").read_text(encoding="utf-8")
        for relative in ("scripts/connector_mesh.py", "scripts/run.py", "scripts/this_skill.py"):
            self.assertEqual((ROOT / relative).read_text(encoding="utf-8"), canonical)


if __name__ == "__main__":
    unittest.main()
