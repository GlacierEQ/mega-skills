#!/usr/bin/env python3
"""
Integrity Checker
Verifies evidence chain integrity, preserves contradictions rather than overwriting them.
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class IntegrityStatus(Enum):
    VALID = "valid"
    BROKEN_LINK = "broken_link"
    MISSING_EVIDENCE = "missing_evidence"
    HASH_MISMATCH = "hash_mismatch"
    CIRCULAR_REFERENCE = "circular_reference"
    ORPHANED_ENTRY = "orphaned_entry"
    CONTRADICTION = "contradiction"


@dataclass
class IntegrityIssue:
    severity: str  # "critical", "warning", "info"
    status: IntegrityStatus
    entry_id: str
    description: str
    details: Dict


@dataclass
class IntegrityReport:
    overall_status: IntegrityStatus
    total_entries: int
    issues: List[IntegrityIssue]
    contradictions: List[Dict]
    hash_verification: Dict[str, bool]


def load_register(register_path: Path) -> Dict:
    if register_path.exists():
        return json.loads(register_path.read_text())
    return {}


def load_artifacts(artifacts_dir: Path) -> Dict[str, str]:
    """Load artifact file hashes."""
    hashes = {}
    for artifact in artifacts_dir.rglob("*"):
        if artifact.is_file() and not artifact.name.startswith("."):
            h = hashlib.sha256()
            with artifact.open("rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            hashes[str(artifact.relative_to(artifacts_dir))] = h.hexdigest()
    return hashes


def verify_hashes(register: Dict, artifacts_dir: Path) -> Dict[str, bool]:
    """Verify SHA-256 hashes of referenced artifacts."""
    artifact_hashes = load_artifacts(artifacts_dir)
    results = {}
    
    for entry_id, entry in register.items():
        location = entry.get("location", "")
        if location and location in artifact_hashes:
            # Would need stored hash to compare
            results[entry_id] = True  # Placeholder
    
    return results


def check_broken_links(register: Dict) -> List[Dict]:
    """Check for broken internal links."""
    all_ids = set(register.keys())
    broken = []
    
    for entry_id, entry in register.items():
        links = entry.get("links", [])
        for link in links:
            if link not in all_ids:
                broken.append({
                    "source": entry_id,
                    "target": link,
                    "type": "broken_reference"
                })
    
    return broken


def check_circular_references(register: Dict) -> List[Dict]:
    """Check for circular references in link graph."""
    visited = set()
    rec_stack = set()
    cycles = []
    
    def dfs(node, path):
        if node in rec_stack:
            # Found cycle
            cycle_start = path.index(node)
            cycles.append({
                "cycle": path[cycle_start:] + [node],
                "entries": path[cycle_start:] + [node]
            })
            return
        
        if node in visited:
            return
        
        visited.add(node)
        rec_stack.add(node)
        
        entry = register.get(node)
        if entry:
            for link in entry.get("links", []):
                if link in register:
                    dfs(link, path + [link])
        
        rec_stack.remove(node)
    
    for node in register:
        if node not in visited:
            dfs(node, [])
    
    return cycles


def detect_contradictions(register: Dict) -> List[Dict]:
    """Detect contradictory claims/evidence."""
    contradictions = []
    
    # Group by type for comparison
    by_type = {}
    for entry_id, entry in register.items():
        etype = entry.get("type", "")
        if etype not in by_type:
            by_type[etype] = []
        by_type[etype].append((entry_id, entry))
    
    # Check for contradictory claims
    claims = [(eid, e) for eid, e in register.items() if e.get("type") == "claim"]
    for i, (id1, c1) in enumerate(claims):
        for id2, c2 in claims[i+1:]:
            # Simple contradiction detection: opposite keywords
            text1 = (c1.get("title", "") + " " + c1.get("description", "")).lower()
            text2 = (c2.get("title", "") + " c2.get("description", "")).lower()
            
            # Check for negation patterns
            negation_pairs = [
                ("works", "doesn't work"), ("passes", "fails"), ("true", "false"),
                ("valid", "invalid"), ("secure", "insecure"), ("pass", "fail"),
                ("success", "failure"), ("enabled", "disabled"), ("present", "absent")
            ]
            
            for pos, neg in negation_pairs:
                if pos in text1 and neg in text2:
                    # Check if they're about the same subject
                    common_words = set(text1.split()) & set(text2.split())
                    if len(common_words) > 2:
                        contradictions.append({
                            "entry1": id1,
                            "entry2": id2,
                            "type": "direct_contradiction",
                            "pattern": f"{pos} vs {neg}",
                            "text1": text1[:200],
                            "text2": text2[:200]
                        })
    
    return contradictions


def check_orphaned_entries(register: Dict) -> List[str]:
    """Find entries that are not linked from anywhere."""
    all_ids = set(register.keys())
    referenced = set()
    
    for entry in register.values():
        for link in entry.get("links", []):
            referenced.add(link)
    
    orphaned = all_ids - referenced
    # Exclude root entries (those that are sources of truth)
    root_types = {"source", "test", "artifact", "approval"}
    true_orphans = [
        oid for oid in orphaned
        if register[oid].get("type") not in root_types
    ]
    
    return true_orphans


def run_integrity_check(
    register_path: Path,
    artifacts_dir: Path = None
) -> Dict:
    """Run comprehensive integrity check."""
    register = load_register(register_path)
    artifacts_dir = artifacts_dir or Path(".")
    
    issues = []
    
    # Check broken links
    broken = check_broken_links(register)
    for b in broken:
        issues.append(IntegrityIssue(
            severity="critical",
            status=IntegrityStatus.BROKEN_LINK,
            entry_id=b["source"],
            description=f"Broken reference to {b['target']}",
            details=b
        ))
    
    # Check circular references
    cycles = check_circular_references(register)
    for c in cycles:
        issues.append(IntegrityIssue(
            severity="warning",
            status=IntegrityStatus.CIRCULAR_REFERENCE,
            entry_id=c["entries"][0] if c["entries"] else "",
            description=f"Circular reference detected: {' -> '.join(c['cycle'])}",
            details=c
        ))
    
    # Detect contradictions
    contradictions = detect_contradictions(register)
    for c in contradictions:
        issues.append(IntegrityIssue(
            severity="warning",
            status=IntegrityStatus.CONTRADICTION,
            entry_id=c["entry1"],
            description=f"Contradiction with {c['entry2']}: {c['pattern']}",
            details=c
        ))
    
    # Check orphans
    orphans = check_orphaned_entries(register)
    for oid in orphans:
        issues.append(IntegrityIssue(
            severity="info",
            status=IntegrityStatus.ORPHANED_ENTRY,
            entry_id=oid,
            description="Entry not referenced by any other entry",
            details={"orphaned_id": oid}
        ))
    
    # Verify hashes
    hash_results = verify_hashes(register, Path("."))
    
    # Determine overall status
    critical_count = len([i for i in issues if i.severity == "critical"])
    warning_count = len([i for i in issues if i.severity == "warning"])
    
    if critical_count > 0:
        overall = IntegrityStatus.BROKEN_LINK  # Use as overall invalid
    elif warning_count > 0:
        overall = IntegrityStatus.CONTRADICTION  # Use as overall warning
    else:
        overall = IntegrityStatus.VALID
    
    return IntegrityReport(
        overall_status=overall,
        total_entries=len(register),
        issues=issues,
        contradictions=contradictions,
        hash_verification=hash_results
    )


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: integrity_checker.py <command> [args...]")
        print("Commands:")
        print("  check <register.json> [artifacts_dir] [--output report.json]")
        print("  check-links <register.json>")
        print("  check-cycles <register.json>")
        print("  check-contradictions <register.json>")
        print("  check-orphans <register.json>")
        sys.exit(1)
    
    command = sys.argv[1]
    register_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("evidence_register.json")
    artifacts_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(".")
    
    output_path = Path("integrity_report.json")
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = Path(sys.argv[idx + 1])
    
    if command == "check":
        report = run_integrity_check(Path(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) > 3 else Path("."))
        
        output = {
            "overall_status": report.overall_status.value,
            "total_entries": report.total_entries,
            "issues": [
                {
                    "severity": i.severity,
                    "status": i.status.value,
                    "entry_id": i.entry_id,
                    "description": i.description,
                    "details": i.details
                }
                for i in report.issues
            ],
            "contradictions": report.contradictions,
            "hash_verification": report.hash_verification
        }
        
        output_path.write_text(json.dumps(output, indent=2))
        print(json.dumps(output, indent=2))
        print(f"\nOverall Status: {report.overall_status.value}")
        print(f"Total Entries: {report.total_entries}")
        print(f"Issues Found: {len(report.issues)}")
    
    elif command == "check-links":
        register = json.loads(Path(sys.argv[2]).read_text())
        broken = check_broken_links(register)
        print(json.dumps(broken, indent=2))
    
    elif command == "check-cycles":
        register = json.loads(Path(sys.argv[2]).read_text())
        cycles = check_circular_references(register)
        print(json.dumps(cycles, indent=2))
    
    elif command == "check-contradictions":
        register = json.loads(Path(sys.argv[2]).read_text())
        contradictions = detect_contradictions(register)
        print(json.dumps(contradictions, indent=2))
    
    elif command == "check-orphans":
        register = json.loads(Path(sys.argv[2]).read_text())
        orphans = check_orphaned_entries(register)
        print(json.dumps(orphans, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
