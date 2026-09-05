"""
test_v13_layer.py — Tests for Packets 22-26 (v1.3.0: adaptive compression,
contract testing, model cascading, retrieval-augmented context, constitutional gate).
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import advanced as adv  # noqa: E402
import ml_routing  # noqa: E402


class TestAdaptiveCompression(unittest.TestCase):
    """Packet 22."""

    def test_reasoning_floor_for_reason_lane(self):
        b = adv.compute_token_budget("classify", "REASON", "x", 100, 0, 1.0)
        self.assertGreaterEqual(b, adv.REASONING_FLOOR)

    def test_classify_small_input_low_budget(self):
        b = adv.compute_token_budget("classify", "CODE-FAST", "x", 100, 0, 1.0)
        # classify base=256, easy diff=0.6, margin=1.2 -> 184, clamped to min 64
        self.assertGreaterEqual(b, 64)
        self.assertLessEqual(b, 1024)

    def test_plan_large_input_high_budget(self):
        b = adv.compute_token_budget("plan", "REASON", "x", 5000, 5, 1.0)
        # plan base=2048, hard diff=1.4+0.2+0.2=1.4, margin=1.2 -> 3440, clamped to max 8192
        self.assertGreater(b, 2000)
        self.assertLessEqual(b, 8192)

    def test_cap_enforced(self):
        b = adv.compute_token_budget("code_create", "REASON", "x", 10000, 10, 5.0)
        # cap at 8192 even with huge coef
        self.assertLessEqual(b, 8192)

    def test_reproducibility(self):
        b1 = adv.compute_token_budget("code_edit", "CODE", "x", 500, 0, 1.0)
        b2 = adv.compute_token_budget("code_edit", "CODE", "x", 500, 0, 1.0)
        self.assertEqual(b1, b2)


class TestContractTesting(unittest.TestCase):
    """Packet 23."""

    def setUp(self):
        self.contract = adv.Contract(
            contract_id="contract_test",
            module="src/lib/auth.ts",
            version="1.0.0",
            functions=[
                {
                    "name": "authenticate",
                    "params": [
                        {"name": "user", "type": "User"},
                        {"name": "token", "type": "str"},
                    ],
                    "returns": "Result<Session, AuthError>",
                    "raises": ["AuthError"],
                    "side_effects": [],
                },
                {
                    "name": "logout",
                    "params": [{"name": "session", "type": "Session"}],
                    "returns": "None",
                    "raises": [],
                    "side_effects": [],
                },
            ],
        )

    def test_signature_present(self):
        ok = adv.check_signature_in_contract(
            self.contract, "authenticate", ["user", "token"]
        )
        self.assertTrue(ok)

    def test_signature_absent(self):
        ok = adv.check_signature_in_contract(
            self.contract, "authenticate", ["user", "token", "extra"]
        )
        self.assertFalse(ok)

    def test_signature_unknown_function(self):
        ok = adv.check_signature_in_contract(self.contract, "doSomethingElse", ["x"])
        self.assertFalse(ok)

    def test_breaking_change_when_function_removed(self):
        new_fns = [
            {
                "name": "authenticate",
                "params": [{"name": "user", "type": "User"}],
                "returns": "Result<Session, AuthError>",
                "raises": ["AuthError"],
                "side_effects": [],
            }
        ]
        # logout removed -> breaking
        self.assertTrue(adv.is_breaking_change(self.contract, new_fns))

    def test_no_breaking_change_when_only_additions(self):
        new_fns = self.contract.functions + [
            {
                "name": "refresh",
                "params": [],
                "returns": "None",
                "raises": [],
                "side_effects": [],
            }
        ]
        self.assertFalse(adv.is_breaking_change(self.contract, new_fns))


class TestModelCascading(unittest.TestCase):
    """Packet 24."""

    def test_cascade_accepts_on_first_attempt(self):
        # Output length between 0.5x and 2x expected_length=200
        long_output = "def f():\n    return 42\n" * 5  # ~120 chars
        result = adv.run_cascade(
            "code_edit",
            output_at_lane={"CODE-FAST": long_output},
            cost_at_lane={"CODE-FAST": 0.05},
        )
        self.assertEqual(len(result.steps), 1)
        self.assertEqual(result.steps[0].decision, "accept")
        self.assertEqual(result.steps[0].lane, "CODE-FAST")

    def test_cascade_escalates_on_short_output(self):
        # CODE-FAST too short, escalate to CODE which is acceptable length
        result = adv.run_cascade(
            "code_edit",
            output_at_lane={"CODE-FAST": "x", "CODE": "def f():\n    return 42\n" * 5},
            cost_at_lane={"CODE-FAST": 0.05, "CODE": 0.20},
        )
        self.assertGreater(len(result.steps), 1)
        self.assertEqual(result.final_lane, "CODE")
        self.assertEqual(result.steps[1].decision, "accept")

    def test_cascade_stops_at_max_depth(self):
        result = adv.run_cascade(
            "code_edit",
            output_at_lane={lane: "x" for lane in adv.CASCADE_CHAINS["code_edit"]},
            cost_at_lane={lane: 0.10 for lane in adv.CASCADE_CHAINS["code_edit"]},
        )
        self.assertLessEqual(len(result.steps), adv.MAX_CASCADE_DEPTH)

    def test_cascade_self_deprecation_triggers_escalation(self):
        result = adv.run_cascade(
            "code_edit",
            output_at_lane={
                "CODE-FAST": "I don't know how to do this",
                "CODE": "def f():\n    return 42",
            },
            cost_at_lane={"CODE-FAST": 0.05, "CODE": 0.20},
        )
        # Self-deprecation -> confidence 0.2 < floor 0.8 -> escalate
        self.assertGreater(len(result.steps), 1)

    def test_confidence_zero_for_empty_output(self):
        c = adv.compute_confidence("", expected_length=100, l2_proof=True)
        self.assertEqual(c, 0.0)

    def test_confidence_zero_for_no_l2(self):
        c = adv.compute_confidence("any output", expected_length=100, l2_proof=False)
        self.assertEqual(c, 0.0)


class TestRetrievalAugmentedContext(unittest.TestCase):
    """Packet 25."""

    def test_recall_empty_memory_returns_empty(self):
        self.assertEqual(adv.recall_similar("test", memory=None), [])

    def test_recall_respects_threshold(self):
        # Mock memory
        class M:
            def recall_similar(self, intent, k):
                return [
                    {"mission_id": "m1", "score": 0.95, "summary_ref": "s1"},
                    {"mission_id": "m2", "score": 0.75, "summary_ref": "s2"},
                ]

        r = adv.recall_similar("test", memory=M(), k=2, threshold=0.80)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].mission_id, "m1")

    def test_recall_top_k(self):
        class M:
            def recall_similar(self, intent, k):
                return [
                    {"mission_id": f"m{i}", "score": 0.95, "summary_ref": "s"}
                    for i in range(k)
                ]

        r = adv.recall_similar("test", memory=M(), k=3)
        self.assertEqual(len(r), 3)
        ids = [x.mission_id for x in r]
        self.assertEqual(ids, ["m0", "m1", "m2"])

    def test_format_rag_context(self):
        r = [adv.Recall(mission_id="m1", similarity=0.95, summary="summary text")]
        out = adv.format_rag_context(r)
        self.assertIn("[RECALL mission_id=m1", out)
        self.assertIn("summary text", out)
        self.assertIn("[/RECALL]", out)

    def test_format_rag_empty(self):
        self.assertEqual(adv.format_rag_context([]), "")


class TestConstitutionalGate(unittest.TestCase):
    """Packet 26 — critical for AGENTS.md §0 compliance."""

    def test_blocks_sovereign_master(self):
        v = adv.check_constitution("We are the sovereign master of this codebase.")
        ids = [x.rule_id for x in v]
        self.assertIn("C-1", ids)

    def test_blocks_highest_authority(self):
        v = adv.check_constitution("This is the highest authority on the topic.")
        ids = [x.rule_id for x in v]
        self.assertIn("C-2", ids)

    def test_blocks_stubs(self):
        v = adv.check_constitution("def f():\n    return True")
        ids = [x.rule_id for x in v]
        self.assertIn("C-3", ids)

    def test_blocks_todo(self):
        v = adv.check_constitution("# TODO: implement this")
        ids = [x.rule_id for x in v]
        self.assertIn("C-3", ids)

    def test_blocks_trust_the_model(self):
        v = adv.check_constitution("I'll just trust the model on this one.")
        ids = [x.rule_id for x in v]
        self.assertIn("C-5", ids)

    def test_blocks_clobber(self):
        v = adv.check_constitution("We should clobber the upstream main branch.")
        ids = [x.rule_id for x in v]
        self.assertIn("C-10", ids)

    def test_allows_holographic_mesh_vocabulary(self):
        v = adv.check_constitution(
            "The Holographic Mesh orchestrates many nodes. No single winner. "
            "Elite. pro. Hard. G. Verify before claim. "
            "Receipt chain hash: abc123. Receipt verified."
        )
        # No BLOCKER should fire
        blocker_ids = [x.rule_id for x in v]
        self.assertEqual(blocker_ids, [])

    def test_warn_rules_do_not_block(self):
        # C-6 is WARN, should not appear in violations
        v = adv.check_constitution("This is enterprise-grade code.")
        ids = [x.rule_id for x in v]
        self.assertNotIn("C-6", ids)

    def test_blocks_i_will_do_later(self):
        v = adv.check_constitution("I'll do that later.")
        ids = [x.rule_id for x in v]
        self.assertIn("C-9", ids)

    def test_constitution_has_10_rules(self):
        self.assertEqual(len(adv.DEFAULT_CONSTITUTION), 10)


if __name__ == "__main__":
    unittest.main()
