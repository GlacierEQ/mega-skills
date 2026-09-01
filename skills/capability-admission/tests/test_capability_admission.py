#!/usr/bin/env python3
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CapabilityAdmissionBehavior(unittest.TestCase):
    def run_payload(self,payload):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input.json"; source.write_text(json.dumps(payload),encoding="utf-8")
            result=subprocess.run([sys.executable,str(ROOT/"skill.py"),"decision-recorder","--input",str(source)],text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            return json.loads(result.stdout)
    def test_admits_only_verified_route(self):
        output=self.run_payload({"capability_id":"demo","mission_scope":"test mission","prerequisites":[{"id":"tool","required":True,"status":"verified"}],"claim_boundary_passed":True,"approval_required":False,"fallback":"manual route"})
        self.assertEqual(output["decision"],"admitted")
        self.assertTrue(output["valid"])
    def test_missing_prerequisite_stays_candidate(self):
        output=self.run_payload({"capability_id":"demo","mission_scope":"test mission","prerequisites":[{"id":"tool","required":True,"status":"missing"}],"claim_boundary_passed":True})
        self.assertEqual(output["decision"],"candidate")
        self.assertFalse(output["valid"])
if __name__=="__main__": unittest.main()
