#!/usr/bin/env python3
"""Additive config proposal for OMP, never replaces existing MCP server definitions."""
import argparse,json,pathlib,os,tempfile,shutil
ENDPOINT='https://mcp.mem.ai/mcp'

def combine(existing,db_path,server_path):
    cfg=json.loads(json.dumps(existing));servers=cfg.setdefault('mcpServers',{})
    wanted={'mem-live':{'type':'http','url':ENDPOINT},'glaciereq-archive':{'type':'stdio','command':'python3','args':[str(server_path),'--db',str(db_path)]}}
    for name,conf in wanted.items():
        if name in servers and servers[name]!=conf:raise ValueError('MCP server name collision: '+name+'; reconcile manually')
        servers[name]=conf
    return cfg

def main():
    a=argparse.ArgumentParser();a.add_argument('--config',required=True);a.add_argument('--db',required=True);a.add_argument('--server',required=True);a.add_argument('--apply',action='store_true');args=a.parse_args()
    target=pathlib.Path(args.config).expanduser()
    if not pathlib.Path(args.db).is_file():raise SystemExit('BLOCKED: database not found')
    if not pathlib.Path(args.server).is_file():raise SystemExit('BLOCKED: server script not found')
    if target.is_symlink():raise SystemExit('BLOCKED: symlink config not allowed')
    config=json.loads(target.read_text()) if target.exists() else {}
    merged=combine(config,str(pathlib.Path(args.db).resolve()),str(pathlib.Path(args.server).resolve()))
    if not args.apply:
        print('DRY RUN ONLY: '+str(target));print(json.dumps(merged,indent=2));return
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():shutil.copy2(target,str(target)+'.backup-before-glaciereq-mem')
    fd,tmp=tempfile.mkstemp(prefix='.mcp-',dir=target.parent)
    try:
        with os.fdopen(fd,'w') as f:json.dump(merged,f,indent=2);f.flush();os.fsync(f.fileno())
        os.chmod(tmp,0o600);os.replace(tmp,target)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    reread=json.loads(target.read_text());assert reread==merged
    print('CONFIG WRITTEN AND READ BACK; OAuth sign-in + tools/list remains unverified')
if __name__=='__main__':main()