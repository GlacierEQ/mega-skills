import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
import subprocess

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


    def test_recovery_tuple_digest_changes_when_binding_moves(self):
        now=datetime(2026,9,12,tzinfo=timezone.utc); pointer=self.pointer(now)
        a=mod.digest(mod.recovery_tuple(pointer))
        pointer["next_executable_frontier"]="moved"
        self.assertNotEqual(a,mod.digest(mod.recovery_tuple(pointer)))

    def test_assert_snapshot_rejects_origin_move(self):
        pointer={"run_sequence":1,"current_run":"r","current_run_commit":"a","provider_state_schema_version":4,
                 "provider_readback_manifest":{"proof_digest_sha256":"a"*64},
                 "host_runtime_proof":{"receipt_digest_sha256":"b"*64},"next_executable_frontier":"f"}
        snapshot={"local_head":"L","origin_main":"O","mission_tuple_sha256":mod.digest(mod.mission_tuple(pointer)),"recovery_tuple_sha256":mod.digest(mod.recovery_tuple(pointer))}
        with patch.object(mod,'git',side_effect=["", "L", "MOVED"]):
            with self.assertRaisesRegex(RuntimeError,'origin/main moved'):
                mod.assert_snapshot_unchanged(snapshot)

    def test_precommit_allows_renewed_proof_but_rejects_mission_move(self):
        pointer={"run_sequence":1,"current_run":"r","current_run_commit":"a","provider_state_schema_version":4,
                 "provider_readback_manifest":{"proof_digest_sha256":"a"*64},
                 "host_runtime_proof":{"receipt_digest_sha256":"b"*64},"next_executable_frontier":"f"}
        snapshot={"local_head":"L","origin_main":"O","mission_tuple_sha256":mod.digest(mod.mission_tuple(pointer))}
        renewed=json.loads(json.dumps(pointer)); renewed['provider_readback_manifest']['proof_digest_sha256']='c'*64; renewed['host_runtime_proof']['receipt_digest_sha256']='d'*64
        with patch.object(mod,'git',side_effect=["", "L", "O"]):
            mod.assert_precommit_snapshot_unchanged(snapshot,renewed)
        renewed['next_executable_frontier']='changed'
        with patch.object(mod,'git',side_effect=["", "L", "O"]):
            with self.assertRaisesRegex(RuntimeError,'mission tuple moved'):
                mod.assert_precommit_snapshot_unchanged(snapshot,renewed)

    def test_repository_lock_rejects_concurrent_holder(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'.git').mkdir()
            old=mod.ROOT; mod.ROOT=root
            try:
                with mod.renewal_lock():
                    with self.assertRaisesRegex(RuntimeError,'another proof renewal'):
                        with mod.renewal_lock(): pass
            finally: mod.ROOT=old

    def test_commit_publish_builds_two_commits_and_uses_force_with_lease(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as rd:
            root=Path(td); ev=root/'evidence/deep-progress-forge'; ev.mkdir(parents=True)
            subprocess.run(['git','init','-q','-b','main'],cwd=root,check=True)
            subprocess.run(['git','config','user.email','test@example.com'],cwd=root,check=True)
            subprocess.run(['git','config','user.name','Test'],cwd=root,check=True)
            remote=Path(rd)/'remote.git'; subprocess.run(['git','init','--bare','-q','-b','main',str(remote)],check=True)
            subprocess.run(['git','remote','add','origin',str(remote)],cwd=root,check=True)
            for name,data in [('LATEST.json',{}),('provider-readback-manifest-v2.json',{'p':1}),('host-skills-lifecycle-latest.json',{'h':1}),('proof-renewal-latest.json',{'r':1})]:
                (ev/name).write_text(json.dumps(data))
            subprocess.run(['git','add','.'],cwd=root,check=True); subprocess.run(['git','commit','-qm','base'],cwd=root,check=True); subprocess.run(['git','push','-q','-u','origin','main'],cwd=root,check=True)
            old=(mod.ROOT,mod.EVIDENCE,mod.LATEST,mod.PROVIDER,mod.HOST,mod.RENEWAL)
            mod.ROOT=root; mod.EVIDENCE=ev; mod.LATEST=ev/'LATEST.json'; mod.PROVIDER=ev/'provider-readback-manifest-v2.json'; mod.HOST=ev/'host-skills-lifecycle-latest.json'; mod.RENEWAL=ev/'proof-renewal-latest.json'
            try:
                base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
                pointer={"run_sequence":1,"current_run":"r","current_run_commit":"a","provider_state_schema_version":4,"provider_readback_manifest":{"path":"evidence/deep-progress-forge/provider-readback-manifest-v2.json","proof_digest_sha256":"a"*64},"host_runtime_proof":{"path":"evidence/deep-progress-forge/host-skills-lifecycle-latest.json","receipt_digest_sha256":"b"*64},"verification_state":{},"next_executable_frontier":"f"}
                snapshot={"local_head":base,"origin_main":base,"mission_tuple":mod.mission_tuple(pointer),"mission_tuple_sha256":mod.digest(mod.mission_tuple(pointer)),"recovery_tuple":mod.recovery_tuple(pointer),"recovery_tuple_sha256":mod.digest(mod.recovery_tuple(pointer))}
                mod._atomic_json(mod.LATEST,pointer); mod._atomic_json(mod.PROVIDER,{"p":2}); mod._atomic_json(mod.HOST,{"h":2})
                receipt={"receipt_digest_sha256":"x"*64}
                result=mod.commit_and_publish(pointer,receipt,snapshot,push=True)
                remote_head=subprocess.check_output(['git','--git-dir',remote,'rev-parse','refs/heads/main'],text=True).strip()
                self.assertEqual(remote_head,result['final_commit'])
                self.assertEqual(subprocess.check_output(['git','rev-list','--count',f'{base}..{remote_head}'],cwd=root,text=True).strip(),'2')
                final_receipt=json.loads(mod.RENEWAL.read_text())
                self.assertEqual(final_receipt['git_finalization']['payload_commit'],result['payload_commit'])
            finally:
                mod.ROOT,mod.EVIDENCE,mod.LATEST,mod.PROVIDER,mod.HOST,mod.RENEWAL=old

    def _abandoned_repo(self):
        td=tempfile.TemporaryDirectory(); rd=tempfile.TemporaryDirectory()
        root=Path(td.name); remote=Path(rd.name)/"remote.git"
        subprocess.run(["git","init","-q","-b","main"],cwd=root,check=True)
        subprocess.run(["git","config","user.email","test@example.com"],cwd=root,check=True)
        subprocess.run(["git","config","user.name","Test"],cwd=root,check=True)
        subprocess.run(["git","init","--bare","-q","-b","main",str(remote)],check=True)
        subprocess.run(["git","remote","add","origin",str(remote)],cwd=root,check=True)
        (root/"base").write_text("base")
        subprocess.run(["git","add","."],cwd=root,check=True); subprocess.run(["git","commit","-qm","base"],cwd=root,check=True)
        subprocess.run(["git","push","-q","-u","origin","main"],cwd=root,check=True)
        base=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
        (root/"payload").write_text("payload"); subprocess.run(["git","add","."],cwd=root,check=True); subprocess.run(["git","commit","-qm","payload"],cwd=root,check=True)
        payload=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
        (root/"final").write_text("final"); subprocess.run(["git","add","."],cwd=root,check=True); subprocess.run(["git","commit","-qm","final"],cwd=root,check=True)
        final=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
        return td,rd,root,remote,base,payload,final

    def test_recover_abandoned_transaction_retries_when_provider_parent_unchanged(self):
        td,rd,root,remote,base,payload,final=self._abandoned_repo(); self.addCleanup(td.cleanup); self.addCleanup(rd.cleanup)
        old=(mod.ROOT,mod.ABANDONED); mod.ROOT=root; mod.ABANDONED=root/'evidence/deep-progress-forge/proof-renewal-abandoned.json'
        try:
            mod._atomic_json(mod.ABANDONED,{"schema_version":1,"status":"ABANDONED_LOCAL_TRANSACTION","origin_parent":base,"payload_commit":payload,"final_commit":final})
            result=mod.recover_abandoned_transaction(push=True)
            self.assertEqual(result["status"],"RECOVERED")
            self.assertFalse(mod.ABANDONED.exists())
            remote_head=subprocess.check_output(["git","--git-dir",remote,"rev-parse","refs/heads/main"],text=True).strip()
            self.assertEqual(remote_head,result["provider_main_after_evidence"])
            self.assertEqual(subprocess.check_output(["git","rev-parse",f"{remote_head}^"],cwd=root,text=True).strip(),final)
            receipt=json.loads((root/result["recovery_receipt"]).read_text())
            self.assertEqual(receipt["origin_parent"],base)
            self.assertEqual(receipt["final_commit"],final)
            self.assertEqual(receipt["provider_main_before"],base)
            self.assertEqual(receipt["provider_main_after"],final)
        finally: mod.ROOT,mod.ABANDONED=old

    def test_recover_abandoned_transaction_is_continuity_gate_end_to_end(self):
        td,rd,root,remote,base,payload,final=self._abandoned_repo(); self.addCleanup(td.cleanup); self.addCleanup(rd.cleanup)
        old=(mod.ROOT,mod.ABANDONED); mod.ROOT=root; mod.ABANDONED=root/'evidence/deep-progress-forge/proof-renewal-abandoned.json'
        mod.ABANDONED.parent.mkdir(parents=True,exist_ok=True)
        try:
            marker={"schema_version":1,"status":"ABANDONED_LOCAL_TRANSACTION","origin_parent":base,"payload_commit":payload,"final_commit":final,"reason":"synthetic rejected lease"}
            mod._atomic_json(mod.ABANDONED,marker)
            with self.assertRaisesRegex(ValueError,"unresolved abandoned proof-renewal transaction"):
                mod.validator.validate_no_abandoned_renewal(root)
            result=mod.recover_abandoned_transaction(push=True)
            self.assertEqual(result["status"],"RECOVERED")
            self.assertEqual(mod.validator.validate_no_abandoned_renewal(root)["status"],"NONE")
            self.assertFalse(mod.ABANDONED.exists())
            self.assertTrue((root/result["recovery_receipt"]).is_file())
        finally: mod.ROOT,mod.ABANDONED=old

    def test_recover_abandoned_no_push_preserves_marker(self):
        td,rd,root,remote,base,payload,final=self._abandoned_repo(); self.addCleanup(td.cleanup); self.addCleanup(rd.cleanup)
        old=(mod.ROOT,mod.ABANDONED); mod.ROOT=root; mod.ABANDONED=root/'evidence/deep-progress-forge/proof-renewal-abandoned.json'
        mod.ABANDONED.parent.mkdir(parents=True,exist_ok=True)
        try:
            mod._atomic_json(mod.ABANDONED,{"schema_version":1,"status":"ABANDONED_LOCAL_TRANSACTION","origin_parent":base,"payload_commit":payload,"final_commit":final})
            result=mod.recover_abandoned_transaction(push=False)
            self.assertEqual(result["status"],"RECOVERABLE")
            self.assertTrue(mod.ABANDONED.exists())
        finally: mod.ROOT,mod.ABANDONED=old

    def test_recover_abandoned_transaction_blocks_when_provider_moved(self):
        td,rd,root,remote,base,payload,final=self._abandoned_repo(); self.addCleanup(td.cleanup); self.addCleanup(rd.cleanup)
        mover=Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__('shutil').rmtree(mover,ignore_errors=True))
        subprocess.run(["git","clone","-q",str(remote),str(mover)],check=True)
        subprocess.run(["git","config","user.email","mover@example.com"],cwd=mover,check=True); subprocess.run(["git","config","user.name","Mover"],cwd=mover,check=True)
        (mover/"move").write_text("moved"); subprocess.run(["git","add","."],cwd=mover,check=True); subprocess.run(["git","commit","-qm","provider moved"],cwd=mover,check=True); subprocess.run(["git","push","-q","origin","main"],cwd=mover,check=True)
        old=(mod.ROOT,mod.ABANDONED); mod.ROOT=root; mod.ABANDONED=root/'evidence/deep-progress-forge/proof-renewal-abandoned.json'
        try:
            mod._atomic_json(mod.ABANDONED,{"schema_version":1,"status":"ABANDONED_LOCAL_TRANSACTION","origin_parent":base,"payload_commit":payload,"final_commit":final})
            result=mod.recover_abandoned_transaction(push=True)
            self.assertEqual(result["status"],"BLOCKED_PROVIDER_MOVED")
            self.assertTrue(mod.ABANDONED.exists())
        finally: mod.ROOT,mod.ABANDONED=old

if __name__ == '__main__': unittest.main()
