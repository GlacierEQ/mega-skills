#!/usr/bin/env python3
"""Behavioral tests for the staleness-assess atomic Skill."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from long_horizon_atomic_runtime import run


class StalenessAssessTests(unittest.TestCase):
    def test_version_and_date_pin_marks_source_current(self):
        out = run(
            "staleness-assess",
            "staleness_recorder",
            {
                "sources": [
                    {
                        "id": "S-01",
                        "url": "https://example.com",
                        "version": "2.5.1",
                        "resolved_at": "2026-09-30",
                    }
                ]
            },
        )
        self.assertEqual(len(out["assessed"]), 1)
        self.assertEqual(len(out["unpinned"]), 0)
        self.assertEqual(out["assessed"][0]["current"], True)

    def test_missing_version_is_reported_unpinned(self):
        out = run(
            "staleness-assess",
            "date_checker",
            {"sources": [{"id": "S-02", "url": "https://example.com", "resolved_at": "2026-09-30"}]},
        )
        self.assertEqual(out["unpinned"], ["S-02"])

    def test_version_pinner_returns_only_pinned_versions(self):
        out = run(
            "staleness-assess",
            "version_pinner",
            {
                "sources": [
                    {"id": "S-03", "version": "1.0.0", "resolved_at": "2026-09-30"},
                    {"id": "S-04", "resolved_at": "2026-09-30"},
                ]
            },
        )
        self.assertEqual(out["pinned"], [{"id": "S-03", "version": "1.0.0"}])


if __name__ == "__main__":
    unittest.main()
