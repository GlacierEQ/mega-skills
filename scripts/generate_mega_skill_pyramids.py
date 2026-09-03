#!/usr/bin/env python3
"""Generate and validate recursive Mega-Skill pyramid projections from canonical registries."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'registry'
OUT=REG/'mega-skill-pyramids.json'

def load(name): return json.loads((REG/name).read_text())

def build():
    skills=load('skills.json')['entries']; combos=load('combo-skills.json')['entries']; megas=load('mega-skills.json')['entries']
    skill_by={x['id']:x for x in skills}; combo_by={x['id']:x for x in combos}
    unresolved=[]; entries=[]
    for mega in megas:
        combo_ids=[]
        for key in ('required_combos','conditional_combos','combos'):
            for cid in mega.get(key,[]):
                if cid not in combo_ids: combo_ids.append(cid)
        nodes=[{'id':mega['id'],'skill_kind':'mega','proper_skill':True,'display_name':mega.get('display_name',mega['id']),'source':mega.get('entrypoint'),'maturity':mega.get('maturity'),'level':0}]
        edges=[]
        for cid in combo_ids:
            co=combo_by.get(cid)
            if not co:
                unresolved.append({'mega':mega['id'],'missing_combo':cid}); continue
            relation='required' if cid in mega.get('required_combos',[]) else 'conditional'
            nodes.append({'id':cid,'skill_kind':'compound','proper_skill':True,'display_name':co.get('display_name',cid),'source':co.get('entrypoint'),'maturity':co.get('maturity'),'level':1,'compound_artifact':co.get('compounding',{}).get('compound_artifact')})
            edges.append({'from':mega['id'],'to':cid,'relation':relation})
            for mem in co.get('members',[]):
                sid=mem['id']; owned=mem.get('kind','skill')=='skill'
                if owned and sid not in skill_by:
                    unresolved.append({'mega':mega['id'],'combo':cid,'missing_skill':sid}); continue
                if not any(n['id']==sid and n['level']==2 for n in nodes):
                    nodes.append({'id':sid,'skill_kind':'atomic' if owned else 'external','proper_skill':True,'display_name':(skill_by.get(sid) or {}).get('display_name',sid),'source':(skill_by.get(sid) or {}).get('entrypoint'),'level':2,'ownership':'glaciereq' if owned else 'external'})
                edges.append({'from':cid,'to':sid,'relation':'member','required':bool(mem.get('required',False)),'role':mem.get('role')})
        entries.append({'id':mega['id'],'display_name':mega.get('display_name',mega['id']),'root_skill_id':mega['id'],'shape':'hierarchical-pyramid','levels':[{'level':0,'name':'mega-apex','semantics':'proper end-to-end integrated workflow/pipeline skill'},{'level':1,'name':'compound-workflow-skills','semantics':'proper reusable skills composed from lower skills'},{'level':2,'name':'atomic-skills','semantics':'proper independently valid skill building blocks'}],'nodes':nodes,'edges':edges,'mission_output':mega.get('mission_output'),'durable_state':mega.get('durable_state',[])})
    if unresolved: raise ValueError('unresolved pyramid references: '+json.dumps(unresolved,indent=2))
    return {'schema_version':1,'ontology':'mega-skill-pyramid','counts':{'atomic_skills':len(skills),'compound_workflow_skills':len(combos),'mega_skills':len(megas)},'entries':entries}

def canonical_bytes(data): return (json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
    data=build(); rendered=canonical_bytes(data)
    if args.check:
        if not OUT.exists(): print('missing registry/mega-skill-pyramids.json',file=sys.stderr); return 1
        if OUT.read_bytes()!=rendered: print('registry/mega-skill-pyramids.json is stale; run scripts/generate_mega_skill_pyramids.py',file=sys.stderr); return 1
    else: OUT.write_bytes(rendered)
    print(json.dumps({'ok':True,'counts':data['counts'],'pyramids':len(data['entries']),'mode':'check' if args.check else 'write'},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
