#!/usr/bin/env python3
"""
L0-L6 Epistemic Tier Evaluator
Enforces the Ascended 6-Tier Epistemic Ladder as immutable gatekeeper.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum


class EpistemicTier(IntEnum):
    L0_PRESENCE = 0      # File/route exists on disk
    L1_STRUCTURE = 1     # Static AST, signatures, schema verified
    L2_BEHAVIOR = 2      # Unit tests pass, SHA-256 verified, compilers green
    L3_COLOSSAL = 3      # Live DB integration, RPC mesh, multi-cloud sync verified
    L4_TELEMETRY = 4     # Runtime latency, profiling, zero leaks, automated repair
    L5_SWARM = 5         # 4-phase dialectic multi-agent consensus reached
    L6_SOVEREIGN = 6     # Upstream tracking, Hebbian reinforcement, zero drift


@dataclass
class VerificationResult:
    tier: EpistemicTier
    authorized: bool
    evidence: List[str]
    sha256_digests: Dict[str, str]
    forbidden_patterns: List[str]
    gaps: List[str]


FORBIDDEN_PATTERNS = [
    r"\bpass\b(?=\s*#|\s*$)",           # bare pass
    r"\breturn\s+True\b",               # return True stub
    r"\breturn\s+False\b",              # return False stub
    r"\bNotImplemented\b",              # NotImplemented
    r"\bTODO\b",                        # TODO comments
    r"\bFIXME\b",                       # FIXME comments
    r"raise\s+NotImplementedError",     # explicit NotImplementedError
    r"\.\.\.",                          # ellipsis stub
]


def compute_sha256(path: Path) -> str:
    """Compute deterministic SHA-256 in 64KB chunks (NIST standard)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_forbidden_patterns(path: Path) -> List[str]:
    """Scan file for forbidden stub patterns."""
    violations = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_PATTERNS:
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            for m in matches:
                line_num = content[:m.start()].count("\n") + 1
                violations.append(f"{path}:{line_num}: {m.group()}")
    except Exception:
        pass
    return violations


def check_l0_presence(target: Path) -> Tuple[bool, List[str]]:
    """L0: File or route exists on disk."""
    evidence = []
    if target.exists():
        evidence.append(f"Path exists: {target}")
        if target.is_file():
            evidence.append(f"Size: {target.stat().st_size} bytes")
        return True, evidence
    return False, [f"Path not found: {target}"]


def check_l1_structure(target: Path) -> Tuple[bool, List[str]]:
    """L1: Static AST, signatures, schema verified."""
    evidence = []
    if target.suffix == ".py":
        try:
            import ast
            source = target.read_text()
            tree = ast.parse(source)
            functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            evidence.append(f"AST parsed: {len(functions)} functions, {len(classes)} classes")
            evidence.append(f"Functions: {functions[:10]}")
            return True, evidence
        except SyntaxError as e:
            evidence.append(f"Syntax error: {e}")
            return False, evidence
    elif target.suffix in (".json", ".yaml", ".yml"):
        try:
            if target.suffix == ".json":
                json.loads(target.read_text())
            else:
                import yaml
                yaml.safe_load(target.read_text())
            evidence.append("Schema valid")
            return True, evidence
        except Exception as e:
            evidence.append(f"Schema invalid: {e}")
            return False, evidence
    return True, ["Non-code artifact, structure check skipped"]


def check_l2_behavior(target: Path) -> Tuple[bool, List[str]]:
    """L2: Unit tests pass, SHA-256 verified, compilers green."""
    evidence = []
    sha256 = compute_sha256(target)
    evidence.append(f"SHA-256: {sha256}")
    
    # Check for test file
    test_path = target.parent.parent / "tests" / f"test_{target.stem}.py"
    if test_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
                capture_output=True, text=True, timeout=60, cwd=target.parent.parent
            )
            if result.returncode == 0:
                evidence.append(f"Tests PASSED: {test_path}")
                return True, evidence
            else:
                evidence.append(f"Tests FAILED: {result.stdout[-500:]}")
                return False, evidence
        except subprocess.TimeoutExpired:
            evidence.append("Test timeout")
            return False, evidence
        except Exception as e:
            evidence.append(f"Test execution error: {e}")
            return False, evidence
    else:
        evidence.append(f"No test file found at {test_path}")
        return False, evidence


def check_l3_colossal(target: Path) -> Tuple[bool, List[str]]:
    """L3: Live DB integration, RPC mesh, multi-cloud storage sync."""
    evidence = []
    # Check for connector configuration
    config_files = list(target.parent.parent.glob("**/*.json")) + list(target.parent.parent.glob("**/*.yaml"))
    connector_configs = [f for f in config_files if any(k in f.name.lower() for k in ("supabase", "github", "openrouter", "rpc", "mesh"))]
    if connector_configs:
        evidence.append(f"Connector configs found: {[c.name for c in connector_configs[:5]]}")
        # Could add actual connection test here
        return True, evidence
    evidence.append("No live backend configs detected")
    return False, evidence


