#!/usr/bin/env python3
"""
L2 Behavioral tests for resource-preflight.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestResourcePreflight:
    """L2 tests for resource-preflight - Inventory completeness, classification accuracy, fallback existence, resource-bound output"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['inventory_builder.py', 'availability_checker.py', 'classifier.py', 'fallback_identifier.py', 'preflight_emitter.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['prerequisite_types.yaml', 'verification_methods.yaml']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()
    
    # TODO: Add actual behavioral tests
    # Inventory completeness, classification accuracy, fallback existence, resource-bound output

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
