#!/usr/bin/env python3
"""
Failure Classifier
Classifies gate failure cause, returns to correct owner, prohibits advancement until route revised.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class FailureCategory(Enum):
    CODE_QUALITY = "code_quality"
    TEST_FAILURE = "test_failure"
    SECURITY_VIOLATION = "security_violation"
    PERFORMANCE_REGRESSION = "performance_regression"
    CONTRACT_VIOLATION = "contract_violation"
    DEPENDENCY_ISSUE = "dependency_issue"
    ENVIRONMENT_ISSUE = "environment_issue"
    DATA_INTEGRITY = "data_integrity"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN = "unknown"


@dataclass
class FailureClassification:
    category: FailureCategory
    owner: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    remediation: str
    blocks_advancement: bool = True


# Classification rules
CLASSIFICATION_RULES = {
    FailureCategory.CODE_QUALITY: {
        "patterns": [
            r"lint", r"style", r"formatting", r"type.*error", r"mypy", r"pyright",
            r"unused.*import", r"undefined.*name", r"syntax.*error"
        ],
        "owner": "dev",
        "severity": "medium",
        "remediation": "Fix code quality issues, run linters/formatters"
    },
    FailureCategory.TEST_FAILURE: {
        "patterns": [
            r"assert.*failed", r"test.*fail", r"pytest.*fail", r"unittest.*fail",
            r"expected.*but got", r"assertion.*error"
        ],
        "owner": "dev",
        "severity": "high",
        "remediation": "Fix failing tests, verify test logic and implementation"
    },
    FailureCategory.SECURITY_VIOLATION: {
        "patterns": [
            r"secret", r"credential", r"api.*key", r"password", r"token",
            r"vulnerability", r"cve", r"injection", r"xss", r"csrf"
        ],
        "owner": "security",
        "severity": "critical",
        "remediation": "Remove secrets, rotate credentials, fix vulnerability"
    },
    FailureCategory.PERFORMANCE_REGRESSION: {
        "patterns": [
            r"timeout", r"latency", r"performance", r"slow", r"regression",
            r"benchmark.*fail", r"sla.*breach"
        ],
        "owner": "performance",
        "severity": "high",
        "remediation": "Profile and optimize, verify against baselines"
    },
    FailureCategory.CONTRACT_VIOLATION: {
        "patterns": [
            r"schema.*valid", r"contract.*fail", r"required.*field", r"type.*mismatch",
            r"interface.*fail", r"api.*contract"
        ],
        "owner": "dev",
        "severity": "high",
        "remediation": "Fix contract violation, update schema or implementation"
    },
    FailureCategory.DEPENDENCY_ISSUE: {
        "patterns": [
            r"import.*error", r"module.*not.*found", r"dependency.*conflict",
            r"version.*conflict", r"package.*not.*found", r"npm.*error", r"pip.*error"
        ],
        "owner": "dev",
        "severity": "medium",
        "remediation": "Resolve dependency conflicts, update lock files"
    },
    FailureCategory.ENVIRONMENT_ISSUE: {
        "patterns": [
            r"permission.*denied", r"not.*found", r"no.*such.*file", r"path.*not.*exist",
            r"docker.*fail", r"container.*fail", r"network.*unreachable"
        ],
        "owner": "ops",
        "severity": "medium",
        "remediation": "Fix environment configuration, verify paths and permissions"
    },
    FailureCategory.DATA_INTEGRITY: {
        "patterns": [
            r"checksum", r"hash.*mismatch", r"corrupt", r"data.*loss", r"integrity",
            r"sha256.*mismatch", r"verification.*fail"
        ],
        "owner": "data",
        "severity": "critical",
        "remediation": "Verify data sources, re-run integrity checks, restore from backup"
    },
    FailureCategory.CONFIGURATION_ERROR: {
        "patterns": [
            r"config.*error", r"invalid.*config", r"missing.*config", r"yaml.*error",
            r"json.*error", r"environment.*variable"
        ],
        "owner": "dev",
        "severity": "medium",
        "remediation": "Fix configuration, verify environment variables and config files"
    },
}


def classify_failure(error_output: str, context: Dict = None) -> Dict:
    """Classify failure based on error output and context."""
    error_lower = error_output.lower()
    
    best_match = None
    best_score = 0
    
    for category, rules in CLASSIFICATION_RULES.items():
        score = 0
        for pattern in rules["patterns"]:
            if re.search(pattern, error_lower, re.IGNORECASE):
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = category
    
    if best_match and best_score > 0:
        rules = CLASSIFICATION_RULES[best_match]
        return {
            "category": best_match.value,
            "owner": rules["owner"],
            "severity": rules["severity"],
            "description": f"Classified as {best_match.value} based on error patterns",
            "remediation": rules["remediation"],
            "blocks_advancement": True,
            "matched_patterns": best_score
        }
    else:
        return {
            "category": FailureCategory.UNKNOWN.value,
            "owner": "dev",
            "severity": "medium",
            "description": "Unable to classify failure automatically",
            "remediation": "Manual investigation required",
            "blocks_advancement": True,
            "matched_patterns": 0
        }


def route_to_owner(classification: Dict, ownership_map: Dict = None) -> Dict:
    """Route failure to correct owner based on classification."""
    owner = classification.get("owner", "dev")
    
    # Override with custom ownership map if provided
    if ownership_map and classification["category"] in ownership_map:
        owner = ownership_map[classification["category"]]
    
    return {
        "routed_to": owner,
        "notification_sent": False,  # Would integrate with notification system
        "escalation_path": get_escalation_path(owner)
    }


def get_escalation_path(owner: str) -> List[str]:
    """Get escalation path for owner."""
    paths = {
        "dev": ["dev-lead", "engineering-manager", "cto"],
        "security": ["security-lead", "ciso"],
        "performance": ["performance-lead", "engineering-manager"],
        "ops": ["ops-lead", "platform-manager"],
        "data": ["data-lead", "engineering-manager"],
        "compliance": ["compliance-officer", "legal"]
    }
    return paths.get(owner, ["dev-lead", "engineering-manager"])


def generate_remediation_plan(classification: Dict, context: Dict = None) -> Dict:
    """Generate remediation plan based on classification."""
    return {
        "category": classification["category"],
        "immediate_actions": [
            classification["remediation"],
            f"Notify {classification['owner']} team",
            "Document failure in incident log"
        ],
        "verification_steps": [
            "Apply fix",
            "Re-run failed gate",
            "Verify criteria pass",
            "Update documentation"
        ],
        "rollback_plan": "Revert to last known good state if fix fails",
        "owner": classification["owner"],
        "severity": classification["severity"],
        "blocks_advancement": classification["blocks_advancement"]
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: failure_classifier.py <command> [args...]")
        print("Commands:")
        print("  classify <error_output> [--context context.json]")
        print("  route <category> [--ownership-map map.json]")
        print("  remediation <category> [--context context.json]")
        print("  rules                     - Show classification rules")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "classify":
        if len(sys.argv) < 3:
            print("Usage: failure_classifier.py classify <error_output> [--context context.json]")
            sys.exit(1)
        
        error_output = sys.argv[2]
        context = {}
        if "--context" in sys.argv:
            idx = sys.argv.index("--context")
            if idx + 1 < len(sys.argv):
                import json
                with open(sys.argv[idx + 1]) as f:
                    context = json.load(f)
        
        classification = classify_failure(sys.argv[2], context)
        routing = route_to_owner(classification)
        remediation = generate_remediation_plan(classification, context)
        
        print(json.dumps({
            "classification": classification,
            "routing": routing,
            "remediation_plan": remediation
        }, indent=2))
    
    elif command == "route":
        if len(sys.argv) < 3:
            print("Usage: failure_classifier.py route <category> [--ownership-map map.json]")
            sys.exit(1)
        classification = {"category": sys.argv[2], "owner": "dev"}
        ownership_map = {}
        if "--ownership-map" in sys.argv:
            idx = sys.argv.index("--ownership-map")
            if idx + 1 < len(sys.argv):
                ownership_map = json.loads(Path(sys.argv[idx + 1]).read_text())
        print(json.dumps(route_to_owner(classification, ownership_map), indent=2))
    
    elif command == "remediation":
        if len(sys.argv) < 3:
            print("Usage: failure_classifier.py remediation <category> [--context context.json]")
            sys.exit(1)
        classification = {"category": sys.argv[2], "remediation": "Manual investigation required", "owner": "dev"}
        context = {}
        if "--context" in sys.argv:
            idx = sys.argv.index("--context")
            if idx + 1 < len(sys.argv):
                context = json.loads(Path(sys.argv[idx + 1]).read_text())
        print(json.dumps(generate_remediation_plan(classification, context), indent=2))
    
    elif command == "rules":
        print(json.dumps({k.value: v for k, v in CLASSIFICATION_RULES.items()}, indent=2))
    
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
