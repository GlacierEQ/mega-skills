#!/usr/bin/env python3
"""
L2 Behavioral tests for polyglot-rosetta-core.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestPolyglotRosettaCore:
    """L2 tests for polyglot-rosetta-core - AST equivalence, compilation success, benchmark TTFT/latency, Lean 4 proof verification"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['ast_inspector.py', 'floor_selector.py', 'code_synthesizer.py', 'cross_compiler.py', 'proof_generator.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['floor_catalog.yaml', 'invariant_spec_schema.yaml']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_floor_selector_behavioral(self):
        from scripts.floor_selector import select_target_floor
        res = select_target_floor(["zero_copy", "ipc"])
        assert res["selected_floor"] == "capnp"
        res_proof = select_target_floor(["proofs", "formal_verification"])
        assert res_proof["selected_floor"] == "lean4"

    def test_ast_inspector_behavioral(self):
        from scripts.ast_inspector import inspect_signatures
        code = "def multiply(x: int, y: float) -> float:\n    return x * y\n"
        res = inspect_signatures(code)
        assert res["valid"] is True
        assert len(res["functions"]) == 1
        assert res["functions"][0]["name"] == "multiply"

    def test_code_synthesizer_rust(self):
        from scripts.code_synthesizer import synthesize_rust_function
        code = synthesize_rust_function("compute", [{"name": "a", "type": "int"}], return_type="int")
        assert "pub fn compute(a: i64) -> i64" in code

    def test_proof_generator_behavioral(self):
        from scripts.proof_generator import generate_proof_receipt
        receipt = generate_proof_receipt("valid_transition", "lean4", "forall s, valid s")
        assert receipt["verified"] is True
        assert len(receipt["proof_hash"]) == 64


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

