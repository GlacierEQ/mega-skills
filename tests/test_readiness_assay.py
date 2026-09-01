import json, importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("readiness_assay",ROOT/"scripts/readiness_assay.py")
MOD=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MOD)

class ReadinessAssayTests(unittest.TestCase):
    def test_generic_adapter_never_claims_execution(self):
        text=MOD.generic_adapter_text("example-skill")
        self.assertIn('"capability_executed": False',text)
        self.assertIn('"execution_unavailable"',text)
        self.assertNotIn('payload["status"] = "executed"',text)
    def test_report_covers_registered_layers(self):
        report=MOD.build_report()
        self.assertEqual(len(report["skills"]),len(json.loads((ROOT/"registry/skills.json").read_text())["entries"]))
        self.assertEqual(len(report["combos"]),len(json.loads((ROOT/"registry/combo-skills.json").read_text())["entries"]))
        self.assertEqual(len(report["megas"]),len(json.loads((ROOT/"registry/mega-skills.json").read_text())["entries"]))
    def test_known_explicit_stub_is_not_ready(self):
        entry=next(e for e in json.loads((ROOT/"registry/skills.json").read_text())["entries"] if e["id"]=="aerospace-trajectory-core")
        state=MOD.inspect_skill(entry)
        self.assertFalse(state["ready"]); self.assertEqual(state["state"],"implementation_partial"); self.assertTrue(state["stub_files"])
if __name__=="__main__": unittest.main()
