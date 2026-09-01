#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RuntimeBehavior(unittest.TestCase):
    def test_transforms_real_input(self):
        payload={"phase":"implementation","verified_progress":["runtime complete"],"blockers":[],"next_action":"run readiness","owner":"orchestrator","inputs":["registry"],"acceptance_test":"far-away-party ready","links":["MISSION.md"],"environment":{"revision":"abc"},"assumptions":["CI available"],"failed_approaches":["stubs replaced"]}
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input.json"
            source.write_text(json.dumps(payload),encoding="utf-8")
            result=subprocess.run([sys.executable,str(ROOT/"skill.py"),"resume-point-encoder","--input",str(source)],text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            output=json.loads(result.stdout)
            self.assertIsInstance(output,dict)
            self.assertTrue(output.get("markdown") or output.get("decision") or output.get("valid") is False)
    def test_empty_input_is_observable_not_exceptional(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input.json"; source.write_text("{}",encoding="utf-8")
            result=subprocess.run([sys.executable,str(ROOT/"skill.py"),"resume-point-encoder","--input",str(source)],text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIsInstance(json.loads(result.stdout),dict)
if __name__=="__main__":
    unittest.main()
