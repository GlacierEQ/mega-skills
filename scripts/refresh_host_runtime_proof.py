#!/usr/bin/env python3
"""Refresh Operator-host Skills proof with reversible lifecycle and executable binding."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_OUT=ROOT/'evidence/deep-progress-forge/host-skills-lifecycle-latest.json'

def stamp(dt): return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def run_json(skills: Path, args: list[str]):
    out=subprocess.check_output([str(skills),*args],text=True,timeout=30)
    return json.loads(out)
def build(skills: Path, ttl_hours: int, skill: str='playwright-skill'):
    observed=datetime.now(timezone.utc); due=observed+timedelta(hours=ttl_hours)
    before=run_json(skills,['status']); activated=False
    try:
        search=run_json(skills,['search','supabase','--limit','5'])
        try: recommend=run_json(skills,['recommend','build a fastapi postgres microservice'])
        except Exception as exc: recommend={'unavailable':type(exc).__name__}
        activate=run_json(skills,['activate',skill]); activated=True
        active=run_json(skills,['status'])
    finally:
        if activated:
            deactivate=run_json(skills,['deactivate',skill])
        else:
            deactivate={'name':skill,'success':False,'action':'not-activated'}
    restored=run_json(skills,['status'])
    sha=hashlib.sha256(skills.read_bytes()).hexdigest()
    receipt={
      'schema_version':2,'lane':'operator_host_runtime','device':subprocess.check_output(['hostname'],text=True).strip(),
      'skills_bin':str(skills),'skills_bin_sha256':sha,'observed_at':stamp(observed),'revalidate_after':stamp(due),
      'commands':['status','search supabase --limit 5','recommend build a fastapi postgres microservice',f'activate {skill}','status',f'deactivate {skill}','status'],
      'observations':{'status_before':before,'search':search,'recommend':recommend,'activate':activate,'status_active':active,'deactivate':deactivate,'status_restored':restored},
      'assertions':{'initial_status_optimal':before.get('status')=='OPTIMAL','search_returned_results':bool(search),'activation_verified':skill in active.get('dynamic_active_skills',[]),'deactivation_verified':skill not in restored.get('dynamic_active_skills',[]),'host_state_restored_exactly':before==restored,'executable_fingerprint_bound':True},
    }
    receipt['receipt_digest_sha256']=hashlib.sha256(canonical(receipt)).hexdigest()
    if not all(receipt['assertions'][k] for k in ('initial_status_optimal','search_returned_results','activation_verified','deactivation_verified','host_state_restored_exactly')):
        raise RuntimeError(f'host proof assertions failed: {receipt["assertions"]}')
    return receipt

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--skills-bin',type=Path,default=Path.home()/'bin/skills'); ap.add_argument('--output',type=Path,default=DEFAULT_OUT); ap.add_argument('--ttl-hours',type=int,default=8); ap.add_argument('--skill',default='playwright-skill'); args=ap.parse_args()
    if not args.skills_bin.is_file(): raise SystemExit(f'skills executable missing: {args.skills_bin}')
    if args.ttl_hours < 1 or args.ttl_hours > 48: raise SystemExit('ttl-hours must be between 1 and 48')
    receipt=build(args.skills_bin,args.ttl_hours,args.skill); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'output':str(args.output),'observed_at':receipt['observed_at'],'revalidate_after':receipt['revalidate_after'],'skills_bin_sha256':receipt['skills_bin_sha256'],'receipt_digest_sha256':receipt['receipt_digest_sha256']},indent=2))
if __name__=='__main__': main()
