#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

STATES=["VERIFIED","SUPPORTED","CANDIDATE","UNVERIFIED","BLOCKED"]

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--target",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    target=json.loads(a.target.read_text(encoding="utf-8"))
    payload={
        "schema_version":2,
        "company":target["company"],
        "role_family":target["role_family"],
        "primary_role":target["primary_role"],
        "identity":target["identity"],
        "snapshot_date":target.get("snapshot_date"),
        "freshness":target.get("freshness",{}),
        "role_tracks":target.get("role_tracks",{}),
        "market_sources":target.get("market_sources",[]),
        "competency_domains":target["competency_domains"],
        "requirements":target.get("requirements",[]),
        "non_evidence_constraints":target.get("non_evidence_constraints",{}),
        "evidence_contract":{
            "states":STATES,
            "required_fields":["claim","source","artifact","verification","state"],
            "score_semantics":"Evidence coverage is proof strength against requirements, not hiring probability."
        },
        "projections":["linkedin","resume","portfolio","interview","job-app-helix"]
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
