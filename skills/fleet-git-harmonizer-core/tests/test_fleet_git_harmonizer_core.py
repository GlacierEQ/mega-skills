#!/usr/bin/env python3
"""
L2 Behavioral tests for fleet-git-harmonizer-core.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestFleetGitHarmonizerCore:
    """L2 tests for fleet-git-harmonizer-core - Zero data loss via archive tags, 100% green regression, no force-push, cryptographic verification"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['divergence_auditor.py', 'ast_diff_extractor.py', 'commit_synthesizer.py', 'regression_gate.py', 'archive_tagger.py', 'branch_pruner.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['archive_tag_schema.yaml', 'regression_adapters.json']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_divergence_auditor_behavioral(self):
        from scripts.divergence_auditor import audit_divergence
        res = audit_divergence(Path(__file__).resolve().parents[3])
        assert "branches" in res
        assert "total_branches_audited" in res

    def test_ast_diff_extractor_behavioral(self):
        from scripts.ast_diff_extractor import compute_ast_diff
        c1 = "def foo():\n    return 1\n"
        c2 = "def foo():\n    return 2\n\ndef bar():\n    return 3\n"
        diff = compute_ast_diff(c1, c2)
        assert diff["semantic_changes_detected"] is True
        assert "bar" in diff["added"]
        assert "foo" in diff["modified"]

    def test_commit_synthesizer_provenance(self):
        from scripts.commit_synthesizer import synthesize_commit_message
        msg = synthesize_commit_message("feat: test", "body text")
        assert "Signed-off-by" in msg["full_message"]
        assert "Evidence-Receipt" in msg["full_message"]

    def test_archive_tagger_dry_run(self):
        from scripts.archive_tagger import create_archive_tag
        res = create_archive_tag(Path(__file__).resolve().parents[3], "main", dry_run=True)
        assert res["dry_run"] is True
        assert "archive/main" in res["tag_name"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

