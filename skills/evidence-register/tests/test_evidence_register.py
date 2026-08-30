#!/usr/bin/env python3
"""
L2 Behavioral tests for evidence-register.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestEvidenceRegister:
    """L2 tests for evidence-register - Traceability completeness, claim-to-evidence mapping, contradiction preservation, gap identification"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['id_assigner.py', 'claim_tracer.py', 'register_updater.py', 'integrity_checker.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['evidence_schema.yaml', 'claim_type_taxonomy.yaml']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()
    
    # TODO: Add actual behavioral tests
    # Traceability completeness, claim-to-evidence mapping, contradiction preservation, gap identification

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
