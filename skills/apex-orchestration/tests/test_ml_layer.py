"""
test_ml_layer.py — Tests for Packets 13, 14, 15, 16 (ML/self-improving layer).
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

import ml_routing  # noqa: E402


class TestEmbeddingMemory(unittest.TestCase):
    """Packet 15: Embedding Memory."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="emb_"))
        self.mem = ml_routing.EmbeddingMemory(root=self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_deterministic_embedding(self):
        v1 = ml_routing.embed_intent("rewrite warp terminal")
        v2 = ml_routing.embed_intent("rewrite warp terminal")
        self.assertEqual(v1, v2, "G1 determinism gate violated")

    def test_embedding_dimension_and_unit_norm(self):
        v = ml_routing.embed_intent("test")
        self.assertEqual(len(v), ml_routing.EMBEDDING_DIM)
        norm = sum(x * x for x in v) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=5)

    def test_different_text_different_embedding(self):
        v1 = ml_routing.embed_intent("alpha")
        v2 = ml_routing.embed_intent("beta")
        self.assertNotEqual(v1, v2)

    def test_cosine_in_range(self):
        v1 = ml_routing.embed_intent("a")
        v2 = ml_routing.embed_intent("b")
        c = ml_routing.cosine(v1, v2)
        self.assertGreaterEqual(c, -1.0)
        self.assertLessEqual(c, 1.0)

    def test_store_and_recall_roundtrip(self):
        rec = self.mem.store(
            "mission_001",
            "fix authentication bug",
            "summary text",
            ["apex", "delivered"],
        )
        self.assertEqual(rec["schema_version"], 1)
        recs = self.mem.recall_similar("fix auth bug", k=1)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["mission_id"], "mission_001")
        # The exact-match query should score high
        self.assertGreater(recs[0]["score"], 0.0)

    def test_recall_with_domain_tag_filter(self):
        self.mem.store("mission_001", "fix auth", "s1", ["apex", "medical"])
        self.mem.store("mission_002", "fix auth", "s2", ["apex", "finance"])
        recs = self.mem.recall_similar("fix auth", k=10, domain_tag="medical")
        ids = [r["mission_id"] for r in recs]
        self.assertIn("mission_001", ids)
        self.assertNotIn("mission_002", ids)

    def test_unknown_schema_version_rejected(self):
        # Write a record with bogus schema_version
        idx = self.tmp / "index.jsonl"
        idx.write_text(
            json.dumps(
                {
                    "mission_id": "x",
                    "ts": "2026-01-01T00:00:00Z",
                    "embedding_ref": "vectors/x.f32",
                    "summary_ref": "summaries/x.md",
                    "tags": [],
                    "schema_version": 999,
                    "intent_text": "x",
                }
            )
            + "\n"
        )
        recs = self.mem.recall_similar("x")
        self.assertEqual(recs, [])


class TestMLRouting(unittest.TestCase):
    """Packet 13: ML Routing."""

    def test_hard_rule_medical(self):
        _, lane, _ = ml_routing.select_lane(
            {"domain": "medical", "kind": "code_edit"}, learned_state={}
        )
        self.assertEqual(lane, "DOMAIN-MED")

    def test_hard_rule_finance(self):
        _, lane, _ = ml_routing.select_lane({"domain": "finance"}, learned_state={})
        self.assertEqual(lane, "DOMAIN-FIN")

    def test_hard_rule_multimodal(self):
        _, lane, _ = ml_routing.select_lane(
            {"input_modality": "image"}, learned_state={}
        )
        self.assertEqual(lane, "NANO-PERCEPTION")

    def test_hard_rule_longctx(self):
        _, lane, _ = ml_routing.select_lane({"input_tokens": 750000}, learned_state={})
        self.assertEqual(lane, "LONG-CTX")

    def test_hard_rule_plan(self):
        _, lane, _ = ml_routing.select_lane(
            {"kind": "plan", "invariants": 4}, learned_state={}
        )
        self.assertEqual(lane, "REASON")

    def test_default_route(self):
        _, lane, _ = ml_routing.select_lane({"kind": "weird"}, learned_state={})
        self.assertEqual(lane, "ROUTER-FREE")

    def test_score_reproducibility(self):
        """G2: same state, same score."""
        state = {
            "CODE": ml_routing.LaneStats(
                lane="CODE", success=8, total=10, latencies_ms=[100, 200, 300]
            )
        }
        s1 = ml_routing.select_lane({"kind": "code_edit"}, state)
        s2 = ml_routing.select_lane({"kind": "code_edit"}, state)
        self.assertEqual(s1, s2, "G2 reproducibility gate violated")

    def test_quota_burn_returns_neg_infinity(self):
        """G5: lane with quota_burn >= 1.0 is excluded."""
        state = {
            "CODE": ml_routing.LaneStats(
                lane="CODE", success=10, total=10, quota_burn=1.0
            )
        }
        _, _, score = ml_routing.select_lane(
            {"kind": "code_edit", "domain": "x"}, state
        )
        self.assertEqual(score, float("-inf"))


