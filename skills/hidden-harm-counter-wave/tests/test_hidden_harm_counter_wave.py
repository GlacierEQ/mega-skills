#!/usr/bin/env python3
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from hidden_harm_counter_wave import compose_plan, select_specialists


class CounterWaveTests(unittest.TestCase):
    def test_github_work_selects_github_plus_remainder(self):
        ids = select_specialists("open a pull request and merge after CI")
        self.assertIn("hidden-harm-counter-wave", ids)
        self.assertIn("hidden-harm-github", ids)
        self.assertIn("hidden-harm-cross-domain", ids)

    def test_memory_work_selects_context(self):
        ids = select_specialists("resume continuity from SuperMemory handoff")
        self.assertIn("hidden-harm-context", ids)

    def test_unknown_work_defaults_to_cross_domain(self):
        ids = select_specialists("paint the shed")
        self.assertEqual(
            ids,
            ["hidden-harm-counter-wave", "hidden-harm-cross-domain"],
        )

    def test_plan_includes_recursive_meta_harms(self):
        plan = compose_plan("wire Iceberg MCP through Aspen Grove")
        self.assertTrue(plan["always_on"])
        self.assertTrue(plan["dynamic_recursive"])
        self.assertIn("bureaucracy_capture", plan["recursive_meta_harms_to_counter"])
        self.assertIn("hidden-harm-connectors", [c["id"] for c in plan["composed"]])

    def test_skill_execute_emits_composition(self):
        skill = ROOT / "skills/hidden-harm-counter-wave/skill.py"
        proc = subprocess.run(
            ["python3", str(skill), "--execute", "audit github branch merge"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["capability_executed"])
        self.assertIn("hidden-harm-github", [c["id"] for c in payload["composed"]])


if __name__ == "__main__":
    unittest.main()
