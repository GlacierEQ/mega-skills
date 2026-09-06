import runpy
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"


class TestDesktopCommanderOverview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = SKILL_MD.read_text(encoding="utf-8")

    def test_skill_md_manifest(self):
        self.assertIn("name: desktop-commander-overview", self.skill_text)
        self.assertIn("description:", self.skill_text)

    def test_execution_contract_is_enforced(self):
        required = [
            "ORIENT → ACQUIRE → EXECUTE → VERIFY → PRESERVE → CONTINUE",
            "No readback = no verified mutation.",
            "pin calls to an explicit `deviceId`",
            "Preserve all unrelated modified/untracked files.",
            "## Failure ladder",
            "## Continuity recovery",
        ]
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill_text)

    def test_pass_through_intelligence_contract(self):
        required = [
            "## Pass-through intelligence",
            "IDENTIFY → ACQUIRE → NORMALIZE → ENRICH → ROUTE → RECEIPT → VERIFY DESTINATION",
            "source-of-truth surface",
            "Never assume local presence means cloud sync completed.",
        ]
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill_text)

    def test_cloud_surface_classifier(self):
        namespace = runpy.run_path(str(SKILL_ROOT / "skill.py"))
        classify = namespace["classify_cloud_surface"]
        self.assertEqual(classify("Dropbox-Team"), "Dropbox")
        self.assertEqual(classify("OneDrive-Personal"), "OneDrive")
        self.assertEqual(classify("GoogleDrive-example"), "Google Drive")

    def test_skill_entry_point_exists_and_executable(self):
        skill_py = SKILL_ROOT / "skill.py"
        self.assertTrue(skill_py.exists())
        self.assertTrue(bool(skill_py.stat().st_mode & 0o111))


if __name__ == "__main__":
    unittest.main()
