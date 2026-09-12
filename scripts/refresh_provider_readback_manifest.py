#!/usr/bin/env python3
"""Refresh cross-repository provider proofs from GitHub via gh CLI."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / 'evidence/deep-progress-forge/LATEST.json'
DEFAULT_OUT = ROOT / 'evidence/deep-progress-forge/provider-readback-manifest-v2.json'

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

def stamp(dt):
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

def gh_commit(repo, sha):
    raw = subprocess.check_output(['gh','api',f'repos/{repo}/commits/{sha}'], text=True)
    row = json.loads(raw)
    if row.get('sha') != sha:
        raise RuntimeError(f'GitHub returned unexpected SHA for {repo}: {row.get("sha")}')
    return {
        'provider_url': row['html_url'],
        'provider_message': row['commit']['message'].splitlines()[0],
        'provider_object': {
            'kind': 'commit',
            'tree_sha': row['commit']['tree']['sha'],
            'parent_shas': [p['sha'] for p in row.get('parents', [])],
        },
    }

def build(pointer, observed_at, ttl_hours):
    proofs=[]
    for name, entry in pointer['verified_provider_state'].items():
        if entry.get('type') != 'cross_repo_commit':
            continue
        meta=gh_commit(entry['repo'], entry['sha'])
        proofs.append({'name':name,'type':'cross_repo_commit','repo':entry['repo'],'sha':entry['sha'],**meta})
    if not proofs:
        raise RuntimeError('no cross_repo_commit entries to refresh')
    due=observed_at+timedelta(hours=ttl_hours)
    manifest={'schema_version':2,'source':'GitHub provider readback via gh api','observed_at':stamp(observed_at),'revalidate_after':stamp(due),'proofs':proofs}
    payload={k:manifest[k] for k in ('schema_version','source','observed_at','revalidate_after','proofs')}
    manifest['proof_digest_sha256']=hashlib.sha256(canonical(payload)).hexdigest()
    return manifest

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--latest', type=Path, default=LATEST)
    ap.add_argument('--output', type=Path, default=DEFAULT_OUT)
    ap.add_argument('--ttl-hours', type=int, default=24)
    args=ap.parse_args()
    if args.ttl_hours < 1 or args.ttl_hours > 168:
        raise SystemExit('ttl-hours must be between 1 and 168')
    pointer=json.loads(args.latest.read_text())
    manifest=build(pointer, datetime.now(timezone.utc), args.ttl_hours)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'output':str(args.output),'proofs':len(manifest['proofs']),'observed_at':manifest['observed_at'],'revalidate_after':manifest['revalidate_after'],'proof_digest_sha256':manifest['proof_digest_sha256']},indent=2))
if __name__=='__main__':
    main()
