#!/usr/bin/env python3
"""Deterministic worker primitives required to activate APEX Always-On Core."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

def as_list(value: Any) -> list:
    if value is None: return []
    return value if isinstance(value,list) else [value]

def load_payload(path: str | None) -> dict[str,Any]:
    if path: return json.loads(Path(path).read_text(encoding="utf-8"))
    raw=sys.stdin.read().strip()
    return json.loads(raw) if raw else {}

def bullets(values:list) -> str:
    return "\n".join("- "+str(v) for v in values) if values else "- None"

def resource_preflight(op:str,p:dict[str,Any]) -> dict[str,Any]:
    prereqs=[]
    for i,v in enumerate(as_list(p.get("prerequisites")),1):
        d=dict(v) if isinstance(v,dict) else {"identifier":str(v)}
        d.setdefault("id",f"R-{i:02d}")
        d.setdefault("type","file")
        d.setdefault("required",True)
        d.setdefault("verification_method","file_exists" if d["type"]=="file" else "command_exists")
        d.setdefault("fallback","")
        prereqs.append(d)
    observed=[]
    for d in prereqs:
        method=d["verification_method"]; ident=str(d.get("identifier") or d.get("expected_identifier") or "")
        if method=="file_exists":
            ok=Path(ident).expanduser().is_file()
            status="verified" if ok else "missing"
            evidence="file exists: "+str(Path(ident).expanduser()) if ok else "file missing: "+ident
        elif method=="command_exists":
            found=shutil.which(ident)
            ok=bool(found); status="verified" if ok else "missing"
            evidence="command found: "+str(found) if ok else "command missing: "+ident
        elif method=="observed_status":
            status=str(d.get("status","missing"))
            ok=status=="verified"; evidence=str(d.get("evidence","status supplied by caller"))
        else:
            status="not_applicable"; ok=not d.get("required",True); evidence="unsupported non-destructive verification method: "+method
        observed.append({**d,"status":status,"verified":ok,"evidence":evidence})
    required_fail=[x for x in observed if x.get("required",True) and x["status"]!="verified"]
    optional_fail=[x for x in observed if not x.get("required",True) and x["status"]!="verified"]
    result="blocked" if required_fail else ("conditional" if optional_fail else "ready")
    if op=="inventory_builder": return {"prerequisites":prereqs}
    if op=="availability_checker": return {"observed":observed}
    if op=="classifier": return {"statuses":{x["id"]:x["status"] for x in observed}}
    if op=="fallback_identifier": return {"fallbacks":{x["id"]:x.get("fallback","") for x in observed if x["status"]!="verified"}}
    lines=["# RESOURCE PREFLIGHT","",f"Result: {result.upper()}","","## Prerequisites"]
    for x in observed:
        lines.append("- ["+x["id"]+"] "+str(x.get("identifier") or x.get("expected_identifier") or "")+" — "+x["status"]+" — "+x["evidence"])
    return {"result":result,"ready":result=="ready","observed":observed,"artifact":"RESOURCE_PREFLIGHT.md","markdown":"\n".join(lines)+"\n"}

def capability_admission(op:str,p:dict[str,Any]) -> dict[str,Any]:
    cid=str(p.get("capability_id","")).strip()
    mission=str(p.get("mission_scope") or p.get("mission") or "").strip()
    prereqs=as_list(p.get("prerequisites"))
    statuses=[]
    for i,v in enumerate(prereqs,1):
        d=dict(v) if isinstance(v,dict) else {"id":f"R-{i:02d}","status":str(v)}
        d.setdefault("id",f"R-{i:02d}"); d.setdefault("required",True); d.setdefault("status","missing"); statuses.append(d)
    gaps=[x["id"] for x in statuses if x.get("required",True) and x.get("status")!="verified"]
    claim_ok=bool(p.get("claim_boundary_passed",False))
    approval_required=bool(p.get("approval_required",False))
    approval_ok=(not approval_required) or bool(p.get("approved",False))
    errors=[]
    if not cid: errors.append("capability_id is required")
    if not mission: errors.append("mission_scope is required")
    if gaps: errors.append("required prerequisites not verified: "+", ".join(gaps))
    if not claim_ok: errors.append("claim boundary has not passed")
    if not approval_ok: errors.append("required approval is absent")
    if not cid or not mission: decision="blocked"
    elif errors: decision="candidate"
    else: decision="admitted"
    record={"capability_id":cid,"mission_scope":mission,"declared_maturity":p.get("maturity","candidate"),
            "observed_prerequisites":statuses,"gaps":gaps,"claim_boundary_passed":claim_ok,
            "approval_required":approval_required,"approved":approval_ok,
            "fallback":str(p.get("fallback","")).strip(),"decision_owner":str(p.get("decision_owner","")).strip(),
            "review_trigger":str(p.get("review_trigger","")).strip(),"decision":decision}
    if op=="admission_evaluator": return {"decision":decision,"errors":errors,"gaps":gaps}
    if op=="preflight_integration": return {"observed_prerequisites":statuses,"gaps":gaps}
    lines=["# CAPABILITY ADMISSION","",f"Capability: {cid}",f"Mission: {mission}",f"Decision: {decision.upper()}","","## Gaps",bullets(gaps),
           "","## Fallback",record["fallback"] or "None declared","","## Review Trigger",record["review_trigger"] or "Re-run when prerequisite or evidence state changes."]
    return {"valid":not errors,"errors":errors,"decision":decision,"record":record,"artifact":"CAPABILITY_ADMISSION.md","markdown":"\n".join(lines)+"\n"}

def calibrate_one(v:Any,i:int) -> dict[str,Any]:
    d=dict(v) if isinstance(v,dict) else {"claim":str(v)}
    claim=str(d.get("claim","")).strip()
    classification=str(d.get("classification","open_question")).strip()
    evidence=as_list(d.get("evidence"))
    limitations=as_list(d.get("limitations"))
    high=bool(d.get("high_consequence",False))
    qualified=bool(d.get("qualified_evidence",False))
    tested=classification in {"observed_fact","tested_behavior"} and bool(evidence)
    derived=classification=="derived_conclusion" and bool(evidence)
    if high and not qualified:
        wording="Not established: "+claim
        escalation=True
    elif tested:
        wording=claim
        escalation=False
    elif derived:
        wording="Evidence supports the scoped conclusion: "+claim
        escalation=False
    elif evidence:
        wording="Evidence is consistent with, but does not fully establish: "+claim
        escalation=False
    else:
        wording="Unverified: "+claim
        escalation=high
    return {"id":d.get("id",f"CL-{i:03d}"),"original_claim":claim,"classification":classification,
            "evidence":evidence,"approved_wording":wording,"limitations":limitations,
            "owner":d.get("owner",""),"next_validation":d.get("next_validation",""),
            "escalation_required":escalation}

def claim_calibration(op:str,p:dict[str,Any]) -> dict[str,Any]:
    rows=[calibrate_one(v,i) for i,v in enumerate(as_list(p.get("claims")),1)]
    if op=="claim_extractor": return {"claims":[{"id":r["id"],"claim":r["original_claim"],"classification":r["classification"]} for r in rows]}
    if op=="evidence_mapper": return {"evidence_map":{r["id"]:r["evidence"] for r in rows}}
    if op=="scope_enforcer": return {"approved_wording":{r["id"]:r["approved_wording"] for r in rows}}
    errors=[] if rows else ["at least one claim is required"]
    lines=["# CLAIM BOUNDARIES",""]
    for r in rows:
        lines += ["## "+r["id"],"Original: "+r["original_claim"],"Classification: "+r["classification"],
                  "Approved wording: "+r["approved_wording"],"Evidence: "+(", ".join(r["evidence"]) if r["evidence"] else "none"),
                  "Limitations: "+(", ".join(map(str,r["limitations"])) if r["limitations"] else "none"),
                  "Next validation: "+str(r["next_validation"] or "none"),""]
    return {"valid":not errors,"errors":errors,"claims":rows,"escalations":[r["id"] for r in rows if r["escalation_required"]],
            "artifact":"CLAIM_BOUNDARIES.md","markdown":"\n".join(lines)}

RUNNERS={"resource-preflight":resource_preflight,"capability-admission":capability_admission,"claim-calibration":claim_calibration}

def run(skill:str,op:str,payload:dict[str,Any]) -> dict[str,Any]:
    if op in {"purpose","procedure","output_contract"}: return {"skill":skill,"operation":op,"runtime":"always-on-atomic"}
    return RUNNERS[skill](op,payload)

def cli(skill:str,op:str|None=None) -> int:
    ap=argparse.ArgumentParser()
    if op is None: ap.add_argument("operation")
    ap.add_argument("--input")
    args=ap.parse_args()
    operation=op or args.operation
    print(json.dumps(run(skill,operation,load_payload(args.input)),indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("skill"); ap.add_argument("operation"); ap.add_argument("--input"); args=ap.parse_args()
    print(json.dumps(run(args.skill,args.operation,load_payload(args.input)),indent=2,sort_keys=True))
