#!/usr/bin/env python3
"""
L2 Behavioral tests for ast-repair-core.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestAstRepairCore:
    """L2 tests for ast-repair-core - Traceback parsing accuracy, AST chunk isolation, patch application, 100% green verification"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['traceback_parser.py', 'ast_chunker.py', 'patch_synthesizer.py', 'patch_applier.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['repair_prompts.md', 'test_adapters.json']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_traceback_parser_behavioral(self):
        from scripts.traceback_parser import parse_pytest_traceback
        sample_output = """
=================================== FAILURES ===================================
_________________________________ test_failure _________________________________
def test_failure():
>       assert 1 == 2
E       assert 1 == 2
tests/test_dummy.py:4: AssertionError
=========================== short test summary info ============================
FAILED tests/test_dummy.py::test_failure - assert 1 == 2
"""
        parsed = parse_pytest_traceback(sample_output)
        assert parsed is not None
        assert parsed.error_type == "AssertionError"
        assert len(parsed.frames) >= 1
        assert parsed.root_cause_frame is not None
        assert parsed.root_cause_frame.line == 4

    def test_ast_chunker_enclosing_node(self):
        import ast
        from scripts.ast_chunker import find_enclosing_node
        code = "def sample():\n    x = 10\n    return x\n"
        tree = ast.parse(code)
        node = find_enclosing_node(tree, 2)
        assert node is not None
        assert isinstance(node, (ast.FunctionDef, ast.Assign))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

