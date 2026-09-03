#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

VALID_STATES={"VERIFIED","SUPPORTED","CANDIDATE","UNVERIFIED","BLOCKED"}

def load(path:Path)->dict[str,Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def dump(path:Path,obj:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def evidence_id(source_id:str,artifact:str,claim:str)->str:
    h=hashlib.sha256(f"{source_id}\0{artifact}\0{claim}".encode()).hexdigest()[:16]
    return f"ev_{h}"

def validate_sources(target:dict[str,Any],sources:dict[str,Any])->None:
    domains=set(target["competency_domains"]); seen=set()
    for src in sources.get("sources",[]):
        sid=src.get("source_id")
        if not sid or sid in seen: raise ValueError(f"invalid/duplicate source_id: {sid!r}")
        seen.add(sid)
        if src.get("state") not in VALID_STATES: raise ValueError(f"{sid}: invalid state")
        if not src.get("locator") or not src.get("artifact") or not src.get("verification"):
            raise ValueError(f"{sid}: locator, artifact, verification required")
        for claim in src.get("claims",[]):
            if not claim.get("claim"): raise ValueError(f"{sid}: empty claim")
            strength=int(claim.get("hiring_signal",0))
            if strength<1 or strength>5: raise ValueError(f"{sid}: hiring_signal must be 1..5")
            unknown=set(claim.get("competencies",[]))-domains
            if unknown: raise ValueError(f"{sid}: unknown competencies {sorted(unknown)}")

def build(target:dict[str,Any],sources:dict[str,Any])->dict[str,Any]:
    validate_sources(target,sources)
    records=[]; metrics=[]; projects=[]
    for src in sources["sources"]:
        project=src.get("project")
        if project:
            projects.append({
                "source_id":src["source_id"],"name":project["name"],"url":src["locator"],
                "role":project.get("role","portfolio"),"summary":project.get("summary",""),
                "state":src["state"],"artifact":src["artifact"],
                "public_safe":bool(project.get("public_safe",src.get("public_safe",True)))
            })
        for metric in src.get("metrics",[]):
            metrics.append({**metric,"source_id":src["source_id"],"artifact":src["artifact"],"state":src["state"]})
        for claim in src.get("claims",[]):
            records.append({
                "evidence_id":evidence_id(src["source_id"],src["artifact"],claim["claim"]),
                "claim":claim["claim"],"source":src["locator"],"source_id":src["source_id"],
                "artifact":src["artifact"],"verification":src["verification"],"state":src["state"],
                "competencies":claim.get("competencies",[]),"hiring_signal":int(claim["hiring_signal"]),
                "gap":claim.get("gap",""),"next_strengthening_action":claim.get("next_strengthening_action",""),
                "public_safe":bool(claim.get("public_safe",True))
            })
    records.sort(key=lambda r:(-r["hiring_signal"],r["source_id"],r["evidence_id"]))
    coverage={}
    for domain in target["competency_domains"]:
        matched=[r for r in records if domain in r["competencies"]]
        coverage[domain]={
            "record_count":len(matched),
            "verified_count":sum(r["state"]=="VERIFIED" for r in matched),
            "max_hiring_signal":max([r["hiring_signal"] for r in matched],default=0),
            "evidence_ids":[r["evidence_id"] for r in matched]
        }
    return {
        "schema_version":1,"company":target["company"],"role_family":target["role_family"],
        "primary_role":target["primary_role"],"identity":target["identity"],"records":records,
        "metrics":metrics,"projects":projects,"coverage":coverage,
        "summary":{
            "sources":len(sources["sources"]),"records":len(records),
            "verified_records":sum(r["state"]=="VERIFIED" for r in records),
            "public_safe_records":sum(r["public_safe"] for r in records),
            "competencies_with_evidence":sum(v["record_count"]>0 for v in coverage.values()),
            "competencies_total":len(coverage)
        }
    }

def verify(target:dict[str,Any],ledger:dict[str,Any])->dict[str,Any]:
    errors=[]; ids=set(); domains=set(target["competency_domains"])
    for r in ledger.get("records",[]):
        rid=r.get("evidence_id")
        if rid in ids: errors.append(f"duplicate evidence_id {rid}")
        ids.add(rid)
        if r.get("state") not in VALID_STATES: errors.append(f"{rid}: invalid state")
        if not all(r.get(k) for k in ("claim","source","artifact","verification")):
            errors.append(f"{rid}: missing required evidence field")
        if set(r.get("competencies",[]))-domains: errors.append(f"{rid}: unknown competency")
    return {"status":"VALID" if not errors else "INVALID","errors":errors,"records":len(ids)}

def project(target:dict[str,Any],ledger:dict[str,Any])->dict[str,Any]:
    visible=[r for r in ledger["records"] if r["public_safe"] and r["state"] in {"VERIFIED","SUPPORTED"}]
    ranked=sorted(visible,key=lambda r:(-r["hiring_signal"],r["source_id"]))
    order=["tower-of-babel","mega-skills","spacex-autonomy","job-application","xai-colossus-cooling","mission-thread-quorum","actuation-receipt-bus"]
    by_source={p["source_id"]:p for p in ledger["projects"]}
    projects=[by_source[s] for s in order if s in by_source and by_source[s].get("public_safe",True)]
    skills=["Forward-Deployed Engineering","AI Systems Architecture","Agentic AI","Multi-Agent Systems",
        "AI Orchestration","Applied Artificial Intelligence","AI Infrastructure","Distributed Systems",
        "System Design","Large Language Model (LLM) Applications","Python","Systems Integration",
        "AI Evaluation","Reliability Engineering","Model Context Protocol (MCP)","Workflow Automation",
        "Human-in-the-Loop Systems","Observability","API Integration"]
    return {
        "schema_version":1,"identity":target["identity"],
        "headline":"Forward Deployed AI Architect | AI Systems Architecture, Agent Infrastructure & Orchestration | Reliable Applied AI",
        "proof_architecture":["architecture","orchestration substrate","applied systems","evidence/release control","bounded consequential systems"],
        "featured_projects":projects,"skills":skills,
        "proof_points":[{"evidence_id":r["evidence_id"],"claim":r["claim"],"source_id":r["source_id"]} for r in ranked[:12]],
        "metrics":[m for m in ledger.get("metrics",[]) if m.get("state") in {"VERIFIED","SUPPORTED"}],
        "coverage_gaps":[d for d,s in ledger.get("coverage",{}).items() if s.get("record_count",0)==0],
        "projection_rule":"Only VERIFIED or SUPPORTED public-safe evidence may populate outward LinkedIn proof claims. CANDIDATE, UNVERIFIED, and BLOCKED records remain internal gaps."
    }

def markdown(p:dict[str,Any])->str:
    lines=["# LinkedIn Evidence Backbone","",f"**Identity:** {p['identity']}","",f"**Headline:** {p['headline']}","",
        "## Proof architecture",""," → ".join(p["proof_architecture"]),"","## Featured / Projects order",""]
    for i,x in enumerate(p["featured_projects"],1):
        lines += [f"{i}. **{x['name']}** — {x['summary']}  ",f"   Evidence: `{x['source_id']}` · `{x['state']}` · {x['url']}"]
    lines += ["","## Highest-signal proof points",""]
    for x in p["proof_points"]: lines.append(f"- `{x['evidence_id']}` **{x['source_id']}** — {x['claim']}")
    lines += ["","## Defensible metrics",""]
    for x in p["metrics"]: lines.append(f"- **{x['name']} = {x['value']}** — {x.get('scope','')} (`{x['source_id']}`)")
    lines += ["","## Current evidence gaps",""]+[f"- {x}" for x in p["coverage_gaps"]]
    lines += ["","## Skill ontology","", " • ".join(p["skills"]),"","## Publication law","",p["projection_rule"],""]
    return "\n".join(lines)

def main()->int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
    b=sub.add_parser("build"); b.add_argument("--target",type=Path,required=True); b.add_argument("--sources",type=Path,required=True); b.add_argument("--output",type=Path,required=True)
    v=sub.add_parser("verify"); v.add_argument("--target",type=Path,required=True); v.add_argument("--ledger",type=Path,required=True)
    q=sub.add_parser("project"); q.add_argument("--target",type=Path,required=True); q.add_argument("--ledger",type=Path,required=True); q.add_argument("--output",type=Path,required=True); q.add_argument("--markdown",type=Path)
    a=p.parse_args()
    if a.cmd=="build": dump(a.output,build(load(a.target),load(a.sources))); return 0
    if a.cmd=="verify":
        result=verify(load(a.target),load(a.ledger)); print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result["status"]=="VALID" else 2
    target,ledger=load(a.target),load(a.ledger); result=project(target,ledger); dump(a.output,result)
    if a.markdown:
        a.markdown.parent.mkdir(parents=True,exist_ok=True); a.markdown.write_text(markdown(result),encoding="utf-8")
    return 0

if __name__=="__main__": raise SystemExit(main())
