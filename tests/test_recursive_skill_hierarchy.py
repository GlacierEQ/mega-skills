from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_hierarchy import detect_compound_cycle, validate_composition_graph  # noqa: E402


class RecursiveSkillHierarchyTests(unittest.TestCase):
    def test_nested_compound_skill_is_valid(self):
        data = {"entries": [{"id": "inner", "members": [{"id": "alpha", "kind": "skill"}, {"id": "beta", "kind": "skill"}]}, {"id": "outer", "members": [{"id": "inner", "kind": "compound-skill"}, {"id": "gamma", "kind": "skill"}]}]}
        resolved = validate_composition_graph(data, {"alpha", "beta", "gamma"}, set())
        self.assertEqual(resolved, {"inner", "outer"})

    def test_recursive_cycle_is_rejected(self):
        data = {"entries": [{"id": "alpha-flow", "members": [{"id": "beta-flow", "kind": "compound-skill"}]}, {"id": "beta-flow", "members": [{"id": "alpha-flow", "kind": "compound-skill"}]}]}
        with self.assertRaisesRegex(ValueError, "compound-skill cycle"):
            validate_composition_graph(data, set(), set())

    def test_unresolved_owned_reference_is_rejected(self):
        data = {"entries": [{"id": "outer", "members": [{"id": "missing", "kind": "compound-skill"}]}]}
        with self.assertRaisesRegex(ValueError, "does not resolve as Compound Skill"):
            validate_composition_graph(data, set(), set())

    def test_cycle_detector_returns_exact_path(self):
        graph = {"a": ["b"], "b": ["c"], "c": ["a"]}
        self.assertEqual(detect_compound_cycle(graph), ["a", "b", "c", "a"])


if __name__ == "__main__":
    unittest.main()
