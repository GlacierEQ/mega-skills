#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--target",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    target=json.loads(a.target.read_text(encoding="utf-8"))
    payload={
        "schema_version":1,
        "company":target["company"],
        "role_family":target["role_family"],
        "primary_role":target["primary_role"],
        "identity":target["identity"],
        "competency_domains":target["competency_domains"],
        "evidence_contract":{
            "states":["VERIFIED","SUPPORTED","CANDIDATE","UNVERIFIED","BLOCKED"],
            "required_fields":["claim","source","artifact","verification","state"]
        },
        "projections":["linkedin","resume","portfolio","interview","job-app-helix"]
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
