#!/usr/bin/env python3
"""
Verifier Coordinator
Coordinates independent verification when creator bias or material consequence affects confidence.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class BiasLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Verifier:
    id: str
    name: str
    expertise: List[str]
    bias_level: BiasLevel
    independent: bool = True


@dataclass
class VerificationAssignment:
    artifact_id: str
    primary_verifier: str
    secondary_verifier: Optional[str] = None
    rationale: str = ""


# Verifier pool
VERIFIER_POOL = [
    Verifier("v1", "Security Auditor", ["security", "crypto", "auth"], BiasLevel.NONE),
    Verifier("v2", "Performance Engineer", ["performance", "latency", "throughput"], BiasLevel.LOW),
    Verifier("v3", "QA Lead", ["testing", "validation", "edge-cases"], BiasLevel.LOW),
    Verifier("v4", "Architect", ["architecture", "scalability", "patterns"], BiasLevel.MEDIUM),
    Verifier("v5", "Compliance Officer", ["compliance", "legal", "policy"], BiasLevel.NONE),
]


def assess_bias(creator_id: str, artifact_type: str, consequence: str) -> BiasLevel:
    """Assess bias level based on creator, artifact type, and consequence."""
    # High consequence + creator involvement = higher bias risk
    if consequence in ["security", "legal", "financial", "safety"]:
        return BiasLevel.HIGH
    elif consequence in ["performance", "data-loss", "downtime"]:
        return BiasLevel.MEDIUM
    return BiasLevel.LOW


def select_verifiers(
    artifact_id: str,
    artifact_type: str,
    creator_id: str,
    consequence: str,
    required_expertise: List[str]
) -> VerificationAssignment:
    """Select independent verifiers based on expertise and bias assessment."""
    
    bias = assess_bias(creator_id, artifact_type, "general")
    
    # Filter verifiers with required expertise and acceptable bias
    candidates = [
        v for v in VERIFIER_POOL
        if v.independent and 
        (not required_expertise or any(e in v.expertise for e in required_expertise)) and
        v.bias_level.value != "high" or bias.value != "high"
    ]
    
    if not candidates:
        # Fallback: use any independent verifier
        candidates = [v for v in VERIFIER_POOL if v.independent]
    
    if not candidates:
        raise ValueError("No independent verifiers available")
    
    # Sort by bias level (prefer lower)
    bias_order = {"none": 0, "low": 1, "medium": 2, "high": 3}
    candidates.sort(key=lambda v: bias_order.get(v.bias_level.value, 3))
    
    primary = candidates[0]
    secondary = candidates[1] if len(candidates) > 1 else None
    
    rationale = f"Selected {primary.name} ({primary.bias_level.value} bias) for {artifact_type} verification. "
    if secondary:
        rationale += f"Secondary: {secondary.name}. "
    rationale += f"Creator bias assessed as {assess_bias(creator_id, artifact_type, consequence).value}."
    
    return VerificationAssignment(
        artifact_id=artifact_id,
        primary_verifier=primary.id,
        secondary_verifier=secondary.id if secondary else None,
        rationale=rationale
    )


def coordinate_verification(
    artifact_path: str,
    criteria: List[Dict],
    creator_id: str,
    artifact_type: str,
    consequence: str
) -> Dict:
    """Coordinate full verification process."""
    
    required_expertise = []
    for c in criteria:
        if "security" in c.get("description", "").lower():
            required_expertise.append("security")
        if "performance" in c.get("description", "").lower():
            required_expertise.append("performance")
    
    assignment = select_verifiers(
        artifact_id=artifact_path,
        artifact_type=artifact_type,
        creator_id=creator_id,
        consequence=consequence,
        required_expertise=required_expertise
    )
    
    return {
        "artifact_id": artifact_path,
        "primary_verifier": assignment.primary_verifier,
        "secondary_verifier": assignment.secondary_verifier,
        "rationale": assignment.rationale,
        "verification_required": True,
        "independent_verification": True
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: verifier_coordinator.py <command> [args...]")
        print("Commands:")
        print("  assign <artifact_id> <creator_id> <type> <consequence> [--expertise e1,e2]")
        print("  pool                    - List verifier pool")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "assign":
        if len(sys.argv) < 6:
            print("Usage: verifier_coordinator.py assign <artifact_id> <creator_id> <type> <consequence> [--expertise e1,e2]")
            sys.exit(1)
        
        artifact_id = sys.argv[2]
        creator_id = sys.argv[3]
        artifact_type = sys.argv[4]
        consequence = sys.argv[5]
        
        expertise = []
        if "--expertise" in sys.argv:
            idx = sys.argv.index("--expertise")
            if idx + 1 < len(sys.argv):
                expertise = sys.argv[idx + 1].split(",")
        
        assignment = select_verifiers(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            creator_id=sys.argv[3],
            consequence=sys.argv[4],
            required_expertise=expertise
        )
        
        print(json.dumps({
            "artifact_id": assignment.artifact_id,
            "primary_verifier": assignment.primary_verifier,
            "secondary_verifier": assignment.secondary_verifier,
            "rationale": assignment.rationale
        }, indent=2))
    
    elif command == "pool":
        print(json.dumps([
            {
                "id": v.id,
                "name": v.name,
                "expertise": v.expertise,
                "bias_level": v.bias_level.value,
                "independent": v.independent
            }
            for v in VERIFIER_POOL
        ], indent=2))
    
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
