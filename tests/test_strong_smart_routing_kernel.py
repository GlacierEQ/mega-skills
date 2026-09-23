import importlib.util, unittest
from pathlib import Path
P=Path(__file__).parents[1]/"skills/strong-smart-routing-kernel/skill.py"
s=importlib.util.spec_from_file_location("strong_smart",P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
def c(i,score,**kw):
 d={"id":i,"authorized":True,"approvals_satisfied":True,"human_control_preserved":True,"safety_pass":True,"evidence_floor":score}; d.update({k:score for k in m.METRICS}); d.update(kw); return d
class TestStrongSmart(unittest.TestCase):
 def test_stronger_coherent_route_wins(self):
  r=m.evaluate({"mission":{"id":"x","required_evidence_floor":.6},"candidates":[c("convenience",.65,cost_pressure=.1),c("mission-complete",.94,cost_pressure=.8)]}); self.assertEqual(r["status"],"SELECTED"); self.assertEqual(r["selected_route"],"mission-complete")
 def test_authorization_is_non_tradeable(self):
  r=m.evaluate({"mission":{"required_evidence_floor":.5},"candidates":[c("unsafe-power",1,authorized=False),c("authorized",.8)]}); self.assertEqual(r["selected_route"],"authorized"); self.assertIn("authorized",r["ranking"][1]["hard_gate_failures"])
 def test_close_routes_require_review(self): self.assertEqual(m.evaluate({"mission":{},"candidates":[c("a",.90),c("b",.89)]})["status"],"REVIEW_REQUIRED")
 def test_no_candidates_fails(self):
  with self.assertRaises(ValueError): m.evaluate({"candidates":[]})
if __name__=="__main__": unittest.main()
