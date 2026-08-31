#!/usr/bin/env python3
"""Chunk Power: Sequential Thinking & Dynamic Cognitive Chunking Engine."""

import json
import sys
import hashlib
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any
from pathlib import Path


@dataclass
class ThoughtStep:
    thought_number: int
    total_thoughts_estimate: int
    thought: str
    is_revision: bool = False
    revises_thought: Optional[int] = None
    branch_id: str = "main"
    branch_from_thought: Optional[int] = None
    confidence: float = 0.8
    epistemic_tier: str = "L2_Behavior"
    next_action: str = ""
    evidence_hashes: List[str] = field(default_factory=list)


class SequentialThinkingEngine:
    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self.history: List[ThoughtStep] = []
        self.branches: Dict[str, List[int]] = {"main": []}

    def add_thought(
        self,
        thought: str,
        total_thoughts_estimate: int = 5,
        is_revision: bool = False,
        revises_thought: Optional[int] = None,
        branch_id: str = "main",
        branch_from_thought: Optional[int] = None,
        confidence: float = 0.8,
        epistemic_tier: str = "L2_Behavior",
        next_action: str = "",
        evidence_data: Optional[str] = None
    ) -> ThoughtStep:
        thought_num = len(self.history) + 1
        evidence_hashes = []
        if evidence_data:
            digest = hashlib.sha256(evidence_data.encode("utf-8")).hexdigest()
            evidence_hashes.append(digest)

        step = ThoughtStep(
            thought_number=thought_num,
            total_thoughts_estimate=max(total_thoughts_estimate, thought_num),
            thought=thought,
            is_revision=is_revision,
            revises_thought=revises_thought,
            branch_id=branch_id,
            branch_from_thought=branch_from_thought,
            confidence=max(0.0, min(1.0, confidence)),
            epistemic_tier=epistemic_tier,
            next_action=next_action,
            evidence_hashes=evidence_hashes
        )
        self.history.append(step)
        if branch_id not in self.branches:
            self.branches[branch_id] = []
        self.branches[branch_id].append(thought_num)
        return step

    def synthesize(self) -> Dict[str, Any]:
        if not self.history:
            return {"status": "empty", "synthesis": "No thoughts recorded."}
        
        avg_confidence = sum(s.confidence for s in self.history) / len(self.history)
        revisions_count = sum(1 for s in self.history if s.is_revision)
        
        summary = {
            "session_id": self.session_id,
            "status": "synthesized",
            "total_steps": len(self.history),
            "revisions_count": revisions_count,
            "active_branches": list(self.branches.keys()),
            "average_confidence": round(avg_confidence, 3),
            "final_tier": self.history[-1].epistemic_tier,
            "final_action": self.history[-1].next_action,
            "provenance_hash": hashlib.sha256(
                json.dumps([asdict(s) for s in self.history], sort_keys=True).encode("utf-8")
            ).hexdigest()
        }
        return summary

    def export_json(self) -> str:
        return json.dumps({
            "session_id": self.session_id,
            "thoughts": [asdict(s) for s in self.history],
            "synthesis": self.synthesize()
        }, indent=2)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        engine = SequentialThinkingEngine("demo-session")
        engine.add_thought("Analyze problem domain and input constraints.", 3, confidence=0.9, next_action="Decompose architecture")
        engine.add_thought("Evaluate edge cases and boundary failures.", 3, confidence=0.85, next_action="Verify test harness")
        engine.add_thought("Synthesize verified execution plan.", 3, confidence=0.98, epistemic_tier="L3_ColossalBackend", next_action="Execute with L2 proof")
        print(engine.export_json())
        return 0

    print(json.dumps({
        "skill": "chunk-power",
        "status": "ready",
        "epistemic_tier": "L2",
        "firewall_active": True,
        "mode": "sequential_thinking_dynamic_chunking"
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
