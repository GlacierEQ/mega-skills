#!/usr/bin/env python3
"""Two-pass readiness reconciliation for GlacierEQ mega-skills."""
# reconciliation-version: 2
from __future__ import annotations
import argparse, json, re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
SKILLS_DIR = ROOT / "skills"
READINESS_REGISTRY = REGISTRY / "skill-readiness.json"
GENERIC_MARKERS = ('"epistemic_tier": "L2"', '"firewall_active": True', 'payload["status"] = "executed"')
EXPLICIT_STUB_MARKERS = ("Status: STUB - implement per skill contract", "# TODO: Implement")
BEHAVIOR_TODO_MARKERS = ("TODO: Add actual behavioral tests", "TODO: implement actual behavioral tests")
SOURCE_SUFFIXES = {".py",".js",".mjs",".cjs",".ts",".tsx",".sh",".go",".rs",".jl"}

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

def is_generic_adapter(text: str) -> bool:
    return all(marker in text for marker in GENERIC_MARKERS)

def generic_adapter_text(skill_id: str) -> str:
    return f'''#!/usr/bin/env python3
"""Compatibility adapter for {skill_id}; package discovery only, not domain execution."""
import json
import sys

def main() -> int:
    wants_execute = "--execute" in sys.argv[1:]
    payload = {{
        "skill": "{skill_id}",
        "adapter": True,
        "capability_executed": False,
        "status": "execution_unavailable" if wants_execute else "adapter_ready",
        "reason": (
            "Generic compatibility adapter has no domain execution implementation. Use SKILL.md or a substantive package entrypoint."
            if wants_execute else "Compatibility adapter is installed and discoverable."
        ),
    }}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 2 if wants_execute else 0

if __name__ == "__main__":
    raise SystemExit(main())
'''

def repair_generic_adapters() -> list[str]:
    changed = []
    for path in sorted(SKILLS_DIR.rglob("*.py")):
        if "/tests/" in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not is_generic_adapter(text):
            continue
        skill_id = path.relative_to(SKILLS_DIR).parts[0]
        replacement = generic_adapter_text(skill_id)
        if text != replacement:
            path.write_text(replacement, encoding="utf-8")
            changed.append(path.relative_to(ROOT).as_posix())
    return changed

def substantive_instruction(skill_md: Path) -> tuple[bool, list[str]]:
    if not skill_md.is_file():
        return False, ["missing SKILL.md"]
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    parts = text.split("---", 2)
    body = parts[2].strip() if len(parts) >= 3 else text.strip()
    reasons = []
    if len(body) < 180:
        reasons.append("instruction body too small")
    if not any(t in body.lower() for t in ("use","purpose","procedure","workflow","when to","capabilit","steps","pattern","role","method","sequence","framework")):
        reasons.append("no actionable procedure/capability language")
    if "TODO: Add reference documentation" in body and len(body) < 600:
        reasons.append("placeholder reference content")
    return not reasons, reasons

def inspect_skill(entry: dict[str, Any]) -> dict[str, Any]:
    root = ROOT / entry["path"]
    instruction_ok, reasons = substantive_instruction(root / "SKILL.md")
    stubs, real_impl, adapters, test_files = [], [], [], []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if "/tests/" in rel and path.suffix == ".py":
            test_files.append(path); continue
        if path.suffix not in SOURCE_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if is_generic_adapter(text) or "Generic compatibility adapter has no domain execution implementation." in text:
            adapters.append(rel); continue
        if any(m in text for m in EXPLICIT_STUB_MARKERS):
            stubs.append(rel); continue
        if len(re.sub(r"\s+","",text)) >= 160 and path.name != "__init__.py":
            real_impl.append(rel)

    behavioral, structural = [], []
    for path in test_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        if any(m in text for m in BEHAVIOR_TODO_MARKERS):
            structural.append(rel); continue
        assertions = len(re.findall(r"\bassert\b|self\.assert", text))
        existence_bias = text.count(".exists()") + text.count("stat().st_mode") + text.count("assertIn(")
        invokes = any(t in text for t in ("subprocess.run","main(","run(","execute(","result","output","sha256","conservation","conver","parse(","validate_"))
        (behavioral if assertions >= 2 and invokes and assertions > existence_bias else structural).append(rel)

    execution_intent = bool(stubs or real_impl)
    reasons = list(reasons)
    if stubs:
        state, ready = "implementation_partial", False
        reasons.append(f"{len(stubs)} explicit implementation stub(s)")
    elif execution_intent and real_impl and behavioral:
        state, ready = "behavior_verified", instruction_ok
    elif execution_intent and real_impl:
        state, ready = "implementation_unverified", False
        reasons.append("implementation exists without behavioral verification")
    elif instruction_ok:
        state, ready = "instruction_ready", True
    else:
        state, ready = "contract_incomplete", False
    return {
        "id": entry["id"], "layer":"skill", "ready":ready, "state":state,
        "declared_maturity":entry.get("maturity"), "instruction_ready":instruction_ok,
        "real_implementation_files":real_impl, "generic_adapter_files":adapters,
        "stub_files":stubs, "behavioral_tests":behavioral, "structural_tests":structural,
        "reasons":reasons
    }