class TestHebbianUpdate(unittest.TestCase):
    """Packet 16: Self-improving loop."""

    def test_hebbian_success_increases_weight(self):
        w = {"CODE": 0.5, "REASON": 0.5}
        # gamma=0.95 applies 5% decay to non-target
        new = ml_routing.hebbian_update(w, "CODE", "success", eta=0.1, gamma=0.95)
        self.assertGreater(new["CODE"], 0.5)
        # Decay applied to non-target (REASON)
        self.assertLess(new["REASON"], 0.5)

    def test_hebbian_failure_decreases_weight(self):
        w = {"CODE": 0.5}
        new = ml_routing.hebbian_update(w, "CODE", "fail", eta=0.1, gamma=1.0)
        self.assertLess(new["CODE"], 0.5)

    def test_hebbian_clamps_to_bounds(self):
        w = {"CODE": 0.99}
        new = ml_routing.hebbian_update(w, "CODE", "success", eta=0.5, gamma=1.0)
        self.assertLessEqual(new["CODE"], 1.0)
        w = {"CODE": 0.01}
        new = ml_routing.hebbian_update(w, "CODE", "fail", eta=0.5, gamma=1.0)
        self.assertGreaterEqual(new["CODE"], 0.0)

    def test_commit_weights_writes_atomic_file(self):
        tmp = Path(tempfile.mkdtemp(prefix="commit_"))
        try:
            # Override state root to tmp
            ml_routing.DEFAULT_STATE_ROOT = tmp
            try:
                v = ml_routing.commit_weights({"w1": 0.3, "w2": 0.2}, "1.0.0")
                self.assertTrue((tmp / "weights" / f"{v}.json").exists())
                self.assertTrue((tmp / "weights" / "CURRENT.json").exists())
                cur = json.loads((tmp / "weights" / "CURRENT.json").read_text())
                self.assertEqual(cur["active"], v)
            finally:
                ml_routing.DEFAULT_STATE_ROOT = (
                    Path.home() / ".local/share/apex-orchestration"
                )
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_rollback_to_prior_version(self):
        tmp = Path(tempfile.mkdtemp(prefix="rollback_"))
        try:
            ml_routing.DEFAULT_STATE_ROOT = tmp
            try:
                v1 = ml_routing.commit_weights({"w1": 0.3}, "0.0.0")
                v2 = ml_routing.commit_weights({"w1": 0.5}, v1)
                ok = ml_routing.rollback_to(v1)
                self.assertTrue(ok)
                cur = json.loads((tmp / "weights" / "CURRENT.json").read_text())
                self.assertEqual(cur["active"], v1)
            finally:
                ml_routing.DEFAULT_STATE_ROOT = (
                    Path.home() / ".local/share/apex-orchestration"
                )
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestRegressionCheck(unittest.TestCase):
    """Packet 16 G1: regression gate."""

    def test_empty_decisions_passes(self):
        ok, ratio = ml_routing.regression_check([], new_weights={}, learned_state={})
        self.assertTrue(ok)
        self.assertEqual(ratio, 1.0)

    def test_all_matching_passes(self):
        decisions = [
            ml_routing.RoutingDecision("s1", "R-CODE-EDIT", "CODE", 0.9)
            for _ in range(10)
        ]
        ok, ratio = ml_routing.regression_check(decisions, {}, {})
        self.assertTrue(ok)
        self.assertEqual(ratio, 1.0)


if __name__ == "__main__":
    unittest.main()
