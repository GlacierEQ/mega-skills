#!/usr/bin/env python3
"""Generate and validate the canonical Mega-Skill pyramid index."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'registry'
OUT=REG/'mega-skill-pyramids.json'

def load(name): return json.loads((REG/name).read_text())

def build():
    skills=load('skills.json')['entries']; combos=load('combo-skills.json')['entries']; megas=load('mega-skills.json')['entries']
    skill_ids={x['id'] for x in skills}; combo_by={x['id']:x for x in combos}
    unresolved=[]
    for combo in combos:
        for member in combo.get('members',[]):
            if member.get('kind','skill')=='skill' and member['id'] not in skill_ids:
                unresolved.append({'combo':combo['id'],'missing_skill':member['id']})
    entries=[]
    for mega in megas:
        required=mega.get('required_combos',[]); conditional=mega.get('conditional_combos',[])
        for cid in required+conditional:
            if cid not in combo_by: unresolved.append({'mega':mega['id'],'missing_compound_skill':cid})
        entries.append({'id':mega['id'],'required_compound_skills':required,'conditional_compound_skills':conditional})
    if unresolved: raise ValueError('unresolved pyramid references: '+json.dumps(unresolved,indent=2))
    return {
        'schema_version':1,
        'ontology':'mega-skill-pyramid-index',
        'resolution':{
            'level_0':'registry/mega-skills.json',
            'level_1':'registry/combo-skills.json',
            'level_2':'registry/skills.json',
            'external':'registry/external-skills.json'
        },
        'counts':{'atomic_skills':len(skills),'compound_skills':len(combos),'mega_skills':len(megas)},
        'entries':entries
    }

def render(data): return json.dumps(data,indent=2,ensure_ascii=False)+'\n'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
    text=render(build())
    if args.check:
        if not OUT.exists() or OUT.read_text()!=text:
            print('registry/mega-skill-pyramids.json is stale; run scripts/generate_mega_skill_pyramids.py',file=sys.stderr); return 1
    else: OUT.write_text(text)
    data=json.loads(text)
    print(json.dumps({'ok':True,'counts':data['counts'],'pyramids':len(data['entries']),'mode':'check' if args.check else 'write'},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
