#!/usr/bin/env python3
"""Behavioral tests for cross-app-pipeline."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestCrossAppPipeline(unittest.TestCase):
    def setUp(self):
        self.skill_dir = ROOT

    def test_run_dispatcher_verification(self):
        run_py = self.skill_dir / "scripts/run.py"
        cmd = [sys.executable, str(run_py), "--verify", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output.get("skill"), "cross-app-pipeline")
        self.assertEqual(output.get("status"), "VERIFIED")
        self.assertEqual(len(output.get("sha256", "")), 64)

    def test_classify_transcript_behavioral(self):
        from pipeline import classify_transcript
        res_legal = classify_transcript("Review court motion and filing evidence")
        res_email = classify_transcript("Draft and send email response to team")
        res_pers = classify_transcript("Weekly shopping checklist")
        self.assertEqual(res_legal, "LEGAL")
        self.assertEqual(res_email, "EMAIL")
        self.assertEqual(res_pers, "PERSONAL")


if __name__ == "__main__":
    unittest.main()

