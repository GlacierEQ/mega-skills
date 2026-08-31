import unittest
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from doc_engine import DocExtractor


class TestDocSynthesis(unittest.TestCase):
    def test_extract_ast_docs(self):
        sample = "class Calculator:\n    '''Calculates numbers.'''\n    def add(self, a, b):\n        return a + b\n"
        res = DocExtractor.extract_from_source(sample)
        self.assertEqual(len(res["classes"]), 1)
        self.assertEqual(res["classes"][0]["name"], "Calculator")
        self.assertEqual(res["classes"][0]["doc"], "Calculates numbers.")
        self.assertIn("add", res["classes"][0]["methods"])
        self.assertEqual(len(res["digest"]), 64)

    def test_skill_manifest(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: automated-documentation-synthesis", skill_md)


if __name__ == "__main__":
    unittest.main()
