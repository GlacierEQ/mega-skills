#!/usr/bin/env python3
"""Behavioral tests for apex-ast-sentinel."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


class TestApexAstSentinel(unittest.TestCase):
    def setUp(self):
        self.root = ROOT

    def test_clean_ast_validation(self):
        from ast_sentinel import validate_ast_invariants
        code = "def add(a: int, b: int) -> int:\n    return a + b\n"
        result = validate_ast_invariants(code, filename="valid.py")
        self.assertTrue(result["valid"])
        self.assertFalse(result["syntax_error"])
        self.assertEqual(len(result["defects"]), 0)
        self.assertTrue(result["node_count"] > 0)

    def test_defect_sentinel_catches_bare_except_and_eval(self):
        from ast_sentinel import validate_ast_invariants
        flawed_code = "try:\n    eval('2 + 2')\nexcept:\n    pass\n"
        result = validate_ast_invariants(flawed_code, filename="unsafe.py")
        self.assertFalse(result["valid"])
        defect_types = [d["type"] for d in result["defects"]]
        self.assertTrue("bare_except" in defect_types)
        self.assertTrue("unsafe_call" in defect_types)


if __name__ == "__main__":
    unittest.main()

