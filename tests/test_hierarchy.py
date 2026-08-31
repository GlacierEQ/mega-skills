import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"


class HierarchyFoundationTests(unittest.TestCase):
    def test_validator_passes_for_the_expanded_graph(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_hierarchy.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_initial_atomic_skill_set_is_independent_and_complete(self):
        skills = json.loads((REGISTRY / "skills.json").read_text(encoding="utf-8"))["entries"]
        expected = {
            "mission-contract", "roadmap-builder", "evidence-register", "context-capsule",
            "work-packet", "quality-gate", "handoff-record",
            "fleet-git-harmonizer-core", "forensic-evidence-chain-core",
            "aerospace-trajectory-core", "polyglot-rosetta-core", "omni-memory-core",
            "fork-overlay-core", "ast-repair-core", "audio-forensic-core",
            "epistemic-gate", "computer-user-core", "connector-bridge", "pipeline-compositor",
            "capability-admission", "resource-preflight", "claim-calibration",
            "mega-skill-forge", "mega-skills-test-runner",
        }
        self.assertTrue(expected.issubset({entry["id"] for entry in skills}))
        for entry in skills:
            self.assertTrue((ROOT / entry["entrypoint"]).is_file())

    def test_long_horizon_combo_composes_all_atomic_skills(self):
        combos = json.loads((REGISTRY / "combo-skills.json").read_text(encoding="utf-8"))["entries"]
        core = next(entry for entry in combos if entry["id"] == "long-horizon-core")
        self.assertEqual(len(core["members"]), 7)
        self.assertTrue(all(member["kind"] == "skill" for member in core["members"]))

    def test_mega_layer_requires_but_does_not_duplicate_core_contracts(self):
        megas = json.loads((REGISTRY / "mega-skills.json").read_text(encoding="utf-8"))["entries"]
        for mega in megas:
            self.assertIn("long-horizon-core", mega["required_combos"])
            self.assertIn("capability-readiness", mega["conditional_combos"])
            self.assertTrue((ROOT / mega["entrypoint"]).is_file())
        self.assertFalse((ROOT / "skills/far-away-party-core").exists())

    def test_capability_readiness_has_its_atomic_foundations(self):
        combos = json.loads((REGISTRY / "combo-skills.json").read_text(encoding="utf-8"))["entries"]
        readiness = next(entry for entry in combos if entry["id"] == "capability-readiness")
        self.assertEqual(
            [member["id"] for member in readiness["members"]],
            ["capability-admission", "resource-preflight", "claim-calibration", "quality-gate"],
        )

    def test_feedback_loops_have_guarded_outputs_and_resolved_members(self):
        combos = json.loads((REGISTRY / "combo-skills.json").read_text(encoding="utf-8"))["entries"]
        by_id = {entry["id"]: entry for entry in combos}
        expected = {
            "signal-to-decision-loop": "SIGNAL_DECISION_RECORD.md",
            "guarded-automation-loop": "GUARDED_RUN_RECORD.md",
            "evidence-to-evolution-loop": "CAPABILITY_EVOLUTION_PROPOSAL.md",
        }
        for combo_id, artifact in expected.items():
            combo = by_id[combo_id]
            self.assertEqual(combo["compounding"]["compound_artifact"], artifact)
            self.assertTrue((ROOT / combo["entrypoint"]).is_file())
            self.assertTrue(combo["integration"]["risk_boundaries"])

    def test_far_away_party_exposes_feedback_loops(self):
        megas = json.loads((REGISTRY / "mega-skills.json").read_text(encoding="utf-8"))["entries"]
        mega = next(entry for entry in megas if entry["id"] == "far-away-party")
        for combo_id in (
            "signal-to-decision-loop",
            "guarded-automation-loop",
            "evidence-to-evolution-loop",
        ):
            self.assertIn(combo_id, mega["conditional_combos"])

    def test_new_end_to_end_megas_require_multiple_resolved_combos(self):
        megas = json.loads((REGISTRY / "mega-skills.json").read_text(encoding="utf-8"))["entries"]
        by_id = {entry["id"]: entry for entry in megas}
        expected = {
            "apex-adaptive-operations": "ADAPTIVE_OPERATIONS_MISSION_RECORD.md",
            "apex-capability-foundry": "CAPABILITY_FOUNDRY_MISSION_RECORD.md",
            "apex-safe-change-orchestrator": "SAFE_CHANGE_MISSION_RECORD.md",
            "apex-web-build-system": "WEB_BUILD_MISSION_RECORD.md",
            "apex-autonomous-agent-foundry": "AGENT_FOUNDRY_MISSION_RESULT.md",
            "apex-architectural-evolution-engine": "ARCHITECTURAL_EVOLUTION_MISSION_RESULT.md",
            "apex-secure-cloud-foundry": "SECURE_CLOUD_MISSION_RESULT.md",
            "apex-accelerated-compute-mesh": "ACCELERATED_COMPUTE_MISSION_RESULT.md",
            "apex-forensic-litigation-sentinel": "FORENSIC_LITIGATION_SENTINEL_RECORD.md",
            "apex-autonomous-software-engineering": "AUTONOMOUS_ENGINEERING_MISSION_RESULT.md",
            "apex-always-on-core": "ALWAYS_ON_CORE_MISSION_RESULT.md",
            "apex-legal-forensic-powerhouse": "LEGAL_FORENSIC_POWERHOUSE_RECORD.md",
            "apex-docgen-synthesis": "DOCGEN_SYNTHESIS_MISSION_RECORD.md",
            "apex-backend-infrastructure-engine": "BACKEND_INFRASTRUCTURE_MISSION_RESULT.md",
        }
        for mega_id, artifact in expected.items():
            mega = by_id[mega_id]
            self.assertGreaterEqual(len(mega["required_combos"]), 2)
            self.assertIn("capability-readiness", mega["conditional_combos"])
            self.assertEqual(mega["mission_output"], artifact)
            self.assertTrue((ROOT / mega["entrypoint"]).is_file())

    def test_web_build_foundation_composes_five_lifecycle_members(self):
        combos = json.loads((REGISTRY / "combo-skills.json").read_text(encoding="utf-8"))["entries"]
        combo = next(entry for entry in combos if entry["id"] == "web-build-foundation")
        self.assertEqual(
            [member["id"] for member in combo["members"]],
            [
                "repository-context-onboarding",
                "imagegen",
                "webdev-readme-static",
                "webdev-readme-fullstack",
                "mega-skills-test-runner",
            ],
        )
        self.assertEqual(combo["compounding"]["compound_artifact"], "WEB_BUILD_FOUNDATION_RECORD.md")
        self.assertTrue((ROOT / combo["entrypoint"]).is_file())
        self.assertEqual([step["step"] for step in combo["execution"]["ordered_steps"]], [1, 2, 3, 4, 5])

    def test_external_skills_are_metadata_only(self):
        self.assertFalse((ROOT / "skills/repository-context-onboarding").exists())
        self.assertTrue((REGISTRY / "external-skills.json").is_file())

    def test_skill_descriptions_match_sub_skill_headings(self):
        pattern = re.compile(r"encompassing (\d+) sub-skills")
        heading = re.compile(r"^## Sub-Skill:", re.M)
        by_id = {
            entry["id"]: entry
            for entry in json.loads((REGISTRY / "skills.json").read_text(encoding="utf-8"))["entries"]
        }
        mismatches = []
        for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
            text = skill_md.read_text(encoding="utf-8")
            match = pattern.search(text)
            if not match:
                continue
            counted = int(match.group(1))
            headings = len(heading.findall(text))
            skill_id = skill_md.parent.name
            if counted != headings:
                mismatches.append(f"{skill_id}: description={counted} headings={headings}")
            purpose = by_id.get(skill_id, {}).get("purpose", "")
            purpose_match = pattern.search(purpose)
            if purpose_match and int(purpose_match.group(1)) != headings:
                mismatches.append(
                    f"{skill_id}: registry purpose={purpose_match.group(1)} headings={headings}"
                )
        self.assertEqual(mismatches, [], "\n".join(mismatches))

    def test_skill_docs_do_not_hardcode_clone_root_or_missing_legal_cli(self):
        clone_root = "/Users/kcbflux/mega-skills"
        stale = []
        for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
            text = skill_md.read_text(encoding="utf-8")
            if clone_root in text:
                stale.append(f"{skill_md.parent.name}: hardcoded clone-root path")
            if ".gemini/config/skills/" in text:
                stale.append(f"{skill_md.parent.name}: stale .gemini skill path")
        legal = (ROOT / "skills/mega-legal-forensic-engine/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("skills/mega-legal-forensic-engine/skill.py", legal)
        self.assertNotIn("engine_cli.py", legal)
        self.assertFalse((ROOT / "skills/mega-legal-forensic-engine/scripts/engine_cli.py").exists())
        self.assertEqual(stale, [], "\n".join(stale))


if __name__ == "__main__":
    unittest.main()