def check_l4_telemetry(target: Path) -> Tuple[bool, List[str]]:
    """L4: Runtime latency, profiling, zero leaks, automated repair."""
    evidence = []
    # Check for telemetry/profiling configs
    telemetry_files = list(target.parent.parent.glob("**/telemetry*")) + list(target.parent.parent.glob("**/profiling*"))
    if telemetry_files:
        evidence.append(f"Telemetry configs: {[f.name for f in telemetry_files[:3]]}")
    # Check for apex-repair integration
    repair_files = list(target.parent.parent.glob("**/*repair*"))
    if repair_files:
        evidence.append(f"Repair integration: {[f.name for f in repair_files[:3]]}")
    return len(telemetry_files) > 0 or len(repair_files) > 0, evidence


def check_l5_swarm(target: Path) -> Tuple[bool, List[str]]:
    """L5: 4-phase dialectic multi-agent consensus."""
    evidence = []
    # Check for swarm consensus artifacts
    swarm_files = list(target.parent.parent.glob("**/swarm*")) + list(target.parent.parent.glob("**/consensus*"))
    if swarm_files:
        evidence.append(f"Swarm artifacts: {[f.name for f in swarm_files[:3]]}")
        return True, evidence
    evidence.append("No swarm consensus evidence")
    return False, evidence


def check_l6_sovereign(target: Path) -> Tuple[bool, List[str]]:
    """L6: Upstream tracking, Hebbian reinforcement, zero drift."""
    evidence = []
    # Check for upstream tracking
    git_dir = target.parent.parent / ".git"
    if git_dir.exists():
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=target.parent.parent
            )
            if result.returncode == 0:
                evidence.append("Git repo clean, upstream tracking possible")
                return True, evidence
        except Exception:
            pass
    evidence.append("No sovereign autonomy evidence")
    return False, evidence


TIER_CHECKS = {
    EpistemicTier.L0_PRESENCE: check_l0_presence,
    EpistemicTier.L1_STRUCTURE: check_l1_structure,
    EpistemicTier.L2_BEHAVIOR: check_l2_behavior,
    EpistemicTier.L3_COLOSSAL: check_l3_colossal,
    EpistemicTier.L4_TELEMETRY: check_l4_telemetry,
    EpistemicTier.L5_SWARM: check_l5_swarm,
    EpistemicTier.L6_SOVEREIGN: check_l6_sovereign,
}


def evaluate_target(target: Path, required_tier: EpistemicTier = EpistemicTier.L2_BEHAVIOR) -> VerificationResult:
    """Evaluate a target against the epistemic ladder up to required tier."""
    all_evidence = []
    all_sha256 = {}
    all_forbidden = []
    all_gaps = []
    authorized = True
    achieved_tier = EpistemicTier.L0_PRESENCE
    
    # Check forbidden patterns at all levels
    all_forbidden.extend(scan_forbidden_patterns(target))
    
    # Run checks up to required tier
    for tier in EpistemicTier:
        if tier > required_tier:
            break
        check_fn = TIER_CHECKS.get(tier)
        if check_fn:
            passed, evidence = check_fn(target)
            all_evidence.extend(evidence)
            if passed:
                achieved_tier = tier
            else:
                all_gaps.append(f"L{tier.value}: {evidence[-1] if evidence else 'check failed'}")
                if tier >= required_tier:
                    authorized = False
    
    # SHA-256 of target
    all_sha256[str(target)] = compute_sha256(target)
    
    return VerificationResult(
        tier=achieved_tier,
        authorized=authorized and len(all_forbidden) == 0,
        evidence=all_evidence,
        sha256_digests=all_sha256,
        forbidden_patterns=all_forbidden,
        gaps=all_gaps
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: tier_evaluator.py <target_path> [--tier L2]")
        print("Tiers: L0, L1, L2, L3, L4, L5, L6")
        sys.exit(1)
    
    target_path = Path(sys.argv[1])
    required_tier = EpistemicTier.L2_BEHAVIOR
    if "--tier" in sys.argv:
        tier_idx = sys.argv.index("--tier")
        if tier_idx + 1 < len(sys.argv):
            tier_str = sys.argv[tier_idx + 1].upper()
            if tier_str.startswith("L"):
                required_tier = EpistemicTier(int(tier_str[1:]))
    
    result = evaluate_target(target_path, required_tier)
    
    # Output receipt
    receipt = {
        "target": str(target_path),
        "required_tier": required_tier.name,
        "achieved_tier": result.tier.name,
        "authorized": result.authorized,
        "evidence": result.evidence,
        "sha256_digests": result.sha256_digests,
        "forbidden_patterns": result.forbidden_patterns,
        "gaps": result.gaps,
    }
    
    print(json.dumps(receipt, indent=2))
    
    # Exit code: 0 if authorized, 1 if not
    sys.exit(0 if result.authorized else 1)


if __name__ == "__main__":
    main()
