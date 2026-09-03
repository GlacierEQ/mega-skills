#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from math import prod
from pathlib import Path
from typing import Any

BACKBONE_VERSION = "2.0.0"
VALID_STATES = {"VERIFIED","SUPPORTED","CANDIDATE","UNVERIFIED","BLOCKED"}
STATE_WEIGHT = {"VERIFIED":1.0,"SUPPORTED":0.72,"CANDIDATE":0.35,"UNVERIFIED":0.0,"BLOCKED":0.0}
SOURCE_WEIGHT = {
    "runtime_receipt":1.0,
    "source_and_tests":0.92,
    "source_verified":0.86,
    "readme_verified":0.72,
    "registry_observed":0.45,
    "candidate_narrative":0.25,
    "operator_attested":0.45
}
DEFAULT_SOURCE_WEIGHT = 0.35

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def dump(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def evidence_id(source_id: str, artifact: str, claim: str) -> str:
    raw = f"{source_id}\0{artifact}\0{claim}".encode()
    return "ev_" + hashlib.sha256(raw).hexdigest()[:16]

def parse_day(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])

def target_requirements(target: dict[str, Any]) -> list[dict[str, Any]]:
    if target.get("requirements"):
        return target["requirements"]
    return [
        {"id": d, "label": d, "competencies": [d], "weight": 1.0, "hard_gate": False,
         "minimum_strength": 0.45}
        for d in target.get("competency_domains", [])
    ]

def validate_target(target: dict[str, Any]) -> None:
    ids = set()
    for req in target_requirements(target):
        rid = req.get("id")
        if not rid or rid in ids:
            raise ValueError(f"invalid/duplicate target requirement id: {rid!r}")
        ids.add(rid)
        weight = float(req.get("weight", 1.0))
        minimum = float(req.get("minimum_strength", 0.45))
        if not 0 < weight <= 2:
            raise ValueError(f"{rid}: requirement weight must be (0,2]")
        if not 0 <= minimum <= 1:
            raise ValueError(f"{rid}: minimum_strength must be [0,1]")

def validate_sources(target: dict[str, Any], sources: dict[str, Any]) -> None:
    validate_target(target)
    domains = set(target.get("competency_domains", []))
    for req in target_requirements(target):
        domains.update(req.get("competencies", []))
    seen = set()
    for src in sources.get("sources", []):
        sid = src.get("source_id")
        if not sid or sid in seen:
            raise ValueError(f"invalid/duplicate source_id: {sid!r}")
        seen.add(sid)
        if src.get("state") not in VALID_STATES:
            raise ValueError(f"{sid}: invalid state")
        if not src.get("locator") or not src.get("artifact") or not src.get("verification"):
            raise ValueError(f"{sid}: locator, artifact, verification required")
        kind = src.get("source_kind", "readme_verified")
        if kind not in SOURCE_WEIGHT:
            raise ValueError(f"{sid}: unknown source_kind {kind!r}")
        for claim in src.get("claims", []):
            if not claim.get("claim"):
                raise ValueError(f"{sid}: empty claim")
            signal = int(claim.get("hiring_signal", 0))
            if not 1 <= signal <= 5:
                raise ValueError(f"{sid}: hiring_signal must be 1..5")
            unknown = set(claim.get("competencies", [])) - domains
            if unknown:
                raise ValueError(f"{sid}: unknown competencies {sorted(unknown)}")

def freshness_factor(observed_at: str | None, as_of: date, max_age_days: int) -> tuple[float, str, int | None]:
    observed = parse_day(observed_at)
    if observed is None:
        return 0.85, "UNKNOWN_DATE", None
    age = max(0, (as_of - observed).days)
    if age <= max_age_days:
        return 1.0, "FRESH", age
    if age <= max_age_days * 3:
        return 0.85, "AGING", age
    return 0.65, "STALE", age

def claim_strength(state: str, source_kind: str, hiring_signal: int, freshness: float) -> float:
    return round(
        STATE_WEIGHT[state]
        * SOURCE_WEIGHT.get(source_kind, DEFAULT_SOURCE_WEIGHT)
        * (hiring_signal / 5.0)
        * freshness,
        4
    )

