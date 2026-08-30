#!/usr/bin/env python3
"""
Register Updater
Maintains EVIDENCE.md with item register, claims trace, test outcomes, unresolved gaps, and stable links.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ItemType(Enum):
    SOURCE = "source"
    TEST = "test"
    ARTIFACT = "artifact"
    APPROVAL = "approval"
    OBSERVATION = "observation"
    CLAIM = "claim"
    ASSUMPTION = "assumption"
    OPEN_QUESTION = "open_question"


class ItemStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
    INVALIDATED = "invalidated"


@dataclass
class RegisterEntry:
    id: str
    type: str
    title: str
    description: str
    origin: str
    timestamp: str
    scope: str
    reliability_limit: str
    location: str
    status: str
    tags: List[str]
    links: List[str]  # Related evidence IDs


class EvidenceRegister:
    def __init__(self, register_path: Path):
        self.register_path = Path(register_path)
        self.entries = self._load_register()
    
    def _load_register(self) -> Dict[str, Dict]:
        if self.register_path.exists():
            return json.loads(self.register_path.read_text())
        return {}
    
    def _save_register(self):
        self.register_path.write_text(json.dumps(self.entries, indent=2))
    
    def add_entry(
        self,
        entry_id: str,
        entry_type: str,
        title: str,
        description: str,
        origin: str,
        scope: str = "mission",
        reliability_limit: str = "observed",
        location: str = "",
        tags: List[str] = None,
        links: List[str] = None
    ) -> Dict:
        entry = {
            "id": entry_id,
            "type": entry_type,
            "title": title,
            "description": description,
            "origin": origin,
            "timestamp": datetime.now().isoformat(),
            "scope": scope,
            "reliability_limit": reliability_limit,
            "location": location,
            "status": "active",
            "tags": tags or [],
            "links": links or []
        }
        self.entries[entry_id] = entry
        self._save_register()
        return self.entries[entry_id]
    
    def update_entry(self, entry_id: str, updates: Dict) -> Optional[Dict]:
        if entry_id in self.entries:
            self.entries[entry_id].update(updates)
            self.entries[entry_id]["updated_at"] = datetime.now().isoformat()
            self._save_register()
            return self.entries[entry_id]
        return None
    
    def archive_entry(self, entry_id: str, reason: str = "") -> bool:
        if entry_id in self.entries:
            self.entries[entry_id]["status"] = "archived"
            self.entries[entry_id]["archive_reason"] = reason
            self.entries[entry_id]["archived_at"] = datetime.now().isoformat()
            self._save_register()
            return True
        return False
    
    def supersede_entry(self, entry_id: str, new_entry_id: str) -> bool:
        if entry_id in self.entries:
            self.entries[entry_id]["status"] = "superseded"
            self.entries[entry_id]["superseded_by"] = new_entry_id
            self.entries[entry_id]["superseded_at"] = datetime.now().isoformat()
            self._save_register()
            return True
        return False
    
    def get_entry(self, entry_id: str) -> Optional[Dict]:
        return self.entries.get(entry_id)
    
    def search_entries(
        self,
        entry_type: str = None,
        status: str = None,
        tag: str = None,
        scope: str = None
    ) -> List[Dict]:
        results = list(self.entries.values())
        
        if entry_type:
            results = [e for e in results if e.get("type") == entry_type]
        if status:
            results = [e for e in results if e.get("status") == status]
        if tag:
            results = [e for e in results if tag in e.get("tags", [])]
        if scope:
            results = [e for e in results if e.get("scope") == scope]
        
        return results
    
    def generate_markdown(self, output_path: Path) -> str:
        """Generate EVIDENCE.md from register."""
        md = f"""# Evidence Register

**Generated:** {datetime.now().isoformat()}
**Total Items:** {len(self.entries)}
**Active:** {len([e for e in self.entries.values() if e.get('status') == 'active'])}

---

## Item Register

| ID | Type | Title | Origin | Scope | Status | Reliability | Location |
|---|---|---|---|---|---|---|---|
"""
        
        for entry in sorted(self.entries.values(), key=lambda x: x.get("timestamp", ""), reverse=True):
            md += f"| {entry['id']} | {entry.get('type', '')} | {entry.get('title', '')[:40]} | {entry.get('origin', '')} | {entry.get('scope', '')} | {entry.get('status', '')} | {entry.get('reliability_limit', '')} | {entry.get('location', '')} |\n"
        
        md += """

---

## Claims Trace

"""
        # Get claims
        claims = [e for e in self.entries.values() if e.get("type") == "claim"]
        if claims:
            md += "| Claim ID | Statement | Evidence IDs | Verification | Status |\n"
            md += "|---|---|---|---|---|\n"
            for c in claims:
                md += f"| {c['id']} | {c.get('title', '')[:60]} | {', '.join(c.get('links', []))} | {c.get('reliability_limit', '')} | {c.get('status', '')} |\n"
        
        md += """

---

## Test Outcomes

