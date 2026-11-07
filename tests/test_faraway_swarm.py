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


    def test_swarm_preserves_existing_mission_and_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous_mission_dir = swarm.MISSION_DIR
            swarm.MISSION_DIR = Path(tmp)
            originals = {
                "MISSION.md": "Original operator scope and independent lanes.\n",
                "ROADMAP.md": "Historical milestones and unresolved requirements.\n",
                "HANDOFF.md": "Operator-authored continuation.\n",
                "EVIDENCE.md": "Existing source receipt and history.\n",
            }
            summary = {"summary": {
                "skills": 2, "combos": 0, "megas": 0,
                "ready_total": 0, "not_ready_total": 2,
            }}
            try:
                for filename, content in originals.items():
                    (swarm.MISSION_DIR / filename).write_text(content, encoding="utf-8")
                swarm.write_state(summary, [], 2)
                for filename, content in originals.items():
                    self.assertEqual((swarm.MISSION_DIR / filename).read_text(), content)
                swarm.write_state(summary, ["mission-test"], 2)
                evidence = (swarm.MISSION_DIR / "EVIDENCE.md").read_text()
                self.assertTrue(evidence.startswith(originals["EVIDENCE.md"]))
                self.assertIn("Instruction-contract file changed: `mission-test`", evidence)
                self.assertNotIn("runtime completion", evidence.lower().split("Existing source receipt")[0])
                swarm.write_state(summary, ["mission-test"], 2)
                self.assertEqual(evidence, (swarm.MISSION_DIR / "EVIDENCE.md").read_text())
                for filename in ("MISSION.md", "ROADMAP.md", "HANDOFF.md"):
                    self.assertEqual((swarm.MISSION_DIR / filename).read_text(), originals[filename])
            finally:
                swarm.MISSION_DIR = previous_mission_dir

    def test_new_generated_mission_has_no_fixed_completed_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous_mission_dir = swarm.MISSION_DIR
            swarm.MISSION_DIR = Path(tmp)
            try:
                summary = {"summary": {"skills": 1, "combos": 0, "megas": 0, "ready_total": 0, "not_ready_total": 1}}
                swarm.write_state(summary, [], 1)
                roadmap = (swarm.MISSION_DIR / "ROADMAP.md").read_text()
                self.assertNotIn("— COMPLETE", roadmap)
                self.assertIn("downstream behavior", roadmap)
                self.assertIn("checkpoints, not proof", (swarm.MISSION_DIR / "HANDOFF.md").read_text())
            finally:
                swarm.MISSION_DIR = previous_mission_dir


if __name__ == "__main__":
    unittest.main()
