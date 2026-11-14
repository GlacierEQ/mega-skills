#!/usr/bin/env python3
"""Behavioral tests for the machine-binding atomic Skill."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from long_horizon_atomic_runtime import run


class MachineBindingTests(unittest.TestCase):
    def test_source_bound_to_observed_property_is_accepted(self):
        out = run(
            "machine-binding",
            "binding_recorder",
            {
                "links": [{"id": "L-01", "url": "https://example.com", "bound_property": "model"}],
                "device_profile": {"model": "MacBookAir7,2", "ram_gb": 8},
            },
        )
        self.assertEqual(len(out["bound"]), 1)
        self.assertEqual(len(out["unbound"]), 0)
        self.assertIn("MACHINE_BINDING.md", out["artifact"])

    def test_source_without_observed_property_is_unbound(self):
        out = run(
            "machine-binding",
            "binding_recorder",
            {
                "links": [{"id": "L-02", "url": "https://example.com", "bound_property": "gpu"}],
                "device_profile": {"model": "MacBookAir7,2"},
            },
        )
        self.assertEqual(len(out["bound"]), 0)
        self.assertEqual(len(out["unbound"]), 1)
        self.assertEqual(out["unbound"][0]["bound"], False)

    def test_scope_comparator_reports_sorted_profile_keys(self):
        out = run(
            "machine-binding",
            "scope_comparator",
            {
                "links": [{"id": "B-01", "bound_property": "ram_gb"}],
                "device_profile": {"model": "MacBookAir7,2", "ram_gb": 8},
            },
        )
        self.assertEqual(out["profile_keys"], ["model", "ram_gb"])
        self.assertEqual(out["bound_count"], 1)


if __name__ == "__main__":
    unittest.main()
