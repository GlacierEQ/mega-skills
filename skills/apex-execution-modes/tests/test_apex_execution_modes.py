import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent


class TestApexExecutionModes(unittest.TestCase):
    def test_skill_md_manifest_and_doing_contract(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: apex-execution-modes", skill_md)
        self.assertIn("description:", skill_md)
        self.assertIn("Prime Execution Law — DOING, Not Watching", skill_md)
        self.assertIn("No final response while an authorized executable next action exists", skill_md)
        self.assertIn("EXECUTE → WATCH", skill_md)
        self.assertIn("ADVANCE → RECONCILE", skill_md)
        self.assertIn("Recurring workers are production executors", skill_md)
        self.assertIn("Substantive mission-work gate", skill_md)
        self.assertIn("support work", skill_md.lower())
        self.assertIn("inspection artifact", skill_md.lower())

    def test_skill_entry_point_exists_and_executable(self):
        skill_py = SKILL_ROOT / "skill.py"
        self.assertTrue(skill_py.exists())
        self.assertTrue(bool(skill_py.stat().st_mode & 0o111))

    def test_execute_request_dispatches_and_carries_durable_continuation(self):
        proc = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "skill.py"), "--execute"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "mission_hydration_required")
        self.assertFalse(payload["dispatch_allowed"])
        self.assertIsNone(payload["operator_mission_gate"])
        self.assertTrue(payload["continue_required"])
        self.assertTrue(payload["continuation_required"])
        self.assertNotIn("execution_unavailable", proc.stdout)

        contract = payload["execution_contract"]
        self.assertEqual(
            contract["loop"],
            [
                "select_substantive_work",
                "do_it",
                "verify",
                "persist_continuation",
                "keep_doing",
            ],
        )
        self.assertEqual(
            contract["completion_gate"],
            "no_final_response_while_authorized_executable_action_exists",
        )
        self.assertIn(
            "watch_instead_of_execute",
            contract["prohibited_terminal_substitutions"],
        )
        self.assertIn(
            "reconcile_instead_of_advance",
            contract["prohibited_terminal_substitutions"],
        )
        self.assertIn(
            "summary_instead_of_hydration",
            contract["prohibited_terminal_substitutions"],
        )
        self.assertIn(
            "reconstruction_instead_of_resume",
            contract["prohibited_terminal_substitutions"],
        )
        self.assertEqual(
            contract["mission_work_gate"],
            "support_work_cannot_satisfy_completion_unless_explicitly_requested_as_mission",
        )
        self.assertIn("inspection", contract["support_work_examples"])
        self.assertIn("meta_tool_repair", contract["support_work_examples"])

        continuity = contract["continuity"]
        self.assertEqual(continuity["boot_context_role"], "routing_hint_only")
        self.assertTrue(continuity["hydrate_before_reconstruct"])
        self.assertEqual(continuity["continuation_engine"], "agent-memory-systems")
        self.assertEqual(
            continuity["projection_role"],
            "resumable_source_map_not_universal_truth_authority",
        )
        self.assertIn("last_verified_state", continuity["required_resume_state"])
        self.assertIn("resolved_questions", continuity["required_resume_state"])
        self.assertIn("open_contradictions", continuity["required_resume_state"])
        self.assertIn("source_pointers", continuity["required_resume_state"])
        self.assertIn("peer_projections", continuity["required_resume_state"])
        self.assertEqual(
            continuity["resume_order"][0],
            "current_operator_request",
        )
        self.assertIn(
            "persist_stronger_continuation",
            continuity["resume_order"],
        )
        self.assertEqual(
            continuity["persistence_sequence"],
            ["mutate", "atomic_save", "integrity_rebind", "readback", "hydrate"],
        )
        self.assertIn(
            "fresh_worker_ignorance_as_project_reset",
            continuity["anti_reconstruction"],
        )

    def test_execute_with_hydrated_mission_input_dispatches_selected_real_work(self):
        import tempfile
        mission = {
            "scope": {"mode": "estate"},
            "objective_graph_hydrated": True,
            "fronts_considered": [{"lane": "nex"}, {"lane": "engineering"}],
            "candidates": [
                {"id": "recent-report", "lane": "nex", "source_state_hydrated": True,
                 "authorized": True, "executable": True, "substantive": True,
                 "result_kind": "report", "selection_basis": ["recent_context"]},
                {"id": "runtime-fix", "lane": "engineering", "source_state_hydrated": True,
                 "authorized": True, "executable": True, "substantive": True,
                 "continuation_valid": True, "operator_impact": 1.0,
                 "capability_gain": 1.0, "execution_readiness": 1.0},
            ],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(mission, handle)
            path = handle.name
        try:
            proc = subprocess.run(
                [sys.executable, str(SKILL_ROOT / "skill.py"), "--execute", "--mission-input", path],
                check=False, capture_output=True, text=True,
            )
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "dispatch_required")
        self.assertTrue(payload["dispatch_allowed"])
        self.assertEqual(payload["operator_mission_gate"]["selected"]["id"], "runtime-fix")

    def test_adapter_without_execute_still_exposes_continuity_contract(self):
        proc = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "skill.py")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "adapter_ready")
        self.assertFalse(payload["continue_required"])
        self.assertFalse(payload["continuation_required"])
        self.assertEqual(
            payload["execution_contract"]["continuity"]["boot_context_role"],
            "routing_hint_only",
        )

    def test_all_entrypoints_share_the_same_non_stalling_execution_contract(self):
        entrypoints = [
            SKILL_ROOT / "skill.py",
            SKILL_ROOT / "scripts" / "run.py",
            SKILL_ROOT / "scripts" / "this_skill.py",
        ]
        for entrypoint in entrypoints:
            with self.subTest(entrypoint=entrypoint.name):
                proc = subprocess.run(
                    [sys.executable, str(entrypoint), "--execute"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertNotIn("execution_unavailable", proc.stdout)
                payload = json.loads(proc.stdout)
                self.assertEqual(payload["status"], "mission_hydration_required")
                self.assertFalse(payload["dispatch_allowed"])
                self.assertTrue(payload["continuation_required"])
                self.assertEqual(
                    payload["execution_contract"]["continuity"]["boot_context_role"],
                    "routing_hint_only",
                )

    def test_scripts_executable(self):
        for script_name in ("run.py", "this_skill.py"):
            p = SKILL_ROOT / "scripts" / script_name
            self.assertTrue(p.exists())
            self.assertTrue(bool(p.stat().st_mode & 0o111))


if __name__ == "__main__":
    unittest.main()
