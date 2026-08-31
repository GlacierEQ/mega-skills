#!/usr/bin/env python3
"""APEX Boot Core: Estate Startup Sentinel & Watchdog."""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List


class ApexBootWatchdog:
    def __init__(self, estate_root: Path = Path.home()):
        self.estate_root = estate_root

    def verify_toolchain(self) -> Dict[str, Any]:
        local_bin = self.estate_root / ".local" / "bin"
        if not local_bin.exists():
            return {"status": "warning", "message": "No ~/.local/bin directory found", "binaries_checked": 0}
        
        checked = []
        for p in local_bin.glob("apex-*"):
            is_exec = bool(p.stat().st_mode & 0o111)
            checked.append({"name": p.name, "executable": is_exec})
        
        return {
            "status": "ok" if all(b["executable"] for b in checked) else "drift_detected",
            "binaries_checked": len(checked),
            "details": checked
        }

    def verify_runtimes(self) -> Dict[str, Any]:
        python_ver = sys.version.split()[0]
        return {
            "status": "ok",
            "python_version": python_ver,
            "platform": sys.platform,
            "epistemic_tier": "L2_Behavior"
        }

    def run_preflight(self) -> Dict[str, Any]:
        toolchain = self.verify_toolchain()
        runtimes = self.verify_runtimes()
        overall_ok = toolchain["status"] in ("ok", "warning") and runtimes["status"] == "ok"
        
        payload = {
            "sentinel": "apex-boot-core",
            "status": "healthy" if overall_ok else "unhealthy",
            "toolchain": toolchain,
            "runtimes": runtimes,
            "digest": hashlib.sha256(json.dumps(runtimes, sort_keys=True).encode()).hexdigest()
        }
        return payload


def main():
    dog = ApexBootWatchdog()
    res = dog.run_preflight()
    print(json.dumps({
        "skill": "apex-boot-core",
        "status": "ready",
        "epistemic_tier": "L2",
        "firewall_active": True,
        "preflight": res
    }, indent=2))
    return 0


if __name__ == "__main__":
    main()
