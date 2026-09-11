#!/usr/bin/env python3
"""
L2 Behavioral tests for fork-overlay-core.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestForkOverlayCore:
    """L2 tests for fork-overlay-core - Upstream merge cleanness, overlay 100% untouched, zero regressions, clean push"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['upstream_fetcher.py', 'overlay_isolator.py', 'merge_engine.py', 'regression_gate.py', 'push_verifier.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['overlay_protection_rules.yaml', 'sync_audit_schema.yaml']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_overlay_isolator_behavioral(self):
        from scripts.overlay_isolator import classify_modifications, OverlayAnalysis
        analysis = classify_modifications(Path(__file__).parent.parent)
        assert isinstance(analysis, OverlayAnalysis)
        assert isinstance(analysis.protected_dirs, list)
        assert "custom/" in analysis.protected_dirs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

