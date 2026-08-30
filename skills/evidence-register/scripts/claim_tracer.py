#!/usr/bin/env python3
"""
Claim Tracer
Maps every material claim to supporting evidence IDs and verification method.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum


class ClaimType(Enum):
    OBSERVED_FACT = "observed_fact"
    DERIVED_CONCLUSION = "derived_conclusion"
    TESTED_BEHAVIOR = "tested_behavior"
    DESIGN_INTENT = "design_intent"
    ASSUMPTION = "assumption"
    ALLEGATION = "allegation"
    OPEN_QUESTION = "open_question"


class VerificationMethod(Enum):
    DIRECT_OBSERVATION = "direct_observation"
    TEST_EXECUTION = "test_execution"
    DOCUMENT_REVIEW = "document_review"
    CODE_ANALYSIS = "code_analysis"
    EXPERT_REVIEW = "expert_review"
    AUTOMATED_CHECK = "automated_check"
    MANUAL_VERIFICATION = "manual_verification"


@dataclass
class Claim:
    id: str
    text: str
    claim_type: ClaimType
    evidence_ids: List[str]
    verification_method: VerificationMethod
    confidence: float
    limitations: List[str]
    owner: str


@dataclass
class ClaimTrace:
    claim_id: str
    claim_text: str
    evidence_chain: List[str]
    verification_methods: List[str]
    gaps: List[str]


# Claim extraction patterns
CLAIM_PATTERNS = [
    (r"we (?:have |observed |found |determined |concluded )?(?:that )?(.+?)[.\n]", ClaimType.OBSERVED_FACT),
    (r"the (?:system|code|test|result) (?:shows|proves|demonstrates|indicates) (?:that )?(.+?)[.\n]", ClaimType.TESTED_BEHAVIOR),
    (r"we (?:assume|expect|believe|estimate) (?:that )?(.+?)[.\n]", ClaimType.ASSUMPTION),
    (r"it is (?:expected|designed|intended) (?:that )?(.+?)[.\n]", ClaimType.DESIGN_INTENT),
    (r"(?:according to|based on|per) (.+?), (.+?)[.\n]", ClaimType.DERIVED_CONCLUSION),
]


def extract_claims_from_text(text: str) -> List[Dict]:
    """Extract potential claims from text using patterns."""
    claims = []
    for pattern, ctype in CLAIM_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            claim_text = match.group(1).strip()
            if len(claim_text) > 10:  # Filter out very short matches
                claims.append({
                    "text": claim_text,
                    "type": ctype.value,
                    "source_text": match.group(0)[:200]
                })
    return claims


def extract_claims_from_document(doc_path: Path) -> List[Dict]:
    """Extract claims from a document file."""
    content = doc_path.read_text(encoding="utf-8", errors="ignore")
    return extract_claims_from_text(content)


def map_claim_to_evidence(claim: Dict, evidence_registry: Dict) -> Dict:
    """Map a claim to relevant evidence IDs in registry."""
    claim_text = claim["text"].lower()
    matched_ids = []
    
    for eid, evidence in evidence_registry.items():
        # Check if evidence is relevant to claim
        evidence_text = (evidence.get("title", "") + " " + evidence.get("description", "")).lower()
        # Simple keyword overlap
        claim_words = set(claim_text.split())
        evidence_words = set(evidence_text.split())
        overlap = claim_words & evidence_words
        if len(overlap) >= 2:  # At least 2 word overlap
            matched_ids.append(eid)
    
    return {
        "claim_id": f"CL-{hashlib.md5(claim['text'].encode()).hexdigest()[:8]}",
        "claim_text": claim["text"],
        "claim_type": claim["type"],
        "evidence_ids": matched_ids,
        "verification_method": "automated_keyword_match",
        "confidence": min(1.0, len(matched_ids) * 0.2),
        "limitations": ["Automated keyword matching only"] if matched_ids else ["No supporting evidence found"],
        "owner": "auto"
    }


def trace_claims_from_directory(dir_path: Path, registry_path: Path) -> List[Dict]:
    """Extract and trace claims from all documents in directory."""
    # Load evidence registry
    evidence_registry = {}
    if Path(Path(__file__).parent.parent / "evidence_registry.json").exists():
        with open(Path(__file__).parent.parent / "evidence_registry.json") as f:
            evidence_registry = json.load(f)
    
    claims = []
    
    # Scan for markdown/text files
    for file_path in dir_path.rglob("*.md"):
        if file_path.name in ["SKILL.md", "README.md", "EVIDENCE.md", "MISSION.md", "ROADMAP.md"]:
            doc_claims = extract_claims_from_document(file_path)
            for claim in doc_claims:
                traced = map_claim_to_evidence(claim, evidence_registry)
                traced["source_file"] = str(file_path.relative_to(dir_path))
                claims.append(traced)
    
    return claims


def build_claim_trace(claim_id: str, evidence_registry: Dict, depth: int = 3) -> Dict:
    """Build full evidence chain for a claim."""
    # Find claim in registry (would need claim registry)
    # For now, return structure
    return {
        "claim_id": claim_id,
        "evidence_chain": [],
        "verification_methods": [],
        "gaps": ["Claim tracing requires claim registry"]
    }


def main():
    import sys
    from pathlib import Path
    import hashlib
    
    if len(sys.argv) < 2:
        print("Usage: claim_tracer.py <command> [args...]")
        print("Commands:")
        print("  extract <dir> [--registry registry.json] [--output claims.json]")
        print("  trace <claim_id> [--registry registry.json] [--depth N]")
        print("  map <claim_text> [--registry registry.json]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "extract":
        if len(sys.argv) < 3:
            print("Usage: claim_tracer.py extract <dir> [--registry registry.json] [--output claims.json]")
            sys.exit(1)
        
        dir_path = Path(sys.argv[2])
        registry_path = Path("evidence_registry.json")
        output_path = Path("extracted_claims.json")
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--registry" and i + 1 < len(sys.argv):
                registry_path = Path(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
                output_path = Path(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        # Load registry
        evidence_registry = {}
        if registry_path.exists():
            with open(registry_path) as f:
                evidence_registry = json.load(f)
        
        claims = trace_claims_from_directory(Path(sys.argv[2]), registry_path)
        
        output_path.write_text(json.dumps({
            "claims": claims,
            "total": len(claims),
            "with_evidence": len([c for c in claims if c.get("evidence_ids")])
        }, indent=2))
        
        print(f"Extracted {len(claims)} claims, {len([c for c in claims if c.get('evidence_ids')])} with evidence")
    
    elif command == "map":
        if len(sys.argv) < 3:
            print("Usage: claim_tracer.py map <claim_text> [--registry registry.json]")
            sys.exit(1)
        
        registry_path = Path("evidence_registry.json")
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--registry" and i + 1 < len(sys.argv):
                registry_path = Path(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        evidence_registry = {}
        if registry_path.exists():
            with open(registry_path) as f:
                evidence_registry = json.load(f)
        
        claim = {"text": sys.argv[2], "type": "observed_fact"}
        result = map_claim_to_evidence(claim, evidence_registry)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
