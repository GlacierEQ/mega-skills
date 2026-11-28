"""Validation tests for TEAM_PIPELINE_REPORT.md artifact."""

import unittest
from pathlib import Path

REPORT_PATH = Path(__file__).resolve().parents[5] / "TEAM_PIPELINE_REPORT.md"


class TeamPipelineReportTests(unittest.TestCase):
    """Tests validating the TEAM_PIPELINE_REPORT.md structure and content."""

    def test_report_exists(self):
        """Report file exists at expected location."""
        self.assertTrue(REPORT_PATH.exists(), f"Report not found at {REPORT_PATH}")

    def test_report_non_empty(self):
        """Report has content."""
        content = REPORT_PATH.read_text()
        self.assertGreater(len(content), 100, "Report should have substantial content")

    def test_report_has_required_sections(self):
        """Report contains all required structural sections."""
        content = REPORT_PATH.read_text()
        required_sections = [
            "# Team Pipeline Smoke Report",
            "Date:",
            "Anchor:",
            "## DAG",
            "## Lane outputs",
            "## Gate verdicts",
            "## Outcome",
        ]
        for section in required_sections:
            self.assertIn(section, content, f"Missing required section: {section}")

    def test_report_references_all_six_cards(self):
        """Report names all six pipeline cards by task ID."""
        content = REPORT_PATH.read_text()
        required_cards = [
            "t_52992036",  # anchor
            "t_19df0fd0",  # lane A
            "t_5fced20a",  # lane B
            "t_38062269",  # verifier
            "t_8c6813a0",  # reviewer
            "t_dd312eb0",  # synthesizer
        ]
        for card_id in required_cards:
            self.assertIn(card_id, content, f"Missing card reference: {card_id}")

    def test_report_records_gate_verdicts(self):
        """Report records both verifier PASS and reviewer APPROVE."""
        content = REPORT_PATH.read_text()
        self.assertIn("Verifier", content)
        self.assertIn("PASS", content)
        self.assertIn("Reviewer", content)
        self.assertIn("APPROVE", content)

    def test_report_has_correct_date(self):
        """Report has the expected date."""
        content = REPORT_PATH.read_text()
        self.assertIn("2026-11-08", content)

    def test_report_lane_a_details(self):
        """Report includes Lane A output details."""
        content = REPORT_PATH.read_text()
        self.assertIn("TEAM_SMOKE_A.md", content)
        self.assertIn("507B", content)
        self.assertIn("lane-a", content)

    def test_report_lane_b_details(self):
        """Report includes Lane B output details."""
        content = REPORT_PATH.read_text()
        self.assertIn("TEAM_SMOKE_B.md", content)
        self.assertIn("982B", content)
        self.assertIn("lane-b", content)


if __name__ == "__main__":
    unittest.main()