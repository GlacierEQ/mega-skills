import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryContinuityStewardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(
            (ROOT / "registry" / "mega-skills.json").read_text(encoding="utf-8")
        )
        cls.mega = next(
            entry
            for entry in cls.registry["entries"]
            if entry["id"] == "apex-repository-continuity-steward"
        )
        cls.contract = (
            ROOT / cls.mega["entrypoint"]
        ).read_text(encoding="utf-8")

    def test_required_routes_resolve_to_distinct_continuity_layers(self):
        self.assertEqual(
            self.mega["required_combos"],
            [
                "long-horizon-core",
                "branch-sprawl-control-loop",
                "signal-to-decision-loop",
            ],
        )
        self.assertEqual(
            self.mega["conditional_combos"],
            [
                "capability-readiness",
                "upstream-fork-harmonization",
                "evidence-to-evolution-loop",
            ],
        )
        self.assertNotEqual(
            set(self.mega["required_combos"]),
            {"long-horizon-core", "upstream-fork-harmonization"},
        )

    def test_contract_preserves_branch_and_fork_boundaries(self):
        for phrase in (
            "BRANCH_SPRAWL_CONTROL_RECORD.json",
            "upstream-fork-harmonization",
            "SIGNAL_DECISION_RECORD.md",
            "REPOSITORY_CONTINUITY_STEWARD_RECORD.md",
            "fail closed",
            "behind explicit human approval",
        ):
            self.assertIn(phrase, self.contract)

    def test_registry_has_read_only_firewall_and_recovery_state(self):
        self.assertEqual(self.mega["maturity"], "candidate")
        self.assertEqual(self.mega["firewall"]["mode"], "read_only")
        self.assertEqual(self.mega["firewall"]["human_control"], "required")
        self.assertIn("deletion", self.mega["firewall"]["forbidden_actions"])
        self.assertEqual(
            self.mega["durable_state"],
            ["MISSION.md", "ROADMAP.md", "CONTEXT.md", "EVIDENCE.md", "HANDOFF.md"],
        )
        self.assertEqual(
            self.mega["mission_output"],
            "REPOSITORY_CONTINUITY_STEWARD_RECORD.md",
        )


if __name__ == "__main__":
    unittest.main()