"""
        tests = [e for e in self.entries.values() if e.get("type") == "test"]
        if tests:
            md += "| Test ID | Name | Outcome | Evidence | Timestamp |\n"
            md += "|---|---|---|---|---|\n"
            for t in tests:
                md += f"| {t['id']} | {t.get('title', '')[:40]} | {t.get('status', '')} | {', '.join(t.get('links', []))} | {t.get('timestamp', '')[:19]} |\n"
        
        md += """

---

## Unresolved Evidence Gaps

"""
        gaps = [e for e in self.entries.values() if e.get("type") == "open_question"]
        if gaps:
            md += "| Gap ID | Description | Priority | Owner |\n"
            md += "|---|---|---|---|\n"
            for g in gaps:
                md += f"| {g['id']} | {g.get('title', '')[:60]} | {g.get('tags', [''])[0] if g.get('tags') else ''} | {g.get('origin', '')} |\n"
        
        md += f"""

---

## Stable Links

All evidence items use stable IDs in format `EV-XXX-<hash>`. Links to artifacts use relative paths from repository root.

*Generated by Evidence Register at {datetime.now().isoformat()}*
"""
        output_path = Path("EVIDENCE.md")
        output_path.write_text(md)
        return md


def main():
    if len(sys.argv) < 2:
        print("Usage: register_updater.py <command> [args...]")
        print("Commands:")
        print("  add <id> <type> <title> <description> <origin> [--scope] [--reliability] [--location] [--tags] [--links]")
        print("  update <id> <key> <value>")
        print("  archive <id> [--reason]")
        print("  supersede <old_id> <new_id>")
        print("  get <id>")
        print("  search [--type] [--status] [--tag] [--scope]")
        print("  generate-md [--output EVIDENCE.md]")
        sys.exit(1)
    
    command = sys.argv[1]
    register = EvidenceRegister(Path("evidence_register.json"))
    
    if command == "add":
        if len(sys.argv) < 7:
            print("Usage: register_updater.py add <id> <type> <title> <description> <origin> [--scope] [--reliability] [--location] [--tags] [--links]")
            sys.exit(1)
        
        entry_id = sys.argv[2]
        entry_type = sys.argv[3]
        title = sys.argv[4]
        description = sys.argv[5]
        origin = sys.argv[6]
        
        scope = "mission"
        reliability = "observed"
        location = ""
        tags = []
        links = []
        
        i = 7
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
            elif sys.argv[i] == "--links" and i + 1 < len(sys.argv):
                links = sys.argv[i + 1].split(",")
                i += 2
            else:
                i += 1
        
        entry = register.add_entry(
            entry_id=sys.argv[2],
            entry_type=sys.argv[3],
            title=sys.argv[4],
            description=sys.argv[5],
            origin=sys.argv[6],
            scope=scope,
            reliability_limit=reliability,
            location=location,
            tags=tags,
            links=links
        )
        print(json.dumps(entry, indent=2))
    
    elif command == "update":
        if len(sys.argv) < 4:
            print("Usage: register_updater.py update <id> <key> <value>")
            sys.exit(1)
        entry = register.update_entry(sys.argv[2], {sys.argv[3]: sys.argv[4]})
        if entry:
            print(json.dumps(entry, indent=2))
        else:
            print(f"Entry {sys.argv[2]} not found")
    
    elif command == "archive":
        if len(sys.argv) < 3:
            print("Usage: register_updater.py archive <id> [--reason]")
            sys.exit(1)
        reason = ""
        if "--reason" in sys.argv:
            idx = sys.argv.index("--reason")
            if idx + 1 < len(sys.argv):
                reason = sys.argv[idx + 1]
        success = register.archive_entry(sys.argv[2], reason)
        print(json.dumps({"success": success}))
    
    elif command == "supersede":
        if len(sys.argv) < 4:
            print("Usage: register_updater.py supersede <old_id> <new_id>")
            sys.exit(1)
        success = register.supersede_entry(sys.argv[2], sys.argv[3])
        print(json.dumps({"success": success}))
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: register_updater.py get <id>")
            sys.exit(1)
        entry = register.get_entry(sys.argv[2])
        if entry:
            print(json.dumps(entry, indent=2))
        else:
            print(f"Entry {sys.argv[2]} not found")
    
    elif command == "search":
        entry_type = None
        status = None
        tag = None
        scope = None
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--type" and i + 1 < len(sys.argv):
                entry_type = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--status" and i + 1 < len(sys.argv):
                status = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--tag" and i + 1 < len(sys.argv):
                tag = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--scope" and i + 1 < len(sys.argv):
                scope = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        results = register.search_entries(entry_type, status, tag, scope)
        print(json.dumps(results, indent=2))
    
    elif command == "generate-md":
        output_path = Path("EVIDENCE.md")
        if "--output" in sys.argv:
            idx = sys.argv.index("--output")
            if idx + 1 < len(sys.argv):
                output_path = Path(sys.argv[idx + 1])
        
        md = register.generate_markdown(output_path)
        print(f"Generated {output_path}")
    
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
