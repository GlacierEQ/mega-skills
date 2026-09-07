#!/usr/bin/env python3
"""Machine-readable capability inventory for agent-memory-systems."""

from __future__ import annotations

import json

CAPABILITIES = {
    "skill": "agent-memory-systems",
    "execution": "substantive",
    "continuation_schema_version": "2.0.0",
    "capabilities": [
        "continuation-projection",
        "source-realized-hydration",
        "provenance-bound-source-pointers",
        "polycentric-peer-state",
        "contradiction-preservation",
        "resolved-state-preservation",
        "explicit-question-reopen",
        "verified-transition-receipts",
        "sha256-state-integrity",
        "atomic-persistence",
        "critical-path-continuation",
        "logical-progress",
        "working-memory",
        "episodic-memory",
        "semantic-memory",
        "procedural-memory",
        "vector-retrieval"
    ],
    "anti_claims": [
        "boot-summary-is-live-state",
        "generated-means-executed",
        "executed-means-verified",
        "single-provider-is-universal-truth"
    ]
}


def main() -> int:
    print(json.dumps(CAPABILITIES, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
