#!/usr/bin/env python3
"""
L2 Behavioral tests for handoff-record.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestHandoffRecord:
    """L2 tests for handoff-record - Resume fidelity, environment verification, next action executability, dead-end prevention"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['resume_point_encoder.py', 'next_action_encoder.py', 'environment_capturer.py', 'assumption_separator.py', 'dead_end_recorder.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['handoff_schema.yaml', 'recovery_checklist.md']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()
    
    # TODO: Add actual behavioral tests
    # Resume fidelity, environment verification, next action executability, dead-end prevention

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
