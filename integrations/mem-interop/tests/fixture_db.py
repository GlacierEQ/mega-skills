"""Synthetic, non-user-content SQLite fixture for public CI of a private archive bridge."""
import json,sqlite3
from pathlib import Path
IDS=['00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000002','00000000-0000-4000-8000-000000000003']

def create(path):
 p=Path(path)
 if p.exists():p.unlink()
 con=sqlite3.connect(p)
 try:
  con.executescript('''
CREATE TABLE notes (note_id TEXT PRIMARY KEY,title TEXT,uri TEXT,created_at TEXT,updated_at TEXT,sensitivity_json TEXT,unfiled INTEGER);
CREATE TABLE note_body (note_id TEXT PRIMARY KEY,content TEXT NOT NULL);
CREATE VIRTUAL TABLE notes_fts USING fts5(note_id UNINDEXED,title);
CREATE VIRTUAL TABLE body_fts USING fts5(note_id UNINDEXED,title,content);
CREATE TABLE content_registry (note_id TEXT PRIMARY KEY,state TEXT,source_file TEXT,original_position INTEGER);
CREATE TABLE collections (collection_id TEXT PRIMARY KEY,title TEXT);
CREATE TABLE matters (matter_id TEXT PRIMARY KEY,name TEXT,source_note_id TEXT,native_verified INTEGER);
CREATE TABLE applications (application_id TEXT PRIMARY KEY);
CREATE TABLE deadlines (deadline_id TEXT PRIMARY KEY);
CREATE TABLE edges (edge_id TEXT PRIMARY KEY,source TEXT,target TEXT,relation TEXT,authority TEXT);
''')
  for i,(title,sens) in enumerate([('Synthetic JBPHH mission',[]),('Synthetic child restricted note',['minor_or_family']),('Synthetic hiring workflow',[])],start=0):
   note_id=IDS[i];con.execute('INSERT INTO notes VALUES (?,?,?,?,?,?,?)',(note_id,title,'mem://notes/'+note_id,'2026-01-01','2026-01-01',json.dumps(sens),0));con.execute('INSERT INTO notes_fts VALUES (?,?)',(note_id,title))
  con.execute('INSERT INTO note_body VALUES (?,?)',(IDS[0],'Synthetic JBPHH continuity for unit tests; NO LIVE CASE FACTS.'))
  con.execute('INSERT INTO body_fts VALUES (?,?,?)',(IDS[0],'Synthetic JBPHH mission','Synthetic JBPHH continuity for unit tests; NO LIVE CASE FACTS.'))
  con.execute('INSERT INTO content_registry VALUES (?,?,?,?)',(IDS[0],'GET_NOTE_COMPLETE','synthetic',1))
  con.execute('INSERT INTO collections VALUES (?,?)',('00000000-0000-4000-8000-000000000004','Synthetic'))
  con.execute('INSERT INTO matters VALUES (?,?,?,?)',('SYNTH-M1','Synthetic JBPHH mission',IDS[0],0))
  con.commit()
 finally:con.close()
 return p
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('output');a=parser.parse_args();create(a.output)