#!/usr/bin/env python3
"""
L2 Behavioral tests for mega-skill-forge.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestMegaSkillForge:
    """L2 tests for mega-skill-forge - Hierarchy validation pass, registry consistency, focused regression test, real integration delta"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['repo_inspector.py', 'mission_drafter.py', 'combo_selector.py', 'readiness_gate.py', 'contract_author.py', 'registry_publisher.py', 'hierarchy_validator.py', 'release_coordinator.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['mega-contract.md', 'release-checklist.md', 'MEGA.md.template', 'mega-registry-entry.json.template']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()
    
    # TODO: Add actual behavioral tests
    # Hierarchy validation pass, registry consistency, focused regression test, real integration delta

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
