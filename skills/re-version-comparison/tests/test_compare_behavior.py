"""Behavioral tests for version-comparison discipline."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import compare


class CompareBehaviorTests(unittest.TestCase):
    def test_inventory_diff_counts(self):
        left = [{"path": "a.js", "sha256": "1"}, {"path": "b.js", "sha256": "2"},
                {"path": "c.js", "sha256": "3"}]
        right = [{"path": "a.js", "sha256": "1"}, {"path": "b.js", "sha256": "9"},
                 {"path": "d.js", "sha256": "4"}]
        result = compare.diff_inventories(left, right)
        self.assertEqual(result["added"], ["d.js"])
        self.assertEqual(result["removed"], ["c.js"])
        self.assertEqual(result["changed"], ["b.js"])
        self.assertEqual(result["unchanged"], ["a.js"])
        self.assertEqual(result["summary"], {"added": 1, "removed": 1, "changed": 1, "unchanged": 1})

    def test_partial_inputs_refused(self):
        with self.assertRaises(ValueError):
            compare.require_complete([{"summary_only": True}])
        with self.assertRaises(ValueError):
            compare.require_complete([{"evidence_id": "ev_x"}])
        compare.require_complete([{"normalized_result": {"status": "changed"}}])

    def test_artifact_comparison_cannot_support_behavior_claim(self):
        comparison = {"comparison_class": "artifact", "dimensions": {"membership": "changed"}}
        result = compare.check_claim_scope(comparison, "behavior")
        self.assertFalse(result["supported"])
        process = {"comparison_class": "process", "dimensions": {"terminal": "changed"}}
        result = compare.check_claim_scope(process, "behavior")
        self.assertTrue(result["supported"])

    def test_promotion_requires_runtime_corroboration(self):
        static_cmp = [{"dimensions": {"pseudocode": "changed", "terminal_note": "changed"}}]
        result = compare.find_changed_behavior(static_cmp, [])
        self.assertEqual(result["static_candidates"], 2)
        self.assertEqual(result["observed_changes"], 0)
        self.assertEqual(result["unresolved"], 2)
        runtime = [{"dimensions": {"pseudocode": "changed"}}]
        result = compare.find_changed_behavior(static_cmp, runtime)
        self.assertEqual(result["observed_changes"], 1)


if __name__ == "__main__":
    unittest.main()
