#!/usr/bin/env python3
"""
Classifier
Classifies each prerequisite as verified/missing/incompatible/restricted/expired/not-applicable.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class Classification(Enum):
    VERIFIED = "verified"
    MISSING = "missing"
    INCOMPATIBLE = "incompatible"
    RESTRICTED = "restricted"
    EXPIRED = "expired"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ClassificationResult:
    prerequisite_id: str
    classification: Classification
    confidence: float
    reasoning: str


# Classification rules
CLASSIFICATION_RULES = {
    Classification.VERIFIED: {
        "conditions": ["status == 'verified'"],
        "confidence": 1.0,
        "reasoning": "Prerequisite observed and meets all requirements"
    },
    Classification.MISSING: {
        "conditions": ["status == 'missing'", "required == true"],
        "confidence": 0.95,
        "reasoning": "Required prerequisite not found in environment"
    },
    Classification.INCOMPATIBLE: {
        "conditions": ["status == 'incompatible'", "version_mismatch == true"],
        "confidence": 0.9,
        "reasoning": "Prerequisite exists but version or configuration incompatible"
    },
    Classification.RESTRICTED: {
        "conditions": ["status == 'restricted'", "permission_denied == true"],
        "confidence": 0.95,
        "reasoning": "Prerequisite exists but access is restricted"
    },
    Classification.EXPIRED: {
        "conditions": ["status == 'expired'", "credential_expired == true"],
        "confidence": 0.9,
        "reasoning": "Credential or license has expired"
    },
    Classification.NOT_APPLICABLE: {
        "conditions": ["required == false", "status in ['missing', 'incompatible']"],
        "confidence": 0.8,
        "reasoning": "Optional prerequisite not available but not required"
    }
}


def classify_result(availability_result: Dict) -> ClassificationResult:
    """Classify a single availability result."""
    status = availability_result.get("status", "missing")
    prereq_id = availability_result.get("prerequisite_id", "unknown")
    evidence = availability_result.get("evidence", "")
    error = availability_result.get("error", "")
    
    # Determine classification
    if status == "verified":
        return ClassificationResult(
            prerequisite_id=prereq_id,
            classification=Classification.VERIFIED,
            confidence=1.0,
            reasoning=f"Prerequisite verified: {evidence}"
        )
    elif status == "missing":
        return ClassificationResult(
            prerequisite_id=prereq_id,
            classification=Classification.MISSING,
            confidence=0.95,
            reasoning=f"Prerequisite not found: {error}"
        )
    elif status == "incompatible":
        return ClassificationResult(
            prerequisite_id=prereq_id,
            classification=Classification.INCOMPATIBLE,
            confidence=0.9,
            reasoning=f"Version or configuration incompatible: {error}"
        )
    elif status == "restricted":
        return ClassificationResult(
            prerequisite_id=prereq_id,
            classification=Classification.RESTRICTED,
            confidence=0.95,
            reasoning=f"Access restricted: {error}"
        )
    elif status == "expired":
        return ClassificationResult(
            prerequisite_id=prereq_id,
            classification=Classification.EXPIRED,
            confidence=0.9,
            reasoning=f"Credential expired: {error}"
        )
    elif status == "not_applicable":
        return ClassificationResult(
            prerequisite_id=prereq_id,
            classification=Classification.NOT_APPLICABLE,
            confidence=0.8,
            reasoning=f"Optional prerequisite not applicable"
        )
    else:
        return ClassificationResult(
            prerequisite_id=prereq_id,
            classification=Classification.MISSING,
            confidence=0.5,
            reasoning=f"Unknown status: {status}"
        )


def classify_availability_results(results_file: Path, output_path: Path):
    """Classify all availability results."""
    data = json.loads(results_file.read_text())
    results = data.get("results", [])
    
    classifications = []
    for result in results:
        classification = classify_result(result)
        classifications.append({
            "prerequisite_id": classification.prerequisite_id,
            "classification": classification.classification.value,
            "confidence": classification.confidence,
            "reasoning": classification.reasoning
        })
    
    # Summary
    summary = {c.value: 0 for c in Classification}
    for c in classifications:
        summary[c["classification"]] += 1
    
    output = {
        "classifications": classifications,
        "summary": summary,
        "overall": "ready" if summary[Classification.VERIFIED.value] + summary[Classification.NOT_APPLICABLE.value] == len(classifications) else "blocked"
    }
    
    output_path.write_text(json.dumps(output, indent=2))
    print(json.dumps(output, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: classifier.py <availability_results.json> [--output classifications.json]")
        sys.exit(1)
    
    results_file = Path(sys.argv[1])
    output_path = Path("classifications.json")
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = Path(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    classify_availability_results(results_file, output_path)


if __name__ == "__main__":
    main()
