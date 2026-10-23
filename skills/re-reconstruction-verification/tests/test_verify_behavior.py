"""Behavioral tests for reconstruction verification semantics."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import verify_recon


class VerifyBehaviorTests(unittest.TestCase):
    def test_full_coverage_conformance(self):
        events = [{"event": "output", "stream": "stdout"},
                  {"event": "exit", "code": 0},
                  {"event": "settlement", "state": "quiesced"}]
        predicates = [{"event": "output"}, {"event": "exit"}, {"event": "settlement"}]
        result = verify_recon.check_trace_conformance(events, predicates)
        self.assertTrue(result["conforms"])
        partial = verify_recon.check_trace_conformance(events, predicates[:2])
        self.assertFalse(partial["conforms"])
        self.assertEqual(partial["uncovered"][0]["index"], 2)

    def test_claim_passes_when_clean(self):
        comparison = {"dimensions": {"terminal": "unchanged"}, "residual_unknown_ids": []}
        claims = [{"claim_id": "c1", "kind": "behavioral", "dimension": "terminal",
                   "predicate": "terminal output equivalent", "unknown_ids": []}]
        result = verify_recon.verify_claims(comparison, claims)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["summary"], {"passed": 1, "failed": 0, "unknown": 0})

    def test_residual_unknown_blocks_promotion(self):
        comparison = {"dimensions": {"exit": "unchanged"},
                      "residual_unknown_ids": ["unk_fs"]}
        claims = [{"claim_id": "exit-behavior", "kind": "behavioral", "dimension": "exit",
                   "predicate": "exit behavior equivalent", "unknown_ids": ["unk_fs"]}]
        result = verify_recon.verify_claims(comparison, claims)
        claim = result["claims"][0]
        self.assertEqual(claim["status"], "unknown")
        self.assertEqual(claim["observed_status"], "unchanged")
        self.assertEqual(claim["blocking_unknowns"], ["unk_fs"])
        self.assertEqual(result["status"], "unknown")

    def test_changed_dimension_fails(self):
        comparison = {"dimensions": {"terminal": "changed"}, "residual_unknown_ids": []}
        claims = [{"claim_id": "t", "kind": "behavioral", "dimension": "terminal",
                   "predicate": "equivalent", "unknown_ids": []}]
        result = verify_recon.verify_claims(comparison, claims)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["claims"][0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
