#!/usr/bin/env python3
"""
Inventory Builder
Builds prerequisite inventory from capability and mission contract.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class PrerequisiteType(Enum):
    TOOL = "tool"
    SCRIPT = "script"
    MODEL = "model"
    DATASET = "dataset"
    CREDENTIAL = "credential"
    SERVICE = "service"
    HARDWARE = "hardware"
    RUNTIME = "runtime"


class VerificationMethod(Enum):
    COMMAND_EXISTS = "command_exists"
    VERSION_CHECK = "version_check"
    API_HEALTH = "api_health"
    FILE_EXISTS = "file_exists"
    PERMISSION_CHECK = "permission_check"
    NETWORK_REACHABLE = "network_reachable"


@dataclass
class Prerequisite:
    id: str
    name: str
    type: PrerequisiteType
    expected_identifier: str
    expected_version: Optional[str] = None
    source_of_truth: str = ""
    owner: str = ""
    required_permission: str = ""
    verification_method: VerificationMethod = VerificationMethod.COMMAND_EXISTS
    required: bool = True
    fallback: Optional[str] = None


def build_inventory(capability_id: str, mission_contract: Dict) -> List[Prerequisite]:
    """Build prerequisite inventory from capability and mission."""
    prerequisites = []
    
    # Common prerequisite patterns by capability
    capability_prereqs = {
        "ast-repair-core": [
            Prerequisite("pytest", "pytest test runner", PrerequisiteType.TOOL, "pytest", ">=7.0", 
                        "requirements.txt", "dev", "", VerificationMethod.COMMAND_EXISTS),
            Prerequisite("python", "Python interpreter", PrerequisiteType.RUNTIME, "python", ">=3.10",
                        "pyproject.toml", "dev", "", VerificationMethod.VERSION_CHECK),
        ],
        "connector-bridge": [
            Prerequisite("httpx", "HTTP client library", PrerequisiteType.TOOL, "httpx", ">=0.25",
                        "requirements.txt", "dev", "", VerificationMethod.COMMAND_EXISTS),
            Prerequisite("openrouter_key", "OpenRouter API key", PrerequisiteType.CREDENTIAL, "OPENROUTER_API_KEY",
                        None, ".env", "ops", "api_key", VerificationMethod.API_HEALTH),
        ],
        "epistemic-gate": [
            Prerequisite("python", "Python interpreter", PrerequisiteType.RUNTIME, "python", ">=3.10",
                        "pyproject.toml", "dev", "", VerificationMethod.VERSION_CHECK),
        ],
        "computer-user-core": [
            Prerequisite("osascript", "AppleScript runner", PrerequisiteType.TOOL, "osascript", None,
                        "macOS", "system", "", VerificationMethod.COMMAND_EXISTS),
            Prerequisite("screencapture", "Screen capture utility", PrerequisiteType.TOOL, "screencapture", None,
                        "macOS", "system", "", VerificationMethod.COMMAND_EXISTS),
            Prerequisite("sips", "Image processing", PrerequisiteType.TOOL, "sips", None,
                        "macOS", "system", "", VerificationMethod.COMMAND_EXISTS),
        ],
        "fork-overlay-core": [
            Prerequisite("git", "Git version control", PrerequisiteType.TOOL, "git", ">=2.30",
                        "system", "dev", "", VerificationMethod.VERSION_CHECK),
        ],
    }
    
    # Add capability-specific prerequisites
    if capability_id in capability_prereqs:
        prerequisites.extend(capability_prereqs[capability_id])
    
    # Add mission-specific prerequisites
    if "required_services" in mission_contract:
        for svc in mission_contract["required_services"]:
            prerequisites.append(Prerequisite(
                f"service_{svc}", f"{svc} service", PrerequisiteType.SERVICE, svc,
                None, "mission_contract", "ops", "", VerificationMethod.API_HEALTH
            ))
    
    if "required_tools" in mission_contract:
        for tool in mission_contract["required_tools"]:
            prerequisites.append(Prerequisite(
                f"tool_{tool}", f"{tool} tool", PrerequisiteType.TOOL, tool,
                None, "mission_contract", "dev", "", VerificationMethod.COMMAND_EXISTS
            ))
    
    return prerequisites


def export_inventory(prerequisites: List[Prerequisite], output_path: Path):
    """Export inventory to JSON."""
    data = {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "prerequisites": [asdict(p) for p in prerequisites]
    }
    # Convert enums to strings
    for p in data["prerequisites"]:
        p["type"] = p["type"].value if hasattr(p["type"], "value") else p["type"]
        p["verification_method"] = p["verification_method"].value if hasattr(p["verification_method"], "value") else p["verification_method"]
    
    output_path.write_text(json.dumps(data, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: inventory_builder.py <capability_id> [mission_contract.json] [--output inventory.json]")
        sys.exit(1)
    
    capability_id = sys.argv[1]
    mission_contract = {}
    output_path = Path("inventory.json")
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = Path(sys.argv[i + 1])
            i += 2
        elif sys.argv[i].endswith(".json"):
            mission_contract = json.loads(Path(sys.argv[i]).read_text())
            i += 1
        else:
            i += 1
    
    prereqs = build_inventory(capability_id, mission_contract)
    export_inventory(prerequisites, output_path)
    
    print(json.dumps({
        "capability_id": capability_id,
        "prerequisites_count": len(prereqs),
        "output": str(output_path)
    }, indent=2))


if __name__ == "__main__":
    main()
