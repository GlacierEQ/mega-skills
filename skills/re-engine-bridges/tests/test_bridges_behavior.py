"""Behavioral tests for engine-bridge readiness and selection."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import bridges


def _ghidra_diag(java_detail, java_ok):
    return {
        "provider_version": "12.1.2",
        "checks": [
            {"name": "installation", "ok": True, "detail": "/opt/ghidra"},
            {"name": "headless", "ok": True, "detail": "/opt/ghidra/support/analyzeHeadless"},
            {"name": "native_decompiler", "ok": True, "detail": "elf x86_64"},
            {"name": "version", "ok": True, "detail": "12.1.2"},
            {"name": "java", "ok": java_ok, "detail": java_detail},
        ],
    }


class BridgesBehaviorTests(unittest.TestCase):
    def test_jre_rejected_at_open_time(self):
        result = bridges.assess_ghidra(_ghidra_diag("21.0.13; 64-bit; runtime only; /opt/jre", False))
        self.assertFalse(result["ready"])
        self.assertTrue(any("full JDK" in b for b in result["blockers"]))

    def test_full_jdk_ready(self):
        result = bridges.assess_ghidra(_ghidra_diag("21.0.13; 64-bit; full JDK", True))
        self.assertTrue(result["ready"])
        self.assertEqual(result["version"], "12.1.2")

    def test_static_questions_do_not_escalate(self):
        result = bridges.select_provider("strings", [])
        self.assertEqual(result["provider"], "rea_static_readers")
        self.assertFalse(result["escalation"])

    def test_pseudocode_without_engine_records_unknown(self):
        result = bridges.select_provider("pseudocode", [])
        self.assertIsNone(result["provider"])
        self.assertTrue(result["escalation"])
        with_ghidra = bridges.select_provider("pseudocode", ["ghidra"])
        self.assertEqual(with_ghidra["provider"], "ghidra")


if __name__ == "__main__":
    unittest.main()
