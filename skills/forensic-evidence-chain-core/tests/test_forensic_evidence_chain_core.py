#!/usr/bin/env python3
"""
L2 Behavioral tests for forensic-evidence-chain-core.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestForensicEvidenceChainCore:
    """L2 tests for forensic-evidence-chain-core - 100% SHA-256 coverage, zero undocumented anomalies, Bates contiguity, PII scrubbing"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['anomaly_scanner.py', 'timestamp_verifier.py', 'sha256_digester.py', 'bates_stamper.py', 'pii_scrubber.py', 'manifest_emitter.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['bates_serial_schema.yaml', 'fre_902_compliance.md']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()
    
    # TODO: Add actual behavioral tests
    # 100% SHA-256 coverage, zero undocumented anomalies, Bates contiguity, PII scrubbing

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
