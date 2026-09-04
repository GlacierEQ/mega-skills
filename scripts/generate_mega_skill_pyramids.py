#!/usr/bin/env python3
"""Generate/check the compact canonical recursive Mega-Skill graph."""
from __future__ import annotations
import argparse,json,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REG=ROOT/'registry'; OUT=REG/'mega-skill-pyramids.json'

def load(n): return json.loads((REG/n).read_text(encoding='utf-8'))
def key(kind,i): return {'skill':'a','compound-skill':'c','external-skill':'x'}[kind]+':'+i

def cycle(graph):
    state={}; stack=[]
    def visit(n):
        if state.get(n)==2:return None
        if state.get(n)==1:
            j=stack.index(n);return stack[j:]+[n]
        state[n]=1;stack.append(n)
        for c in sorted(graph.get(n,[])):
            z=visit(c)
            if z:return z
        stack.pop();state[n]=2;return None
    for n in sorted(graph):
        z=visit(n)
        if z:return z
    return None

def build():
    skills=load('skills.json')['entries']; combos=load('combo-skills.json')['entries']; megas=load('mega-skills.json')['entries']; external=load('external-skills.json')['entries']
    sid={x['id'] for x in skills}; cid={x['id'] for x in combos}; xid={x['id'] for x in external}; parents=defaultdict(set); leaves=set(); adj={x['id']:[] for x in combos}; unresolved=[]; cnodes=[]
    for c in combos:
        members=[]
        for m in c.get('members',[]):
            k=m.get('kind','skill'); i=m['id']; ok=(i in sid if k=='skill' else i in cid if k=='compound-skill' else i in xid if k=='external-skill' else False)
            if not ok: unresolved.append({'compound_skill':c['id'],'member_id':i,'member_kind':k}); continue
            nk=key(k,i); members.append([nk,1 if m.get('required') else 0]); parents[nk].add('c:'+c['id'])
            if k=='compound-skill': adj[c['id']].append(i)
            else: leaves.add(nk)
        cnodes.append(['c:'+c['id'],c['id'],members])
    z=cycle(adj)
    if z: raise ValueError('compound-skill cycle: '+' -> '.join(z))
    roots=[]
    for m in megas:
        req=['c:'+x for x in m.get('required_combos',[])]; cond=['c:'+x for x in m.get('conditional_combos',[])]; missing=[x for x in req+cond if x[2:] not in cid]
        if missing: unresolved.append({'mega':m['id'],'missing_compound_keys':missing})
        rk='m:'+m['id'];
        for x in req+cond: parents[x].add(rk)
        roots.append([rk,m['id'],req,cond])
    if unresolved: raise ValueError('unresolved recursive Skill references: '+json.dumps(unresolved,indent=2))
    shared=sorted(k for k,v in parents.items() if len(v)>1)
    extrefs=sum(1 for c in combos for m in c.get('members',[]) if m.get('kind')=='external-skill')
    return {'schema_version':2,'ontology':'recursive-proper-skill-pyramid','key_prefixes':{'a':'atomic','c':'compound','m':'mega','x':'external'},'sources':{'a':'registry/skills.json','c':'registry/combo-skills.json','m':'registry/mega-skills.json','x':'registry/external-skills.json'},'contract_ref':{'compound_member':'compound registry entry by exact id; member array position equals canonical members[] index; role=members[i].role; artifact/validation=execution.ordered_steps where member_id matches','node':'mega artifact=mission_output/validation=firewall.required_evidence; compound artifact=compounding.compound_artifact/validation=integration.quality_gates+compounding.next_layer_ready_when; atomic artifact=output_contract/validation=local_validation'},'counts':{'atomic_skills':len(skills),'compound_skills':len(combos),'mega_skills':len(megas),'external_member_references':extrefs,'mega_pyramids':len(roots),'unresolved_owned_references':0,'compound_cycles':0},'mega_roots':roots,'compound_nodes':cnodes,'leaf_keys':sorted(leaves),'shared_lineage':{'derive':'reverse mega_roots + compound_nodes; every parent reference is retained','keys':shared}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args()
    try:data=build()
    except ValueError as e: print(e,file=sys.stderr); return 1
    text=json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n'
    if a.check:
        if not OUT.exists(): print('missing registry/mega-skill-pyramids.json',file=sys.stderr); return 1
        try: current=json.loads(OUT.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e: print(f'invalid pyramid registry: {e}',file=sys.stderr); return 1
        if current!=data: print('registry/mega-skill-pyramids.json is stale; run scripts/generate_mega_skill_pyramids.py',file=sys.stderr); return 1
    else: OUT.write_text(text,encoding='utf-8')
    print(json.dumps({'ok':True,'pyramids':len(data['mega_roots']),'compound_nodes':len(data['compound_nodes']),'leaf_nodes':len(data['leaf_keys']),'counts':data['counts'],'mode':'check' if a.check else 'write'},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
