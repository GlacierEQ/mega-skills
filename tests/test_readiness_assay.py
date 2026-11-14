import json, importlib.util, shutil, unittest
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
        mock_path = ROOT / "tests" / "_mock_stub_skill"
        mock_path.mkdir(parents=True, exist_ok=True)
        (mock_path / "SKILL.md").write_text("# Mock Stub Skill\n## Purpose\nActionable procedure and workflow for testing stubs.\n", encoding="utf-8")
        (mock_path / "stub.py").write_text("#!/usr/bin/env python3\n# Status: STUB - implement per skill contract\n", encoding="utf-8")
        self.addCleanup(lambda: shutil.rmtree(mock_path, ignore_errors=True))

        entry = {"id": "mock-stub-skill", "path": "tests/_mock_stub_skill", "maturity": "candidate"}
        state = MOD.inspect_skill(entry)
        self.assertFalse(state["ready"]); self.assertEqual(state["state"],"implementation_partial"); self.assertTrue(state["stub_files"])
    def test_receipt_only_runner_is_a_scaffold_not_an_implementation(self):
        runner=(ROOT/"skills/ai-deal-finder/scripts/run.py").read_text(encoding="utf-8")
        self.assertIn('"status": "VERIFIED"',runner)
        self.assertTrue(MOD.is_generated_scaffold(runner))
        entry=next(e for e in json.loads((ROOT/"registry/skills.json").read_text())["entries"] if e["id"]=="ai-deal-finder")
        state=MOD.inspect_skill(entry)
        self.assertIn("skills/ai-deal-finder/scripts/run.py",state["scaffold_files"])
        self.assertNotIn("skills/ai-deal-finder/scripts/run.py",state["real_implementation_files"])
        self.assertNotEqual(state["state"],"implementation_unverified")
    def test_existence_only_test_harness_is_structural_not_behavioral(self):
        mock_path = ROOT / "tests" / "_mock_structural_skill"
        (mock_path / "tests").mkdir(parents=True, exist_ok=True)
        (mock_path / "SKILL.md").write_text("# Mock Structural Skill\n## Purpose\nActionable procedure and workflow for testing structural harness in isolation.\n", encoding="utf-8")
        (mock_path / "impl.py").write_text("#!/usr/bin/env python3\n" + "# Substantive domain implementation block\n" * 6 + "def run_engine(data):\n    return data\n", encoding="utf-8")
        harness_path = mock_path / "tests" / "test_mock.py"
        harness_path.write_text("import unittest\nfrom pathlib import Path\nclass TestStruct(unittest.TestCase):\n    def test_exists(self):\n        self.assertTrue(Path('impl.py').exists())\n", encoding="utf-8")
        self.addCleanup(lambda: shutil.rmtree(mock_path, ignore_errors=True))

        entry = {"id": "mock-structural-skill", "path": "tests/_mock_structural_skill", "maturity": "candidate"}
        state = MOD.inspect_skill(entry)
        harness = "tests/_mock_structural_skill/tests/test_mock.py"
        self.assertIn(harness,state["structural_tests"])
        self.assertNotIn(harness,state["behavioral_tests"])
        self.assertEqual(state["state"],"implementation_unverified")
    def test_inspection_file_lists_are_deterministically_sorted(self):
        entry=next(e for e in json.loads((ROOT/"registry/skills.json").read_text())["entries"] if e["id"]=="mega-xai-colossus-2")
        state=MOD.inspect_skill(entry)
        for field in ("real_implementation_files","generic_adapter_files","scaffold_files","stub_files","behavioral_tests","structural_tests"):
            self.assertEqual(state[field], sorted(state[field]), field)

if __name__=="__main__": unittest.main()
