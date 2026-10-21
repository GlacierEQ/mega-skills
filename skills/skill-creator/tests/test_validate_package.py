"""Contract tests for the Skill Creator's read-only preflight."""
import importlib.util
import tempfile
import zipfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "validate_package.py"
spec = importlib.util.spec_from_file_location("validate_package", MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class SkillPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "my-skill"
        self.root.mkdir()
        (self.root / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: 'Use when validating a reusable skill.'\n---\n"
            "# My Skill\n\nUse when a task requires the following decision.\n"
            "Verify input evidence before execution, document decisions, and check output.\n"
            "For a missing dependency, stop that branch but continue unaffected work.\n"
            "Reject unsupported or unauthorized mutation and provide a verified handoff.\n",
            encoding="utf-8",
        )

    def result(self):
        return validator.inspect_skill(self.root)

    def test_valid_package_is_only_statically_passed(self):
        result = self.result()
        self.assertEqual(result["status"], "PASS_STATIC_ONLY")
        self.assertEqual(result["behavioral_evaluation"], "NOT_RUN")
        self.assertEqual(result["provider_execution"], "NOT_RUN")
        self.assertEqual(len(result["package_sha256"]), 64)

    def test_missing_manifest_is_blocking(self):
        (self.root / "SKILL.md").unlink()
        self.assertIn("SKILL_MANIFEST_MISSING_OR_LINKED", self.result()["errors"])

    def test_mismatched_directory_name_is_blocking(self):
        p = self.root / "SKILL.md"
        p.write_text(p.read_text().replace("name: my-skill", "name: other-skill"))
        self.assertIn("INVALID_OR_MISMATCHED_SKILL_NAME", self.result()["errors"])

    def test_link_outside_skill_is_blocking(self):
        p = self.root / "SKILL.md"
        p.write_text(p.read_text() + "\n[bad](../../secrets.txt)\n")
        self.assertTrue(any(e.startswith("REFERENCE_ESCAPES_SKILL:") for e in self.result()["errors"]))

    def test_broken_local_reference_is_blocking(self):
        p = self.root / "SKILL.md"
        p.write_text(p.read_text() + "\n[missing](references/absent.md)\n")
        self.assertTrue(any(e.startswith("BROKEN_LOCAL_REFERENCE:") for e in self.result()["errors"]))

    def test_symlink_is_blocking(self):
        (self.root / "leak").symlink_to(Path(self.temp.name))
        self.assertTrue(any(e.startswith("SYMLINK_RESOURCE:") for e in self.result()["errors"]))

    def test_potential_secret_is_blocking(self):
        (self.root / "config.txt").write_text("api_key=" + ("a" * 35))
        self.assertIn("POTENTIAL_EMBEDDED_SECRET:config.txt", self.result()["errors"])

    def test_edit_changes_digest(self):
        before = self.result()["package_sha256"]
        (self.root / "SKILL.md").write_text((self.root / "SKILL.md").read_text() + "\nExtra evidence.\n")
        self.assertNotEqual(before, self.result()["package_sha256"])

    def test_package_is_deterministic_and_uses_safe_prefix(self):
        output = Path(self.temp.name) / "dist"
        first = validator.package_validated_skill(self.root, output)
        self.assertTrue(first["artifact"].is_file())
        self.assertEqual(first["sha256"], validator.package_validated_skill(self.root, output)["sha256"])
        with zipfile.ZipFile(first["artifact"]) as zf:
            self.assertIn("my-skill/SKILL.md", zf.namelist())
            self.assertTrue(all(p.startswith("my-skill/") for p in zf.namelist()))

    def test_generated_bytecode_does_not_change_source_digest_or_archive(self):
        before = self.result()["package_sha256"]
        cache = self.root / "scripts" / "__pycache__"
        cache.mkdir(parents=True)
        (cache / "run.cpython-311.pyc").write_bytes(b"generated content")
        (self.root / ".DS_Store").write_bytes(b"os generated")
        self.assertEqual(before, self.result()["package_sha256"])
        archive = validator.package_validated_skill(self.root, Path(self.temp.name) / "dist")
        with zipfile.ZipFile(archive["artifact"]) as zf:
            self.assertFalse(any("__pycache__" in x or x.endswith(".pyc") or x.endswith(".DS_Store") for x in zf.namelist()))

    def test_packaging_rejects_invalid_or_nested_destination(self):
        p = self.root / "SKILL.md"
        p.write_text(p.read_text().replace("name: my-skill", "name: other-skill"))
        with self.assertRaises(ValueError):
            validator.package_validated_skill(self.root, Path(self.temp.name) / "dist")
        p.write_text(p.read_text().replace("name: other-skill", "name: my-skill"))
        with self.assertRaises(ValueError):
            validator.package_validated_skill(self.root, self.root / "dist")

    def test_one_missing_candidate_does_not_invalidate_other_skill(self):
        result = validator.inspect_skill(self.root / "missing")
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(self.result()["status"], "PASS_STATIC_ONLY")


if __name__ == "__main__":
    unittest.main()