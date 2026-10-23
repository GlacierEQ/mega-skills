#!/usr/bin/env python3
"""Evidence ledger with first-class unknowns, mirroring REA's record rules.

Implements the re-evidence-record discipline locally:
- Evidence entries are content-addressed: evidence_id = "ev_" + sha256 of
  the canonical record (operation, subject digest, normalized result).
- Statements are classified observation / inference / unknown; an
  observation must cite evidence, an inference must cite its basis.
- Unknowns carry a revision chain (record at revision 1; updates must name
  the current revision and extend the chain digest).
- A "verified" resolution is accepted only when at least one supporting
  evidence record qualifies: its authority equals the unknown's required
  authority and its confidence rank meets the required confidence. This is
  the exact qualification rule REA's ledger enforces (frida observations
  carry authority "external-service"; static records "shipped-artifact").
"""
from __future__ import annotations

import hashlib
import json

CONFIDENCE_RANK = {"inferred": 1, "derived": 2, "observed": 3}
AUTHORITIES = {"shipped-artifact", "controlled-replay", "historical-reference",
               "external-service", "analyst-inference"}


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def evidence_id_for(record: dict) -> str:
    return "ev_" + hashlib.sha256(_canonical(record).encode()).hexdigest()


def make_evidence(operation: str, subject_sha256: str, normalized_result,
                  authority: str, confidence: str, limitations=None) -> dict:
    if authority not in AUTHORITIES:
        raise ValueError(f"unknown authority class: {authority}")
    if confidence not in CONFIDENCE_RANK:
        raise ValueError(f"unknown confidence class: {confidence}")
    record = {
        "operation": operation,
        "subject": {"sha256": subject_sha256},
        "normalized_result": normalized_result,
        "authority": authority,
        "confidence": confidence,
        "limitations": list(limitations or []),
    }
    record["evidence_id"] = evidence_id_for(record)
    return record


class Ledger:
    """In-memory ledger enforcing the record rules on every mutation."""

    def __init__(self):
        self.evidence: dict[str, dict] = {}
        self.unknowns: dict[str, dict] = {}

    def add_evidence(self, record: dict) -> dict:
        expected = evidence_id_for({k: record[k] for k in
                                    ("operation", "subject", "normalized_result",
                                     "authority", "confidence", "limitations")})
        if record.get("evidence_id") != expected:
            raise ValueError("evidence_id does not match the record content")
        self.evidence[record["evidence_id"]] = record
        return record

    def record_unknown(self, question: str, domain: str, severity: str,
                       required_authority: str, required_confidence: str) -> dict:
        seed = {"question": question, "domain": domain}
        unknown_id = "unk_" + hashlib.sha256(_canonical(seed).encode()).hexdigest()
        unknown = {
            "unknown_id": unknown_id,
            "question": question,
            "domain": domain,
            "severity": severity,
            "status": "open",
            "revision": 1,
            "previous_revision_digest": None,
            "required_authority": required_authority,
            "required_confidence": required_confidence,
            "supporting_evidence_ids": [],
            "resolution": None,
        }
        unknown["revision_digest"] = hashlib.sha256(_canonical(unknown).encode()).hexdigest()
        self.unknowns[unknown_id] = unknown
        return unknown

    def _qualifies(self, unknown: dict, evidence_id: str) -> bool:
        record = self.evidence.get(evidence_id)
        if record is None:
            return False
        if record["authority"] != unknown["required_authority"]:
            return False
        return CONFIDENCE_RANK[record["confidence"]] >= CONFIDENCE_RANK[unknown["required_confidence"]]

    def update_unknown(self, unknown_id: str, expected_revision: int,
                       status: str, supporting_evidence_ids=None,
                       resolution: dict | None = None) -> dict:
        current = self.unknowns.get(unknown_id)
        if current is None:
            raise KeyError(f"unknown not found: {unknown_id}")
        if current["revision"] != expected_revision:
            raise ValueError(
                f"revision conflict: current is {current['revision']}, update named {expected_revision}; "
                "reread the current revision instead of retrying blindly")
        supporting = list(supporting_evidence_ids or [])
        for evidence_id in supporting:
            if evidence_id not in self.evidence:
                raise ValueError(f"supporting evidence not in ledger: {evidence_id}")
        if status == "resolved":
            if not resolution or resolution.get("disposition") != "verified":
                raise ValueError("a resolved status requires a resolution with disposition 'verified'")
            if not any(self._qualifies(current, eid) for eid in supporting):
                raise ValueError(
                    "no supporting evidence qualifies: authority must equal the required "
                    "authority and confidence must meet the required confidence")
        updated = dict(current)
        updated.update({
            "status": status,
            "revision": current["revision"] + 1,
            "previous_revision_digest": current["revision_digest"],
            "supporting_evidence_ids": supporting,
            "resolution": resolution,
        })
        updated["revision_digest"] = hashlib.sha256(
            _canonical({k: v for k, v in updated.items() if k != "revision_digest"}).encode()).hexdigest()
        self.unknowns[unknown_id] = updated
        return updated

    def verify_resolution(self, unknown_id: str) -> dict:
        unknown = self.unknowns.get(unknown_id)
        if unknown is None:
            raise KeyError(f"unknown not found: {unknown_id}")
        valid = (
            unknown["status"] == "resolved"
            and unknown["resolution"] is not None
            and unknown["resolution"].get("disposition") == "verified"
            and any(self._qualifies(unknown, eid) for eid in unknown["supporting_evidence_ids"])
        )
        return {"valid": valid, "truthVerified": valid, "unknown": unknown}

    def classify_statement(self, kind: str, text: str, evidence_ids=None, basis_ids=None) -> dict:
        if kind == "observation" and not evidence_ids:
            raise ValueError("an observation must cite its evidence")
        if kind == "inference" and not basis_ids:
            raise ValueError("an inference must cite the evidence it derives from")
        if kind not in ("observation", "inference", "unknown"):
            raise ValueError(f"unknown statement class: {kind}")
        return {"class": kind, "text": text,
                "evidence_ids": list(evidence_ids or []), "basis_ids": list(basis_ids or [])}

    def closeout(self, checklist: list[dict]) -> dict:
        rows = []
        for row in checklist:
            unknown = self.unknowns.get(row.get("unknown_id", ""))
            if row.get("evidence_ids"):
                status = "answered"
            elif unknown is not None and unknown["status"] != "resolved":
                status = "unresolved"
            else:
                status = "partially_answered"
            rows.append({"question": row["question"], "status": status})
        return {"rows": rows,
                "complete": all(r["status"] == "answered" for r in rows),
                "open_unknowns": [u["unknown_id"] for u in self.unknowns.values() if u["status"] == "open"]}


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Exercise the ledger lifecycle on a built-in scenario.")
    parser.parse_args(argv)
    ledger = Ledger()
    ev = ledger.add_evidence(make_evidence(
        "instrument_with_frida", "ab" * 32, {"stdout": "pan=-40 L=1000 R=600"},
        authority="external-service", confidence="observed",
        limitations=["stdout observed via write hook only"]))
    unknown = ledger.record_unknown("Which taper does the shipped binary implement?",
                                    "behavioral", "medium", "external-service", "observed")
    ledger.update_unknown(unknown["unknown_id"], 1, "resolved",
                          supporting_evidence_ids=[ev["evidence_id"]],
                          resolution={"disposition": "verified",
                                      "rationale": "Runtime stdout matches the linear taper."})
    result = ledger.verify_resolution(unknown["unknown_id"])
    print(json.dumps({"valid": result["valid"], "truthVerified": result["truthVerified"]}, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