def inspect_combo(entry, skill_states, external_ids):
    reasons=[]
    for member in entry.get("members",[]):
        mid, kind = member.get("id"), member.get("kind")
        if kind=="skill":
            state=skill_states.get(mid)
            if state is None: reasons.append(f"unresolved skill: {mid}")
            elif member.get("required",True) and not state["ready"]: reasons.append(f"required skill not ready: {mid}")
        elif kind=="external-skill" and mid not in external_ids:
            reasons.append(f"unresolved external skill: {mid}")
    doc=ROOT/entry.get("entrypoint","")
    if not doc.is_file() or len(doc.read_text(encoding="utf-8",errors="replace").strip())<300:
        reasons.append("COMBO.md contract missing or too small")
    ready=not reasons
    return {"id":entry["id"],"layer":"combo","ready":ready,"state":"composition_ready" if ready else "composition_candidate","declared_maturity":entry.get("maturity"),"reasons":reasons}

def inspect_mega(entry, combo_states):
    reasons=[]
    for cid in entry.get("required_combos",[]):
        if cid not in combo_states or not combo_states[cid]["ready"]:
            reasons.append(f"required combo not ready: {cid}")
    doc=ROOT/entry.get("entrypoint","")
    if not doc.is_file() or len(doc.read_text(encoding="utf-8",errors="replace").strip())<300:
        reasons.append("MEGA.md contract missing or too small")
    ready=not reasons
    return {"id":entry["id"],"layer":"mega","ready":ready,"state":"mission_contract_ready" if ready else "mission_candidate","execution_scope":entry.get("firewall",{}).get("mode","unspecified"),"declared_maturity":entry.get("maturity"),"reasons":reasons}

def build_report():
    skills_doc=load_json(REGISTRY/"skills.json")
    combos_doc=load_json(REGISTRY/"combo-skills.json")
    megas_doc=load_json(REGISTRY/"mega-skills.json")
    external_doc=load_json(REGISTRY/"external-skills.json")
    external_ids={e["id"] for e in external_doc.get("entries",[])}
    skills=[inspect_skill(e) for e in skills_doc.get("entries",[])]
    sm={e["id"]:e for e in skills}
    combos=[inspect_combo(e,sm,external_ids) for e in combos_doc.get("entries",[])]
    cm={e["id"]:e for e in combos}
    megas=[inspect_mega(e,cm) for e in megas_doc.get("entries",[])]
    all_entries=skills+combos+megas
    return {"schema_version":1,"policy":"No package may claim active/ready without observable readiness evidence.","summary":{
      "skills":len(skills),"combos":len(combos),"megas":len(megas),
      "ready_total":sum(e["ready"] for e in all_entries),
      "not_ready_total":sum(not e["ready"] for e in all_entries),
      "skill_states":dict(Counter(e["state"] for e in skills)),
      "combo_states":dict(Counter(e["state"] for e in combos)),
      "mega_states":dict(Counter(e["state"] for e in megas))},
      "skills":skills,"combos":combos,"megas":megas}

def apply_maturity(report):
    changed=Counter()
    for filename,key in (("skills.json","skills"),("combo-skills.json","combos"),("mega-skills.json","megas")):
        path=REGISTRY/filename; doc=load_json(path); states={e["id"]:e for e in report[key]}
        for entry in doc.get("entries",[]):
            desired="active" if states[entry["id"]]["ready"] else "candidate"
            if entry.get("maturity")!=desired:
                entry["maturity"]=desired; changed[filename]+=1
        dump_json(path,doc)
    return dict(changed)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--pass",dest="pass_number",type=int,choices=(1,2),required=True); p.add_argument("--apply",action="store_true"); p.add_argument("--report",type=Path)
    a=p.parse_args()
    changed=[]
    if a.pass_number==1 and a.apply: changed=repair_generic_adapters()
    report=build_report(); report["pass"]=a.pass_number; report["pass1_adapter_repairs"]=len(changed)
    if a.pass_number==2 and a.apply:
        report["maturity_changes"]=apply_maturity(report)
        report=build_report(); report["pass"]=2
    dump_json(READINESS_REGISTRY,report)
    if a.report: dump_json((a.report if a.report.is_absolute() else ROOT/a.report),report)
    print(json.dumps(report["summary"],indent=2,sort_keys=True))
    if changed: print(f"Pass 1 repaired {len(changed)} false-success compatibility adapters.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
