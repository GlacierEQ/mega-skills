#!/usr/bin/env python3
"""Shared deterministic runtime for Far Away Party long-horizon atomic skills."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

def as_list(value: Any) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]

def load_payload(path: str | None) -> dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    raw=sys.stdin.read().strip()
    return json.loads(raw) if raw else {}

def bullets(values: list) -> str:
    return "\n".join("- "+str(v) for v in values) if values else "- None declared"

def mission(op: str, p: dict[str, Any]) -> dict[str, Any]:
    raw_criteria=as_list(p.get("acceptance_criteria") or p.get("criteria"))
    criteria=[]
    for i,v in enumerate(raw_criteria,1):
        if isinstance(v,dict):
            text=str(v.get("criterion") or v.get("text") or "").strip()
            evidence=as_list(v.get("evidence"))
        else:
            text=str(v).strip(); evidence=[]
        if text:
            criteria.append({"id":f"AC-{i:02d}","criterion":text,"evidence":evidence})
    m={
      "outcome":str(p.get("outcome","")).strip(),
      "deliverables":as_list(p.get("deliverables") or p.get("includes")),
      "exclusions":as_list(p.get("exclusions") or p.get("excludes")),
      "constraints":as_list(p.get("constraints")),
      "acceptance_criteria":criteria,
      "assumptions":as_list(p.get("assumptions")),
      "approvals":as_list(p.get("approvals")),
      "risks":as_list(p.get("risks")),
      "stop_condition":str(p.get("stop_condition","")).strip(),
      "next_decision":str(p.get("next_decision","")).strip(),
    }
    if op=="outcome_framer": return {"outcome":m["outcome"]}
    if op=="scope_separator": return {"deliverables":m["deliverables"],"exclusions":m["exclusions"]}
    if op=="constraint_mapper": return {"constraints":m["constraints"],"approvals":m["approvals"],"risks":m["risks"]}
    if op=="criteria_definer": return {"acceptance_criteria":criteria}
    if op=="assumption_bounder": return {"assumptions":m["assumptions"],"next_decision":m["next_decision"]}
    errors=[]
    if not m["outcome"]: errors.append("outcome is required")
    if not criteria: errors.append("at least one acceptance criterion is required")
    if not m["stop_condition"]: errors.append("stop_condition is required")
    md=(
      "# MISSION\n\n## Outcome\n"+m["outcome"]+
      "\n\n## Deliverables\n"+bullets(m["deliverables"])+
      "\n\n## Exclusions\n"+bullets(m["exclusions"])+
      "\n\n## Constraints\n"+bullets(m["constraints"])+
      "\n\n## Acceptance Criteria\n"+bullets([c["id"]+" "+c["criterion"] for c in criteria])+
      "\n\n## Assumptions\n"+bullets(m["assumptions"])+
      "\n\n## Approvals\n"+bullets(m["approvals"])+
      "\n\n## Risks\n"+bullets(m["risks"])+
      "\n\n## Stop Condition\n"+m["stop_condition"]+
      "\n\n## Next Decision\n"+(m["next_decision"] or "Begin roadmap construction.")+"\n"
    )
    return {"valid":not errors,"errors":errors,"mission":m,"artifact":"MISSION.md","markdown":md if not errors else ""}

def roadmap(op: str, p: dict[str, Any]) -> dict[str, Any]:
    m=p.get("mission",p)
    raw=as_list(m.get("acceptance_criteria") or m.get("criteria"))
    criteria=[]
    for v in raw:
        text=str(v.get("criterion") or v.get("text") or "") if isinstance(v,dict) else str(v)
        if text.strip(): criteria.append(text.strip())
    artifacts=as_list(p.get("artifacts") or m.get("deliverables"))
    chunks=[]
    for i,text in enumerate(criteria,1):
        chunks.append({
          "id":f"CH-{i:02d}","objective":"Satisfy acceptance criterion: "+text,
          "inputs":["MISSION.md"],"owner":"assigned-specialist",
          "deliverable":artifacts[i-1] if i-1<len(artifacts) else f"artifact-{i:02d}",
          "dependencies":[] if i==1 else [f"CH-{i-1:02d}"],
          "failure_path":"record evidence, repair the failed criterion, and rerun verification",
          "verification":text,"status":"pending"
        })
    if op=="artifact_lister": return {"artifacts":[c["deliverable"] for c in chunks]}
    if op=="dependency_optimizer": return {"dependencies":{c["id"]:c["dependencies"] for c in chunks}}
    if op=="phase_grouper": return {"phases":[{"id":"PH-01","chunks":[c["id"] for c in chunks]}]}
    if op=="chunk_definer": return {"chunks":chunks}
    if op=="parallelism_validator":
        return {"safe_parallel_pairs":[],"reason":"default roadmap is dependency-ordered unless independence is explicit"}
    errors=[] if chunks else ["no acceptance criteria to map"]
    lines=["# ROADMAP","","## Phase 1 — Verified Execution",""]
    for c in chunks:
        lines += ["### "+c["id"]+" — "+c["objective"],"- Owner: "+c["owner"],"- Deliverable: "+str(c["deliverable"]),
                  "- Dependencies: "+(", ".join(c["dependencies"]) if c["dependencies"] else "none"),
                  "- Verification: "+c["verification"],"- Failure path: "+c["failure_path"],""]
    lines += ["## Exact Next Action",chunks[0]["id"] if chunks else "Define acceptance criteria."]
    return {"valid":not errors,"errors":errors,"chunks":chunks,"artifact":"ROADMAP.md","markdown":"\n".join(lines)+"\n"}

def evidence(op: str, p: dict[str, Any]) -> dict[str, Any]:
    items=[]
    for i,v in enumerate(as_list(p.get("items") or p.get("evidence")),1):
        d=dict(v) if isinstance(v,dict) else {"value":v}
        d.setdefault("id",f"E-{i:03d}"); d.setdefault("kind","source"); d.setdefault("reliability_limit","not stated")
        items.append(d)
    claims=[]
    for i,v in enumerate(as_list(p.get("claims")),1):
        d=dict(v) if isinstance(v,dict) else {"claim":str(v),"evidence":[]}
        d.setdefault("id",f"C-{i:03d}"); d["evidence"]=as_list(d.get("evidence")); claims.append(d)
    ids={x["id"] for x in items}; gaps=[]
    for c in claims:
        missing=[eid for eid in c["evidence"] if eid not in ids]
        if missing: gaps.append({"claim_id":c["id"],"missing_evidence":missing})
        if not c["evidence"]: gaps.append({"claim_id":c["id"],"missing_evidence":["none linked"]})
    if op=="id_assigner": return {"items":items}
    if op=="claim_tracer": return {"claims":claims}
    if op=="integrity_checker": return {"valid":not gaps,"gaps":gaps}
    lines=["# EVIDENCE","","## Register"]
    lines += ["- ["+x["id"]+"] "+x.get("kind","source")+": "+str(x.get("value") or x.get("description") or x.get("path") or "unnamed") for x in items]
    lines += ["","## Claims"]
    lines += ["- ["+c["id"]+"] "+str(c.get("claim",""))+" -> "+(", ".join(c["evidence"]) if c["evidence"] else "UNLINKED") for c in claims]
    lines += ["","## Gaps"] + (["- "+g["claim_id"]+": "+", ".join(g["missing_evidence"]) for g in gaps] or ["- None detected"])
    return {"valid":not gaps,"items":items,"claims":claims,"gaps":gaps,"artifact":"EVIDENCE.md","markdown":"\n".join(lines)+"\n"}

def context(op: str, p: dict[str, Any]) -> dict[str, Any]:
    keep=("current_objective","constraints","decisions","artifacts","blocking_questions","risks","next_verification","next_action","environment","assumptions")
    def compact(src):
        return {k:src[k] for k in keep if k in src and src[k] not in (None,"",[],{})}
    if op=="drift_detector":
        prev=compact(p.get("previous",{})); cur=compact(p.get("current",p.get("state",{})))
        changed=sorted(k for k in set(prev)|set(cur) if prev.get(k)!=cur.get(k))
        return {"changed_keys":changed,"drift":bool(changed)}
    c=compact(p.get("state",p))
    if op=="state_compactor": return {"context":c}
    if op=="assumption_tracker": return {"assumptions":as_list(c.get("assumptions"))}
    lines=["# CONTEXT"]
    for k,v in c.items():
        lines += ["","## "+k.replace("_"," ").title()]
        lines += [bullets(v)] if isinstance(v,list) else [json.dumps(v,indent=2,sort_keys=True) if isinstance(v,dict) else str(v)]
    valid=bool(c.get("current_objective")) and bool(c.get("next_action"))
    return {"valid":valid,"context":c,"artifact":"CONTEXT.md","markdown":"\n".join(lines)+"\n"}

def packet(op: str, p: dict[str, Any]) -> dict[str, Any]:
    x={"objective":str(p.get("objective","")).strip(),"owner":str(p.get("owner","")).strip(),
       "authority":str(p.get("authority","")).strip(),"inputs":as_list(p.get("inputs")),"output":p.get("output") or {},
       "acceptance_test":str(p.get("acceptance_test","")).strip(),"boundaries":as_list(p.get("boundaries")),
       "escalation":str(p.get("escalation","")).strip(),"state_update":as_list(p.get("state_update"))}
    if op=="objective_namer": return {"objective":x["objective"],"owner":x["owner"]}
    if op=="input_lister": return {"inputs":x["inputs"]}
    if op=="output_specifier": return {"output":x["output"]}
    if op=="acceptance_tester": return {"acceptance_test":x["acceptance_test"],"defined":bool(x["acceptance_test"])}
    if op=="boundary_enforcer": return {"boundaries":x["boundaries"],"authority":x["authority"]}
    if op=="state_updater": return {"state_update":x["state_update"]}
    errors=[k+" is required" for k in ("objective","owner","acceptance_test") if not x[k]]
    md=("# WORK PACKET\n\n## Objective\n"+x["objective"]+"\n\n## Owner\n"+x["owner"]+
        "\n\n## Inputs\n"+bullets(x["inputs"])+"\n\n## Output\n"+json.dumps(x["output"],indent=2,sort_keys=True)+
        "\n\n## Acceptance Test\n"+x["acceptance_test"]+"\n\n## Boundaries\n"+bullets(x["boundaries"])+
        "\n\n## Escalation\n"+(x["escalation"] or "Escalate when acceptance cannot be satisfied within boundaries.")+
        "\n\n## State Update\n"+bullets(x["state_update"])+"\n")
    return {"valid":not errors,"errors":errors,"packet":x,"artifact":"WORK_PACKET.md","markdown":md if not errors else ""}

def quality(op: str, p: dict[str, Any]) -> dict[str, Any]:
    criteria=[]
    for i,v in enumerate(as_list(p.get("criteria")),1):
        d=dict(v) if isinstance(v,dict) else {"criterion":str(v),"passed":False}
        d.setdefault("id",f"Q-{i:02d}"); d["passed"]=bool(d.get("passed")); d["evidence"]=as_list(d.get("evidence")); criteria.append(d)
    exceptions=as_list(p.get("exceptions"))
    failed=[c["id"] for c in criteria if not c["passed"] or not c["evidence"]]
    state="fail" if failed else ("conditional_pass" if exceptions else "pass")
    if op=="criteria_reader": return {"criteria":criteria}
    if op=="artifact_inspector": return {"failed_or_unproven":failed}
    if op=="verifier_coordinator": return {"requires_independent_verifier":bool(p.get("material_consequence") or p.get("creator_bias"))}
    if op=="failure_classifier": return {"failure_class":"evidence_or_criterion_failure" if failed else "none"}
    lines=["# QUALITY GATE","", "Decision: "+state.upper(),"","## Criteria"]
    for c in criteria:
        lines.append("- ["+c["id"]+"] "+("PASS" if c["passed"] and c["evidence"] else "FAIL")+" — "+str(c.get("criterion",""))+" — evidence: "+(", ".join(c["evidence"]) or "none"))
    lines += ["","## Exceptions"] + ([ "- "+str(x) for x in exceptions] or ["- None"])
    return {"decision":state,"criteria":criteria,"failed_or_unproven":failed,"exceptions":exceptions,"artifact":"QUALITY_GATE.md","markdown":"\n".join(lines)+"\n"}

def handoff(op: str, p: dict[str, Any]) -> dict[str, Any]:
    x={"phase":str(p.get("phase","")).strip(),"verified_progress":as_list(p.get("verified_progress")),"blockers":as_list(p.get("blockers")),
       "next_action":str(p.get("next_action","")).strip(),"owner":str(p.get("owner","")).strip(),"inputs":as_list(p.get("inputs")),
       "acceptance_test":str(p.get("acceptance_test","")).strip(),"links":as_list(p.get("links")),"environment":p.get("environment") or {},
       "assumptions":as_list(p.get("assumptions")),"failed_approaches":as_list(p.get("failed_approaches"))}
    if op=="resume_point_encoder": return {"phase":x["phase"],"verified_progress":x["verified_progress"],"blockers":x["blockers"]}
    if op=="next_action_encoder": return {"next_action":x["next_action"],"owner":x["owner"],"acceptance_test":x["acceptance_test"]}
    if op=="environment_capturer": return {"environment":x["environment"]}
    if op=="assumption_separator": return {"assumptions":x["assumptions"]}
    if op=="dead_end_recorder": return {"failed_approaches":x["failed_approaches"]}
    errors=[k+" is required" for k in ("phase","next_action","owner","acceptance_test") if not x[k]]
    md=("# HANDOFF\n\n## Current Phase\n"+x["phase"]+"\n\n## Verified Progress\n"+bullets(x["verified_progress"])+
        "\n\n## Blockers\n"+bullets(x["blockers"])+"\n\n## Exact Next Action\n"+x["next_action"]+
        "\n\nOwner: "+x["owner"]+"\n\nAcceptance test: "+x["acceptance_test"]+
        "\n\n## Required Inputs\n"+bullets(x["inputs"])+"\n\n## State Links\n"+bullets(x["links"])+
        "\n\n## Environment\n"+json.dumps(x["environment"],indent=2,sort_keys=True)+
        "\n\n## Assumptions\n"+bullets(x["assumptions"])+"\n\n## Failed Approaches\n"+bullets(x["failed_approaches"])+"\n")
    return {"valid":not errors,"errors":errors,"handoff":x,"artifact":"HANDOFF.md","markdown":md if not errors else ""}

def link_admission(op: str, p: dict[str, Any]) -> dict[str, Any]:
    cands=p.get("candidates")
    if cands is None:
        cands=[{"url":str(p.get("url","")).strip(),"authority":str(p.get("authority","")).strip(),"relevance":str(p.get("relevance","")).strip()}]
    admitted=[];rejected=[]
    for i,v in enumerate(as_list(cands),1):
        d=dict(v) if isinstance(v,dict) else {"url":str(v)}
        d.setdefault("id",f"L-{i:02d}")
        for k in ("url","authority","relevance"): d[k]=str(d.get(k,"")).strip()
        errs=[k+" is required" for k in ("url","authority","relevance") if not d[k]]
        d["admitted"]=not errs
        (admitted if not errs else rejected).append(d)
    if op=="authority_classifier": return {"admitted":[{k:a[k] for k in ("id","url","authority")} for a in admitted]}
    if op=="relevance_scorer": return {"scored":[{k:a[k] for k in ("id","url","relevance")} for a in admitted]}
    if op=="admission_recorder":
        lines=["# LINK ADMISSION","", "Admitted: %d | Rejected: %d"%(len(admitted),len(rejected)),"","## Admitted"]
        lines+=["- [%s] %s — %s — %s"%(a["id"],a["url"],a["authority"],a["relevance"]) for a in admitted] or ["- None"]
        lines+=["","## Rejected"]+["- [%s] %s"%(r["id"],r.get("url","")) for r in rejected] or ["- None"]
        return {"admitted":admitted,"rejected":rejected,"artifact":"LINK_ADMISSION.md","markdown":"\n".join(lines)+"\n"}
    return {"admitted":admitted,"rejected":rejected}

def machine_binding(op: str, p: dict[str, Any]) -> dict[str, Any]:
    links=p.get("links") or p.get("admitted") or []
    profile=p.get("device_profile") or {}
    bound=[];unbound=[]
    for i,v in enumerate(as_list(links),1):
        d=dict(v) if isinstance(v,dict) else {"url":str(v)}
        d.setdefault("id",f"B-{i:02d}")
        d["bound_property"]=str(d.get("bound_property","")).strip()
        ok=bool(d["bound_property"]) and (not isinstance(profile,dict) or not profile or d["bound_property"] in profile)
        d["bound"]=ok
        (bound if ok else unbound).append(d)
    if op=="property_resolver": return {"bound":[{"id":b["id"],"bound_property":b["bound_property"]} for b in bound]}
    if op=="scope_comparator": return {"profile_keys":sorted(profile.keys()) if isinstance(profile,dict) else [],"bound_count":len(bound),"unbound_count":len(unbound)}
    if op=="binding_recorder":
        lines=["# MACHINE BINDING","", "Bound: %d | Unbound: %d"%(len(bound),len(unbound)),""]
        lines+=["- [%s] %s → %s"%(b["id"],b.get("url",""),b["bound_property"]) for b in bound] or ["- None bound"]
        lines+=["","## Unbound"]+["- [%s] %s — no observed device property"%(u["id"],u.get("url","")) for u in unbound] or ["- None"]
        return {"bound":bound,"unbound":unbound,"artifact":"MACHINE_BINDING.md","markdown":"\n".join(lines)+"\n"}
    return {"bound":bound,"unbound":unbound}

def staleness_assess(op: str, p: dict[str, Any]) -> dict[str, Any]:
    srcs=p.get("sources") or p.get("bound") or []
    assessed=[];unpinned=[]
    for i,v in enumerate(as_list(srcs),1):
        d=dict(v) if isinstance(v,dict) else {"url":str(v)}
        d.setdefault("id",f"S-{i:02d}")
        for k in ("resolved_at","version"): d[k]=str(d.get(k,"")).strip()
        errs=[k+" is required" for k in ("resolved_at","version") if not d[k]]
        d["current"]=not errs
        (assessed if not errs else unpinned).append(d)
    if op=="version_pinner": return {"pinned":[{"id":a["id"],"version":a["version"]} for a in assessed]}
    if op=="date_checker": return {"unpinned":[s["id"] for s in unpinned]}
    if op=="staleness_recorder":
        lines=["# LINK STALENESS","", "Current: %d | Unpinned: %d"%(len(assessed),len(unpinned)),"","## Current"]
        lines+=["- [%s] %s — %s @ %s"%(a["id"],a.get("url",""),a["version"],a["resolved_at"]) for a in assessed] or ["- None"]
        lines+=["","## Unpinned"]+["- [%s] %s"%(u["id"],u.get("url","")) for u in unpinned] or ["- None"]
        return {"assessed":assessed,"unpinned":unpinned,"artifact":"LINK_STALENESS.md","markdown":"\n".join(lines)+"\n"}
    return {"assessed":assessed,"unpinned":unpinned}

def library_quality_audit(op: str, p: dict[str, Any]) -> dict[str, Any]:
    claims=p.get("claims") or []
    known=set(str(x) for x in as_list(p.get("sources")))
    known|={str((s or {}).get("id","")) for s in as_list(p.get("assessed")) if isinstance(s,dict)}
    known|={str((s or {}).get("id","")) for s in as_list(p.get("bound")) if isinstance(s,dict)}
    rows=[];unsupported=[]
    for i,v in enumerate(as_list(claims),1):
        d=dict(v) if isinstance(v,dict) else {"claim":str(v)}
        d.setdefault("id",f"C-{i:02d}")
        d["source_id"]=str(d.get("source_id","")).strip()
        d["supported"]=bool(d["source_id"]) and d["source_id"] in known
        if not d["supported"]: unsupported.append(d)
        rows.append(d)
    state="fail" if unsupported else "pass"
    if op=="claim_mapper": return {"claims":rows,"unsupported":[c["id"] for c in unsupported]}
    if op=="source_verifier": return {"known_source_ids":sorted(x for x in known if x)}
    if op=="unresolved_claim_lister": return {"unsupported":[{"id":c["id"],"claim":c.get("claim","")} for c in unsupported]}
    lines=["# MACBOOK AIR LINK AUDIT","","Decision: "+state.upper(),"","## Claims"]
    lines+=["- [%s] %s — %s"%(c["id"],"SUPPORTED" if c["supported"] else "UNSUPPORTED",c.get("claim","")) for c in rows] or ["- None"]
    lines+=["","## Unsupported claims"]+["- [%s] %s"%(c["id"],c.get("claim","")) for c in unsupported] or ["- None"]
    return {"decision":state,"claims":rows,"unsupported":unsupported,"artifact":"MACBOOK_AIR_LINK_AUDIT.md","markdown":"\n".join(lines)+"\n"}

RUNNERS={"mission-contract":mission,"roadmap-builder":roadmap,"evidence-register":evidence,"context-capsule":context,
         "work-packet":packet,"quality-gate":quality,"handoff-record":handoff,
         "link-admission":link_admission,"machine-binding":machine_binding,
         "staleness-assess":staleness_assess,"library-quality-audit":library_quality_audit}

def run(skill: str, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
    if skill not in RUNNERS:
        raise ValueError("unknown long-horizon skill: "+skill)
    if operation in {"purpose","procedure","output_contract"}:
        return {"skill":skill,"operation":operation,"runtime":"long-horizon-atomic"}
    return RUNNERS[skill](operation,payload)

def cli(skill: str, operation: str | None = None) -> int:
    ap=argparse.ArgumentParser()
    if operation is None:
        ap.add_argument("operation")
    ap.add_argument("--input")
    args=ap.parse_args()
    op=operation or args.operation
    print(json.dumps(run(skill,op,load_payload(args.input)),indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("skill"); ap.add_argument("operation"); ap.add_argument("--input")
    args=ap.parse_args()
    print(json.dumps(run(args.skill,args.operation,load_payload(args.input)),indent=2,sort_keys=True))
