import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/renew_proof_leases.py"
spec = importlib.util.spec_from_file_location("renew_proof_leases", SCRIPT)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


class RenewProofLeasesTests(unittest.TestCase):
    def pointer(self, now):
        return {
            "run_sequence": 9,
            "next_executable_frontier": "atomic renewal",
            "provider_readback_manifest": {"path":"evidence/deep-progress-forge/provider.json","proof_digest_sha256":"a"*64},
            "host_runtime_proof": {"path":"evidence/deep-progress-forge/host.json","receipt_digest_sha256":"b"*64,
                "observed_at":mod.provider_mod.stamp(now),"revalidate_after":mod.provider_mod.stamp(now+timedelta(hours=8)),"executable_sha256":"c"*64},
            "verification_state": {},
        }

    def test_status_recommends_near_expiry(self):
        now=datetime(2026,9,12,tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'evidence/deep-progress-forge').mkdir(parents=True)
            provider_path=root/'evidence/deep-progress-forge/provider.json'
            provider_path.write_text(json.dumps({"revalidate_after":mod.provider_mod.stamp(now+timedelta(minutes=30))}))
            pointer=self.pointer(now); pointer['provider_readback_manifest']['path']=str(provider_path.relative_to(root))
            old=mod.ROOT; mod.ROOT=root
            try:
                status=mod.lease_status(pointer,now=now,renew_within_hours=2)
            finally: mod.ROOT=old
            self.assertTrue(status['provider']['renew_recommended'])
            self.assertTrue(status['renewal_required'])

    def test_renew_preserves_sequence_and_frontier(self):
        now=datetime(2026,9,12,tzinfo=timezone.utc); pointer=self.pointer(now)
        provider={"proof_digest_sha256":"d"*64,"observed_at":mod.provider_mod.stamp(now),"revalidate_after":mod.provider_mod.stamp(now+timedelta(hours=24))}
        host={"receipt_digest_sha256":"e"*64,"observed_at":mod.provider_mod.stamp(now),"revalidate_after":mod.provider_mod.stamp(now+timedelta(hours=8)),"skills_bin_sha256":"f"*64}
        candidate,_,_,delta=mod.renew(pointer,Path('/tmp/skills'),now=now,provider_builder=lambda _:provider,host_builder=lambda:host,validate=lambda _: {"status":"PASS"})
        self.assertEqual(candidate['run_sequence'],9)
        self.assertEqual(candidate['next_executable_frontier'],'atomic renewal')
        self.assertEqual(delta['before']['run_sequence'],delta['after']['run_sequence'])
        self.assertEqual(delta['before']['frontier'],delta['after']['frontier'])

    def test_commit_transaction_rolls_back_all_files_on_validation_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); ev=root/'evidence/deep-progress-forge'; ev.mkdir(parents=True)
            paths={name:ev/name for name in ['LATEST.json','provider-readback-manifest-v2.json','host-skills-lifecycle-latest.json','proof-renewal-latest.json']}
            for i,p in enumerate(paths.values()): p.write_text(f'old-{i}')
            old_constants=(mod.LATEST,mod.PROVIDER,mod.HOST,mod.RENEWAL)
            mod.LATEST,mod.PROVIDER,mod.HOST,mod.RENEWAL=paths.values()
            before={p:p.read_bytes() for p in paths.values()}
            try:
                with self.assertRaisesRegex(RuntimeError,'validation failed'):
                    mod.commit_transaction({"x":1},{"p":2},{"h":3},{"before":{"run_sequence":9,"frontier":"f","provider_digest":"a","host_digest":"b"},"after":{"run_sequence":9,"frontier":"f","provider_digest":"c","host_digest":"d"}},validate=lambda _: (_ for _ in ()).throw(RuntimeError('validation failed')))
                self.assertEqual({p:p.read_bytes() for p in paths.values()},before)
            finally:
                mod.LATEST,mod.PROVIDER,mod.HOST,mod.RENEWAL=old_constants

    def test_commit_transaction_writes_receipt_only_after_validation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); ev=root/'evidence/deep-progress-forge'; ev.mkdir(parents=True)
            paths=[ev/'LATEST.json',ev/'provider-readback-manifest-v2.json',ev/'host-skills-lifecycle-latest.json',ev/'proof-renewal-latest.json']
            for p in paths: p.write_text('{}')
            old=(mod.LATEST,mod.PROVIDER,mod.HOST,mod.RENEWAL); mod.LATEST,mod.PROVIDER,mod.HOST,mod.RENEWAL=paths
            delta={"before":{"run_sequence":9,"frontier":"f","provider_digest":"a","host_digest":"b"},"after":{"run_sequence":9,"frontier":"f","provider_digest":"c","host_digest":"d"}}
            try:
                receipt=mod.commit_transaction({"candidate":True},{"p":2},{"h":3},delta,validate=lambda _: {"status":"PASS"})
                self.assertTrue(receipt['invariants']['run_sequence_unchanged'])
                self.assertTrue(receipt['invariants']['frontier_unchanged'])
                self.assertTrue(receipt['invariants']['both_lanes_changed'])
                self.assertEqual(json.loads(paths[0].read_text()),{"candidate":True})
                self.assertEqual(json.loads(paths[3].read_text())['transaction'],'atomic_proof_renewal')
            finally: mod.LATEST,mod.PROVIDER,mod.HOST,mod.RENEWAL=old

if __name__ == '__main__': unittest.main()
