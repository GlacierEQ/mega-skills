"""Package-local behavioral coverage for registered strong-smart routing."""
import importlib.util
import unittest
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "skill.py"
spec = importlib.util.spec_from_file_location("strong_smart_routing", FILE)
routing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(routing)

def candidate(name, quality, **changes):
    data = {"id":name, "authorized":True, "approvals_satisfied":True,
            "human_control_preserved":True, "safety_pass":True,
            "evidence_floor":quality}
    data.update({metric: quality for metric in routing.METRICS})
    data.update(changes)
    return data

class RoutingBehavior(unittest.TestCase):
    def test_mission_fit_beats_convenience(self):
        result = routing.evaluate({"mission":{"required_evidence_floor":0.6},
             "candidates":[candidate("convenience",0.65), candidate("outcome",0.95)]})
        self.assertEqual(result["selected_route"],"outcome")
        self.assertEqual(result["status"],"SELECTED")
    def test_authority_gate_blocks_unsafe_strength(self):
        result = routing.evaluate({"mission":{},"candidates":[
            candidate("unapproved",1.0,authorized=False), candidate("approved",0.8)]})
        self.assertEqual(result["selected_route"],"approved")
        self.assertIn("authorized", next(x for x in result["ranking"] if x["id"]=="unapproved")["hard_gate_failures"])

if __name__=="__main__": unittest.main()
