#!/usr/bin/env python3
"""
Preflight Emitter
Produces RESOURCE_PREFLIGHT.md with prerequisite table, status, evidence, owner, fallback, result.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class PreflightEntry:
    prerequisite_id: str
    name: str
    type: str
    expected_version: str
    required: bool
    verification_method: str
    status: str
    evidence: str
    owner: str
    fallback: str
    result: str  # "ready", "conditional", "blocked"


def generate_preflight_report(
    inventory_file: Path,
    availability_file: Path,
    classifications_file: Path,
    fallbacks_file: Path,
    output_path: Path
):
    """Generate RESOURCE_PREFLIGHT.md report."""
    
    inventory = json.loads(inventory_file.read_text()) if inventory_file.exists() else {"prerequisites": []}
    availability = json.loads(availability_file.read_text()) if availability_file.exists() else {"results": []}
    classifications = json.loads(classifications_file.read_text()) if classifications_file.exists() else {"classifications": []}
    fallbacks = json.loads(fallbacks_file.read_text()) if fallbacks_file.exists() else {"fallbacks": []}
    
    # Build lookup maps
    avail_map = {r["prerequisite_id"]: r for r in availability.get("results", [])}
    class_map = {c["prerequisite_id"]: c for c in classifications.get("classifications", [])}
    fallback_map = {}
    for fb in json.loads(fallbacks_file.read_text()).get("fallbacks", []) if fallbacks_file.exists() else []:
        pid = fb.get("prerequisite_id", "unknown")
        if pid not in fallback_map:
            fallback_map[pid] = []
        fallback_map[pid].append(fb)
    
    entries = []
    for prereq in inventory.get("prerequisites", []):
        pid = prereq.get("id", prereq.get("name", "unknown"))
        
        avail = avail_map.get(pid, {})
        classif = class_map.get(pid, {})
        fb_list = fallback_map.get(pid, [])
        
        status = avail.get("status", "missing")
        classification = classif.get("classification", status)
        fallback_desc = "; ".join([f["description"] for f in fb_list]) if fb_list else "None"
        
        # Determine result
        if status == "verified":
            result = "ready"
        elif status == "missing" and not prereq.get("required", True):
            result = "conditional"
        elif status in ["missing", "incompatible", "restricted", "expired"]:
            result = "blocked"
        else:
            result = "conditional"
        
        entries.append(PreflightEntry(
            prerequisite_id=pid,
            name=prereq.get("name", pid),
            type=prereq.get("type", "tool"),
            expected_version=prereq.get("expected_version", "any"),
            required=prereq.get("required", True),
            verification_method=prereq.get("verification_method", "command_exists"),
            status=status,
            evidence=avail.get("evidence", avail.get("error", "No evidence")),
            owner=prereq.get("owner", "dev"),
            fallback=fallback_desc,
            result=result
        ))
    
    # Generate markdown
    md = f"""# Resource Preflight Report

**Generated:** {datetime.now().isoformat()}
**Total Prerequisites:** {len(entries)}
**Ready:** {len([e for e in entries if e.result == 'ready'])}
**Conditional:** {len([e for e in entries if e.result == 'conditional'])}
**Blocked:** {len([e for e in entries if e.result == 'blocked'])}

---

## Prerequisite Table

| ID | Name | Type | Required | Expected | Method | Status | Evidence | Owner | Fallback | Result |
|---|---|---|---|---|---|---|---|---|---|---|
"""
    
    for e in entries:
        md += f"| {e.prerequisite_id} | {e.name} | {e.type} | {str(e.required).lower()} | {e.expected_version} | {e.verification_method} | {e.status} | {e.evidence[:50]} | {e.owner} | {e.fallback[:50]} | {e.result} |\n"
    
    md += f"""

---

## Detailed Evidence

"""
    for e in entries:
        avail = avail_map.get(e.prerequisite_id, {})
        md += f"### {e.prerequisite_id}\n\n"
        md += f"- **Name:** {e.name}\n"
        md += f"- **Type:** {e.type}\n"
        md += f"- **Required:** {e.required}\n"
        md += f"- **Expected Version:** {e.expected_version}\n"
        md += f"- **Verification Method:** {e.verification_method}\n"
        md += f"- **Status:** {e.status}\n"
        md += f"- **Evidence:** {e.evidence}\n"
        md += f"- **Owner:** {e.owner}\n"
        md += f"- **Fallback:** {e.fallback}\n"
        md += f"- **Result:** {e.result}\n\n"
    
    md += f"""

---

## Summary

- **Total Prerequisites:** {len(entries)}
- **Ready:** {len([e for e in entries if e.result == 'ready'])}
- **Conditional:** {len([e for e in entries if e.result == 'conditional'])}
- **Blocked:** {len([e for e in entries if e.result == 'blocked'])}

## Recommendations

"""
    
    blocked = [e for e in entries if e.result == "blocked"]
    if blocked:
        md += "### Blocked Prerequisites (Action Required)\n\n"
        for e in blocked:
            md += f"- **{e.prerequisite_id}** ({e.name}): {e.evidence}\n"
            if e.fallback != "None":
                md += f"  - **Fallback:** {e.fallback}\n"
            md += "\n"
    else:
        md += "All prerequisites satisfied. Ready to proceed.\n"
    
    # Write output
    output_path = Path("RESOURCE_PREFLIGHT.md")
    output_path.write_text(md)
    print(f"RESOURCE_PREFLIGHT.md written to {output_path}")


def main():
    import sys
    from datetime import datetime
    
    if len(sys.argv) < 5:
        print("Usage: preflight_emitter.py <inventory.json> <availability.json> <classifications.json> <fallbacks.json> [--output RESOURCE_PREFLIGHT.md]")
        sys.exit(1)
    
    inventory_file = Path(sys.argv[1])
    availability_file = Path(sys.argv[2])
    classifications_file = Path(sys.argv[3])
    fallbacks_file = Path(sys.argv[4])
    
    output_path = Path("RESOURCE_PREFLIGHT.md")
    i = 5
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = Path(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    generate_preflight_report(
        Path(sys.argv[1]),
        Path(sys.argv[2]),
        Path(sys.argv[3]),
        Path(sys.argv[4]),
        output_path
    )


if __name__ == "__main__":
    main()
