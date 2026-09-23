#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any
METRICS=("mission_coverage","intelligence_fit","evidence_strength","verification_depth","resilience","composability","strategic_leverage","execution_readiness")
DEFAULT_WEIGHTS={"mission_coverage":1.6,"intelligence_fit":1.4,"evidence_strength":1.5,"verification_depth":1.4,"resilience":1.2,"composability":1.0,"strategic_leverage":1.2,"execution_readiness":1.1}
HARD_GATES=("authorized","approvals_satisfied","human_control_preserved","safety_pass")
def clamp(v:Any)->float:
 x=float(v); return max(0.0,min(1.0,x))
def receipt(payload:dict[str,Any])->str:
 return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def evaluate(payload:dict[str,Any])->dict[str,Any]:
 mission=payload.get("mission") or {}; candidates=payload.get("candidates") or []
 if not candidates: raise ValueError("candidates must contain at least one route")
 floor=clamp(mission.get("required_evidence_floor",0.0)); weights=DEFAULT_WEIGHTS|{k:float(v) for k,v in (mission.get("weights") or {}).items() if k in METRICS}; total=sum(weights.values()); ranked=[]
 for c in candidates:
  cid=str(c.get("id") or "").strip()
  if not cid: raise ValueError("every candidate requires id")
  failures=[g for g in HARD_GATES if c.get(g) is not True]
  if clamp(c.get("evidence_floor",0))<floor: failures.append("evidence_floor")
  power=sum(clamp(c.get(m,0))*weights[m] for m in METRICS)/total; pressure=(clamp(c.get("cost_pressure",0))+clamp(c.get("complexity_pressure",0)))/2; coherent=power-(0.08*pressure)
  ranked.append({"id":cid,"eligible":not failures,"hard_gate_failures":failures,"power_fit":round(power,6),"coherent_score":round(coherent,6),"metrics":{m:clamp(c.get(m,0)) for m in METRICS}})
 ranked.sort(key=lambda x:(x["eligible"],x["coherent_score"],x["power_fit"]),reverse=True); eligible=[r for r in ranked if r["eligible"]]
 if not eligible: status="BLOCKED"; selected=None; reason="No route satisfies hard gates."
 elif len(eligible)>1 and eligible[0]["coherent_score"]-eligible[1]["coherent_score"]<0.025: status="REVIEW_REQUIRED"; selected=None; reason="Top eligible routes are within the review margin."
 else: status="SELECTED"; selected=eligible[0]["id"]; reason="Highest strongest-intelligent-fit score among hard-gate-passing routes."
 result={"schema_version":1,"kernel":"strong-smart-routing-kernel","mission_id":mission.get("id","unspecified"),"status":status,"selected_route":selected,"reason":reason,"ranking":ranked,"operator_invariant":"STRONG AND SMART, NOT SMALL AND MINIMAL"}; result["receipt_sha256"]=receipt({"input":payload,"decision":result}); return result
def main(argv=None)->int:
 p=argparse.ArgumentParser(); sp=p.add_subparsers(dest="cmd",required=True); e=sp.add_parser("evaluate"); e.add_argument("--input",type=Path,required=True); e.add_argument("--output",type=Path); a=p.parse_args(argv); out=evaluate(json.loads(a.input.read_text())); text=json.dumps(out,indent=2,sort_keys=True)+"\n"
 if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text)
 print(text,end=""); return 0 if out["status"]=="SELECTED" else 2
if __name__=="__main__": raise SystemExit(main())
