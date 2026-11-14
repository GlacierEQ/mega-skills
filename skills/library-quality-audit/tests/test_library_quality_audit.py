#!/usr/bin/env python3
"""Behavioral tests for the library-quality-audit atomic Skill."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from long_horizon_atomic_runtime import run


class LibraryQualityAuditTests(unittest.TestCase):
    def test_every_claim_with_known_source_passes(self):
        out = run(
            "library-quality-audit",
            "claim_mapper",
            {
                "claims": [{"id": "C-01", "claim": "Model is MacBookAir7,2", "source_id": "S-01"}],
                "sources": ["S-01"],
            },
        )
        self.assertEqual(out["unsupported"], [])
        self.assertEqual(out["claims"][0]["supported"], True)

    def test_claim_without_known_source_fails_audit(self):
        out = run(
            "library-quality-audit",
            "claim_mapper",
            {
                "claims": [{"id": "C-02", "claim": "GPU is Intel HD 6000", "source_id": "S-99"}],
                "sources": ["S-01"],
            },
        )
        self.assertEqual(out["unsupported"], ["C-02"])
        self.assertEqual(out["claims"][0]["supported"], False)

    def test_source_verifier_collects_assessed_and_bound_ids(self):
        out = run(
            "library-quality-audit",
            "source_verifier",
            {"assessed": [{"id": "S-01"}], "bound": [{"id": "B-01"}]},
        )
        self.assertEqual(out["known_source_ids"], ["B-01", "S-01"])

    def test_recorder_emits_fail_decision_for_unsupported_claim(self):
        out = run(
            "library-quality-audit",
            "audit_recorder",
            {
                "claims": [{"id": "C-03", "claim": "Unsupported", "source_id": "S-404"}],
                "sources": ["S-01"],
            },
        )
        self.assertEqual(out["decision"], "fail")
        self.assertIn("MACBOOK_AIR_LINK_AUDIT.md", out["artifact"])


if __name__ == "__main__":
    unittest.main()
