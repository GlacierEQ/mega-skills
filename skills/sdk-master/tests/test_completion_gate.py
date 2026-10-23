import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts" / "completion_gate.py"
spec = importlib.util.spec_from_file_location("completion_gate", path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

REQUIRED = gate.REQUIRED

def valid():
    rev = "a" * 40
    return {"state":"VERIFIED", "revision":rev, "ci":"passed",
            "criteria":{k:{"status":"passed","revision":rev,"evidence":"receipt://"+k,"kind":"runtime"} for k in REQUIRED},
            "outstanding_actions":[], "unresolved_defects":[]}

class CompletionGateTests(unittest.TestCase):
    def test_positive_complete(self):
        self.assertTrue(gate.decide(valid())["accepted"])

    def test_missing_criterion(self):
        m=valid(); del m["criteria"]["integration"]
        self.assertFalse(gate.decide(m)["accepted"])

    def test_static_integration_rejected(self):
        m=valid(); m["criteria"]["integration"]["kind"]="static"
        self.assertFalse(gate.decide(m)["accepted"])

    def test_mock_only_rejected(self):
        m=valid(); m["criteria"]["real_execution"]["kind"]="mock"
        self.assertFalse(gate.decide(m)["accepted"])

    def test_missing_provider_readback(self):
        m=valid(); m["provider_mutation"]=True
        self.assertFalse(gate.decide(m)["accepted"])

    def test_failed_ci(self):
        m=valid(); m["ci"]="failed"
        self.assertFalse(gate.decide(m)["accepted"])

    def test_stale_revision(self):
        m=valid(); m["criteria"]["tests"]["revision"]="b"*40
        self.assertFalse(gate.decide(m)["accepted"])

    def test_unresolved_defect(self):
        m=valid(); m["unresolved_defects"]=["broken retry"]
        self.assertFalse(gate.decide(m)["accepted"])

    def test_interrupted(self):
        m=valid(); m["interrupted"]=True
        self.assertFalse(gate.decide(m)["accepted"])

    def test_ambiguous_mutation(self):
        m=valid(); m["ambiguous_mutation"]=True
        self.assertFalse(gate.decide(m)["accepted"])

    def test_draft_not_deployed(self):
        m=valid(); m["claims_complete"]=True; m["draft_only"]=True
        self.assertFalse(gate.decide(m)["accepted"])

    def test_missing_deployment_readback(self):
        m=valid(); m["deployed"]=True
        self.assertFalse(gate.decide(m)["accepted"])

    def test_outstanding_actions(self):
        m=valid(); m["outstanding_actions"]=["run live conformance"]
        self.assertFalse(gate.decide(m)["accepted"])

if __name__=="__main__":
    unittest.main()
