#!/usr/bin/env python3
"""Behavioral tests for gmail-orchestrator."""
import json
import subprocess
import sys
import unittest
from pathlib import Path


class TestGmailOrchestrator(unittest.TestCase):
    def setUp(self):
        self.skill_dir = Path(__file__).resolve().parent.parent

    def test_run_dispatcher_verification(self):
        run_py = self.skill_dir / "scripts/run.py"
        cmd = [sys.executable, str(run_py), "--verify", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output.get("skill"), "gmail-orchestrator")
        self.assertEqual(output.get("status"), "VERIFIED")
        self.assertEqual(len(output.get("sha256", "")), 64)

    def test_orchestrator_module_structure(self):
        orchestrator_py = self.skill_dir / "orchestrator.py"
        text = orchestrator_py.read_text(encoding="utf-8")
        self.assertTrue("class GmailOrchestrator" in text)
        self.assertTrue("def login" in text)
        self.assertTrue("FORENSIC_DATE_START" in text)


if __name__ == "__main__":
    unittest.main()

