import unittest
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from backend_engine import BackendDispatcher


class TestColossalBackend(unittest.TestCase):
    def test_plan_migration(self):
        res = BackendDispatcher.plan_migration("legal_vault", "v2.4")
        self.assertEqual(res["status"], "planned")
        self.assertTrue(res["idempotent"])
        self.assertEqual(len(res["digest"]), 64)

    def test_skill_manifest(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: colossal-backend-engine", skill_md)


if __name__ == "__main__":
    unittest.main()
