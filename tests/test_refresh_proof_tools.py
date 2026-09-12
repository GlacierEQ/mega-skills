import importlib.util, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
provider=load('refresh_provider',Path('scripts/refresh_provider_readback_manifest.py'))
host=load('refresh_host',Path('scripts/refresh_host_runtime_proof.py'))

class RefreshProofToolsTests(unittest.TestCase):
    def test_provider_refresh_binds_immutable_metadata_and_lease(self):
        pointer={'verified_provider_state':{'x':{'type':'cross_repo_commit','repo':'GlacierEQ/Genius-Mastery','sha':'a'*40}}}
        meta={'provider_url':'https://github.com/x','provider_message':'m','provider_object':{'kind':'commit','tree_sha':'b'*40,'parent_shas':['c'*40]}}
        with patch.object(provider,'gh_commit',return_value=meta):
            m=provider.build(pointer,datetime(2026,9,12,tzinfo=timezone.utc),24)
        self.assertEqual(m['proofs'][0]['provider_object']['tree_sha'],'b'*40)
        self.assertEqual(m['revalidate_after'],'2026-09-13T00:00:00Z')
        self.assertEqual(len(m['proof_digest_sha256']),64)

    def test_host_refresh_restores_state_and_binds_executable(self):
        with tempfile.TemporaryDirectory() as td:
            exe=Path(td)/'skills'; exe.write_bytes(b'fixture'); exe.chmod(0o755)
            base={'status':'OPTIMAL','dynamic_active_skills':[]}; active={'status':'OPTIMAL','dynamic_active_skills':['playwright-skill']}
            calls=[]
            def fake(_skills,args):
                calls.append(tuple(args))
                if args==['status']:
                    return active if ('activate','playwright-skill') in calls and ('deactivate','playwright-skill') not in calls else base
                if args[0]=='search': return [{'name':'supabase'}]
                if args[0]=='recommend': return [{'name':'postgres'}]
                if args[0]=='activate': return {'success':True}
                if args[0]=='deactivate': return {'success':True}
                raise AssertionError(args)
            with patch.object(host,'run_json',side_effect=fake), patch.object(host.subprocess,'check_output',return_value='fixture-host\n'):
                r=host.build(exe,8)
            self.assertTrue(r['assertions']['host_state_restored_exactly'])
            self.assertTrue(r['assertions']['activation_verified'])
            self.assertIn(('deactivate','playwright-skill'),calls)
            self.assertEqual(len(r['skills_bin_sha256']),64)

    def test_host_refresh_deactivates_after_post_activation_failure(self):
        with tempfile.TemporaryDirectory() as td:
            exe=Path(td)/'skills'; exe.write_bytes(b'fixture'); exe.chmod(0o755); calls=[]; status_count=0
            def fake(_skills,args):
                nonlocal status_count; calls.append(tuple(args))
                if args==['status']:
                    status_count+=1
                    if status_count==2: raise RuntimeError('readback failed')
                    return {'status':'OPTIMAL','dynamic_active_skills':[]}
                if args[0] in {'search','recommend'}: return [{}]
                if args[0] in {'activate','deactivate'}: return {'success':True}
            with patch.object(host,'run_json',side_effect=fake), patch.object(host.subprocess,'check_output',return_value='fixture-host\n'):
                with self.assertRaisesRegex(RuntimeError,'readback failed'): host.build(exe,8)
            self.assertIn(('deactivate','playwright-skill'),calls)

if __name__=='__main__': unittest.main()
