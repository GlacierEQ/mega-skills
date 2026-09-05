#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--projection",type=Path,required=True)
    p.add_argument("--audit",type=Path,required=True)
    p.add_argument("--activation",type=Path,required=True)
    p.add_argument("--ledger",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()

    projection,audit,activation,ledger=map(load,[a.projection,a.audit,a.activation,a.ledger])
    featured=projection.get("featured_projects",[])
    gateway=activation["portfolio_gateway"]
    front=[
        {
            "type":"portfolio_gateway",
            "name":"GlacierEQ Hiring System",
            "url":gateway["url"],
            "purpose":gateway["purpose"],
            "state":gateway["status"]
        }
    ] + [
        {
            "type":"project",
            "source_id":x["source_id"],
            "name":x["name"],
            "url":x["url"],
            "summary":x["summary"],
            "evidence_state":x["state"]
        }
        for x in featured[:4]
    ]

    blocked=[x for x in audit["claims"] if x["status"]=="BLOCKED"]
    manual=[]
    if activation["recommendations"]["status"]!="COMPLETE":
        manual.append({"id":"recommendations","status":activation["recommendations"]["status"]})
    otw=activation["open_to_work"]
    if not otw.get("locations") or not otw.get("workplace_types") or not otw.get("employment_types"):
        manual.append({"id":"open_to_work_preferences","status":"NEEDS_INPUT"})
    if activation["identity_verification"]["status"]!="COMPLETE":
        manual.append({"id":"identity_verification","status":activation["identity_verification"]["status"]})
    for key,state in activation.get("manual_profile_checks",{}).items():
        if state not in {"VERIFIED","COMPLETE"}:
            manual.append({"id":key,"status":state})

    pack={
        "schema_version":1,
        "source_authority":"missions/anthropic-applied-ai/LINKEDIN_PROFILE_SOURCE.md",
        "publication_decision":"READY_WITH_BOUNDED_GAPS",
        "identity":projection["identity"],
        "headline":projection["headline"],
        "about_policy":"Publish from LINKEDIN_PROFILE_SOURCE.md; do not regenerate or silently rewrite operator-authored About copy.",
        "front_featured":front,
        "projects_section":[
            {"source_id":x["source_id"],"name":x["name"],"url":x["url"],"summary":x["summary"],"state":x["state"]}
            for x in featured[:8]
        ],
        "skills":projection["skills"],
        "defensible_metrics":projection.get("metrics",[]),
        "claim_ceiling":{
            "blocked_claims":[
                {"claim_id":x["claim_id"],"requirement_id":x.get("requirement_id"),"reason":x["note"]}
                for x in blocked
            ],
            "rule":projection["projection_rule"]
        },
        "evidence_status":{
            "coverage_score":ledger["summary"]["evidence_coverage_score"],
            "score_semantics":ledger["score_semantics"],
            "requirements_satisfied":ledger["summary"]["requirements_satisfied"],
            "requirements_total":ledger["summary"]["requirements_total"],
            "hard_gates_open":ledger["summary"]["hard_gates_open"],
            "open_gaps":ledger["gap_queue"]
        },
        "manual_actions":manual,
        "input_sha256":{
            "projection":digest(a.projection),
            "claim_audit":digest(a.audit),
            "activation":digest(a.activation),
            "ledger":digest(a.ledger)
        }
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(pack,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":"READY_WITH_BOUNDED_GAPS",
        "featured":len(pack["front_featured"]),
        "projects":len(pack["projects_section"]),
        "blocked_claims":len(pack["claim_ceiling"]["blocked_claims"]),
        "manual_actions":len(manual)
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
