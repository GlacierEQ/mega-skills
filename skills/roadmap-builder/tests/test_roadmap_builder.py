#!/usr/bin/env python3
"""
L2 Behavioral tests for roadmap-builder.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestRoadmapBuilder:
    """L2 tests for roadmap-builder - Criteria-to-chunk mapping, dependency correctness, gate existence, resumption fidelity"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['artifact_lister.py', 'dependency_optimizer.py', 'phase_grouper.py', 'chunk_definer.py', 'parallelism_validator.py', 'roadmap_emitter.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['phase_gate_schema.yaml', 'chunk_packet_schema.yaml']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()
    
    # TODO: Add actual behavioral tests
    # Criteria-to-chunk mapping, dependency correctness, gate existence, resumption fidelity

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
