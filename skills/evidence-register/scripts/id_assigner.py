#!/usr/bin/env python3
"""
ID Assigner
Assigns stable IDs to sources, tests, artifacts, approvals, and observed system results.
"""

import json
import hashlib
import uuid
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class EvidenceType(Enum):
    SOURCE = "source"
    TEST = "test"
    ARTIFACT = "artifact"
    APPROVAL = "approval"
    OBSERVATION = "observation"
    CLAIM = "claim"
    ASSUMPTION = "assumption"
    OPEN_QUESTION = "open_question"


@dataclass
class EvidenceItem:
    id: str
    type: EvidenceType
    title: str
    description: str
    origin: str
    timestamp: str
    scope: str
    reliability_limit: str
    location: str
    tags: List[str]


# Global registry
EVIDENCE_REGISTRY = {}


def generate_id(evidence_type: EvidenceType, title: str, origin: str) -> str:
    """Generate stable ID from type, title, and origin."""
    # Create deterministic hash
    content = f"{evidence_type.value}:{title}:{origin}"
    hash_digest = hashlib.sha256(content.encode()).hexdigest()[:12]
    return f"EV-{evidence_type.value[:3].upper()}-{hash_digest}"


def register_evidence(
    evidence_type: EvidenceType,
    title: str,
    description: str,
    origin: str,
    scope: str = "mission",
    reliability_limit: str = "observed",
    location: str = "",
    tags: List[str] = None
) -> str:
    """Register new evidence item and return its ID."""
    evidence_id = generate_id(EvidenceType(evidence_type), title, origin)
    
    if evidence_id in EVIDENCE_REGISTRY:
        return evidence_id  # Already registered
    
    item = EvidenceItem(
        id=evidence_id,
        type=EvidenceType(evidence_type),
        title=title,
        description=description,
        origin=origin,
        timestamp=datetime.now().isoformat(),
        scope=scope,
        reliability_limit=reliability_limit,
        location=location,
        tags=tags or []
    )
    
    EVIDENCE_REGISTRY[evidence_id] = asdict(item)
    # Convert enum
    EVIDENCE_REGISTRY[evidence_id]["type"] = evidence_type.value
    
    return evidence_id


def get_evidence(evidence_id: str) -> Optional[Dict]:
    return EVIDENCE_REGISTRY.get(evidence_id)


def list_evidence(evidence_type: EvidenceType = None) -> List[Dict]:
    items = list(EVIDENCE_REGISTRY.values())
    if evidence_type:
        items = [i for i in items if i["type"] == evidence_type.value]
    return items


def load_registry(registry_path: Path):
    """Load registry from file."""
    global EVIDENCE_REGISTRY
    if registry_path.exists():
        EVIDENCE_REGISTRY = json.loads(registry_path.read_text())


def save_registry(registry_path: Path):
    """Save registry to file."""
    registry_path.write_text(json.dumps(EVIDENCE_REGISTRY, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: id_assigner.py <command> [args...]")
        print("Commands:")
        print("  register <type> <title> <description> <origin> [--scope scope] [--reliability limit] [--location loc] [--tags t1,t2]")
        print("  get <evidence_id>")
        print("  list [--type type]")
        print("  load <registry.json>")
        print("  save <registry.json>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "register":
        if len(sys.argv) < 6:
            print("Usage: id_assigner.py register <type> <title> <description> <origin> [--scope scope] [--reliability limit] [--location loc] [--tags t1,t2]")
            sys.exit(1)
        
        ev_type = sys.argv[2]
        title = sys.argv[3]
        description = sys.argv[4]
        origin = sys.argv[5]
        
        scope = "mission"
        reliability = "observed"
        location = ""
        tags = []
        
        i = 6
        while i < len(sys.argv):
            if sys.argv[i] == "--scope" and i + 1 < len(sys.argv):
                scope = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--reliability" and i + 1 < len(sys.argv):
                reliability = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--location" and i + 1 < len(sys.argv):
                location = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--tags" and i + 1 < len(sys.argv):
                tags = sys.argv[i + 1].split(",")
                i += 2
            else:
                i += 1
        
        eid = register_evidence(
            evidence_type=ev_type,
            title=title,
            description=description,
            origin=origin,
            scope=scope,
            reliability_limit=reliability,
            location=location,
            tags=tags
        )
        print(f"Registered: {eid}")
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: id_assigner.py get <evidence_id>")
            sys.exit(1)
        item = EVIDENCE_REGISTRY.get(sys.argv[2])
        if item:
            print(json.dumps(item, indent=2))
        else:
            print(f"Evidence {sys.argv[2]} not found")
    
    elif command == "list":
        ev_type = None
        if "--type" in sys.argv:
            idx = sys.argv.index("--type")
            if idx + 1 < len(sys.argv):
                ev_type = sys.argv[idx + 1]
        
        items = list_evidence(EvidenceType(ev_type) if ev_type else None)
        print(json.dumps(items, indent=2))
    
    elif command == "load":
        if len(sys.argv) < 3:
            print("Usage: id_assigner.py load <registry.json>")
            sys.exit(1)
        load_registry(Path(sys.argv[2]))
        print(f"Loaded {len(EVIDENCE_REGISTRY)} items")
    
    elif command == "save":
        if len(sys.argv) < 3:
            print("Usage: id_assigner.py save <registry.json>")
            sys.exit(1)
        save_registry(Path(sys.argv[2]))
        print(f"Saved {len(EVIDENCE_REGISTRY)} items")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
