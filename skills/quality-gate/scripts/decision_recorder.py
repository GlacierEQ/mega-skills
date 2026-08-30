#!/usr/bin/env python3
"""
Decision Recorder
Records pass/fail/conditional decisions with exception owner, expiry, impact, review trigger.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta


class Decision(Enum):
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"


@dataclass
class GateRecord:
    gate_id: str
    artifact_id: str
    decision: Decision
    timestamp: str
    criteria_met: List[str]
    criteria_failed: List[str]
    exceptions: List[Dict]
    owner: str
    next_action: str
    review_trigger: Optional[str] = None
    expiry: Optional[str] = None
    impact: str = ""
    verifier: str = ""


class DecisionRecorder:
    def __init__(self, record_path: Path):
        self.record_path = Path(record_path)
        self.records = self._load_records()
    
    def _load_records(self) -> List[Dict]:
        if self.record_path.exists():
            return json.loads(self.record_path.read_text())
        return []
    
    def _save_records(self):
        self.record_path.write_text(json.dumps(self.records, indent=2))
    
    def record_decision(
        self,
        gate_id: str,
        artifact_id: str,
        decision: Decision,
        criteria_met: List[str],
        criteria_failed: List[str],
        owner: str,
        next_action: str,
        exceptions: List[Dict] = None,
        review_trigger: str = None,
        expiry_days: int = None,
        impact: str = "",
        verifier: str = ""
    ) -> GateRecord:
        """Record a gate decision."""
        timestamp = datetime.now().isoformat()
        
        expiry = None
        if expiry_days:
            expiry = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        # Conditional pass requires exception details
        if decision == Decision.CONDITIONAL and not exceptions:
            raise ValueError("Conditional pass requires exception details")
        
        record = GateRecord(
            gate_id=gate_id,
            artifact_id=artifact_id,
            decision=decision,
            timestamp=timestamp,
            criteria_met=criteria_met,
            criteria_failed=criteria_failed,
            exceptions=exceptions or [],
            owner=owner,
            next_action=next_action,
            review_trigger=review_trigger,
            expiry=expiry,
            impact=impact,
            verifier=verifier
        )
        
        self.records.append(asdict(record))
        self._save_records()
        return record
    
    def get_record(self, gate_id: str) -> Optional[Dict]:
        for r in self.records:
            if r["gate_id"] == gate_id:
                return r
        return None
    
    def get_recent(self, days: int = 30) -> List[Dict]:
        cutoff = datetime.now() - timedelta(days=days)
        return [
            r for r in self.records
            if datetime.fromisoformat(r["timestamp"]) > cutoff
        ]
    
    def get_by_artifact(self, artifact_id: str) -> List[Dict]:
        return [r for r in self.records if r["artifact_id"] == artifact_id]
    
    def get_pending_reviews(self) -> List[Dict]:
        """Get records with review triggers that have been reached."""
        now = datetime.now()
        pending = []
        for r in self.records:
            if r.get("review_trigger"):
                try:
                    trigger_time = datetime.fromisoformat(r["review_trigger"])
                    if trigger_time <= now:
                        pending.append(r)
                except Exception:
                    pass
        return pending
    
    def get_expired_conditionals(self) -> List[Dict]:
        """Get conditional passes that have expired."""
        now = datetime.now()
        expired = []
        for r in self.records:
            if r["decision"] == "conditional" and r.get("expiry"):
                try:
                    expiry_time = datetime.fromisoformat(r["expiry"])
                    if expiry_time <= now:
                        expired.append(r)
                except Exception:
                    pass
        return expired


def main():
    if len(sys.argv) < 2:
        print("Usage: decision_recorder.py <command> [args...]")
        print("Commands:")
        print("  record <gate_id> <artifact_id> <pass|fail|conditional> <owner> <next_action> [options]")
        print("  get <gate_id>")
        print("  recent [days]")
        print("  by-artifact <artifact_id>")
        print("  pending-reviews")
        print("  expired-conditionals")
        sys.exit(1)
    
    command = sys.argv[1]
    recorder = DecisionRecorder(Path("quality_gates.json"))
    
    if command == "record":
        if len(sys.argv) < 7:
            print("Usage: decision_recorder.py record <gate_id> <artifact_id> <pass|fail|conditional> <owner> <next_action> [--exceptions 'json'] [--review-trigger ISO_DATE] [--expiry-days N] [--impact TEXT] [--verifier ID]")
            sys.exit(1)
        
        gate_id = sys.argv[2]
        artifact_id = sys.argv[3]
        decision_str = sys.argv[4]
        owner = sys.argv[4] if len(sys.argv) > 4 else "unknown"  # Fix: sys.argv[4] is decision
        # Fix indices
        gate_id = sys.argv[2]
        artifact_id = sys.argv[3]
        decision_str = sys.argv[4]
        owner = sys.argv[5]
        next_action = sys.argv[6]
        
        # Fix: correct indices
        gate_id = sys.argv[2]
        artifact_id = sys.argv[3]
        decision_str = sys.argv[4]
        owner = sys.argv[5]
        next_action = sys.argv[6]
        
        exceptions = []
        review_trigger = None
        expiry_days = None
        impact = ""
        verifier = ""
        
        i = 7
        while i < len(sys.argv):
            if sys.argv[i] == "--exceptions" and i + 1 < len(sys.argv):
                exceptions = json.loads(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--review-trigger" and i + 1 < len(sys.argv):
                review_trigger = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--expiry-days" and i + 1 < len(sys.argv):
                expiry_days = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--impact" and i + 1 < len(sys.argv):
                impact = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--verifier" and i + 1 < len(sys.argv):
                verifier = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        decision = Decision(decision_str)
        record = recorder.record_decision(
            gate_id=gate_id,
            artifact_id=artifact_id,
            decision=decision,
            criteria_met=[],  # Would be populated from actual check
            criteria_failed=[],
            owner=owner,
            next_action=next_action,
            exceptions=exceptions,
            review_trigger=review_trigger,
            expiry_days=expiry_days,
            impact=impact,
            verifier=verifier
        )
        
        print(json.dumps(asdict(record), indent=2))
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: decision_recorder.py get <gate_id>")
            sys.exit(1)
        record = recorder.get_record(sys.argv[2])
        if record:
            print(json.dumps(record, indent=2))
        else:
            print(f"Gate {sys.argv[2]} not found")
    
    elif command == "recent":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        records = recorder.get_recent(days)
        print(json.dumps(records, indent=2))
    
    elif command == "by-artifact":
        if len(sys.argv) < 3:
            print("Usage: decision_recorder.py by-artifact <artifact_id>")
            sys.exit(1)
        records = recorder.get_by_artifact(sys.argv[2])
        print(json.dumps(records, indent=2))
    
    elif command == "pending-reviews":
        records = recorder.get_pending_reviews()
        print(json.dumps(records, indent=2))
    
    elif command == "expired-conditionals":
        records = recorder.get_expired_conditionals()
        print(json.dumps(records, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
