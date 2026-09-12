import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_deep_progress_latest.py"
spec = importlib.util.spec_from_file_location("validate_deep_progress_latest", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


class DeepProgressLatestTests(unittest.TestCase):
    def fixture(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        rel = Path("evidence/deep-progress-forge/run-06.json")
        path = root / rel
        path.parent.mkdir(parents=True)
        frontier = "execute the next verified source-level correction"
        receipt = {
            "stream": "deep-progress-forge",
            "run_sequence": 6,
            "verbatim_sources": ["MASTER IT. DO NOT MUTILATE IT."],
            "failure_pattern_attacked": "stale recovery pointer",
            "durable_sources_changed": ["LATEST.json"],
            "concrete_outputs": ["validator", "tests", "receipt"],
            "verification": ["unit contract"],
            "objective_state_delta": {
                "changed": True,
                "before": "pointer can drift silently",
                "after": "pointer drift fails closed",
            },
            "unresolved": ["host runtime remains separately unverified"],
            "next_executable_frontier": frontier,
        }
        path.write_text(json.dumps(receipt), encoding="utf-8")
        pointer = {
            "stream": "deep-progress-forge",
            "run_sequence": 6,
            "current_run": str(rel),
            "current_run_commit": "a" * 40,
            "next_executable_frontier": frontier,
        }
        return tmp, root, path, pointer

    @staticmethod
    def provider_state():
        return {
            "runtime_commit": {
                "type": "repo_commit",
                "repo": "GlacierEQ/mega-skills",
                "sha": "b" * 40,
            },
            "genius_mastery_head": {
                "type": "cross_repo_commit",
                "repo": "GlacierEQ/Genius-Mastery",
                "sha": "c" * 40,
            },
            "host_lane_test_blob": {
                "type": "blob",
                "repo": "GlacierEQ/mega-skills",
                "sha": "d" * 40,
            },
        }

    def enable_provider_v2(self, pointer):
        pointer["provider_state_schema_version"] = 2
        pointer["verified_provider_state"] = self.provider_state()
        return pointer

    def test_accepts_consistent_pointer(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        result = mod.validate_pointer(pointer, root, lambda _: "a" * 40)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["run_sequence"], 6)
        self.assertEqual(result["provider_state"]["status"], "LEGACY")

    def test_rejects_stale_receipt_commit(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        with self.assertRaisesRegex(ValueError, "current_run_commit drifted"):
            mod.validate_pointer(pointer, root, lambda _: "b" * 40)

    def test_rejects_sequence_regression(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        pointer["run_sequence"] = 5
        with self.assertRaisesRegex(ValueError, "sequence disagrees"):
            mod.validate_pointer(pointer, root, lambda _: "a" * 40)

    def test_rejects_support_only_receipt(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        receipt = json.loads(path.read_text())
        receipt["objective_state_delta"]["changed"] = False
        path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "changed=true"):
            mod.validate_pointer(pointer, root, lambda _: "a" * 40)

    def test_rejects_frontier_disagreement(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        pointer["next_executable_frontier"] = "different frontier"
        with self.assertRaisesRegex(ValueError, "frontier disagrees"):
            mod.validate_pointer(pointer, root, lambda _: "a" * 40)

    def test_v2_accepts_reachable_same_repo_and_typed_external_refs(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v2(pointer)
        result = mod.validate_pointer(
            pointer,
            root,
            lambda _: "a" * 40,
            lambda sha, _: sha == "b" * 40,
        )
        self.assertEqual(result["provider_state"]["status"], "PASS")
        self.assertEqual(result["provider_state"]["same_repo_commits"], 1)

    def test_v2_rejects_nonexistent_same_repo_commit(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v2(pointer)
        with self.assertRaisesRegex(ValueError, "not reachable from repository HEAD"):
            mod.validate_pointer(
                pointer,
                root,
                lambda _: "a" * 40,
                lambda _sha, _root: False,
            )

    def test_v2_rejects_untyped_hex_identifier(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v2(pointer)
        pointer["verified_provider_state"]["runtime_commit"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "must be a typed object"):
            mod.validate_pointer(
                pointer,
                root,
                lambda _: "a" * 40,
                lambda _sha, _root: True,
            )

    def test_v2_rejects_same_repo_disguised_as_cross_repo(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v2(pointer)
        pointer["verified_provider_state"]["runtime_commit"]["type"] = "cross_repo_commit"
        with self.assertRaisesRegex(ValueError, "cannot classify a same-repository commit"):
            mod.validate_pointer(
                pointer,
                root,
                lambda _: "a" * 40,
                lambda _sha, _root: True,
            )


if __name__ == "__main__":
    unittest.main()
