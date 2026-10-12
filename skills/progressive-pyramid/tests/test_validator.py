import copy, unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_run import validate_run

C={"schema_id":"glaciereq.progressive-pyramid.contract.v1","stages":[{"stage":s,"produces":v} for s,v in zip(["corner_1_context","corner_2_objective","corner_3_constraints","corner_4_resources","center_point"],["V1","V2","V3","V4","verified_result_or_active_continuation"])]}

def sample():
    out={"protocol":C['schema_id'],"mission_id":"m-1","original_outcome":"Deployed feature", "recovered_sources":["repo@sha"],"acceptance_criteria":["live-feature"],"stages":[],"center_point":{"status":"ACTIVE","outcome_proofs":[]}}
    prev=None
    for s,v in [("corner_1_context","V1"),("corner_2_objective","V2"),("corner_3_constraints","V3"),("corner_4_resources","V4")]:
        ref=f"artifact://{v}"
        out['stages'].append({"stage":s,"version":v,"artifact_ref":ref,"inherits":prev,"verified_gains":["fact-1"]})
        prev=ref
    return out

class ValidatorTests(unittest.TestCase):
    def check(self,r,verifier=None):return validate_run(r,C,verifier=verifier)
    def test_valid_active(self):self.assertEqual(self.check(sample()),[])
    def test_missing_recovery(self):
        r=sample();r['recovered_sources']=[];self.assertTrue(any('recovered_sources' in x for x in self.check(r)))
    def test_inheritance_break(self):
        r=sample();r['stages'][2]['inherits']=None;self.assertTrue(any('inherit' in x for x in self.check(r)))
    def test_verified_gain_dropped(self):
        r=sample();r['stages'][3]['verified_gains']=[];self.assertTrue(any('gain' in x for x in self.check(r)))
    def test_stage_order(self):
        r=sample();r['stages'].reverse();self.assertTrue(self.check(r))
    def test_false_completion(self):
        r=sample();r['center_point']['status']='MISSION_COMPLETE'; self.assertTrue(any('proof' in x or 'verifier' in x for x in self.check(r)))
    def test_self_attestation_fails(self):
        r=sample();r['center_point']={'status':'MISSION_COMPLETE','outcome_proofs':[{'criterion':'live-feature','source_ref':'provider://receipt','verified':True}]};self.assertTrue(any('verifier' in x for x in self.check(r)))
    def test_independent_verifier(self):
        r=sample();r['center_point']={'status':'MISSION_COMPLETE','outcome_proofs':[{'criterion':'live-feature','source_ref':'provider://receipt'}]}
        self.assertEqual(self.check(r,verifier=lambda criterion,receipt: criterion=='live-feature' and receipt=='provider://receipt'),[])
    def test_verifier_denies(self):
        r=sample();r['center_point']={'status':'MISSION_COMPLETE','outcome_proofs':[{'criterion':'live-feature','source_ref':'provider://receipt'}]}
        self.assertTrue(any('failed' in x for x in self.check(r,verifier=lambda *_:False)))
    def test_unknown_criterion(self):
        r=sample();r['center_point']={'status':'MISSION_COMPLETE','outcome_proofs':[{'criterion':'other','source_ref':'x'}]};self.assertTrue(self.check(r,verifier=lambda *_:True))
    def test_blocked_not_complete(self):
        r=sample();r['center_point']={'status':'BLOCKED','outcome_proofs':[],'blockers':['awaiting source']};self.assertEqual(self.check(r),[])
    def test_blocked_requires_blocker(self):
        r=sample();r['center_point']['status']='BLOCKED';self.assertTrue(any('blocker' in x for x in self.check(r)))

if __name__=='__main__':unittest.main()
