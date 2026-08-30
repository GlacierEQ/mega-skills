#!/usr/bin/env python3
"""
Criteria Reader
Reads acceptance criteria, artifact contract, evidence register, and risk boundaries.
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AcceptanceCriteria:
    id: str
    description: str
    measurable: bool
    verification_method: str
    required: bool = True


@dataclass
class ArtifactContract:
    name: str
    format: str
    location: str
    required_fields: List[str]
    quality_thresholds: Dict


@dataclass
class RiskBoundary:
    id: str
    description: str
    severity: str
    mitigation: str
    owner: str


def read_acceptance_criteria(file_path: Path) -> List[AcceptanceCriteria]:
    """Read acceptance criteria from markdown or JSON."""
    if file_path.suffix in [".md", ".markdown"]:
        return parse_markdown_criteria(file_path)
    elif file_path.suffix == ".json":
        return parse_json_criteria(file_path)
    else:
        return []


def parse_markdown_criteria(file_path: Path) -> List[AcceptanceCriteria]:
    """Parse acceptance criteria from markdown file."""
    content = file_path.read_text()
    criteria = []
    
    # Look for criteria in tables or lists
    lines = content.split('\n')
    in_table = False
    for i, line in enumerate(lines):
        if "|" in line and "description" in line.lower() and "criteria" in line.lower():
            in_table = True
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 2:
                criteria.append(AcceptanceCriteria(
                    id=f"AC-{len(criteria)+1}",
                    description=parts[1],
                    measurable="measurable" in line.lower() or "test" in line.lower(),
                    verification_method="manual" if "manual" in line.lower() else "automated"
                ))
        elif in_table and not line.startswith("|"):
            in_table = False
    
    return criteria


def parse_json_criteria(file_path: Path) -> List[AcceptanceCriteria]:
    data = json.loads(file_path.read_text())
    criteria = []
    for item in data.get("criteria", data.get("acceptance_criteria", [])):
        criteria.append(AcceptanceCriteria(
            id=item.get("id", f"AC-{len(criteria)+1}"),
            description=item.get("description", ""),
            measurable=item.get("measurable", True),
            verification_method=item.get("verification_method", "automated"),
            required=item.get("required", True)
        ))
    return criteria


def read_artifact_contract(file_path: Path) -> Optional[ArtifactContract]:
    """Read artifact contract from JSON/YAML."""
    if file_path.suffix in [".json"]:
        data = json.loads(file_path.read_text())
    elif file_path.suffix in [".yaml", ".yml"]:
        data = yaml.safe_load(file_path.read_text())
    else:
        return None
    
    return ArtifactContract(
        name=data.get("name", ""),
        format=data.get("format", ""),
        location=data.get("location", ""),
        required_fields=data.get("required_fields", []),
        quality_thresholds=data.get("quality_thresholds", {})
    )


def read_evidence_register(file_path: Path) -> Dict:
    """Read evidence register from markdown or JSON."""
    if file_path.suffix in [".md", ".markdown"]:
        return parse_markdown_evidence(file_path)
    elif file_path.suffix == ".json":
        return json.loads(file_path.read_text())
    return {}


def parse_markdown_evidence(file_path: Path) -> Dict:
    """Parse evidence register from markdown."""
    content = file_path.read_text()
    evidence = {"items": [], "claims": [], "gaps": []}
    
    lines = content.split('\n')
    current_section = ""
    
    for line in lines:
        line_lower = line.lower()
        if "evidence" in line_lower and "register" in line_lower:
            current_section = "items"
        elif "claim" in line_lower:
            current_section = "claims"
        elif "gap" in line_lower:
            current_section = "gaps"
        elif line.startswith("|") and current_section:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3 and not parts[0].startswith("-"):
                evidence[current_section].append({
                    "id": parts[0],
                    "description": parts[1],
                    "source": parts[2] if len(parts) > 2 else ""
                })
    
    return evidence


def read_risk_boundaries(file_path: Path) -> List[RiskBoundary]:
    """Read risk boundaries from JSON/YAML."""
    if file_path.suffix in [".json"]:
        data = json.loads(file_path.read_text())
    elif file_path.suffix in [".yaml", ".yml"]:
        data = yaml.safe_load(file_path.read_text())
    else:
        return []
    
    boundaries = []
    for item in data.get("risks", data.get("risk_boundaries", [])):
        boundaries.append(RiskBoundary(
            id=item.get("id", ""),
            description=item.get("description", ""),
            severity=item.get("severity", "medium"),
            mitigation=item.get("mitigation", ""),
            owner=item.get("owner", "")
        ))
    return boundaries


def read_all_inputs(
    criteria_path: Path,
    contract_path: Path,
    evidence_path: Path,
    risk_path: Path
) -> Dict:
    """Read all quality gate inputs."""
    return {
        "acceptance_criteria": read_acceptance_criteria(criteria_path),
        "artifact_contract": read_artifact_contract(contract_path),
        "evidence_register": read_evidence_register(evidence_path),
        "risk_boundaries": read_risk_boundaries(risk_path)
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: criteria_reader.py <command> [args...]")
        print("Commands:")
        print("  read-all <criteria> <contract> <evidence> <risk> [--output combined.json]")
        print("  criteria <file> [--output criteria.json]")
        print("  contract <file> [--output contract.json]")
        print("  evidence <file> [--output evidence.json]")
        print("  risks <file> [--output risks.json]")
        sys.exit(1)
    
    command = sys.argv[1]
    output_path = Path("output.json")
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = Path(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    if command == "read-all":
        if len(sys.argv) < 6:
            print("Usage: criteria_reader.py read-all <criteria> <contract> <evidence> <risk> [--output]")
            sys.exit(1)
        data = read_all_inputs(
            Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5])
        )
        # Convert to serializable
        output = {
            "acceptance_criteria": [asdict(c) for c in data["acceptance_criteria"]],
            "artifact_contract": asdict(data["artifact_contract"]) if data["artifact_contract"] else None,
            "evidence_register": data["evidence_register"],
            "risk_boundaries": [asdict(r) for r in data["risk_boundaries"]]
        }
        Path(output_path).write_text(json.dumps(output, indent=2))
        print(json.dumps(output, indent=2))
    
    elif command == "criteria":
        if len(sys.argv) < 3:
            print("Usage: criteria_reader.py criteria <file>")
            sys.exit(1)
        criteria = read_acceptance_criteria(Path(sys.argv[2]))
        Path(output_path).write_text(json.dumps([asdict(c) for c in criteria], indent=2))
    
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
