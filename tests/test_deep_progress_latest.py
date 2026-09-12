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

    def enable_provider_v3(self, pointer, root):
        pointer["provider_state_schema_version"] = 3
        pointer["verified_provider_state"] = self.provider_state()
        proofs = [
            {
                "name": "genius_mastery_head",
                "type": "cross_repo_commit",
                "repo": "GlacierEQ/Genius-Mastery",
                "sha": "c" * 40,
                "provider_url": "https://github.com/GlacierEQ/Genius-Mastery/commit/" + "c" * 40,
            }
        ]
        digest = mod.canonical_digest(proofs)
        rel = Path("evidence/deep-progress-forge/provider-readback-manifest-v1.json")
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "schema_version": 1,
            "source": "test provider readback",
            "proofs": proofs,
            "proof_digest_sha256": digest,
        }), encoding="utf-8")
        pointer["provider_readback_manifest"] = {
            "path": str(rel),
            "proof_digest_sha256": digest,
        }
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

    def test_v3_accepts_reachable_same_repo_and_typed_external_refs(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v3(pointer, root)
        result = mod.validate_pointer(
            pointer,
            root,
            lambda _: "a" * 40,
            lambda sha, _: sha == "b" * 40,
            lambda sha, _: "blob" if sha == "d" * 40 else None,
        )
        self.assertEqual(result["provider_state"]["status"], "PASS")
        self.assertEqual(result["provider_state"]["same_repo_commits"], 1)
        self.assertEqual(result["provider_state"]["same_repo_blobs"], 1)
        self.assertEqual(result["provider_state"]["cross_repo_proofs"], 1)

    def test_v3_rejects_nonexistent_same_repo_commit(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v3(pointer, root)
        with self.assertRaisesRegex(ValueError, "not reachable from repository HEAD"):
            mod.validate_pointer(
                pointer,
                root,
                lambda _: "a" * 40,
                lambda _sha, _root: False,
            )

    def test_v3_rejects_untyped_hex_identifier(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v3(pointer, root)
        pointer["verified_provider_state"]["runtime_commit"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "must be a typed object"):
            mod.validate_pointer(
                pointer,
                root,
                lambda _: "a" * 40,
                lambda _sha, _root: True,
            )

    def test_v3_rejects_same_repo_disguised_as_cross_repo(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v3(pointer, root)
        pointer["verified_provider_state"]["runtime_commit"]["type"] = "cross_repo_commit"
        with self.assertRaisesRegex(ValueError, "cannot classify a same-repository commit"):
            mod.validate_pointer(
                pointer,
                root,
                lambda _: "a" * 40,
                lambda _sha, _root: True,
            )

    def test_v3_rejects_tampered_provider_manifest_digest(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v3(pointer, root)
        manifest_path = root / pointer["provider_readback_manifest"]["path"]
        manifest = json.loads(manifest_path.read_text())
        manifest["proofs"][0]["sha"] = "e" * 40
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "manifest digest mismatch"):
            mod.validate_pointer(
                pointer, root, lambda _: "a" * 40, lambda _sha, _root: True,
                lambda _sha, _root: "blob",
            )

    def test_v3_rejects_cross_repo_reference_without_matching_proof(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v3(pointer, root)
        pointer["verified_provider_state"]["genius_mastery_head"]["sha"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "lacks matching provider readback proof"):
            mod.validate_pointer(
                pointer, root, lambda _: "a" * 40, lambda _sha, _root: True,
                lambda _sha, _root: "blob",
            )

    def enable_provider_v4(self, pointer, root, *, stale_provider=False, stale_host=False):
        from datetime import datetime, timedelta, timezone
        now = datetime(2026, 9, 12, 4, 45, tzinfo=timezone.utc)
        pointer["provider_state_schema_version"] = 4
        pointer["verified_provider_state"] = self.provider_state()
        provider_observed = now - timedelta(hours=2 if stale_provider else 0)
        provider_due = now - timedelta(hours=1) if stale_provider else now + timedelta(hours=24)
        proofs = [{
            "name": "genius_mastery_head", "type": "cross_repo_commit",
            "repo": "GlacierEQ/Genius-Mastery", "sha": "c" * 40,
            "provider_url": "https://github.com/GlacierEQ/Genius-Mastery/commit/" + "c" * 40,
            "provider_object": {"kind": "commit", "tree_sha": "e" * 40, "parent_shas": ["f" * 40]},
        }]
        manifest = {
            "schema_version": 2, "source": "test GitHub readback",
            "observed_at": provider_observed.isoformat().replace("+00:00", "Z"),
            "revalidate_after": provider_due.isoformat().replace("+00:00", "Z"),
            "proofs": proofs,
        }
        digest = mod.canonical_digest(mod.manifest_digest_payload(manifest))
        manifest["proof_digest_sha256"] = digest
        mrel = Path("evidence/deep-progress-forge/provider-readback-manifest-v2.json")
        (root / mrel).write_text(json.dumps(manifest), encoding="utf-8")
        pointer["provider_readback_manifest"] = {"path": str(mrel), "proof_digest_sha256": digest}

        host_observed = now - timedelta(hours=2 if stale_host else 0)
        host_due = now - timedelta(hours=1) if stale_host else now + timedelta(hours=8)
        host = {
            "schema_version": 2, "lane": "operator_host_runtime", "device": "test-host",
            "skills_bin": "~/bin/skills", "skills_bin_sha256": "1" * 64,
            "observed_at": host_observed.isoformat().replace("+00:00", "Z"),
            "revalidate_after": host_due.isoformat().replace("+00:00", "Z"),
            "commands": ["status"], "observations": {"status": "OPTIMAL"},
            "assertions": {"host_state_restored_exactly": True},
        }
        host["receipt_digest_sha256"] = mod.receipt_digest(host)
        hrel = Path("evidence/deep-progress-forge/host-skills-lifecycle-test.json")
        (root / hrel).write_text(json.dumps(host), encoding="utf-8")
        pointer["host_runtime_proof"] = {
            "path": str(hrel), "receipt_digest_sha256": host["receipt_digest_sha256"],
            "observed_at": host["observed_at"], "revalidate_after": host["revalidate_after"],
            "executable_sha256": host["skills_bin_sha256"],
        }
        return now

    def test_v3_rejects_non_blob_same_repo_blob_reference(self):
        tmp, root, path, pointer = self.fixture()
        self.addCleanup(tmp.cleanup)
        self.enable_provider_v3(pointer, root)
        with self.assertRaisesRegex(ValueError, "not a same-repository blob object"):
            mod.validate_pointer(
                pointer, root, lambda _: "a" * 40, lambda _sha, _root: True,
                lambda _sha, _root: "tree",
            )

    def test_v4_accepts_fresh_provider_and_host_leases(self):
        tmp, root, path, pointer = self.fixture(); self.addCleanup(tmp.cleanup)
        now = self.enable_provider_v4(pointer, root)
        result = mod.validate_pointer(pointer, root, lambda _: "a" * 40,
            lambda sha, _: sha == "b" * 40, lambda sha, _: "blob" if sha == "d" * 40 else None, now=now)
        self.assertEqual(result["provider_state"]["status"], "PASS")
        self.assertEqual(result["host_runtime_proof"]["status"], "PASS")

    def test_v4_rejects_stale_provider_lease(self):
        tmp, root, path, pointer = self.fixture(); self.addCleanup(tmp.cleanup)
        now = self.enable_provider_v4(pointer, root, stale_provider=True)
        with self.assertRaisesRegex(ValueError, "provider readback proof is stale"):
            mod.validate_pointer(pointer, root, lambda _: "a" * 40, lambda _sha, _root: True, lambda _sha, _root: "blob", now=now)

    def test_v4_rejects_stale_host_lease(self):
        tmp, root, path, pointer = self.fixture(); self.addCleanup(tmp.cleanup)
        now = self.enable_provider_v4(pointer, root, stale_host=True)
        with self.assertRaisesRegex(ValueError, "host runtime proof is stale"):
            mod.validate_pointer(pointer, root, lambda _: "a" * 40, lambda _sha, _root: True, lambda _sha, _root: "blob", now=now)

    def test_v4_rejects_host_executable_fingerprint_drift(self):
        tmp, root, path, pointer = self.fixture(); self.addCleanup(tmp.cleanup)
        now = self.enable_provider_v4(pointer, root)
        pointer["host_runtime_proof"]["executable_sha256"] = "2" * 64
        with self.assertRaisesRegex(ValueError, "executable fingerprint disagrees"):
            mod.validate_pointer(pointer, root, lambda _: "a" * 40, lambda _sha, _root: True, lambda _sha, _root: "blob", now=now)

    def test_v4_rejects_provider_metadata_without_tree_identity(self):
        tmp, root, path, pointer = self.fixture(); self.addCleanup(tmp.cleanup)
        now = self.enable_provider_v4(pointer, root)
        manifest_path = root / pointer["provider_readback_manifest"]["path"]
        manifest = json.loads(manifest_path.read_text())
        manifest["proofs"][0]["provider_object"].pop("tree_sha")
        manifest["proof_digest_sha256"] = mod.canonical_digest(mod.manifest_digest_payload(manifest))
        manifest_path.write_text(json.dumps(manifest))
        pointer["provider_readback_manifest"]["proof_digest_sha256"] = manifest["proof_digest_sha256"]
        with self.assertRaisesRegex(ValueError, "requires provider tree_sha"):
            mod.validate_pointer(pointer, root, lambda _: "a" * 40, lambda _sha, _root: True, lambda _sha, _root: "blob", now=now)

    def _renewal_chain_fixture(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        subprocess = __import__("subprocess")
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        ev = root / "evidence/deep-progress-forge"; ev.mkdir(parents=True)
        provider = ev / "provider-readback-manifest-v2.json"; provider.write_text('{"provider":1}')
        host = ev / "host-skills-lifecycle-latest.json"; host.write_text('{"host":1}')
        latest = ev / "LATEST.json"; latest.write_text('{}')
        renewal = ev / "proof-renewal-latest.json"; renewal.write_text('{}')
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "origin parent"], cwd=root, check=True)
        origin = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        provider.write_text('{"provider":2}'); host.write_text('{"host":2}')
        subprocess.run(["git", "add", str(provider.relative_to(root)), str(host.relative_to(root))], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "payload"], cwd=root, check=True)
        payload = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        payload_tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=root, text=True).strip()
        blobs = {
            "provider": subprocess.check_output(["git", "rev-parse", f"{payload}:evidence/deep-progress-forge/provider-readback-manifest-v2.json"], cwd=root, text=True).strip(),
            "host": subprocess.check_output(["git", "rev-parse", f"{payload}:evidence/deep-progress-forge/host-skills-lifecycle-latest.json"], cwd=root, text=True).strip(),
        }
        receipt = {"schema_version":1,"transaction":"atomic_proof_renewal","git_finalization":{"origin_parent":origin,"payload_commit":payload,"payload_tree":payload_tree,"payload_blob_shas":blobs}}
        receipt["receipt_digest_sha256"] = mod.receipt_digest(receipt)
        renewal.write_text(json.dumps(receipt))
        pointer = {"verification_state":{"latest_proof_renewal_payload_commit":payload,"latest_proof_renewal_payload_tree":payload_tree,"latest_proof_renewal_origin_parent":origin,"latest_proof_renewal_receipt_digest":receipt["receipt_digest_sha256"]}}
        latest.write_text(json.dumps(pointer))
        subprocess.run(["git", "add", str(renewal.relative_to(root)), str(latest.relative_to(root))], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "finalization"], cwd=root, check=True)
        final = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        final_tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=root, text=True).strip()
        pointer["verification_state"]["latest_proof_renewal_finalization_commit"] = final
        pointer["verification_state"]["latest_proof_renewal_finalization_tree"] = final_tree
        return tmp, root, pointer, receipt

    def test_v4_renewal_chain_traverses_commits_trees_blobs_and_receipt(self):
        tmp, root, pointer, receipt = self._renewal_chain_fixture(); self.addCleanup(tmp.cleanup)
        result = mod.validate_latest_renewal_chain(pointer, root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["payload_blob_shas"], receipt["git_finalization"]["payload_blob_shas"])

    def test_v4_renewal_chain_rejects_payload_blob_drift(self):
        tmp, root, pointer, receipt = self._renewal_chain_fixture(); self.addCleanup(tmp.cleanup)
        path = root / "evidence/deep-progress-forge/proof-renewal-latest.json"
        receipt["git_finalization"]["payload_blob_shas"]["provider"] = "0" * 40
        receipt["receipt_digest_sha256"] = mod.receipt_digest(receipt)
        path.write_text(json.dumps(receipt))
        pointer["verification_state"]["latest_proof_renewal_receipt_digest"] = receipt["receipt_digest_sha256"]
        with self.assertRaisesRegex(ValueError, "provider blob identity mismatch"):
            mod.validate_latest_renewal_chain(pointer, root)

    def test_v4_renewal_chain_rejects_wrong_payload_parent(self):
        tmp, root, pointer, receipt = self._renewal_chain_fixture(); self.addCleanup(tmp.cleanup)
        pointer["verification_state"]["latest_proof_renewal_origin_parent"] = "0" * 40
        receipt["git_finalization"]["origin_parent"] = "0" * 40
        receipt["receipt_digest_sha256"] = mod.receipt_digest(receipt)
        (root / "evidence/deep-progress-forge/proof-renewal-latest.json").write_text(json.dumps(receipt))
        pointer["verification_state"]["latest_proof_renewal_receipt_digest"] = receipt["receipt_digest_sha256"]
        with self.assertRaisesRegex(ValueError, "payload parent"):
            mod.validate_latest_renewal_chain(pointer, root)

    def test_history_hydration_turns_shallow_repo_into_full_history(self):
        import subprocess
        with tempfile.TemporaryDirectory() as remote_dir, tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as clone_parent:
            remote = Path(remote_dir) / "remote.git"
            source = Path(source_dir)
            subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=source, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=source, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=source, check=True)
            (source / "x").write_text("one")
            subprocess.run(["git", "add", "."], cwd=source, check=True); subprocess.run(["git", "commit", "-qm", "one"], cwd=source, check=True)
            (source / "x").write_text("two")
            subprocess.run(["git", "commit", "-qam", "two"], cwd=source, check=True)
            subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=source, check=True); subprocess.run(["git", "push", "-q", "origin", "main"], cwd=source, check=True)
            clone = Path(clone_parent) / "clone"
            subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + str(remote), str(clone)], check=True)
            self.assertEqual(subprocess.check_output(["git", "rev-parse", "--is-shallow-repository"], cwd=clone, text=True).strip(), "true")
            result = mod.ensure_repository_history(clone)
            self.assertTrue(result["hydrated"])
            self.assertEqual(subprocess.check_output(["git", "rev-parse", "--is-shallow-repository"], cwd=clone, text=True).strip(), "false")


if __name__ == "__main__":
    unittest.main()
