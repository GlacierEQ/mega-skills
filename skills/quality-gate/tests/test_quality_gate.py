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
        payload={"criteria":[{"criterion":"tests pass","passed":True,"evidence":["run-123"]},{"criterion":"artifact exists","passed":True,"evidence":["artifact.md"]}]}
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input.json"; source.write_text(json.dumps(payload),encoding="utf-8")
            result=subprocess.run([sys.executable,str(ROOT/"skill.py"),"decision-recorder","--input",str(source)],text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            output=json.loads(result.stdout)
            self.assertEqual(output["decision"],"pass")
            self.assertTrue(output["markdown"])
    def test_missing_evidence_fails_gate(self):
        payload={"criteria":[{"criterion":"tests pass","passed":True,"evidence":[]}]}
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input.json"; source.write_text(json.dumps(payload),encoding="utf-8")
            result=subprocess.run([sys.executable,str(ROOT/"skill.py"),"decision-recorder","--input",str(source)],text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0)
            self.assertEqual(json.loads(result.stdout)["decision"],"fail")
if __name__=="__main__":
    unittest.main()
