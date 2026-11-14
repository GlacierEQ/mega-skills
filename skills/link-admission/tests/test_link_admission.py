#!/usr/bin/env python3
"""Behavioral tests for the link-admission atomic Skill."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from long_horizon_atomic_runtime import run


class LinkAdmissionTests(unittest.TestCase):
    def test_candidate_with_authority_and_relevance_is_admitted(self):
        out = run(
            "link-admission",
            "admission_recorder",
            {
                "candidates": [
                    {
                        "url": "https://support.apple.com/mac",
                        "authority": "Apple first-party",
                        "relevance": "model specifications",
                    }
                ]
            },
        )
        self.assertEqual(len(out["admitted"]), 1)
        self.assertEqual(len(out["rejected"]), 0)
        self.assertIn("LINK_ADMISSION.md", out["artifact"])

    def test_candidate_missing_relevance_is_rejected_with_reason(self):
        out = run(
            "link-admission",
            "admission_recorder",
            {"candidates": [{"url": "https://example.com", "authority": "community"}]},
        )
        self.assertEqual(len(out["admitted"]), 0)
        self.assertEqual(len(out["rejected"]), 1)
        self.assertEqual(out["rejected"][0]["admitted"], False)

    def test_classifier_returns_only_admitted_authority_fields(self):
        out = run(
            "link-admission",
            "authority_classifier",
            {"url": "https://example.com", "authority": "vendor", "relevance": "install steps"},
        )
        self.assertEqual(len(out["admitted"]), 1)
        self.assertEqual(set(out["admitted"][0]), {"id", "url", "authority"})


if __name__ == "__main__":
    unittest.main()
