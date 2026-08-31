#!/usr/bin/env python3
"""test-runner execution dispatcher."""

import json
import sys
import hashlib

def main():
    payload = {
        "skill": "test-runner",
        "status": "ready",
        "epistemic_tier": "L2",
        "firewall_active": True
    }
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload["status"] = "executed"
        payload["sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    print(json.dumps(payload, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
