#!/usr/bin/env python3
"""
L2 Behavioral tests for local-skill.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestLocalSkill:
    """L2 tests for local-skill - structural integrity, dispatcher, generation surface"""

    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111

    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = [
            "inspect.py",
            "extract.py",
            "generate.py",
            "validate.py",
            "pattern_catalog.py",
            "this_skill.py",
        ]
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"

    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = [
            "local_skill_config.yaml",
            "local_skill_schema.json",
            "SKILL.md.template",
            "skill.py.template",
        ]
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"

    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()

    def test_skill_md_front_matter(self):
        skill_md = Path(__file__).parent.parent / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        assert text.lstrip().startswith("---")
        assert "name: local-skill" in text

    def test_references_exist(self):
        ref = Path(__file__).parent.parent / "references" / "pattern-catalog.md"
        assert ref.exists()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
