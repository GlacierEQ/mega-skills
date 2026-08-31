#!/usr/bin/env python3
"""Deterministic integration simulation for the autonomous engineering pipeline."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from typing import Dict, List

STAGES = [
    "frame", "inspect", "architecture", "plan", "implement", "test",
    "security", "performance", "integrate", "tower", "quality_gate",
    "review", "approval", "release", "observe",
]
ROUTES = {
    "happy": ["architecture", "implement", "test", "security", "performance", "quality_gate", "review", "approval", "release"],
    "security-block": ["architecture", "implement", "test", "security", "quality_gate", "review", "approval", "release"],
    "approval-required": ["architecture", "implement", "test", "security", "performance", "quality_gate", "review", "approval", "release"],
    "tower-route": ["architecture", "implement", "test", "security", "performance", "tower", "quality_gate", "review", "approval", "release"],
    "handoff-recovery": ["architecture", "implement", "test", "security", "performance", "quality_gate", "review", "approval", "release"],
}
TOWER_ORDER = ["preflight", "source_of_truth", "exhibits_proof", "validate", "generate", "tests", "build", "integrity", "receipt"]

@dataclass
class Handoff:
    sender: str
    receiver: str
    artifact: str
    acceptance: str
    status: str = "VERIFIED"
    failure_route: str = ""

@dataclass
class Simulation:
    scenario: str
    mission_id: str = "SIM-AUTONOMOUS-SE-001"
    state: str = "READY"
    current_stage: str = "frame"
    events: List[Dict[str, str]] = field(default_factory=list)
    handoffs: List[Handoff] = field(default_factory=list)
    evidence: Dict[str, str] = field(default_factory=dict)
    blocked_reason: str = ""
    approval_requested: bool = False
    approval_granted: bool = False
    recovered: bool = False

    def event(self, kind: str, detail: str, status: str = "VERIFIED") -> None:
        self.events.append({"kind": kind, "detail": detail, "status": status})

    def transition(self, stage: str) -> None:
        if stage not in STAGES:
            raise ValueError(f"unknown stage: {stage}")
        self.current_stage = stage
        self.state = "ACTIVE"
        self.event("stage", stage)

    def handoff(self, sender: str, receiver: str, artifact: str, acceptance: str, fail: bool = False) -> None:
        h = Handoff(sender, receiver, artifact, acceptance, "BLOCKED" if fail else "VERIFIED", "retry from sender" if fail else "")
        self.handoffs.append(h)
        self.event("handoff", f"{sender} -> {receiver}: {artifact}", h.status)
        if fail:
            self.state = "BLOCKED"
            self.blocked_reason = f"handoff acceptance failed: {artifact}"
            self.event("gate", self.blocked_reason, "BLOCKED")
            raise RuntimeError(self.blocked_reason)

    def run(self) -> Dict[str, object]:
        self.event("mission", self.mission_id)
        for stage in ["frame", "inspect"]:
            self.transition(stage)
        self.evidence["scope"] = "authorized repository; bounded source changes"
        self.evidence["baseline"] = "clean baseline recorded"
        for stage in ROUTES[self.scenario]:
            try:
                self.transition(stage)
                if stage == "architecture":
                    self.evidence["architecture"] = "typed graph; zero unapproved cycles"
                    self.handoff("autonomous-software-engineering", "automated-architecture-analysis", "architecture-plan.json", "graph and boundary policy verified")
                elif stage == "implement":
                    self.evidence["implementation"] = "bounded patch planned"
                    self.handoff("automated-architecture-analysis", "automated-code-refactoring", "architecture-decision.json", "scope and invariants accepted")
                elif stage == "test":
                    self.evidence["tests"] = "focused and full test plan ready"
                    self.handoff("automated-code-refactoring", "automated-test-generation", "implementation-patch.diff", "patch parses and stays in scope")
                elif stage == "security":
                    if self.scenario == "security-block":
                        self.state = "BLOCKED"
                        self.blocked_reason = "critical vulnerability remains unresolved"
                        self.event("security_gate", self.blocked_reason, "BLOCKED")
                        break
                    self.evidence["security"] = "no unresolved release-blocking findings"
                    self.handoff("automated-test-generation", "automated-security-scanning", "test-and-coverage-receipt.json", "security scan scope accepted")
                elif stage == "performance":
                    self.evidence["performance"] = "baseline/post-change protocol reproducible"
                    self.handoff("automated-security-scanning", "automated-performance-profiling", "security-receipt.json", "security gate verified")
                elif stage == "tower":
                    for tower_stage in TOWER_ORDER:
                        self.event("tower", tower_stage)
                    self.evidence["tower"] = "ordered Tower evidence route complete"
                elif stage == "quality_gate":
                    if self.state == "BLOCKED":
                        break
                    self.evidence["quality_gate"] = "architecture, tests, security, performance, and diff checks pass"
                    self.handoff("autonomous-software-engineering", "quality-gate", "engineering-evidence.json", "all required gates verified")
                elif stage == "review":
                    self.evidence["review"] = "human-readable diff and rollback reviewed"
                elif stage == "approval":
                    self.approval_requested = True
                    self.event("approval", "release mutation requires explicit confirmation", "ESCALATED")
                    if self.scenario == "approval-required":
                        self.state = "ESCALATED"
                        self.blocked_reason = "awaiting explicit release approval"
                        break
                    self.approval_granted = True
                    self.event("approval", "release approval granted", "VERIFIED")
                elif stage == "release":
                    if not self.approval_granted:
                        self.state = "ESCALATED"
                        self.blocked_reason = "release attempted without approval"
                        self.event("release", self.blocked_reason, "BLOCKED")
                        break
                    self.evidence["release"] = "atomic commit and publish authorized"
                    self.state = "VERIFIED"
            except RuntimeError:
                break
        if self.scenario == "handoff-recovery" and self.state == "VERIFIED":
            self.recovered = True
            self.event("recovery", "failed handoff retried after bounded correction", "VERIFIED")
        if self.state == "ACTIVE":
            self.state = "VERIFIED" if self.current_stage in {"release", "observe"} else "BLOCKED"
        return {
            "mission_id": self.mission_id,
            "scenario": self.scenario,
            "state": self.state,
            "current_stage": self.current_stage,
            "blocked_reason": self.blocked_reason,
            "approval_requested": self.approval_requested,
            "approval_granted": self.approval_granted,
            "recovered": self.recovered,
            "evidence": self.evidence,
            "handoffs": [asdict(h) for h in self.handoffs],
            "events": self.events,
        }

def run_scenario(name: str) -> Dict[str, object]:
    if name not in ROUTES:
        raise ValueError(f"unknown scenario: {name}")
    sim = Simulation(name)
    if name == "handoff-recovery":
        try:
            sim.handoff("automated-code-refactoring", "automated-test-generation", "implementation-patch.diff", "patch parses and stays in scope", fail=True)
        except RuntimeError:
            sim.state = "ACTIVE"
            sim.blocked_reason = ""
            sim.event("recovery", "retrying from failed handoff with corrected artifact", "ACTIVE")
    return sim.run()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=sorted(ROUTES), default="happy")
    args = parser.parse_args()
    print(json.dumps(run_scenario(args.scenario), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
