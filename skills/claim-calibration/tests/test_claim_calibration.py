#!/usr/bin/env python3
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ClaimCalibrationBehavior(unittest.TestCase):
    def run_payload(self,payload):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input.json"; source.write_text(json.dumps(payload),encoding="utf-8")
            result=subprocess.run([sys.executable,str(ROOT/"skill.py"),"boundary-recorder","--input",str(source)],text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            return json.loads(result.stdout)
    def test_tested_claim_keeps_scoped_wording(self):
        output=self.run_payload({"claims":[{"claim":"The parser rejects malformed input.","classification":"tested_behavior","evidence":["test-1"]}]})
        self.assertEqual(output["claims"][0]["approved_wording"],"The parser rejects malformed input.")
        self.assertTrue(output["valid"])
    def test_high_consequence_unqualified_claim_escalates(self):
        output=self.run_payload({"claims":[{"claim":"System is legally certified.","classification":"design_intent","evidence":[],"high_consequence":True,"qualified_evidence":False}]})
        self.assertIn("CL-001",output["escalations"])
        self.assertTrue(output["claims"][0]["approved_wording"].startswith("Not established:"))
if __name__=="__main__": unittest.main()
