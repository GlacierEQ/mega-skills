#!/usr/bin/env python3
"""
L2 Behavioral tests for mega-skills-test-runner.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestMegaSkillsTestRunner:
    """L2 tests for mega-skills-test-runner - Canonical validation sequence, JSON evidence emission, failure diagnosis, revision capture"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['run_checks.py', 'report_emitter.py', 'failure_diagnostic.py', 'revision_recorder.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['checks.md', 'standard_tree.md']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_revision_recorder_behavioral(self):
        from scripts.revision_recorder import record_revision
        record = record_revision(Path(__file__).resolve().parents[3])
        assert isinstance(record, dict)
        assert "head" in record
        assert "clean" in record

    def test_report_emitter_behavioral(self, tmp_path):
        from scripts.report_emitter import emit_report
        out = tmp_path / "report.json"
        payload = emit_report(out, status="PASS", checks=[{"check": "dummy", "returncode": 0}])
        assert payload["status"] == "PASS"
        assert out.is_file()

    def test_failure_diagnostic_behavioral(self):
        from scripts.failure_diagnostic import diagnose_failure
        diag = diagnose_failure("Validation error in entry: test-skill at field: description on line 42")
        assert diag["boundary"] == "schema_validation"
        assert diag["entry"] == "test-skill"
        assert diag["field"] == "description"
        assert diag["line"] == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

