import unittest
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from chunk_engine import SequentialThinkingEngine, ThoughtStep


class TestChunkPower(unittest.TestCase):
    def setUp(self):
        self.engine = SequentialThinkingEngine("test_session")

    def test_add_thought_and_sequence(self):
        step1 = self.engine.add_thought("Step 1: Frame the core invariant.", 3, confidence=0.9)
        self.assertEqual(step1.thought_number, 1)
        self.assertEqual(step1.branch_id, "main")
        self.assertEqual(len(self.engine.history), 1)

    def test_revision_and_branching(self):
        self.engine.add_thought("Initial assumption.", 4, confidence=0.6)
        rev = self.engine.add_thought("Corrected assumption based on AST.", 4, is_revision=True, revises_thought=1, confidence=0.95)
        self.assertTrue(rev.is_revision)
        self.assertEqual(rev.revises_thought, 1)

        branch_step = self.engine.add_thought("Explore edge case path.", 4, branch_id="edge-case-alpha", confidence=0.88)
        self.assertEqual(branch_step.branch_id, "edge-case-alpha")
        self.assertIn("edge-case-alpha", self.engine.branches)

    def test_synthesis_and_provenance_hash(self):
        self.engine.add_thought("Thought 1", 2, confidence=0.9)
        self.engine.add_thought("Thought 2", 2, confidence=1.0, epistemic_tier="L2_Behavior", next_action="Seal receipt")
        summary = self.engine.synthesize()
        self.assertEqual(summary["status"], "synthesized")
        self.assertEqual(summary["total_steps"], 2)
        self.assertEqual(summary["average_confidence"], 0.95)
        self.assertTrue(len(summary["provenance_hash"]) == 64)

    def test_skill_manifest(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: chunk-power", skill_md)
        self.assertIn("description:", skill_md)


if __name__ == "__main__":
    unittest.main()
