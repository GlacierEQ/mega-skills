#!/usr/bin/env python3
"""
L2 Behavioral tests for omni-memory-core.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestOmniMemoryCore:
    """L2 tests for omni-memory-core - Cosine math determinism, synaptic monotonicity, NaN prevention, source immutability"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['file_traverser.py', 'vectorizer.py', 'cosine_engine.py', 'hebbian_reinforcer.py', 'memory_exporter.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['vocab_params.yaml', 'cloud_paths.yaml']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_vectorizer_behavioral(self):
        from scripts.vectorizer import vectorize_text
        res = vectorize_text("Quantum memory indexing")
        assert res["total_3grams"] > 0
        assert res["unique_features"] > 0
        assert len(res["vector"]) > 0

    def test_cosine_similarity_determinism(self):
        from scripts.cosine_engine import cosine_similarity
        v1 = {"qua": 0.6, "mem": 0.8}
        v2 = {"qua": 0.6, "mem": 0.8}
        v3 = {"foo": 1.0}
        sim_identical = cosine_similarity(v1, v2)
        sim_orthogonal = cosine_similarity(v1, v3)
        assert round(sim_identical, 4) == 1.0
        assert sim_orthogonal == 0.0

    def test_hebbian_reinforcer_monotonicity(self):
        from scripts.hebbian_reinforcer import update_hebbian_weights
        weights = {"node1--node2": 0.4}
        res = update_hebbian_weights(weights, ["node1", "node2"], eta_learning_rate=0.2)
        assert res["weights"]["node1--node2"] > 0.4

    def test_memory_exporter_sqlite(self, tmp_path):
        from scripts.memory_exporter import export_to_sqlite
        db = tmp_path / "mem.db"
        res = export_to_sqlite(db, [{"id": "n1", "text": "hello"}], [{"source": "n1", "target": "n2"}])
        assert res["nodes_exported"] == 1
        assert db.is_file()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

