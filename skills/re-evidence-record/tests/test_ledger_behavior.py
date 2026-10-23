"""Behavioral tests for the evidence ledger implementation."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import ledger as ledger_mod


def _frida_evidence(led):
    return led.add_evidence(ledger_mod.make_evidence(
        "instrument_with_frida", "cd" * 32, {"stdout": "L=1000 R=600"},
        authority="external-service", confidence="observed"))


class LedgerBehaviorTests(unittest.TestCase):
    def test_evidence_ids_are_content_addressed(self):
        record = ledger_mod.make_evidence(
            "inspect_sqlite_database", "ab" * 32, {"tables": ["t"]},
            authority="shipped-artifact", confidence="observed")
        self.assertTrue(record["evidence_id"].startswith("ev_"))
        self.assertEqual(len(record["evidence_id"]), 67)
        again = ledger_mod.make_evidence(
            "inspect_sqlite_database", "ab" * 32, {"tables": ["t"]},
            authority="shipped-artifact", confidence="observed")
        self.assertEqual(record["evidence_id"], again["evidence_id"])

    def test_full_unknown_lifecycle_verifies(self):
        led = ledger_mod.Ledger()
        ev = _frida_evidence(led)
        unknown = led.record_unknown("Which taper ships?", "behavioral", "medium",
                                     "external-service", "observed")
        updated = led.update_unknown(
            unknown["unknown_id"], 1, "resolved",
            supporting_evidence_ids=[ev["evidence_id"]],
            resolution={"disposition": "verified", "rationale": "stdout matches linear taper"})
        self.assertEqual(updated["revision"], 2)
        result = led.verify_resolution(unknown["unknown_id"])
        self.assertTrue(result["valid"])
        self.assertTrue(result["truthVerified"])

    def test_unqualified_authority_cannot_resolve(self):
        led = ledger_mod.Ledger()
        static_ev = led.add_evidence(ledger_mod.make_evidence(
            "inspect_binary_layout", "ef" * 32, {"sections": []},
            authority="shipped-artifact", confidence="observed"))
        unknown = led.record_unknown("Runtime behavior?", "behavioral", "high",
                                     "external-service", "observed")
        with self.assertRaises(ValueError):
            led.update_unknown(unknown["unknown_id"], 1, "resolved",
                               supporting_evidence_ids=[static_ev["evidence_id"]],
                               resolution={"disposition": "verified", "rationale": "looks right"})

    def test_stale_revision_rejected(self):
        led = ledger_mod.Ledger()
        ev = _frida_evidence(led)
        unknown = led.record_unknown("Q?", "behavioral", "low", "external-service", "observed")
        led.update_unknown(unknown["unknown_id"], 1, "investigating",
                           supporting_evidence_ids=[ev["evidence_id"]])
        with self.assertRaises(ValueError):
            led.update_unknown(unknown["unknown_id"], 1, "resolved",
                               supporting_evidence_ids=[ev["evidence_id"]],
                               resolution={"disposition": "verified", "rationale": "x"})

    def test_statement_classification_enforced(self):
        led = ledger_mod.Ledger()
        with self.assertRaises(ValueError):
            led.classify_statement("observation", "it printed X")
        result = led.classify_statement("inference", "probably linear", basis_ids=["ev_x"])
        self.assertEqual(result["class"], "inference")

    def test_closeout_reports_open_unknowns(self):
        led = ledger_mod.Ledger()
        unknown = led.record_unknown("Open?", "behavioral", "low", "external-service", "observed")
        output = led.closeout([{"question": "Open?", "unknown_id": unknown["unknown_id"]}])
        self.assertFalse(output["complete"])
        self.assertEqual(output["rows"][0]["status"], "unresolved")
        self.assertEqual(output["open_unknowns"], [unknown["unknown_id"]])


if __name__ == "__main__":
    unittest.main()
