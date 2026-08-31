import unittest
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from boot_watchdog import ApexBootWatchdog


class TestApexBootCore(unittest.TestCase):
    def setUp(self):
        self.watchdog = ApexBootWatchdog()

    def test_verify_runtimes(self):
        res = self.watchdog.verify_runtimes()
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["epistemic_tier"], "L2_Behavior")
        self.assertTrue(len(res["python_version"]) > 0)

    def test_run_preflight_returns_digest(self):
        res = self.watchdog.run_preflight()
        self.assertEqual(res["sentinel"], "apex-boot-core")
        self.assertEqual(res["status"], "healthy")
        self.assertEqual(len(res["digest"]), 64)

    def test_skill_md_manifest(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: apex-boot-core", skill_md)
        self.assertIn("description:", skill_md)


if __name__ == "__main__":
    unittest.main()
