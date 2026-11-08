#!/usr/bin/env python3
"""GlacierEQ portable memory archive MCP (stdio, offline/read-only). Python stdlib only.
No write tools, no external network, no credential storage. Private local database.
"""
import argparse, json, os, re, sqlite3, sys
from pathlib import Path
UUID=re.compile(r'^[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')
SENSITIVE={'minor_or_family','health_sensitive','legal_work','financial_private','credential_title'}

def as_dict(row):return dict(row) if row is not None else None

def fts_phrase(query):
    # Treat arbitrary user input as data, never FTS syntax / SQL.
    if re.search(r'--|;|\b(?:OR|AND)\s+\d+\s*=\s*\d+',query or '',re.IGNORECASE):return ''
    words=re.findall(r'[\w-]{2,}',query or '',re.UNICODE)[:12]
    return ' OR '.join('"'+w.replace('"','')+'"' for w in words)

class MemoryArchive:
    def __init__(self,path):
        p=Path(path).expanduser().resolve(strict=True)
        if not p.is_file():raise ValueError('not a database file')
        self.db=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA query_only=ON')
        if self.db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('database integrity failed')
        for required in ('notes','note_body','body_fts','collections','matters','applications','deadlines','edges'):
            if not self.db.execute('SELECT 1 FROM sqlite_master WHERE name=?',(required,)).fetchone():raise ValueError('unknown memory archive schema: '+required)
    def close(self):self.db.close()
    def status(self):
        counts={t:self.db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('notes','note_body','collections','matters','applications','deadlines','edges')}
        return {'notes':counts['notes'],'bodies':counts['note_body'],'collections':counts['collections'],'matters_or_resources':counts['matters'],'job_entries':counts['applications'],'deadline_source_rows':counts['deadlines'],'relationships':counts['edges'],'source_class':'MEM_SECONDARY','native_provider_live':False,'external_actions_verified':False,'mutations_allowed':False,'access_policy_enforced':False,'body_access_env_opt_in':os.environ.get('GLACIEREQ_MEM_ALLOW_BODIES')=='1'}
    def search(self,query,limit=10):
        limit=max(1,min(int(limit),25));phrase=fts_phrase(query)
        if not phrase:return []
        try:
            rows=self.db.execute('''SELECT n.note_id,n.title,n.uri,n.updated_at,n.sensitivity_json,
               (SELECT state FROM content_registry WHERE note_id=n.note_id) content_state
               FROM notes n WHERE n.note_id IN (
                 SELECT note_id FROM notes_fts WHERE notes_fts MATCH ?
                 UNION SELECT note_id FROM body_fts WHERE body_fts MATCH ?)
               ORDER BY n.updated_at DESC LIMIT ?''',(phrase,phrase,limit)).fetchall()
        except sqlite3.OperationalError:return []
        return [dict(id=r['note_id'],title=r['title'],uri=r['uri'],updated_at=r['updated_at'],content_state=r['content_state'] or 'METADATA_ONLY',source_class='MEM_SECONDARY',provider_outcome_verified=False,sensitivity_hint=json.loads(r['sensitivity_json'] or '[]')) for r in rows]
    def note(self,note_id,include_body=False):
        if not UUID.fullmatch(note_id):raise ValueError('invalid note UUID')
        r=self.db.execute('''SELECT n.*,b.content,(SELECT state FROM content_registry WHERE note_id=n.note_id) content_state FROM notes n LEFT JOIN note_body b ON b.note_id=n.note_id WHERE n.note_id=?''',(note_id,)).fetchone()
        if r is None:return {'found':False,'id':note_id,'source_class':'MEM_SECONDARY'}
        hints=json.loads(r['sensitivity_json'] or '[]')
        res={'found':True,'id':r['note_id'],'title':r['title'],'uri':r['uri'],'created_at':r['created_at'],'updated_at':r['updated_at'],'source_class':'MEM_SECONDARY','provider_outcome_verified':False,'content_state':r['content_state'] or 'METADATA_ONLY','sensitivity_hint':hints,'sensitivity_enforcement_is_not_access_control':True}
        allowed=bool(include_body and os.getenv('GLACIEREQ_MEM_ALLOW_BODIES')=='1' and (os.getenv('GLACIEREQ_MEM_ALLOW_RESTRICTED')=='1' or not SENSITIVE.intersection(hints)))
        res['body_disclosure_allowed']=allowed
        if allowed and r['content'] is not None:res['body']=r['content'][:18000];res['body_truncated_for_transport']=len(r['content'])>18000
        return res
    def mission(self,term):
        q=(term or '').strip()[:120]
        if len(q)<2:return {'source_class':'MEM_SECONDARY','provider_outcome_verified':False,'matters':[],'notes':[]}
        rows=self.db.execute("SELECT matter_id,name,source_note_id,native_verified FROM matters WHERE name LIKE ? ESCAPE '\\' LIMIT 12",('%'+q.replace('%','\\%').replace('_','\\_')+'%',)).fetchall()
        return {'source_class':'MEM_SECONDARY','provider_outcome_verified':False,'matters':[{'matter_id':r['matter_id'],'name':r['name'],'router_source_note_id':r['source_note_id'],'native_verified_in_snapshot':bool(r['native_verified'])} for r in rows],'notes':self.search(q,8),'mandate':'Recover official owner/source before action; this is a secondary pointer only.'}
    def neighbors(self,note_id,limit=15):
        if not UUID.fullmatch(note_id):raise ValueError('invalid note UUID')
        from_id='note:'+note_id
        rows=self.db.execute('SELECT source,target,relation,authority FROM edges WHERE source=? OR target=? LIMIT ?',(from_id,from_id,max(1,min(int(limit),30)))).fetchall()
        return [{'source':r['source'],'target':r['target'],'type':r['relation'],'authority':r['authority'],'proof_class':'NAVIGATION_ONLY'} for r in rows]

