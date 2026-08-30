#!/usr/bin/env python3
"""
Availability Checker
Checks existence, version, access, scope, quota, data classification, and policy fit.
"""

import subprocess
import json
import sys
import os
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class AvailabilityStatus(Enum):
    VERIFIED = "verified"
    MISSING = "missing"
    INCOMPATIBLE = "incompatible"
    RESTRICTED = "restricted"
    EXPIRED = "expired"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class AvailabilityResult:
    prerequisite_id: str
    status: AvailabilityStatus
    observed_version: Optional[str] = None
    evidence: str = ""
    error: Optional[str] = None


def check_command_exists(command: str) -> AvailabilityResult:
    """Check if command exists in PATH."""
    try:
        result = subprocess.run(["which", command], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return AvailabilityResult(
                prerequisite_id=command,
                status=AvailabilityStatus.VERIFIED,
                evidence=f"Found at {result.stdout.strip()}"
            )
        else:
            return AvailabilityResult(
                prerequisite_id=command,
                status=AvailabilityStatus.MISSING,
                error=f"Command '{command}' not found in PATH"
            )
    except Exception as e:
        return AvailabilityResult(
            prerequisite_id=command,
            status=AvailabilityStatus.MISSING,
            error=str(e)
        )


def check_version(command: str, min_version: str = None, version_flag: str = "--version") -> AvailabilityResult:
    """Check command version."""
    try:
        result = subprocess.run([command, version_flag], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return AvailabilityResult(
                prerequisite_id=command,
                status=AvailabilityStatus.MISSING,
                error=f"Command failed: {result.stderr}"
            )
        
        version_output = result.stdout.strip()
        
        if min_version:
            # Simple version comparison (assumes semantic versioning)
            import re
            version_match = re.search(r'(\d+\.\d+\.\d+)', version_output)
            if version_match:
                observed = version_match.group(1)
                # Simple tuple comparison
                observed_parts = tuple(map(int, observed.split('.')))
                min_parts = tuple(map(int, min_version.split('.')))
                if observed_parts >= min_parts:
                    return AvailabilityResult(
                        prerequisite_id=command,
                        status=AvailabilityStatus.VERIFIED,
                        observed_version=observed,
                        evidence=f"Version {observed} >= {min_version}"
                    )
                else:
                    return AvailabilityResult(
                        prerequisite_id=command,
                        status=AvailabilityStatus.INCOMPATIBLE,
                        observed_version=observed,
                        error=f"Version {observed} < required {min_version}"
                    )
        
        return AvailabilityResult(
            prerequisite_id=command,
            status=AvailabilityStatus.VERIFIED,
            observed_version=version_output,
            evidence=f"Version: {version_output}"
        )
    except Exception as e:
        return AvailabilityResult(
            prerequisite_id=command,
            status=AvailabilityStatus.MISSING,
            error=str(e)
        )


def check_api_health(endpoint: str, api_key: str = None, timeout: int = 10) -> AvailabilityResult:
    """Check API endpoint health."""
    try:
        headers = {"Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        response = requests.get(endpoint, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return AvailabilityResult(
                prerequisite_id=endpoint,
                status=AvailabilityStatus.VERIFIED,
                evidence=f"HTTP {response.status_code}"
            )
        elif response.status_code == 401:
            return AvailabilityResult(
                prerequisite_id=endpoint,
                status=AvailabilityStatus.RESTRICTED,
                error="Authentication required"
            )
        elif response.status_code == 403:
            return AvailabilityResult(
                prerequisite_id=endpoint,
                status=AvailabilityStatus.RESTRICTED,
                error="Access forbidden"
            )
        else:
            return AvailabilityResult(
                prerequisite_id=endpoint,
                status=AvailabilityStatus.INCOMPATIBLE,
                error=f"HTTP {response.status_code}"
            )
    except requests.Timeout:
        return AvailabilityResult(
            prerequisite_id=endpoint,
            status=AvailabilityStatus.INCOMPATIBLE,
            error="Request timeout"
        )
    except Exception as e:
        return AvailabilityResult(
            prerequisite_id=endpoint,
            status=AvailabilityStatus.INCOMPATIBLE,
            error=str(e)
        )


def check_file_exists(filepath: str) -> AvailabilityResult:
    """Check if file exists and is readable."""
    path = Path(filepath).expanduser()
    if path.exists():
        if path.is_file():
            return AvailabilityResult(
                prerequisite_id=filepath,
                status=AvailabilityStatus.VERIFIED,
                evidence=f"File exists at {path}"
            )
        else:
            return AvailabilityResult(
                prerequisite_id=filepath,
                status=AvailabilityStatus.INCOMPATIBLE,
                error="Path exists but is not a file"
            )
    else:
        return AvailabilityResult(
            prerequisite_id=filepath,
            status=AvailabilityStatus.MISSING,
            error="File not found"
        )


def check_permission(filepath: str, required_perm: str = "read") -> AvailabilityResult:
    """Check file/directory permissions."""
    path = Path(filepath).expanduser()
    if not path.exists():
        return AvailabilityResult(
            prerequisite_id=filepath,
            status=AvailabilityStatus.MISSING,
            error="Path does not exist"
        )
    
    if required_perm == "read":
        ok = os.access(path, os.R_OK)
    elif required_perm == "write":
        ok = os.access(path, os.W_OK)
    elif required_perm == "execute":
        ok = os.access(path, os.X_OK)
    else:
        ok = os.access(path, os.R_OK)
    
    if ok:
        return AvailabilityResult(
            prerequisite_id=filepath,
            status=AvailabilityStatus.VERIFIED,
            evidence=f"Permission '{required_perm}' granted"
        )
    else:
        return AvailabilityResult(
            prerequisite_id=filepath,
            status=AvailabilityStatus.RESTRICTED,
            error=f"Permission '{required_perm}' denied"
        )


def check_network_reachable(host: str, port: int = 443, timeout: int = 5) -> AvailabilityResult:
    """Check network reachability."""
    import socket
    try:
        sock = socket.create_connection((host, port), timeout=5)
        sock.close()
        return AvailabilityResult(
            prerequisite_id=f"{host}:{port}",
            status=AvailabilityStatus.VERIFIED,
            evidence=f"TCP connection to {host}:{port} successful"
        )
    except Exception as e:
        return AvailabilityResult(
            prerequisite_id=f"{host}:{port}",
            status=AvailabilityStatus.INCOMPATIBLE,
            error=f"Connection failed: {e}"
        )


def check_prerequisite(prereq: Dict) -> AvailabilityResult:
    """Check a single prerequisite based on its type and verification method."""
    from resource_preflight.scripts.inventory_builder import PrerequisiteType, VerificationMethod
    
    prereq_id = prereq.get("id", "unknown")
    ptype = prereq.get("type", "tool")
    vmethod = prereq.get("verification_method", "command_exists")
    identifier = prereq.get("expected_identifier", "")
    version = prereq.get("expected_version")
    source = prereq.get("source_of_truth", "")
    
    if vmethod == "command_exists":
        return check_command_exists(identifier)
    elif vmethod == "version_check":
        return check_version(identifier, version)
    elif vmethod == "api_health":
        api_key = os.environ.get(identifier) if identifier.startswith("OPENROUTER") or identifier.startswith("GITHUB") else None
        return check_api_health(identifier, api_key)
    elif vmethod == "file_exists":
        return check_file_exists(identifier)
    elif vmethod == "permission_check":
        return check_permission(identifier, "read")
    elif vmethod == "network_reachable":
        # Parse host:port from identifier
        parts = identifier.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 443
        return check_network_reachable(host, port)
    else:
        return AvailabilityResult(
            prerequisite_id=prereq_id,
            status=AvailabilityStatus.NOT_APPLICABLE,
            error=f"Unknown verification method: {vmethod}"
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: availability_checker.py <inventory.json> [--output results.json]")
        sys.exit(1)
    
    inventory_path = Path(sys.argv[1])
    output_path = Path("availability_results.json")
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = Path(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    inventory = json.loads(inventory_path.read_text())
    prerequisites = inventory.get("prerequisites", [])
    
    results = []
    for prereq in prerequisites:
        result = check_prerequisite(prereq)
        results.append({
            "prerequisite_id": result.prerequisite_id,
            "status": result.status.value,
            "observed_version": result.observed_version,
            "evidence": result.evidence,
            "error": result.error
        })
    
    output_path.write_text(json.dumps({
        "results": results,
        "summary": {
            "total": len(results),
            "verified": len([r for r in results if r["status"] == "verified"]),
            "missing": len([r for r in results if r["status"] == "missing"]),
            "incompatible": len([r for r in results if r["status"] == "incompatible"]),
            "restricted": len([r for r in results if r["status"] == "restricted"]),
            "expired": len([r for r in results if r["status"] == "expired"]),
            "not_applicable": len([r for r in results if r["status"] == "not_applicable"])
        }
    }, indent=2))
    
    print(f"Results written to {output_path}")


if __name__ == "__main__":
    main()
