#!/usr/bin/env python3
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ResourcePreflightBehavior(unittest.TestCase):
    def run_payload(self,payload):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input.json"; source.write_text(json.dumps(payload),encoding="utf-8")
            result=subprocess.run([sys.executable,str(ROOT/"skill.py"),"preflight-emitter","--input",str(source)],text=True,capture_output=True,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            return json.loads(result.stdout)
    def test_existing_file_is_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"present.txt"; f.write_text("ok",encoding="utf-8")
            output=self.run_payload({"prerequisites":[{"id":"file","type":"file","identifier":str(f),"required":True,"verification_method":"file_exists"}]})
            self.assertEqual(output["result"],"ready")
            self.assertTrue(output["ready"])
    def test_missing_required_file_blocks(self):
        output=self.run_payload({"prerequisites":[{"id":"file","type":"file","identifier":"/definitely/not/here","required":True,"verification_method":"file_exists","fallback":"provide local fixture"}]})
        self.assertEqual(output["result"],"blocked")
        self.assertFalse(output["ready"])
if __name__=="__main__": unittest.main()
