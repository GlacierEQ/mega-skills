#!/usr/bin/env python3
from pathlib import Path
import argparse,json
MAP={'skills':'skills.json','combo_skills':'combo-skills.json','mega_skills':'mega-skills.json','pipelines':'pipelines.json'}
def upsert(entries,new):
 by={x['id']:x for x in entries}; order=[x['id'] for x in entries]
 for x in new:
  if x['id'] not in by: order.append(x['id'])
  by[x['id']]=x
 return [by[i] for i in order]
def main():
 p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,default=Path.cwd()); p.add_argument('--check',action='store_true'); a=p.parse_args(); reg=a.root/'registry'; src=json.loads((reg/'apex-strong-smart-execution-engine.entries.json').read_text()); changed=[]
 for key,file in MAP.items():
  path=reg/file; doc=json.loads(path.read_text()); merged=upsert(doc['entries'],src[key])
  if merged!=doc['entries']:
   changed.append(file)
   if not a.check: doc['entries']=merged; path.write_text(json.dumps(doc,indent=2)+'\n')
 print(json.dumps({'ok':not(a.check and changed),'mode':'check' if a.check else 'write','changed':changed},indent=2)); return 1 if a.check and changed else 0
if __name__=='__main__': raise SystemExit(main())
