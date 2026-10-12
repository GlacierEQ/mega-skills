import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_hierarchy import skill_frontmatter_name  # noqa: E402

class SkillFrontmatterTests(unittest.TestCase):
    def test_quoted_yaml_name(self):
        self.assertEqual(skill_frontmatter_name('---\nname: "github"\ndescription: hi\n---\n'), "github")
    def test_plain_yaml_name(self):
        self.assertEqual(skill_frontmatter_name("---\nname: progressive-pyramid\ndescription: hi\n---\n"), "progressive-pyramid")
    def test_no_name(self):
        self.assertEqual(skill_frontmatter_name("---\ndescription: hi\n---\n"), None)

if __name__ == "__main__":
    unittest.main()
