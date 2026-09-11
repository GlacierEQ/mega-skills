#!/usr/bin/env python3
"""Behavioral tests for icloud-voice-memos."""
import json
import subprocess
import sys
import unittest
from pathlib import Path


class TestICloudVoiceMemos(unittest.TestCase):
    def setUp(self):
        self.skill_dir = Path(__file__).resolve().parent.parent

    def test_run_dispatcher_verification(self):
        run_py = self.skill_dir / "scripts/run.py"
        cmd = [sys.executable, str(run_py), "--verify", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output.get("skill"), "icloud-voice-memos")
        self.assertEqual(output.get("status"), "VERIFIED")
        self.assertEqual(len(output.get("sha256", "")), 64)

    def test_harvester_module_structure(self):
        harvester_py = self.skill_dir / "harvester.py"
        text = harvester_py.read_text(encoding="utf-8")
        self.assertTrue("class VoiceMemosHarvester" in text or "def harvest" in text or "iCloud" in text)
        self.assertTrue("memos" in text.lower())


if __name__ == "__main__":
    unittest.main()

