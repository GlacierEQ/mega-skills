#!/usr/bin/env python3
"""
L2 Behavioral tests for quality-gate.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestQualityGate:
    """L2 tests for quality-gate - Decision reproducibility, evidence-backed acceptance, actionable remediation on failure"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['criteria_reader.py', 'artifact_inspector.py', 'verifier_coordinator.py', 'decision_recorder.py', 'failure_classifier.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['gate_checklist.yaml', 'conditional_pass_schema.yaml']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()
    
    # TODO: Add actual behavioral tests
    # Decision reproducibility, evidence-backed acceptance, actionable remediation on failure

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
