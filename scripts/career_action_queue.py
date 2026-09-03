#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

PACKETS = {
    "production_llm_delivery": "missions/anthropic-applied-ai/work-packets/production-llm-delivery.json",
    "customer_discovery": "missions/anthropic-applied-ai/work-packets/customer-discovery.json",
    "deployment_adoption": "missions/anthropic-applied-ai/work-packets/deployment-adoption.json",
}

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def dump(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def build(ledger, activation):
    queue = []

    for gap in ledger.get("gap_queue", []):
        rid = gap["requirement_id"]
        queue.append({
            "id": f"evidence-retrieval:{rid}",
            "owner": "system",
            "type": "evidence_retrieval",
            "status": "READY",
            "priority": round(100 * gap["priority"], 1),
            "requirement_id": rid,
            "instruction": (
                f"Search existing repositories, receipts, deployment records, Helix artifacts, "
                f"and verified project history for stronger evidence of: {gap['label']}. "
                "Preserve source lineage; never promote examples, forks, market intelligence, "
                "candidate narrative, or unexecuted code into proof."
            ),
            "completion": (
                "A stronger typed evidence source is added and the ledger is regenerated, "
                "or retrieval is explicitly exhausted with NO_QUALIFYING_EVIDENCE."
            ),
        })
        queue.append({
            "id": f"proof-build:{rid}",
            "owner": "system",
            "type": "proof_build",
            "status": "BLOCKED_ON_RETRIEVAL",
            "priority": round(90 * gap["priority"], 1),
            "requirement_id": rid,
            "work_packet": PACKETS.get(
                rid,
                f"missions/anthropic-applied-ai/work-packets/{rid.replace('_', '-')}.json",
            ),
            "instruction": f"Only after retrieval is exhausted, execute the bounded proof packet for {gap['label']}.",
            "completion": (
                "Executable or externally observed proof, its receipt, and a public-safe artifact "
                "are ingested into evidence-sources.json."
            ),
        })

    recommendations = activation.get("recommendations", {})
    if recommendations.get("status") != "COMPLETE":
        queue.append({
            "id": "linkedin:recommendations",
            "owner": "operator",
            "type": "linkedin_manual",
            "status": recommendations.get("status", "OPERATOR_ACTION_REQUIRED"),
            "priority": 72,
            "instruction": (
                f"Request up to {recommendations.get('target_count', 5)} real recommendations "
                f"covering distinct firsthand dimensions: {', '.join(recommendations.get('dimensions', []))}."
            ),
            "completion": "Visible recommendations exist or each request is explicitly unavailable/declined.",
        })

    otw = activation.get("open_to_work", {})
    if not otw.get("locations") or not otw.get("workplace_types") or not otw.get("employment_types"):
        queue.append({
            "id": "linkedin:open-to-work-preferences",
            "owner": "operator",
            "type": "linkedin_manual",
            "status": "NEEDS_INPUT",
            "priority": 68,
            "instruction": "Set actual location, workplace-type, and employment-type preferences. Do not infer them.",
            "completion": "Locations, workplace types, and employment types are explicitly populated.",
        })

    identity = activation.get("identity_verification", {})
    if identity.get("status") != "COMPLETE":
        queue.append({
            "id": "linkedin:identity-verification",
            "owner": "operator",
            "type": "linkedin_manual",
            "status": identity.get("status", "OPERATOR_ACTION_REQUIRED"),
            "priority": 55,
            "instruction": "Complete LinkedIn identity verification if eligible and desired.",
            "completion": "Status becomes COMPLETE, UNAVAILABLE, or DECLINED.",
        })

    for key, state in activation.get("manual_profile_checks", {}).items():
        if state not in {"VERIFIED", "COMPLETE"}:
            queue.append({
                "id": f"linkedin:verify-{key.replace('_', '-')}",
                "owner": "operator",
                "type": "linkedin_manual",
                "status": state,
                "priority": 48,
                "instruction": f"Inspect and verify LinkedIn {key.replace('_', ' ')} against the current career positioning.",
                "completion": f"{key} is VERIFIED, COMPLETE, or intentionally deferred.",
            })

    post_number = 1
    for topic in activation.get("technical_activity", {}).get("topics", []):
        if topic.get("publication_state") == "READY":
            queue.append({
                "id": f"linkedin:technical-post:{post_number}",
                "owner": "operator",
                "type": "linkedin_content",
                "status": "READY",
                "priority": 40 - ((post_number - 1) * 2),
                "instruction": f"Publish an evidence-linked technical post: {topic['topic']}",
                "evidence_source": topic.get("evidence_source"),
                "completion": "Post is published with its evidence boundary intact.",
            })
            post_number += 1

    queue.sort(key=lambda item: (-float(item["priority"]), item["id"]))
    return {
        "schema_version": 2,
        "generated_from": {
            "ledger_backbone_version": ledger.get("backbone_version"),
            "ledger_as_of": ledger.get("as_of"),
            "evidence_coverage_score": ledger.get("summary", {}).get("evidence_coverage_score"),
            "open_hard_gates": ledger.get("summary", {}).get("hard_gates_open"),
        },
        "queue": queue,
        "summary": {
            "total": len(queue),
            "system": sum(item["owner"] == "system" for item in queue),
            "operator": sum(item["owner"] == "operator" for item in queue),
            "ready": sum(item["status"] == "READY" for item in queue),
            "blocked_on_retrieval": sum(item["status"] == "BLOCKED_ON_RETRIEVAL" for item in queue),
        },
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dump(args.output, build(load(args.ledger), load(args.activation)))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
