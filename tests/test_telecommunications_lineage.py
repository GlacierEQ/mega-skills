from __future__ import annotations
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TelecomLineageTests(unittest.TestCase):
    def test_registry_lineage(self):
        skills={x["id"] for x in json.loads((ROOT/"registry/skills.json").read_text())["entries"]}
        combos={x["id"] for x in json.loads((ROOT/"registry/combo-skills.json").read_text())["entries"]}
        megas={x["id"] for x in json.loads((ROOT/"registry/mega-skills.json").read_text())["entries"]}
        pipes={x["id"] for x in json.loads((ROOT/"registry/pipelines.json").read_text())["entries"]}
        self.assertIn("telecommunications-execution-core",skills)
        self.assertIn("telecommunications-mission-orchestration",combos)
        self.assertIn("apex-telecommunications",megas)
        self.assertIn("telecommunications-evolution",pipes)
    def test_pipeline_safe_and_full_span(self):
        p=json.loads((ROOT/"pipelines/telecommunications-evolution.json").read_text())
        expected=["inception","readiness","recon","design","build","verify","package","deploy-gate","handoff","evolve"]
        self.assertEqual(p["span"],expected); self.assertEqual([x["id"] for x in p["stages"]],expected)
        self.assertEqual(p["deploy_mode"],"approval_packet_only")
        self.assertTrue(next(x for x in p["stages"] if x["id"]=="deploy-gate")["approval_required"])
        for st in p["stages"]:
            cmd=" ".join(st["command"]).lower()
            for token in ("git push","git merge","network send","vercel deploy"): self.assertNotIn(token,cmd)
    def test_atomic_skill_suite(self):
        proc=subprocess.run([sys.executable,str(ROOT/"skills/telecommunications-execution-core/tests/test_telecommunications_execution_core.py")],capture_output=True,text=True)
        self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
if __name__=="__main__": unittest.main()
