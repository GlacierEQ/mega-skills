import json
import stat
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent


class TestLinearOps(unittest.TestCase):
    def test_skill_md_manifest(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: linear-ops", skill_md)
        self.assertIn("description:", skill_md)
        self.assertIn("Protected layer", skill_md)

    def test_references_exist(self):
        self.assertTrue((SKILL_ROOT / "references" / "cleanup-playbook.md").exists())
        self.assertTrue((SKILL_ROOT / "references" / "issue-schema.md").exists())

    def test_skill_entry_point_exists(self):
        skill_py = SKILL_ROOT / "skill.py"
        self.assertTrue(skill_py.exists())

    def test_scripts_exist(self):
        for script_name in ("run.py", "this_skill.py", "analyze_board.py"):
            p = SKILL_ROOT / "scripts" / script_name
            self.assertTrue(p.exists(), msg=script_name)

    def test_analyze_board_clusters(self):
        from scripts.analyze_board import analyze_issues

        sample = [
            {
                "id": "HI-1",
                "title": "[GitHub PR] org/repo #1: hash optimize",
                "status": "In Progress",
                "statusType": "started",
                "priority": {"value": 2, "name": "High"},
                "project": "AI",
                "labels": ["Improvement"],
                "updatedAt": "2026-10-12T00:00:00Z",
            },
            {
                "id": "HI-2",
                "title": "Real mission next action",
                "status": "Todo",
                "statusType": "unstarted",
                "priority": {"value": 2, "name": "High"},
                "project": "Mesh",
                "labels": ["Mission: KEKOA"],
                "updatedAt": "2026-10-16T00:00:00Z",
            },
            {
                "id": "HI-3",
                "title": "Finished step",
                "status": "Done",
                "statusType": "completed",
                "priority": {"value": 3, "name": "Medium"},
                "project": "Mesh",
                "labels": [],
                "updatedAt": "2026-10-15T00:00:00Z",
            },
        ]
        result = analyze_issues(sample)
        self.assertEqual(result["scanned"], 3)
        self.assertEqual(len(result["github_pr_mirrors"]), 1)
        self.assertEqual(len(result["hash_pr_cluster"]), 1)
        self.assertTrue(result["recommended_actions"])


if __name__ == "__main__":
    unittest.main()
