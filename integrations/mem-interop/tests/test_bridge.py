import os, pathlib, sqlite3, subprocess, sys, tempfile, unittest, json
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bridge'))
DB=pathlib.Path(os.environ.get('MEM_TEST_DB',str(ROOT/'.state-source-do-not-commit.sqlite')))
class BridgeTest(unittest.TestCase):
 def setUp(self):
  from mem_archive_mcp import MemoryArchive
  self.archive=MemoryArchive(DB)
 def tearDown(self): self.archive.close()
 def test_status_truthful(self):
  data=self.archive.status();self.assertEqual(data['notes'],835);self.assertEqual(data['bodies'],219);self.assertEqual(data['source_class'],'MEM_SECONDARY')
 def test_search_bounded_and_source_class(self):
  out=self.archive.search('JBPHH',limit=4);self.assertLessEqual(len(out),4);self.assertTrue(out);self.assertTrue(all(item['source_class']=='MEM_SECONDARY' for item in out))
 def test_mission_not_native_proof(self):
  out=self.archive.mission('JBPHH');self.assertIn('MEM_SECONDARY',out['source_class']);self.assertFalse(out['provider_outcome_verified'])
 def test_body_is_opt_in_and_sensitive_denied_by_default(self):
  cur=self.archive.db.execute('SELECT note_id FROM note_body LIMIT 1').fetchone()[0]
  x=self.archive.note(cur);self.assertNotIn('body',x)
  x=self.archive.note(cur,include_body=True);self.assertNotIn('body',x)
 def test_queries_read_only_and_not_sql_injectable(self):
  self.assertEqual([],self.archive.search('" OR 1=1 --',limit=5))
  before=self.archive.status()['notes'];self.archive.search('drop table notes');self.assertEqual(self.archive.status()['notes'],before)
 def test_stdio_mcp_initialize_and_tools(self):
  cmd=[sys.executable,str(ROOT/'bridge'/'mem_archive_mcp.py'),'--db',str(DB)]
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   reqs=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/list'},{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'memory_status','arguments':{}}}]
   out,_=p.communicate(''.join(json.dumps(v)+'\n' for v in reqs),timeout=8)
   rows=[json.loads(l) for l in out.splitlines()];self.assertEqual([1,2,3],[v['id'] for v in rows]);self.assertGreaterEqual(len(rows[1]['result']['tools']),4)
   self.assertIn('835',rows[2]['result']['content'][0]['text'])
  finally:
   if p.poll() is None:p.kill()
 def test_missing_db_fails_closed(self):
  from mem_archive_mcp import MemoryArchive
  with self.assertRaises((FileNotFoundError,ValueError,sqlite3.OperationalError)): MemoryArchive('/tmp/glaciereq-no-such-db.sqlite')
class ConfigTest(unittest.TestCase):
 def test_config_merger_preserves_existing(self):
  from pathlib import Path
  sys.path.insert(0,str(ROOT/'scripts'))
  from install_omp import combine
  old={'mcpServers':{'personal':{'type':'stdio','command':'safe'}},'disabledServers':['x']}
  updated=combine(old,'/abs/db.sqlite',str(ROOT/'bridge'/'mem_archive_mcp.py'))
  self.assertEqual(old['mcpServers']['personal'],updated['mcpServers']['personal']);self.assertEqual(['x'],updated['disabledServers'])
  self.assertIn('mem-live',updated['mcpServers']);self.assertIn('glaciereq-archive',updated['mcpServers'])
 def test_existing_name_collision_rejected(self):
  from install_omp import combine
  with self.assertRaises(ValueError):combine({'mcpServers':{'mem-live':{'type':'http','url':'https://unknown'}}},'/abs/db.sqlite','/abs/mcp.py')
if __name__=='__main__':unittest.main()

class ExtraSafetyTest(unittest.TestCase):
 def test_config_writes_atomically_and_keeps_prior_bytes_backup(self):
  from install_omp import combine
  with tempfile.TemporaryDirectory() as tmp:
   orig=pathlib.Path(tmp)/'mcp.json'
   content=json.dumps({'mcpServers':{'existing':{'command':'echo','args':['hello']}}})
   orig.write_text(content)
   cmd=[sys.executable,str(ROOT/'scripts'/'install_omp.py'),'--config',str(orig),'--db',str(DB),'--server',str(ROOT/'bridge'/'mem_archive_mcp.py')]
   preview=subprocess.run(cmd,capture_output=True,text=True,check=True)
   self.assertIn('DRY RUN ONLY',preview.stdout);self.assertEqual(content,orig.read_text())
   apply=subprocess.run(cmd+['--apply'],capture_output=True,text=True,check=True)
   self.assertIn('WRITTEN AND READ BACK',apply.stdout)
   self.assertEqual(content,(pathlib.Path(str(orig)+'.backup-before-glaciereq-mem')).read_text())
   self.assertEqual('hello',json.loads(orig.read_text())['mcpServers']['existing']['args'][0])
 def test_body_access_requires_explicit_opt_in(self):
  from mem_archive_mcp import MemoryArchive
  archive=MemoryArchive(DB)
  try:
   non_sensitive=archive.db.execute('''SELECT b.note_id FROM note_body b JOIN notes n ON n.note_id=b.note_id
             WHERE n.sensitivity_json='[]' AND length(b.content)>12 LIMIT 1''').fetchone()
   self.assertIsNotNone(non_sensitive)
   with mock.patch.dict(os.environ,{'GLACIEREQ_MEM_ALLOW_BODIES':'1'},clear=False):
    permitted=archive.note(non_sensitive[0],include_body=True)
    self.assertIn('body',permitted)
    locked=archive.note(non_sensitive[0],include_body=False)
    self.assertNotIn('body',locked)
  finally:archive.close()