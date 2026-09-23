#!/usr/bin/env python3
"""Exact-ID materialization for the Strong-Smart hierarchy.

Preserves every unrelated registry entry and enriches the pipeline registry row
from the canonical pipeline document before writing.
"""
from pathlib import Path
import argparse,json
MAP={'skills':'skills.json','combo_skills':'combo-skills.json','mega_skills':'mega-skills.json','pipelines':'pipelines.json'}
def upsert(entries,new):
 by={x['id']:x for x in entries}; order=[x['id'] for x in entries]
 for x in new:
  if x['id'] not in by: order.append(x['id'])
  by[x['id']]=x
 return [by[i] for i in order]
def pipeline_entry(root, staged):
 doc=json.loads((root/'pipelines'/'strong-smart-mission.json').read_text(encoding='utf-8'))
 return {**staged,'ownership':'glaciereq','maturity':'active','version':'1.0.0','span':doc['span'],'required_combos':doc['required_combos'],'runner':'scripts/run_deep_work_pipeline.py','stage_runner':'scripts/strong_smart_stage.py'}
def main():
 p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,default=Path.cwd()); p.add_argument('--check',action='store_true'); a=p.parse_args(); root=a.root.resolve(); reg=root/'registry'; src=json.loads((reg/'apex-strong-smart-execution-engine.entries.json').read_text(encoding='utf-8')); src['pipelines']=[pipeline_entry(root,x) for x in src['pipelines']]; changed=[]
 for key,file in MAP.items():
  path=reg/file; doc=json.loads(path.read_text(encoding='utf-8')); merged=upsert(doc['entries'],src[key])
  if merged!=doc['entries']:
   changed.append(file)
   if not a.check: doc['entries']=merged; path.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(json.dumps({'ok':not(a.check and changed),'mode':'check' if a.check else 'write','changed':changed},indent=2)); return 1 if a.check and changed else 0
if __name__=='__main__': raise SystemExit(main())