def combined_strength(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(1.0 - prod(1.0 - max(0.0, min(1.0, v)) for v in values), 4)

def build(target: dict[str, Any], sources: dict[str, Any], as_of: str | None = None) -> dict[str, Any]:
    validate_sources(target, sources)
    as_of_day = parse_day(as_of or target.get("snapshot_date")) or datetime.now(timezone.utc).date()
    max_age = int(target.get("freshness", {}).get("max_source_age_days", 30))

    records, metrics, projects, source_health = [], [], [], []
    for src in sources["sources"]:
        fresh_factor, fresh_state, age_days = freshness_factor(src.get("observed_at"), as_of_day, max_age)
        sid = src["source_id"]
        source_health.append({
            "source_id": sid,
            "independence_group": src.get("independence_group", sid),
            "freshness_state": fresh_state,
            "age_days": age_days,
            "freshness_factor": fresh_factor,
            "state": src["state"],
            "source_kind": src.get("source_kind", "readme_verified")
        })

        project = src.get("project")
        if project:
            projects.append({
                "source_id": sid,
                "name": project["name"],
                "url": src["locator"],
                "role": project.get("role", "portfolio"),
                "summary": project.get("summary", ""),
                "state": src["state"],
                "artifact": src["artifact"],
                "public_safe": bool(project.get("public_safe", src.get("public_safe", True))),
                "source_kind": src.get("source_kind", "readme_verified"),
                "freshness_state": fresh_state
            })

        for metric in src.get("metrics", []):
            metrics.append({
                **metric,
                "source_id": sid,
                "artifact": src["artifact"],
                "state": src["state"],
                "source_kind": src.get("source_kind", "readme_verified"),
                "freshness_state": fresh_state
            })

        for claim in src.get("claims", []):
            strength = claim_strength(
                src["state"],
                src.get("source_kind", "readme_verified"),
                int(claim["hiring_signal"]),
                fresh_factor
            )
            records.append({
                "evidence_id": evidence_id(sid, src["artifact"], claim["claim"]),
                "claim": claim["claim"],
                "source": src["locator"],
                "source_id": sid,
                "artifact": src["artifact"],
                "verification": src["verification"],
                "state": src["state"],
                "source_kind": src.get("source_kind", "readme_verified"),
                "independence_group": src.get("independence_group", sid),
                "competencies": claim.get("competencies", []),
                "hiring_signal": int(claim["hiring_signal"]),
                "proof_strength": strength,
                "freshness_state": fresh_state,
                "age_days": age_days,
                "limitations": claim.get("limitations", []),
                "gap": claim.get("gap", ""),
                "next_strengthening_action": claim.get("next_strengthening_action", ""),
                "public_safe": bool(claim.get("public_safe", True))
            })

    records.sort(key=lambda r: (-r["proof_strength"], -r["hiring_signal"], r["source_id"], r["evidence_id"]))

    requirements = {}
    for req in target_requirements(target):
        competencies = set(req.get("competencies", []))
        matched = [r for r in records if competencies.intersection(r["competencies"])]
        grouped = {}
        for r in matched:
            group = r.get("independence_group", r["source_id"])
            grouped[group] = max(grouped.get(group, 0.0), r["proof_strength"])
        strength = combined_strength(list(grouped.values()))
        minimum = float(req.get("minimum_strength", 0.45))
        status = "SATISFIED" if strength >= minimum else ("PARTIAL" if strength > 0 else "MISSING")
        requirements[req["id"]] = {
            "label": req.get("label", req["id"]),
            "weight": float(req.get("weight", 1.0)),
            "hard_gate": bool(req.get("hard_gate", False)),
            "minimum_strength": minimum,
            "proof_strength": strength,
            "coverage_percent": round(strength * 100, 1),
            "status": status,
            "evidence_ids": [r["evidence_id"] for r in matched],
            "verified_evidence_ids": [r["evidence_id"] for r in matched if r["state"] == "VERIFIED"],
            "public_safe_evidence_ids": [r["evidence_id"] for r in matched if r["public_safe"]],
            "independent_groups": sorted(grouped)
        }

    total_weight = sum(x["weight"] for x in requirements.values()) or 1.0
    coverage_score = round(
        100.0 * sum(x["weight"] * x["proof_strength"] for x in requirements.values()) / total_weight,
        1
    )

    gaps = []
    for rid, item in requirements.items():
        deficit = max(0.0, item["minimum_strength"] - item["proof_strength"])
        priority = item["weight"] * (1.5 if item["hard_gate"] else 1.0) * deficit
        if item["status"] != "SATISFIED":
            gaps.append({
                "requirement_id": rid,
                "label": item["label"],
                "status": item["status"],
                "hard_gate": item["hard_gate"],
                "proof_strength": item["proof_strength"],
                "minimum_strength": item["minimum_strength"],
                "priority": round(priority, 4),
                "evidence_ids": item["evidence_ids"]
            })
    gaps.sort(key=lambda g: (-g["priority"], g["requirement_id"]))

    return {
        "schema_version": 2,
        "backbone_version": BACKBONE_VERSION,
        "as_of": as_of_day.isoformat(),
        "company": target["company"],
        "role_family": target["role_family"],
        "primary_role": target["primary_role"],
        "identity": target["identity"],
        "records": records,
        "metrics": metrics,
        "projects": projects,
        "source_health": source_health,
        "requirements": requirements,
        "gap_queue": gaps,
        "summary": {
            "sources": len(sources["sources"]),
            "records": len(records),
            "verified_records": sum(r["state"] == "VERIFIED" for r in records),
            "public_safe_records": sum(r["public_safe"] for r in records),
            "requirements_total": len(requirements),
            "requirements_satisfied": sum(x["status"] == "SATISFIED" for x in requirements.values()),
            "hard_gates_open": sum(x["hard_gate"] and x["status"] != "SATISFIED" for x in requirements.values()),
            "evidence_coverage_score": coverage_score
        },
        "score_semantics": "Evidence coverage score measures strength and breadth of retained proof against the target contract. Correlated claims are collapsed by independence group before evidence is compounded. It is not a hiring probability, seniority rating, or claim of employer fit."
    }

def verify(target: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    errors, ids = [], set()
    req_ids = {r["id"] for r in target_requirements(target)}
    for r in ledger.get("records", []):
        rid = r.get("evidence_id")
        if rid in ids:
            errors.append(f"duplicate evidence_id {rid}")
        ids.add(rid)
        if r.get("state") not in VALID_STATES:
            errors.append(f"{rid}: invalid state")
        if not all(r.get(k) for k in ("claim","source","artifact","verification")):
            errors.append(f"{rid}: missing required evidence field")
        if not 0 <= float(r.get("proof_strength", -1)) <= 1:
            errors.append(f"{rid}: proof_strength outside [0,1]")
    if req_ids != set(ledger.get("requirements", {})):
        errors.append("ledger requirement set does not match target contract")
    if "score_semantics" not in ledger:
        errors.append("missing score semantics")
    return {"status":"VALID" if not errors else "INVALID","errors":errors,"records":len(ids)}

def target_check(target: dict[str, Any], as_of: str | None = None) -> dict[str, Any]:
    validate_target(target)
    as_of_day = parse_day(as_of) or datetime.now(timezone.utc).date()
    snap = parse_day(target.get("snapshot_date"))
    max_age = int(target.get("freshness", {}).get("max_target_age_days", 14))
    age = (as_of_day - snap).days if snap else None
    freshness = "UNKNOWN_DATE" if age is None else ("FRESH" if age <= max_age else "STALE")
    return {
        "status":"VALID" if freshness != "STALE" else "STALE",
        "snapshot_date":target.get("snapshot_date"),
        "age_days":age,
        "freshness":freshness,
        "market_sources":len(target.get("market_sources", [])),
        "role_tracks":list(target.get("role_tracks", {})),
        "requirements":len(target_requirements(target))
    }

def project(target: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    visible = [
        r for r in ledger["records"]
        if r["public_safe"] and r["state"] in {"VERIFIED","SUPPORTED"}
        and r["proof_strength"] >= 0.45 and r["freshness_state"] != "STALE"
    ]
    ranked = sorted(visible, key=lambda r: (-r["proof_strength"], -r["hiring_signal"], r["source_id"]))
    order = ["tower-of-babel","spacex-autonomy","job-application","xai-colossus-cooling","mission-thread-quorum","computer-user"]
    by_source = {p["source_id"]:p for p in ledger["projects"]}
    projects = [by_source[s] for s in order if s in by_source and by_source[s].get("public_safe", True)]
    skills = [
        "Forward-Deployed Engineering","AI Systems Architecture","Agentic AI","Multi-Agent Systems",
        "AI Orchestration","Applied Artificial Intelligence","AI Infrastructure","Distributed Systems",
        "System Design","Large Language Model (LLM) Applications","Python","Systems Integration",
        "AI Evaluation","Reliability Engineering","Model Context Protocol (MCP)","Workflow Automation",
        "Human-in-the-Loop Systems","Observability","API Integration"
    ]
    gaps = [
        {"requirement_id":g["requirement_id"],"label":g["label"],"status":g["status"],
         "priority":g["priority"],"hard_gate":g["hard_gate"]}
        for g in ledger.get("gap_queue", [])
    ]
    return {
        "schema_version":2,
        "backbone_version":BACKBONE_VERSION,
        "identity":target["identity"],
        "headline":"Forward Deployed AI Architect | AI Systems Architecture, Agent Infrastructure & Orchestration | Reliable Applied AI",
        "proof_architecture":["architecture","orchestration substrate","applied systems","evidence/release control","bounded consequential systems"],
        "featured_projects":projects,
        "skills":skills,
        "proof_points":[
            {"evidence_id":r["evidence_id"],"claim":r["claim"],"source_id":r["source_id"],"proof_strength":r["proof_strength"]}
            for r in ranked[:12]
        ],
        "metrics":[m for m in ledger.get("metrics", []) if m.get("state") in {"VERIFIED","SUPPORTED"} and m.get("freshness_state") != "STALE"],
        "gap_queue":gaps,
        "evidence_coverage_score":ledger["summary"]["evidence_coverage_score"],
        "score_semantics":ledger["score_semantics"],
        "projection_rule":"Only VERIFIED or SUPPORTED, public-safe, sufficiently strong, non-stale evidence may populate outward LinkedIn proof claims. Private, CANDIDATE, UNVERIFIED, BLOCKED, weak, or stale evidence remains internal."
    }

def markdown(p: dict[str, Any]) -> str:
    lines = [
        "# LinkedIn Evidence Backbone v2","",
        f"**Identity:** {p['identity']}","",
        f"**Headline:** {p['headline']}","",
        f"**Evidence coverage score:** {p['evidence_coverage_score']} / 100  ",
        f"_{p['score_semantics']}_","",
        "## Proof architecture","",
        " → ".join(p["proof_architecture"]),"",
        "## Featured / Projects order",""
    ]
    for i,x in enumerate(p["featured_projects"],1):
        lines += [f"{i}. **{x['name']}** — {x['summary']}  ", f"   Evidence: `{x['source_id']}` · `{x['state']}` · {x['url']}"]
    lines += ["","## Highest-signal public proof",""]
    for x in p["proof_points"]:
        lines.append(f"- `{x['evidence_id']}` [{x['proof_strength']:.2f}] **{x['source_id']}** — {x['claim']}")
    lines += ["","## Defensible metrics",""]
    for x in p["metrics"]:
        lines.append(f"- **{x['name']} = {x['value']}** — {x.get('scope','')} (`{x['source_id']}`)")
    lines += ["","## Ranked proof gaps",""]
    for x in p["gap_queue"]:
        lines.append(f"- **{x['label']}** — {x['status']} · priority `{x['priority']}`" + (" · HARD GATE" if x["hard_gate"] else ""))
    lines += ["","## Skill ontology","", " • ".join(p["skills"]),"","## Publication law","",p["projection_rule"],""]
    return "\n".join(lines)

def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--target", type=Path, required=True)
    b.add_argument("--sources", type=Path, required=True)
    b.add_argument("--output", type=Path, required=True)
    b.add_argument("--as-of")
    v = sub.add_parser("verify")
    v.add_argument("--target", type=Path, required=True)
    v.add_argument("--ledger", type=Path, required=True)
    t = sub.add_parser("target-check")
    t.add_argument("--target", type=Path, required=True)
    t.add_argument("--as-of")
    q = sub.add_parser("project")
    q.add_argument("--target", type=Path, required=True)
    q.add_argument("--ledger", type=Path, required=True)
    q.add_argument("--output", type=Path, required=True)
    q.add_argument("--markdown", type=Path)

    a = p.parse_args()
    if a.cmd == "build":
        dump(a.output, build(load(a.target), load(a.sources), a.as_of))
        return 0
    if a.cmd == "verify":
        result = verify(load(a.target), load(a.ledger))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "VALID" else 2
    if a.cmd == "target-check":
        result = target_check(load(a.target), a.as_of)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] != "STALE" else 3
    target, ledger = load(a.target), load(a.ledger)
    result = project(target, ledger)
    dump(a.output, result)
    if a.markdown:
        a.markdown.parent.mkdir(parents=True, exist_ok=True)
        a.markdown.write_text(markdown(result), encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
