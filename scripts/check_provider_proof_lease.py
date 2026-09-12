#!/usr/bin/env python3
"""Fail generic provider CI only when provider proof is near expiry.

Host proof freshness is renewed and enforced by host-capable execution; generic CI
must not become permanently red merely because the Operator host is offline.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import renew_proof_leases as renewal

ROOT = Path(__file__).resolve().parents[1]
POINTER = ROOT / "evidence/deep-progress-forge/LATEST.json"


def provider_status(pointer: dict, renew_within_hours: float) -> dict:
    all_status = renewal.lease_status(pointer, renew_within_hours=renew_within_hours)
    provider = dict(all_status["provider"])
    provider["renewal_required"] = bool(provider["renew_recommended"])
    provider["lane"] = "provider"
    return provider


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--renew-within-hours", type=float, default=2.0)
    args = ap.parse_args()
    pointer = renewal.read_json(POINTER)
    status = provider_status(pointer, args.renew_within_hours)
    print(json.dumps(status, indent=2, sort_keys=True))
    return 3 if status["renewal_required"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