TOOLS=[
('memory_status','Inspect offline snapshot counts and provenance. No live Mem credentials used.',{},[]),
('memory_search','Search original Mem note UUIDs and titles; results are secondary memory, not source proof.',{'query':{'type':'string'},'limit':{'type':'integer','minimum':1,'maximum':25}},['query']),
('memory_get_note','Read one archived note by its original UUID; body disabled unless controlled local opt-in.',{'note_id':{'type':'string'},'include_body':{'type':'boolean'}},['note_id']),
('memory_mission','Resolve a named mission to existing owner notes and case router, without claiming current status.',{'query':{'type':'string'}},['query']),
('memory_neighbors','Inspect explicitly stored note graph links by original UUID.',{'note_id':{'type':'string'},'limit':{'type':'integer','minimum':1,'maximum':30}},['note_id']),
]
def mcp_tools():return [{'name':n,'description':d,'inputSchema':{'type':'object','properties':p,'required':r,'additionalProperties':False}} for n,d,p,r in TOOLS]
def dispatch(archive,request):
    method=request.get('method');params=request.get('params') or {}
    if method=='initialize':return {'protocolVersion':'2025-06-18','capabilities':{'tools':{'listChanged':False}},'serverInfo':{'name':'glaciereq-mem-archive','version':'1.0.0'}}
    if method=='ping':return {}
    if method=='tools/list':return {'tools':mcp_tools()}
    if method=='tools/call':
        name=params.get('name');a=params.get('arguments') or {}
        methods={'memory_status':lambda:archive.status(),'memory_search':lambda:archive.search(a['query'],a.get('limit',10)),'memory_get_note':lambda:archive.note(a['note_id'],a.get('include_body',False)),'memory_mission':lambda:archive.mission(a['query']),'memory_neighbors':lambda:archive.neighbors(a['note_id'],a.get('limit',15))}
        if name not in methods:raise ValueError('unknown tool')
        return {'content':[{'type':'text','text':json.dumps(methods[name](),ensure_ascii=False)}],'isError':False}
    raise ValueError('unsupported MCP method')
def run_server(db):
    archive=MemoryArchive(db)
    try:
        for line in sys.stdin:
            if not line.strip():continue
            try:
                req=json.loads(line)
                if req.get('id') is None:continue
                try:resp={'jsonrpc':'2.0','id':req['id'],'result':dispatch(archive,req)}
                except (ValueError,KeyError,TypeError,sqlite3.Error) as exc:resp={'jsonrpc':'2.0','id':req['id'],'error':{'code':-32602,'message':str(exc)[:160]}}
            except json.JSONDecodeError:
                resp={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'invalid JSON'}}
            sys.stdout.write(json.dumps(resp,ensure_ascii=False,separators=(',',':'))+'\n');sys.stdout.flush()
    finally:archive.close()
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--db',required=True);args=ap.parse_args()
    try:run_server(args.db)
    except (FileNotFoundError,sqlite3.Error,ValueError) as e:print('MCP START BLOCKED: '+str(e)[:160],file=sys.stderr);sys.exit(2)