#!/usr/bin/env python3
"""APEX telecommunications mission + provider receipt verifier."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FRESHNESS_SECONDS = 1800
VOICE_CHANNELS = {"VOICE_CALL", "SIP", "PSTN", "WEBRTC", "VOICEMAIL"}

def _parse_ts(value: str) -> datetime:
    value = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

def _digest(payload: Any) -> str:
    raw=json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def preflight(mission: dict[str, Any], now: datetime | None=None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    reasons=[]
    required=("mission_id","action_id","idempotency_key","source_freshness_at","channel","destination")
    for key in required:
        if not mission.get(key): reasons.append(f"MISSING_{key.upper()}")
    try:
        age=(now-_parse_ts(str(mission.get("source_freshness_at","")))).total_seconds()
        if age < -60 or age > FRESHNESS_SECONDS: reasons.append("STALE_CONTEXT")
    except Exception:
        reasons.append("INVALID_SOURCE_FRESHNESS")
    if mission.get("authorized") is not True: reasons.append("AUTHORIZATION_MISSING")
    destination=mission.get("destination") if isinstance(mission.get("destination"),dict) else {}
    if not destination.get("value"): reasons.append("INVALID_DESTINATION")
    if destination.get("allowlisted") is not True: reasons.append("DESTINATION_NOT_ALLOWLISTED")
    return {"status":"READY" if not reasons else "BLOCKED","blocking_reasons":sorted(set(reasons))}

def false_success_findings(receipt: dict[str, Any]) -> list[str]:
    f=[]
    transport=str(receipt.get("transport_state",""))
    contact=str(receipt.get("contact_state",""))
    mission=str(receipt.get("mission_state",""))
    ack=str(receipt.get("acknowledgement_state",""))
    tracking=receipt.get("tracking_numbers") or []
    if contact=="VOICEMAIL" and ack not in {"", "UNCONFIRMED"}: f.append("VOICEMAIL_IS_NOT_ACKNOWLEDGEMENT")
    if contact in {"WRONG_NUMBER","WRONG_UNIT"} and mission=="OBJECTIVE_SATISFIED": f.append("WRONG_ENDPOINT_NOT_SUCCESS")
    if contact=="HUMAN_REACHED" and not receipt.get("assigned_units") and mission=="OBJECTIVE_SATISFIED": f.append("HUMAN_IS_NOT_CORRECT_UNIT")
    if receipt.get("investigation_opened") and tracking and not receipt.get("investigation_opened_evidence"): f.append("TRACKING_IS_NOT_INVESTIGATION")
    if transport=="COMPLETED" and contact in {"", "NO_CONTACT"} and mission=="OBJECTIVE_SATISFIED": f.append("TRANSPORT_IS_NOT_CONTACT")
    if receipt.get("channel")=="SMS" and receipt.get("delivered_at") and ack=="FORMAL" and not receipt.get("reply"): f.append("SMS_DELIVERED_NOT_ACKNOWLEDGED")
    if len(set(tracking))>1 and mission=="OBJECTIVE_SATISFIED": f.append("CONFLICTING_TRACKING")
    return sorted(set(f))

def verify_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    native=receipt.get("provider_returned_fields") or receipt.get("native_provider_payload") or []
    findings=false_success_findings(receipt)
    evidence_ok=bool(native or receipt.get("provider_reference") or receipt.get("provider_run_id"))
    verdict="ACCEPT" if evidence_ok and not findings else "REPAIR"
    normalized={k:receipt.get(k) for k in ("transport_state","contact_state","mission_state","acknowledgement_state")}
    return {"verdict":verdict,"provider_evidence_present":evidence_ok,"false_success_findings":findings,"normalized_state":normalized}

def evaluate(mission: dict[str, Any], receipt: dict[str, Any] | None=None, now: datetime | None=None) -> dict[str, Any]:
    pre=preflight(mission, now=now)
    verification=verify_receipt(receipt) if receipt is not None else None
    status="BLOCKED" if pre["status"]=="BLOCKED" else (verification["verdict"] if verification else "READY")
    payload={"schema_version":1,"skill":"telecommunications-execution-core","status":status,"preflight":pre,"receipt_verification":verification}
    payload["sha256"]=_digest(payload)
    return payload

def main(argv=None) -> int:
    p=argparse.ArgumentParser(); p.add_argument("--mission",required=True); p.add_argument("--receipt"); p.add_argument("--output")
    a=p.parse_args(argv)
    mission=json.loads(Path(a.mission).read_text()); receipt=json.loads(Path(a.receipt).read_text()) if a.receipt else None
    out=evaluate(mission,receipt)
    text=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if a.output: Path(a.output).write_text(text)
    else: print(text,end="")
    return 0 if out["status"] in {"READY","ACCEPT"} else 2
if __name__=="__main__": raise SystemExit(main())
