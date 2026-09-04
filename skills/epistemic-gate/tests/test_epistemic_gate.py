#!/usr/bin/env python3
"""Tests for epistemic-gate.
Structural checks plus L2 behavioral coverage: tier evaluation, forbidden-stub
detection, SHA-256 determinism, gate denial below L2, and receipt generation.
Run with: python -m unittest discover -s tests -v   (or pytest)
"""

import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import gate_enforcer
import receipt_generator
import sha256_verifier
import tier_evaluator


class TestEpistemicGate:
    """Structural checks: package layout, executable scripts, resources."""

    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111

    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['tier_evaluator.py', 'sha256_verifier.py', 'receipt_generator.py', 'gate_enforcer.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"

    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['epistemic_spectrum.yaml', 'forbidden_patterns.yaml']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"

    def test_requirements_exist(self):
        req = Path(__file__).parent.parent / "requirements.txt"
        assert req.exists()


class TestEpistemicGateBehavior(unittest.TestCase):
    """Behavioral coverage for the epistemic ladder, verifier, and receipts."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="eg"))

    def test_sha256_determinism_and_verify_modes(self):
        target = self.tmp / "evidence.bin"
        payload = b"apex epistemic gate coverage" * 4096
        target.write_bytes(payload)
        expected = hashlib.sha256(payload).hexdigest()
        self.assertEqual(sha256_verifier.compute_sha256(target), expected)
        match, actual = sha256_verifier.verify_sha256(target, expected)
        self.assertTrue(match)
        self.assertEqual(actual, expected)
        mismatch, _ = sha256_verifier.verify_sha256(target, "0" * 64)
        self.assertFalse(mismatch)

    def test_tree_hash_and_manifest_writer(self):
        (self.tmp / "a.txt").write_text("alpha", encoding="utf-8")
        nested = self.tmp / "sub"
        nested.mkdir()
        (nested / "b.txt").write_text("bravo", encoding="utf-8")
        digests = sha256_verifier.compute_tree_hash(self.tmp)
        self.assertEqual(sorted(digests.keys()), ["a.txt", "sub/b.txt"])
        self.assertEqual(digests["a.txt"], hashlib.sha256(b"alpha").hexdigest())
        out = self.tmp / "manifest.json"
        sha256_verifier.write_manifest(digests, out)
        manifest = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(manifest["algorithm"], "SHA-256")
        self.assertEqual(manifest["chunk_size"], 65536)
        self.assertEqual(manifest["file_count"], 2)

    def test_tier_evaluation_l0_l1_on_real_module(self):
        module = self.tmp / "real_module.py"
        module.write_text(
            "def add(a, b):\n    result = a + b\n    return result\n",
            encoding="utf-8")
        result = tier_evaluator.evaluate_target(module, tier_evaluator.EpistemicTier.L1_STRUCTURE)
        self.assertTrue(result.authorized)
        self.assertGreaterEqual(result.tier.value, 1)
        self.assertTrue(result.evidence)
        self.assertEqual(result.forbidden_patterns, [])
        self.assertEqual(result.sha256_digests[str(module)],
                         hashlib.sha256(module.read_bytes()).hexdigest())

    def test_forbidden_stub_patterns_deny_authorization(self):
        stub = self.tmp / "stub_module.py"
        stub.write_text(
            "def compute(value):\n    return True\n\ndef other():\n    raise NotImplementedError\n",
            encoding="utf-8")
        hits = tier_evaluator.scan_forbidden_patterns(stub)
        self.assertGreaterEqual(len(hits), 2)
        result = tier_evaluator.evaluate_target(stub, tier_evaluator.EpistemicTier.L1_STRUCTURE)
        self.assertFalse(result.authorized)
        clean = self.tmp / "clean_module.py"
        clean.write_text("VALUE = 42\n", encoding="utf-8")
        self.assertEqual(tier_evaluator.scan_forbidden_patterns(clean), [])

    def test_gate_denies_json_below_l2_without_tests(self):
        case_dir = self.tmp / "casepkg"
        (case_dir / "data").mkdir(parents=True)
        target = case_dir / "data" / "claim.json"
        target.write_text(json.dumps({"claim": "verified only with behavior"}), encoding="utf-8")
        result = gate_enforcer.enforce_gate(target, context="local")
        self.assertFalse(result.authorized)
        self.assertGreaterEqual(result.tier.value, 1)
        self.assertTrue(any("L2" in gap for gap in result.gaps))

    def test_receipt_generator_cryptographic_fields(self):
        target = self.tmp / "subject.py"
        target.write_text("X = 1\n", encoding="utf-8")
        receipt = receipt_generator.generate_receipt(
            target, tier="L2", authorized=True,
            evidence=["unit tests green"], gaps=[], forbidden=[])
        self.assertEqual(receipt["version"], "1.0")
        self.assertEqual(receipt["epistemic_tier"], "L2")
        self.assertTrue(receipt["authorized"])
        self.assertEqual(receipt["target_sha256"],
                         hashlib.sha256(target.read_bytes()).hexdigest())
        parsed = datetime.fromisoformat(receipt["timestamp"])
        self.assertIsNotNone(parsed.tzinfo)
        self.assertEqual(receipt["evidence"], ["unit tests green"])
        self.assertIsInstance(receipt["git"], dict)

    def test_evaluate_target_l0_boundary_and_missing_path(self):
        existing = self.tmp / "present.txt"
        existing.write_text("here", encoding="utf-8")
        result = tier_evaluator.evaluate_target(existing, tier_evaluator.EpistemicTier.L0_PRESENCE)
        self.assertTrue(result.authorized)
        self.assertEqual(result.tier, tier_evaluator.EpistemicTier.L0_PRESENCE)
        missing = self.tmp / "absent.txt"
        gone = tier_evaluator.evaluate_target(missing, tier_evaluator.EpistemicTier.L0_PRESENCE)
        self.assertFalse(gone.authorized)
        self.assertTrue(gone.gaps)


if __name__ == "__main__":
    unittest.main()
