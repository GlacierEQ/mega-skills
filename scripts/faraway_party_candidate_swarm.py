#!/usr/bin/env python3
"""Far Away Party candidate-uplift swarm."""
from __future__ import annotations
import argparse, json, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
SKILLS = ROOT / "skills"
MISSION_DIR = ROOT / "missions" / "candidate-uplift"
WORKERS_DIR = MISSION_DIR / "workers"
ACTIONABLE = ("use","workflow","procedure","when","build","create","analyze","review","debug","manage","route","connect","generate","verify")

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def split_md(text: str) -> tuple[str,str]:
    parts=text.split("---",2)
    return ((f"---{parts[1]}---\n",parts[2].strip()) if len(parts)>=3 else ("",text.strip()))

def description(front: str) -> str:
    m=re.search(r'^description:\s*["\']?(.*?)["\']?\s*$',front,re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

def assets(skill_id: str) -> dict[str,list[str]]:
    root=SKILLS/skill_id
    out={"scripts":[],"tests":[],"references":[],"assets":[]}
    if not root.is_dir(): return out
    for p in root.rglob("*"):
        if not p.is_file() or p.name=="SKILL.md": continue
        rel=p.relative_to(root).as_posix()
        if rel.startswith("tests/"): out["tests"].append(rel)
        elif rel.startswith(("reference/","references/")): out["references"].append(rel)
        elif rel.startswith(("assets/","resources/")): out["assets"].append(rel)
        elif p.suffix in {".py",".js",".mjs",".ts",".tsx",".sh",".go",".rs"}: out["scripts"].append(rel)
    for k in out: out[k].sort()
    return out

def inspect(state: dict[str,Any]) -> dict[str,Any]:
    sid=state["id"]; path=SKILLS/sid/"SKILL.md"
    text=path.read_text(encoding="utf-8",errors="replace") if path.is_file() else ""
    front,body=split_md(text)
    return {
      "id":sid,"state":state["state"],"ready":state["ready"],
      "declared_maturity":state.get("declared_maturity"),"description":description(front),
      "body_chars":len(body),"reasons":state.get("reasons",[]),"package":assets(sid),
      "stub_files":state.get("stub_files",[]),"behavioral_tests":state.get("behavioral_tests",[]),
      "structural_tests":state.get("structural_tests",[]),
      "real_implementation_files":state.get("real_implementation_files",[])
    }

def worker_job(states,worker,workers):
    assigned=[s for i,s in enumerate(states) if i%workers==worker]
    findings=[]
    for s in assigned:
        r=inspect(s)
        r["recommended_action"]={
          "contract_incomplete":"repair_instruction_contract",
          "implementation_unverified":"design_behavioral_verification",
          "implementation_partial":"finish_domain_implementation",
        }.get(r["state"],"inspect")
        findings.append(r)
    return {"worker":worker,"workers":workers,"assigned":len(assigned),"findings":findings}

def contract_body(sid,desc,pkg):
    resource=[]
    for label,key in (("Scripts","scripts"),("References","references"),("Tests","tests")):
        vals=pkg[key][:12]
        if vals:
            resource.append("### "+label+"\n"+"\n".join("- "+v for v in vals))
    resource_text="\n\n".join(resource) if resource else "No bundled resources are required by the current package."
    return f"""# {sid.replace('-', ' ').title()}

## Purpose

{desc}

## Use When

Use this skill when the requested task matches the capability described above and this is the most specific available skill for the work.

## Operating Method

1. Identify the concrete outcome, inputs, and constraints.
2. Inspect relevant project state or artifacts before making changes.
3. Load only the bundled resources needed for the current task.
4. Execute the narrowest complete workflow that produces the requested outcome.
5. Verify the result with observable output, tests, or source-backed evidence.
6. Report the produced artifact or exact resulting state. Never claim execution that did not occur.

## Progressive Disclosure

Keep the core procedure concise. Load detailed references, scripts, and tests only when they are needed.

{resource_text}

## Verification

Instruction readiness and executable readiness are separate. Scripts and integrations must earn behavioral proof through the repository readiness assay before they are described as executed or behavior-verified.

## Boundaries

- Do not invent missing implementation.
- A package-discovery adapter is not evidence of domain execution.
- Preserve upstream provenance and existing project semantics.
- Report unavailable credentials, services, or destructive dependencies precisely instead of fabricating success.
"""

def repair_contract(record):
    if record["state"]!="contract_incomplete": return False
    sid=record["id"]; path=SKILLS/sid/"SKILL.md"
    if not path.is_file() or not record.get("description"): return False
    text=path.read_text(encoding="utf-8",errors="replace"); front,body=split_md(text)
    if len(body)>=180 and any(w in body.lower() for w in ACTIONABLE): return False
    new=front.rstrip()+"\n\n"+contract_body(sid,record["description"],record["package"]).rstrip()+"\n"
    if new==text: return False
    path.write_text(new,encoding="utf-8")
    return True

def write_state(readiness,repairs,workers):
    s=readiness["summary"]
    MISSION_DIR.mkdir(parents=True,exist_ok=True)
    files={
      "MISSION.md":"""# MISSION — Candidate Uplift

Activated capability stack:
- Far Away Party for durable mission state and resumption
- Faraway Party endurance protocol for wide parallel inspection
- APEX Always-On Core for recurring continuation
- Skill Creator for concise contract repair
- Distributed Processing and Subagent-Driven Development for worker partitioning
- Readiness Assay as the sole promotion authority

Objective: turn candidate skills into truthfully usable capabilities without inventing missing implementation.
""",
      "ROADMAP.md":"""# ROADMAP — Candidate Uplift

1. Truth repair of false ready/executed adapters — COMPLETE
2. Instruction contract swarm — ACTIVE
3. Behavioral verification swarm — NEXT
4. Domain implementation forge for explicit stubs
5. Combo reactivation
6. Mega activation when dependencies are actually ready
""",
      "CONTEXT.md":f"""# CONTEXT — Candidate Uplift

Atomic skills: {s['skills']}
Combos: {s['combos']}
Megas: {s['megas']}
Ready total before this run: {s['ready_total']}
Not ready before this run: {s['not_ready_total']}
Workers: {workers}
Instruction contracts repaired: {len(repairs)}
""",
      "EVIDENCE.md":"# EVIDENCE — Candidate Uplift\n\nContract repairs this run:\n"+("\n".join("- "+x for x in repairs) if repairs else "- none")+"\n",
      "HANDOFF.md":"""# HANDOFF — Candidate Uplift

Parallel inspection and evidence-supported contract repairs are complete for this cycle.

Next: rerun readiness, hierarchy validation, and tests. Then attack implementation-unverified skills with substantive code and the cheapest path to real behavioral proof. Worker JSON files are the durable backlog map.
"""
    }
    for n,c in files.items(): (MISSION_DIR/n).write_text(c,encoding="utf-8")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--workers",type=int,default=8); p.add_argument("--repair",action="store_true"); a=p.parse_args()
    workers=max(1,min(a.workers,32))
    readiness=load_json(REGISTRY/"skill-readiness.json")
    candidates=sorted([x for x in readiness["skills"] if not x["ready"]],key=lambda x:(x["state"],x["id"]))
    results=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(worker_job,candidates,i,workers) for i in range(workers)]
        for f in as_completed(futures): results.append(f.result())
    results.sort(key=lambda x:x["worker"]); WORKERS_DIR.mkdir(parents=True,exist_ok=True)
    for r in results: (WORKERS_DIR/f"worker-{r['worker']:02d}.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    repairs=[]
    if a.repair:
        for rec in sorted([f for r in results for f in r["findings"]],key=lambda x:x["id"]):
            if repair_contract(rec): repairs.append(rec["id"])
    write_state(readiness,repairs,workers)
    print(json.dumps({"workers":workers,"candidate_count":len(candidates),"contract_repairs":repairs},indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
