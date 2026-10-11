"""Detect inadvertent mission-shrinkage in high-level GlacierEQ skill entrypoints.

These are source contract regressions. Target-host execution still requires a
real runtime invocation and provider-native outcome readback.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def skill(path):
    return (ROOT / "skills" / path / "SKILL.md").read_text(encoding="utf-8")

class MissionScopeIngressRegression(unittest.TestCase):
    def test_autonomous_software_engineering_composes_full_skill_coalition(self):
        content = skill("autonomous-software-engineering")
        self.assertIn("strongest coherent coalition", content)
        self.assertNotIn("route each bounded concern to the narrowest specialized skill", content)

    def test_a_single_local_failure_does_not_freeze_other_engineering_work(self):
        content = skill("autonomous-software-engineering")
        self.assertIn("continue independent authorized work", content)
        self.assertIn("do not close the entire mission", content)

    def test_a_test_failure_blocks_claim_or_release_not_the_entire_mission(self):
        content = skill("autonomous-software-engineering")
        self.assertIn("verification failure blocks only unsupported release claims", content)
        self.assertIn("preserve independent execution lanes", content)

    def test_sales_route_composes_customer_outcome(self):
        content = skill("sales")
        self.assertIn("complete requested customer or revenue outcome", content)
        self.assertNotIn("Select the narrowest focused workflow", content)

    def test_analytics_route_composes_full_analysis(self):
        content = skill("data-analytics")
        self.assertIn("complete requested analytical outcome", content)
        self.assertNotIn("Select the narrowest focused workflow", content)

    def test_existing_mutation_security_boundaries_are_retained(self):
        self.assertIn("Do not treat earlier approval as authorization", skill("autonomous-software-engineering"))
        self.assertIn("unapproved external writes",skill("sales"))
        self.assertIn("unapproved external writes",skill("data-analytics"))

if __name__ == "__main__":
    unittest.main()
