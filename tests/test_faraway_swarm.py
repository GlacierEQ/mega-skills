import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import faraway_party_candidate_swarm as swarm  # noqa: E402
from readiness_assay import substantive_instruction  # noqa: E402

EMPTY_PACKAGE = {"scripts": [], "tests": [], "references": [], "assets": []}


def write_skill(root: Path, sid: str, body: str) -> Path:
    (root / sid).mkdir()
    path = root / sid / "SKILL.md"
    path.write_text(f'---\nname: {sid}\ndescription: "Operational capability for {sid}."\n---\n\n{body}\n', encoding="utf-8")
    return path


def record(sid: str) -> dict:
    return {"id": sid, "state": "contract_incomplete", "description": f"Operational capability for {sid}.", "package": EMPTY_PACKAGE}


class SwarmRepairTests(unittest.TestCase):
    def run_repair(self, root: Path, sid: str) -> bool:
        original = swarm.SKILLS
        swarm.SKILLS = root
        try:
            return swarm.repair_contract(record(sid))
        finally:
            swarm.SKILLS = original

    def test_repair_preserves_the_original_body_and_satisfies_the_assay(self):
        body = "# Attio\n\n## Overview\nUnified interface for the Attio API.\n\n## Planned Tools\n- list_cases\n- add_note\n\n## Configuration\n- ATTIO_API_KEY"
        with tempfile.TemporaryDirectory() as tmp:
            path = write_skill(Path(tmp), "attio", body)
            self.assertFalse(substantive_instruction(path)[0])
            self.assertTrue(self.run_repair(Path(tmp), "attio"))
            text = path.read_text(encoding="utf-8")
            self.assertIn(body, text)
            self.assertIn("## Contract Completion", text)
            self.assertTrue(substantive_instruction(path)[0])

    def test_repair_uses_the_assay_vocabulary_so_the_loop_converges(self):
        body = "Standardized test execution.\n\n```bash\ntest-runner mastermind --verbose\n```\n\n| Target | Path |\n|---|---|\n| mastermind | ~/mastermind |\n" * 3
        with tempfile.TemporaryDirectory() as tmp:
            path = write_skill(Path(tmp), "test-runner", body)
            self.assertGreater(len(body), 180)
            self.assertFalse(substantive_instruction(path)[0])
            self.assertTrue(self.run_repair(Path(tmp), "test-runner"))
            self.assertTrue(substantive_instruction(path)[0])
            self.assertIn("| mastermind | ~/mastermind |", path.read_text(encoding="utf-8"))

    def test_substantive_body_is_left_untouched(self):
        body = "# Skill\n\n## Purpose\nDo the thing for the caller.\n\n## Use when\nThe task needs the thing and no more specific skill applies.\n\n## Method\n1. Inspect the current state.\n2. Act within the declared boundary.\n3. Verify with observable output and report the exact state produced."
        with tempfile.TemporaryDirectory() as tmp:
            path = write_skill(Path(tmp), "thing", body)
            self.assertTrue(substantive_instruction(path)[0])
            before = path.read_text(encoding="utf-8")
            self.assertFalse(self.run_repair(Path(tmp), "thing"))
            self.assertEqual(before, path.read_text(encoding="utf-8"))

    def test_empty_body_gets_the_full_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_skill(Path(tmp), "blank", "")
            self.assertTrue(self.run_repair(Path(tmp), "blank"))
            text = path.read_text(encoding="utf-8")
            self.assertIn("# Blank\n\n## Purpose", text)
            self.assertNotIn("## Contract Completion", text)
            self.assertTrue(substantive_instruction(path)[0])


if __name__ == "__main__":
    unittest.main()
