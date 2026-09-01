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
        payload={"state":{"current_objective":"Finish long horizon core","constraints":["truthful readiness"],"decisions":["use worker swarm"],"artifacts":["registry/skill-readiness.json"],"next_verification":"tests pass","next_action":"implement blockers","assumptions":["CI available"],"noise":"discard"}}
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input.json"
            source.write_text(json.dumps(payload),encoding="utf-8")
            result=subprocess.run([sys.executable,str(ROOT/"skill.py"),"capsule-generator","--input",str(source)],text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            output=json.loads(result.stdout)
            self.assertIsInstance(output,dict)
            self.assertTrue(output.get("markdown") or output.get("decision") or output.get("valid") is False)
    def test_empty_input_is_observable_not_exceptional(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input.json"; source.write_text("{}",encoding="utf-8")
            result=subprocess.run([sys.executable,str(ROOT/"skill.py"),"capsule-generator","--input",str(source)],text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIsInstance(json.loads(result.stdout),dict)
if __name__=="__main__":
    unittest.main()
