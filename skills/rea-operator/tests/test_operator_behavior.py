"""Behavioral tests for REA installation verification."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import rea_installation

GOOD = {"name": "rea-agents", "version": "6.7.0", "license": "MIT",
        "repository": {"type": "git", "url": "git+https://github.com/morluto/rea.git"}}

DOCTOR = """providers:
  - name: node
    ok: true
    classification: healthy
    detail: v24.22.1
  - name: ghidra
    ok: true
    classification: healthy
    detail: /opt/ghidra_12.1.2_PUBLIC
  - name: hopper
    ok: false
    classification: missing
    detail: not installed
"""


class OperatorBehaviorTests(unittest.TestCase):
    def test_canonical_package_accepted(self):
        result = rea_installation.verify_package_identity(dict(GOOD), "6.7.0")
        self.assertTrue(result["accepted"])
        self.assertEqual(result["problems"], [])

    def test_lookalike_rejected(self):
        fake = {"name": "rea-agents", "version": "6.7.0", "license": "MIT",
                "repository": {"url": "https://github.com/example/rea-fork.git"}}
        result = rea_installation.verify_package_identity(fake, "6.7.0")
        self.assertFalse(result["accepted"])
        self.assertTrue(any("morluto/rea" in p for p in result["problems"]))

    def test_unpinned_version_rejected(self):
        drifted = dict(GOOD, version="9.9.9")
        result = rea_installation.verify_package_identity(drifted, "6.7.0")
        self.assertFalse(result["accepted"])

    def test_doctor_classification(self):
        result = rea_installation.summarize_doctor(DOCTOR)
        self.assertEqual(result["healthy"], ["node", "ghidra"])
        self.assertEqual(result["missing"], ["hopper"])
        self.assertIsNone(result["session_connected"])

    def test_recovery_ladder(self):
        result = rea_installation.remedy_for("engine_missing")
        self.assertIn("static readers", result["remedy"])
        unknown = rea_installation.remedy_for("something_new")
        self.assertIsNone(unknown["remedy"])


if __name__ == "__main__":
    unittest.main()
