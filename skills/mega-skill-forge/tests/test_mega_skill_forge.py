#!/usr/bin/env python3
"""
L2 Behavioral tests for mega-skill-forge.
Run with: python -m pytest tests/ -v
"""

import json
import pytest
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR))
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from combo_selector import select_combos
from repo_inspector import inspect_repo
from mission_drafter import draft_mission_contract
from contract_author import render_mega_contract
from readiness_gate import evaluate_readiness_gate
from hierarchy_validator import validate_mega_candidate
from registry_publisher import build_registry_entry
from release_coordinator import compile_release_packet


class TestMegaSkillForge:
    """L2 tests for mega-skill-forge - Hierarchy validation pass, registry consistency, focused regression test, real integration delta"""

    def test_skill_entry_point_exists(self):
        skill_py = SKILL_DIR / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111

    def test_scripts_exist(self):
        scripts_dir = SKILL_DIR / "scripts"
        expected = [
            'repo_inspector.py',
            'mission_drafter.py',
            'combo_selector.py',
            'readiness_gate.py',
            'contract_author.py',
            'registry_publisher.py',
            'hierarchy_validator.py',
            'release_coordinator.py',
        ]
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"

    def test_combo_selector_behavior(self, tmp_path):
        dummy_reg = tmp_path / "combos.json"
        dummy_reg.write_text(
            json.dumps({
                "entries": [
                    {"id": "code-repair-loop", "description": "Automated repair of AST and syntax"},
                    {"id": "cloud-deploy", "description": "Production deploy procedures"},
                ]
            }),
            encoding="utf-8",
        )
        matched = select_combos(dummy_reg, ["repair"])
        assert len(matched) == 1
        assert matched[0] == "code-repair-loop"

        unmatched = select_combos(dummy_reg, ["quantum-flux"])
        assert len(unmatched) == 0

    def test_repo_inspector_behavior(self):
        repo_root = SKILL_DIR.parent.parent
        report = inspect_repo(repo_root)
        assert report["skills_count"] > 100
        assert report["combos_count"] > 10
        assert report["megas_count"] > 10
        assert report["has_validator"] is True
        assert report["has_test_suite"] is True

    def test_mission_drafter_behavior(self):
        contract = draft_mission_contract(
            mega_id="apex-test-mega",
            outcome="Autonomous end-to-end verification",
            required_combos=["combo-alpha", "combo-beta"],
        )
        assert contract["mega_id"] == "apex-test-mega"
        assert len(contract["required_combos"]) == 2
        assert "capability-readiness" in contract["conditional_combos"]
        assert len(contract["durable_state_artifacts"]) == 5

        with pytest.raises(ValueError):
            draft_mission_contract("too-few", "fail", ["combo-only-one"])

    def test_contract_author_behavior(self):
        rendered = render_mega_contract(
            display_name="Apex Test Mega",
            mission_description="End-to-end verified autonomous ops",
            required_combos=["combo-one", "combo-two"],
        )
        assert "# Apex Test Mega Mega Skill" in rendered
        assert "| `combo-one` | `capability-readiness`" in rendered
        assert "## Durable state" in rendered

    def test_readiness_gate_behavior(self, tmp_path):
        dummy_readiness = tmp_path / "skill-readiness.json"
        dummy_readiness.write_text(
            json.dumps({
                "combos": {
                    "combo-ready-1": {"readiness_status": "composition_ready"},
                    "combo-ready-2": {"readiness_status": "active"},
                    "combo-unready": {"readiness_status": "draft"},
                }
            }),
            encoding="utf-8",
        )
        gate_pass = evaluate_readiness_gate(["combo-ready-1", "combo-ready-2"], dummy_readiness)
        assert gate_pass["passed"] is True
        assert len(gate_pass["unready_combos"]) == 0
        assert "capability-readiness" in gate_pass["conditional_combos"]

        gate_fail = evaluate_readiness_gate(["combo-ready-1", "combo-unready"], dummy_readiness)
        assert gate_fail["passed"] is False
        assert "combo-unready" in gate_fail["unready_combos"]

    def test_hierarchy_validator_behavior(self, tmp_path):
        dummy_combo_reg = tmp_path / "combo-skills.json"
        dummy_combo_reg.write_text(
            json.dumps({
                "entries": [
                    {"id": "valid-combo-1"},
                    {"id": "valid-combo-2"},
                ]
            }),
            encoding="utf-8",
        )
        ok, issues = validate_mega_candidate("valid-mega", ["valid-combo-1", "valid-combo-2"], dummy_combo_reg)
        assert ok is True
        assert len(issues) == 0

        bad, issues = validate_mega_candidate("invalid-mega", ["valid-combo-1", "missing-combo"], dummy_combo_reg)
        assert bad is False
        assert any("missing-combo" in msg for msg in issues)

    def test_registry_publisher_behavior(self):
        entry = build_registry_entry(
            mega_id="apex-orchestrator",
            display_name="Apex Orchestrator",
            required_combos=["combo-1", "combo-2"],
        )
        assert entry["id"] == "apex-orchestrator"
        assert entry["maturity"] == "candidate"
        assert len(entry["required_combos"]) == 2
        assert "capability-readiness" in entry["conditional_combos"]
        assert len(entry["durable_state"]) == 5

    def test_release_coordinator_behavior(self):
        repo_root = SKILL_DIR.parent.parent
        packet = compile_release_packet(repo_root)
        assert "head_commit" in packet["git"]
        assert packet["hierarchy_validator_passed"] is True
        assert packet["authorized_for_release"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
