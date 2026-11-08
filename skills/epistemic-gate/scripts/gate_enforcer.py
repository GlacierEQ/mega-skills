#!/usr/bin/env python3
"""
Epistemic Gate Enforcer
Denies execution below L2 (local) or L5 (enterprise) with full receipt.
"""

import json
import subprocess
import sys
from pathlib import Path

# Import the tier evaluator
sys.path.insert(0, str(Path(__file__).parent))
from tier_evaluator import evaluate_target, EpistemicTier, VerificationResult


def enforce_gate(target: Path, context: str = "local") -> VerificationResult:
    """
    Enforce epistemic gate.
    context: "local" -> requires L2, "enterprise" -> requires L5
    """
    required = EpistemicTier.L2_BEHAVIOR if context == "local" else EpistemicTier.L5_SWARM
    return evaluate_target(target, required)


def main():
    if len(sys.argv) < 2:
        print("Usage: gate_enforcer.py <target> [--context local|enterprise] [--fail-hard]")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    context = "local"
    fail_hard = False
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--context" and i + 1 < len(sys.argv):
            context = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--fail-hard":
            fail_hard = True
            i += 1
        else:
            i += 1
    
    result = enforce_gate(target, context)
    
    # Print summary
    print(f"Target: {target}")
    print(f"Context: {context} (requires {('L2' if context=='local' else 'L5')})")
    print(f"Achieved: {result.tier.name}")
    print(f"Authorized: {result.authorized}")
    print(f"Forbidden patterns: {len(result.forbidden_patterns)}")
    print(f"Gaps: {len(result.gaps)}")
    
    if result.forbidden_patterns:
        print("\nFORBIDDEN PATTERNS:")
        for fp in result.forbidden_patterns:
            print(f"  {fp}")
    
    if result.gaps:
        print("\nGAPS:")
        for gap in result.gaps:
            print(f"  {gap}")
    
    # Exit code
    if not result.authorized:
        print(f"\n❌ GATE DENIED: {target} does not meet {context} requirements")
        if fail_hard:
            sys.exit(1)
    else:
        print(f"\n✅ GATE PASSED: {target} authorized for {context} execution")
        sys.exit(0)


if __name__ == "__main__":
    main()
