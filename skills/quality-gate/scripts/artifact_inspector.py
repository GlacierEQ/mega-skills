#!/usr/bin/env python3
"""
Artifact Inspector
Inspects artifacts and executes tests - no creator claim reliance.
"""

import json
import subprocess
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class InspectionResult:
    artifact_path: str
    checks: Dict[str, bool]
    overall_pass: bool
    details: Dict


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_checksum(filepath: Path, expected_sha256: str) -> bool:
    return compute_sha256(filepath) == expected_sha256


def check_file_exists(filepath: Path) -> bool:
    return filepath.exists() and filepath.is_file()


def check_file_size(filepath: Path, min_bytes: int = 0, max_bytes: int = None) -> bool:
    if not filepath.exists():
        return False
    size = filepath.stat().st_size
    if size < min_bytes:
        return False
    if max_bytes and size > max_bytes:
        return False
    return True


def check_json_valid(filepath: Path) -> bool:
    try:
        json.loads(filepath.read_text())
        return True
    except Exception:
        return False


def check_yaml_valid(filepath: Path) -> bool:
    try:
        import yaml
        yaml.safe_load(filepath.read_text())
        return True
    except Exception:
        return False


def run_artifact_tests(filepath: Path, test_command: str = None) -> Dict:
    """Run tests associated with artifact."""
    if not test_command:
        return {"success": True, "output": "No test command specified"}
    
    try:
        result = subprocess.run(
            test_command.split(),
            cwd=filepath.parent,
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[-1000:],
            "stderr": result.stderr[-1000:],
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Test timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def inspect_artifact(
    artifact_path: Path,
    contract: Dict = None,
    expected_sha256: str = None,
    test_command: str = None,
    min_size: int = 0,
    max_size: int = None
) -> InspectionResult:
    """Perform comprehensive artifact inspection."""
    checks = {}
    details = {}
    
    # Existence
    checks["exists"] = check_file_exists(artifact_path)
    details["exists"] = artifact_path.exists()
    
    if not artifact_path.exists():
        return InspectionResult(
            artifact_path=str(artifact_path),
            checks=checks,
            overall_pass=False,
            details={"error": "File does not exist"}
        )
    
    # Size checks
    checks["size_min"] = check_file_size(artifact_path, min_size)
    checks["size_max"] = check_file_size(artifact_path, max_size=max_size) if max_size else True
    details["size_bytes"] = artifact_path.stat().st_size
    
    # SHA-256
    if expected_sha256:
        actual = hashlib.sha256()
        with artifact_path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                actual.update(chunk)
        checks["sha256"] = actual.hexdigest() == expected_sha256
        details["expected_sha256"] = expected_sha256
        details["actual_sha256"] = actual.hexdigest()
    
    # Format validation
    if artifact_path.suffix == ".json":
        checks["valid_json"] = check_json_valid(artifact_path)
    elif artifact_path.suffix in [".yaml", ".yml"]:
        checks["valid_yaml"] = check_yaml_valid(artifact_path)
    
    # Run tests
    if test_command:
        test_result = run_artifact_tests(artifact_path, test_command)
        checks["tests_pass"] = test_result.get("success", False)
        details["test_output"] = test_result.get("stdout", "")
        details["test_error"] = test_result.get("stderr", "")
    
    # Contract validation
    if contract and artifact_path.suffix == ".json":
        try:
            data = json.loads(artifact_path.read_text())
            required = contract.get("required_fields", [])
            missing = [f for f in required if f not in data]
            checks["contract_fields"] = len(missing) == 0
            details["missing_fields"] = missing
        except Exception:
            checks["contract_fields"] = False
    
    overall = all(checks.values())
    
    return InspectionResult(
        artifact_path=str(artifact_path),
        checks=checks,
        overall_pass=overall,
        details=details
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: artifact_inspector.py <artifact_path> [--contract contract.json] [--sha256 HASH] [--test CMD] [--min-size N] [--max-size N]")
        sys.exit(1)
    
    artifact_path = Path(sys.argv[1])
    contract_path = None
    expected_sha256 = None
    test_command = None
    min_size = 0
    max_size = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--contract" and i + 1 < len(sys.argv):
            contract = json.loads(Path(sys.argv[i + 1]).read_text())
            i += 2
        elif sys.argv[i] == "--sha256" and i + 1 < len(sys.argv):
            expected_sha256 = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--test" and i + 1 < len(sys.argv):
            test_command = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--min-size" and i + 1 < len(sys.argv):
            min_size = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--max-size" and i + 1 < len(sys.argv):
            max_size = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    result = inspect_artifact(Path(sys.argv[1]), contract, expected_sha256, test_command, min_size, max_size)
    
    print(json.dumps({
        "artifact_path": result.artifact_path,
        "checks": result.checks,
        "overall_pass": result.overall_pass,
        "details": result.details
    }, indent=2))
    
    sys.exit(0 if result.overall_pass else 1)


if __name__ == "__main__":
    main()
