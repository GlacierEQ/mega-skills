"""
test_advanced_layer.py — Tests for Packets 17-21 (cutting-edge dev techniques).
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


class TestSpeculativeDecoding(unittest.TestCase):
    """Packet 17."""

    def test_can_speculate_when_verifier_better(self):
        self.assertTrue(adv.can_speculate(draft_trust=0.5, verify_trust=0.92))
        self.assertFalse(adv.can_speculate(draft_trust=0.92, verify_trust=0.92))

    def test_can_speculate_respects_threshold(self):
        cfg = adv.SpeculationConfig(trust_threshold=0.2)
        # With threshold 0.2, need verify >= draft + 0.2
        self.assertTrue(adv.can_speculate(0.5, 0.71, cfg))
        self.assertFalse(adv.can_speculate(0.5, 0.69, cfg))

    def test_use_verify_when_fast_and_l2(self):
        d = adv.speculation_decision(200, 1500, True, True)
        self.assertEqual(d, "use_verify")

    def test_use_draft_when_verify_slow(self):
        d = adv.speculation_decision(500, 3000, True, True)
        self.assertEqual(d, "use_draft_unverified")

    def test_block_timeout_when_both_slow(self):
        d = adv.speculation_decision(3000, 5000, True, True)
        self.assertEqual(d, "block_timeout")

    def test_block_when_l2_missing(self):
        d = adv.speculation_decision(100, 100, True, False)
        # verify not l2, draft is, draft under SLA -> draft unverified
        self.assertEqual(d, "use_draft_unverified")
        d = adv.speculation_decision(100, 100, False, True)
        # verify l2, under SLA -> verify
        self.assertEqual(d, "use_verify")


class TestSemanticCache(unittest.TestCase):
    """Packet 18."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="scache_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_store_and_lookup_hit(self):
        cache = adv.SemanticCache(root=self.tmp)
        v1 = ml_routing.embed_intent("rewrite warp terminal")
        v2 = ml_routing.embed_intent("rewrite warp terminal")
        receipt = {
            "lane": "CODE",
            "task_type": "code_edit",
            "l2_proof": True,
            "result": "ok",
        }
        cache.store("CODE", "code_edit", v1, receipt)
        hit = cache.lookup("CODE", "code_edit", v2, threshold=0.95)
        self.assertIsNotNone(hit)
        self.assertEqual(hit[0]["result"], "ok")
        self.assertEqual(hit[1], 1.0)  # identical vectors

    def test_lookup_miss_for_different_intent(self):
        cache = adv.SemanticCache(root=self.tmp)
        v1 = ml_routing.embed_intent("alpha")
        v2 = ml_routing.embed_intent("beta zebra quantum flux")
        cache.store(
            "CODE", "code_edit", v1, {"lane": "CODE", "l2_proof": True, "result": "ok"}
        )
        hit = cache.lookup("CODE", "code_edit", v2, threshold=0.95)
        self.assertIsNone(hit)

    def test_lane_scoped_cache(self):
        cache = adv.SemanticCache(root=self.tmp)
        v = ml_routing.embed_intent("any")
        cache.store(
            "CODE", "code_edit", v, {"lane": "CODE", "l2_proof": True, "result": "ok"}
        )
        hit = cache.lookup(
            "VERIFY", "code_edit", v, threshold=0.0
        )  # even with threshold 0
        self.assertIsNone(hit, "G3: cache is lane-scoped")

    def test_ttl_expiry(self):
        cache = adv.SemanticCache(root=self.tmp)
        # Manually create an expired entry
        v = ml_routing.embed_intent("test")
        cache.store(
            "CODE", "code_edit", v, {"lane": "CODE", "l2_proof": True, "result": "ok"}
        )
        # Tamper with the file to set ts far in the past
        for ef in (cache.root / "entries").glob("*.json"):
            data = json.loads(ef.read_text())
            data["ts"] = data["ts"] - 1000 * 3600  # 1000h ago
            ef.write_text(json.dumps(data))
        hit = cache.lookup("CODE", "code_edit", v, threshold=0.0)
        self.assertIsNone(hit, "G2: expired entries are misses")

    def test_key_is_deterministic(self):
        cache = adv.SemanticCache(root=self.tmp)
        v = ml_routing.embed_intent("test")
        k1 = cache.make_key("CODE", "code_edit", v)
        k2 = cache.make_key("CODE", "code_edit", v)
        self.assertEqual(k1, k2)
        # Different lane -> different key
        k3 = cache.make_key("VERIFY", "code_edit", v)
        self.assertNotEqual(k1, k3)


