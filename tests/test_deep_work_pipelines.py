#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIPELINES = ROOT / "pipelines"
STAGE = ROOT / "scripts" / "deep_work_stage.py"
RUNNER = ROOT / "scripts" / "run_deep_work_pipeline.py"
GENERATOR = ROOT / "scripts" / "generate_family_pipelines.py"

FAMILY_PIPELINES = (
    "inception-to-deployment",
    "control-plane",
    "memory-fleet",
    "change-swe",
    "ship-cloud",
)

BANNED = ("git push", "git merge", "vercel deploy", "gh release", "supabase db push")
SPAN = (
    "inception",
    "readiness",
    "recon",
    "design",
    "build",
    "verify",
    "package",
    "deploy-gate",
    "handoff",
    "evolve",
)


class DeepWorkPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if GENERATOR.is_file():
            subprocess.run([sys.executable, str(GENERATOR)], check=True, cwd=ROOT)

    def test_registry_lists_family_pipelines(self) -> None:
        registry = json.loads((ROOT / "registry" / "pipelines.json").read_text(encoding="utf-8"))
        ids = {entry["id"] for entry in registry["entries"]}
        for pipeline_id in FAMILY_PIPELINES:
            self.assertIn(pipeline_id, ids)
            self.assertTrue((PIPELINES / f"{pipeline_id}.json").is_file())

    def test_family_pipelines_cover_full_span(self) -> None:
        for pipeline_id in FAMILY_PIPELINES:
            spec = json.loads((PIPELINES / f"{pipeline_id}.json").read_text(encoding="utf-8"))
            self.assertEqual(spec["schema_version"], 1)
            self.assertEqual(spec["id"], pipeline_id)
            self.assertEqual(spec["deploy_mode"], "approval_packet_only")
            self.assertEqual(spec["span"], list(SPAN))
            stage_ids = [stage["id"] for stage in spec["stages"]]
            self.assertEqual(stage_ids, list(SPAN))
            self.assertTrue(spec["mega_roots"])
            for stage in spec["stages"]:
                command = " ".join(stage["command"]).lower()
                for token in BANNED:
                    self.assertNotIn(token, command)
                expected_runner = (
                    "scripts/runtime_amplified_stage.py"
                    if pipeline_id == "control-plane"
                    else "scripts/deep_work_stage.py"
                )
                self.assertEqual(stage["command"][1], expected_runner)

    def test_deploy_gate_requires_approval(self) -> None:
        spec = json.loads((PIPELINES / "inception-to-deployment.json").read_text(encoding="utf-8"))
        gate = next(stage for stage in spec["stages"] if stage["id"] == "deploy-gate")
        self.assertTrue(gate["approval_required"])

    def test_stage_runner_emits_local_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "deep_work_stage.py").write_text(STAGE.read_text(encoding="utf-8"), encoding="utf-8")
            (root / "mega-skills" / "apex-always-on-core").mkdir(parents=True)
            (root / "mega-skills" / "apex-always-on-core" / "MEGA.md").write_text("# always-on\n", encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(root / "scripts" / "deep_work_stage.py"),
                    "--root",
                    str(root),
                    "--pipeline-id",
                    "control-plane",
                    "--family",
                    "control-plane",
                    "--stage",
                    "all",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            mission = root / "missions" / "control-plane"
            decision = json.loads((mission / "DEPLOYMENT_DECISION.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["publication_decision"], "READY_PENDING_HUMAN_APPROVAL")
            self.assertFalse(decision["allowed"])
            self.assertTrue((mission / "RELEASE_PACKET.md").is_file())
            self.assertTrue((mission / "HANDOFF.md").is_file())
            self.assertTrue((mission / "EVOLUTION_BACKLOG.json").is_file())

    def test_runner_validate_only_when_engine_present(self) -> None:
        engine = ROOT / "skills" / "pipeline-compositor" / "scripts" / "engine.py"
        if not engine.is_file():
            self.skipTest("pipeline compositor engine not in this workspace")
        proc = subprocess.run(
            [sys.executable, str(RUNNER), "--root", str(ROOT), "--pipeline", "control-plane", "--validate-only"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "VALID")
        self.assertEqual(payload["stages"], 10)


if __name__ == "__main__":
    unittest.main()
