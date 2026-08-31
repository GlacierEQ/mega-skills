import unittest
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from connector_mesh import AspenGroveMesh, BaseConnector


class TestAspenGroveConnectors(unittest.TestCase):
    def setUp(self):
        self.mesh = AspenGroveMesh(force_mock=True)

    def test_all_standard_services_present(self):
        mesh = AspenGroveMesh(force_mock=True)
        expected = ["github", "notion", "supabase", "dropbox", "linear", "clickup", "vercel", "duckdb", "pinecone", "taskade"]
        for s in expected:
            self.assertIn(s, mesh.connectors)

    def test_health_check_all(self):
        mesh = AspenGroveMesh(force_mock=True)
        health = mesh.health_all()
        self.assertEqual(len(health), 10)
        self.assertIn("github", health)
        self.assertTrue("online" in health["github"]["status"])

    def test_mock_dispatch_payload_and_digest(self):
        mesh = AspenGroveMesh(force_mock=True)
        res = mesh.dispatch("supabase", "/rest/v1/evidence", {"query": "select * from exhibits"})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["service"], "supabase")
        self.assertTrue("digest" in res)
        self.assertEqual(len(res["digest"]), 64)

    def test_invalid_service_raises_keyerror(self):
        mesh = AspenGroveMesh(force_mock=True)
        with self.assertRaises(KeyError):
            mesh.get_connector("non_existent_service_xyz")


if __name__ == "__main__":
    import unittest
    unittest.main()