class TestDAGScheduler(unittest.TestCase):
    """Packet 19."""

    def test_dag_with_no_cycle(self):
        nodes = {
            "A": adv.DAGNode(id="A", lane="CODE", gate="L2"),
            "B": adv.DAGNode(id="B", lane="VERIFY", gate="L2", depends_on=["A"]),
            "C": adv.DAGNode(id="C", lane="REVIEW", gate="L2", depends_on=["A"]),
            "D": adv.DAGNode(id="D", lane="FUSE", gate="FUSE", depends_on=["B", "C"]),
        }
        self.assertFalse(adv.detect_cycles(nodes))
        waves = adv.schedule_dag(nodes, max_parallel=2)
        self.assertEqual(len(waves), 3)
        self.assertEqual(waves[0], ["A"])
        self.assertEqual(waves[1], ["B", "C"])
        self.assertEqual(waves[2], ["D"])

    def test_cycle_detected(self):
        # A -> B -> A is a cycle
        nodes = {
            "A": adv.DAGNode(id="A", lane="CODE", gate="L2", depends_on=["B"]),
            "B": adv.DAGNode(id="B", lane="VERIFY", gate="L2", depends_on=["A"]),
        }
        self.assertTrue(adv.detect_cycles(nodes))
        with self.assertRaises(ValueError) as ctx:
            adv.schedule_dag(nodes)
        self.assertIn("F-DEC-01", str(ctx.exception))

    def test_concurrency_cap(self):
        # 8 ready nodes, cap 3 -> 3 in first wave
        nodes = {
            f"N{i}": adv.DAGNode(id=f"N{i}", lane="CODE", gate="L2") for i in range(8)
        }
        waves = adv.schedule_dag(nodes, max_parallel=3)
        self.assertEqual(len(waves[0]), 3)
        # Total dispatched = 8
        total = sum(len(w) for w in waves)
        self.assertEqual(total, 8)

    def test_block_propagation(self):
        # B depends on A. If A fails, B is BLOCKED.
        nodes = {
            "A": adv.DAGNode(id="A", lane="CODE", gate="L2"),
            "B": adv.DAGNode(id="B", lane="VERIFY", gate="L2", depends_on=["A"]),
        }
        # Simulate A failing
        nodes["A"].status = "FAILED"
        blocked = adv.propagate_block(nodes, "A")
        self.assertIn("B", blocked)
        self.assertEqual(nodes["B"].status, "BLOCKED")
        self.assertIn("upstream_failure:A", nodes["B"].cause)

    def test_deterministic_wave_order(self):
        # Same DAG, two runs -> same waves
        def make_dag():
            return {
                "A": adv.DAGNode(id="A", lane="CODE", gate="L2"),
                "B": adv.DAGNode(id="B", lane="VERIFY", gate="L2", depends_on=["A"]),
                "C": adv.DAGNode(id="C", lane="REVIEW", gate="L2", depends_on=["A"]),
                "D": adv.DAGNode(
                    id="D", lane="FUSE", gate="FUSE", depends_on=["B", "C"]
                ),
            }

        w1 = adv.schedule_dag(make_dag(), max_parallel=4)
        w2 = adv.schedule_dag(make_dag(), max_parallel=4)
        self.assertEqual(w1, w2)


class TestPropertyBasedTesting(unittest.TestCase):
    """Packet 20."""

    def test_idempotence_property_passes_on_sorted(self):
        prop = adv.Property(
            name="sorted_idempotent",
            func=lambda x: sorted(sorted(x)) == sorted(x),
            description="sorted is idempotent",
        )
        examples = [[3, 1, 2], [1], [], [5, 5, 5], [9, 8, 7, 6]]
        passed, falsifier, n = adv.run_property(prop, examples, shrink=False)
        self.assertTrue(passed)
        self.assertIsNone(falsifier)

    def test_property_finds_falsifier(self):
        # Property that claims x + 1 == x (always false)
        prop = adv.Property(
            name="broken",
            func=lambda x: x + 1 == x,
            description="claim x+1==x (wrong)",
        )
        passed, falsifier, n = adv.run_property(prop, [1, 2, 3], shrink=False)
        self.assertFalse(passed)
        self.assertEqual(falsifier, 1)

    def test_shrinking_finds_minimal_falsifier(self):
        # Property: "" is not in "abc"  -> false; minimal counterexample is ""
        prop = adv.Property(
            name="empty_in_abc",
            func=lambda x: "" not in x,
            description="empty not in x (wrong for strings)",
        )
        passed, falsifier, n = adv.run_property(prop, ["abc"], shrink=True)
        self.assertFalse(passed)
        # Shrink should find the smallest
        self.assertEqual(falsifier, "")

    def test_detect_properties_from_signatures(self):
        sigs = [("sorted", "list -> list"), ("reversed", "list -> list")]
        props = adv.detect_properties("subject", sigs)
        names = {p.name for p in props}
        self.assertTrue(any("sorted" in n for n in names))
        self.assertTrue(any("reversed" in n for n in names))


class TestMutationTesting(unittest.TestCase):
    """Packet 21."""

    def test_mutation_score_calculation(self):
        results = [
            adv.MutationResult(operator="AOR", site="0", killed=True),
            adv.MutationResult(operator="AOR", site="1", killed=False),
            adv.MutationResult(operator="ROR", site="0", killed=True),
        ]
        self.assertAlmostEqual(adv.mutation_score(results), 2 / 3)

    def test_mutation_score_target(self):
        # Below target = F-VER-02
        self.assertFalse(adv.should_pass_mutation_gate(0.5, target=0.8))
        # At target = pass
        self.assertTrue(adv.should_pass_mutation_gate(0.8, target=0.8))
        # Above target = pass
        self.assertTrue(adv.should_pass_mutation_gate(0.9, target=0.8))

    def test_all_operators_applied(self):
        # Mutator must be able to apply any of the 8 operators
        source = "x = 0\nif x < 1:\n    return x"
        for op in adv.MUTATION_OPERATORS:
            mutated = adv.apply_simple_mutation(source, op, 0)
            self.assertIsInstance(mutated, str)

    def test_mutation_score_zero_for_all_surviving(self):
        results = [
            adv.MutationResult(operator="AOR", site=str(i), killed=False)
            for i in range(5)
        ]
        self.assertEqual(adv.mutation_score(results), 0.0)

    def test_mutation_score_one_for_all_killed(self):
        results = [
            adv.MutationResult(operator="AOR", site=str(i), killed=True)
            for i in range(5)
        ]
        self.assertEqual(adv.mutation_score(results), 1.0)


if __name__ == "__main__":
    unittest.main()
