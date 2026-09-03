#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def load(p:Path): return json.loads(p.read_text(encoding="utf-8"))
def dump(p:Path,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def build(ledger,activation):
    q=[]
    for g in ledger.get("gap_queue",[]):
        rid=g["requirement_id"]
        q.append({
            "id":f"evidence-retrieval:{rid}",
            "owner":"system",
            "type":"evidence_retrieval",
            "status":"READY",
            "priority":round(100*g["priority"],1),
            "requirement_id":rid,
            "instruction":f"Search existing repositories, receipts, deployment records, Helix artifacts, and verified project history for stronger evidence of: {g['label']}. Preserve source lineage; do not upgrade narrative into proof.",
            "completion":"At least one stronger typed evidence source is added and the ledger is regenerated, or retrieval is exhausted with an explicit NO_EVIDENCE_FOUND result."
        })
        q.append({
            "id":f"proof-build:{rid}",
            "owner":"system",
            "type":"proof_build",
            "status":"BLOCKED_ON_RETRIEVAL",
            "priority":round(90*g["priority"],1),
            "requirement_id":rid,
            "instruction":f"If retrieval cannot satisfy {g['label']}, create the smallest credible proof build that demonstrates the missing behavior with executable verification and a public-safe case study.",
            "completion":"Executable proof + receipt + bounded public artifact exists and is ingested into evidence-sources.json."
        })

    rec=activation.get("recommendations",{})
    if rec.get("status")!="COMPLETE":
        q.append({"id":"linkedin:recommendations","owner":"operator","type":"linkedin_manual","status":rec.get("status","READY"),"priority":72,"instruction":f"Request up to {rec.get('target_count',5)} recommendations from real first-degree connections who can truthfully cover distinct dimensions: "+", ".join(rec.get("dimensions",[]))+".","completion":"Recommendations are visible on LinkedIn or explicitly declined/unavailable."})
    otw=activation.get("open_to_work",{})
    if not otw.get("locations") or not otw.get("workplace_types") or not otw.get("employment_types"):
        q.append({"id":"linkedin:open-to-work-preferences","owner":"operator","type":"linkedin_manual","status":"NEEDS_INPUT","priority":68,"instruction":"Set real location, workplace-type, and employment-type preferences. Do not infer them.","completion":"All three preference groups are explicitly populated."})
    ident=activation.get("identity_verification",{})
    if ident.get("status")!="COMPLETE":
        q.append({"id":"linkedin:identity-verification","owner":"operator","type":"linkedin_manual","status":ident.get("status","READY"),"priority":55,"instruction":"Complete LinkedIn identity verification if eligible and desired.","completion":"LinkedIn confirms verification, or status records unavailable/declined."})
    for key,state in activation.get("manual_profile_checks",{}).items():
        if state not in {"VERIFIED","COMPLETE"}:
            q.append({"id":f"linkedin:verify-{key.replace('_','-')}","owner":"operator","type":"linkedin_manual","status":state,"priority":48,"instruction":f"Inspect and verify LinkedIn {key.replace('_',' ')} against the current career positioning.","completion":f"{key} status becomes VERIFIED, COMPLETE, or intentionally deferred."})
    topics=activation.get("technical_activity",{}).get("topics",[])
    for i,t in enumerate(topics[:5],1):
        if t.get("publication_state")=="READY":
            q.append({"id":f"linkedin:technical-post:{i}","owner":"operator","type":"linkedin_content","status":"READY","priority":40-(i-1)*2,"instruction":f"Publish an evidence-linked technical post: {t['topic']}","evidence_source":t.get("evidence_source"),"completion":"Post is published and linked back to its evidence source without inflating claims."})

    q.sort(key=lambda x:(-float(x["priority"]),x["id"]))
    return {
        "schema_version":1,
        "generated_from":{
            "ledger_backbone_version":ledger.get("backbone_version"),
            "ledger_as_of":ledger.get("as_of"),
            "evidence_coverage_score":ledger.get("summary",{}).get("evidence_coverage_score")
        },
        "queue":q,
        "summary":{
            "total":len(q),
            "system":sum(x["owner"]=="system" for x in q),
            "operator":sum(x["owner"]=="operator" for x in q),
            "ready":sum(x["status"]=="READY" for x in q)
        }
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ledger",type=Path,required=True)
    p.add_argument("--activation",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    dump(a.output,build(load(a.ledger),load(a.activation)))
    return 0

if __name__=="__main__": raise SystemExit(main())
