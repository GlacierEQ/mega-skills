# Packet 03 — RECEIPT-FORMAT

**Owner:** apex-orchestration v1.0.0
**Maturity:** 9 / "Cryptographically verifiable, schema-locked, version-chained"
**Layer:** Skill
**Scope:** The single format every dispatched subtask returns. Without it, the FUSE step has no evidence.

---

## Invariant (L5)

A subtask return is a valid receipt iff:

1. It is valid JSON.
2. It conforms to `schemas/receipt.schema.json`.
3. `l2_proof == true` AND `sha256[]` covers every entry in `files_changed[]`.
4. `tests` block (if present) has `exit == 0`.

A receipt missing any of these is a **draft**, never a deliverable. FUSE rejects drafts.

## Schema (canonical, JSON-Schema draft 2020-12)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://glaciereq.com/schemas/receipt.schema.json",
  "title": "Apex Orchestration Subtask Receipt",
  "type": "object",
  "required": ["lane", "model", "task", "l2_proof"],
  "additionalProperties": false,
  "properties": {
    "lane": {"type": "string", "minLength": 1},
    "model": {"type": "string", "pattern": "^[a-z0-9./:-]+$"},
    "task": {"type": "string", "minLength": 1, "maxLength": 240},
    "files_changed": {"type": "array", "items": {"type": "string", "pattern": "^.+$"}},
    "sha256": {"type": "array", "minItems": 0, "items": {"type": "string", "pattern": "^[a-f0-9]{64}$"}},
    "tests": {
      "type": "object",
      "required": ["cmd", "exit"],
      "additionalProperties": false,
      "properties": {
        "cmd": {"type": "string"},
        "exit": {"type": "integer"},
        "summary": {"type": "string"}
      }
    },
    "duration_ms": {"type": "integer", "minimum": 0},
    "l2_proof": {"type": "boolean", "const": true},
    "evidence_uri": {"type": "string", "format": "uri-reference"},
    "parent_mission_id": {"type": "string", "pattern": "^mission_[a-z0-9]+$"}
  }
}
```

## SHA-256 chain

Every receipt is hashed. The hash is appended to `delivery.json` as `receipt_chain_sha256`, computed as:

```
chain = sha256( receipt_1 || receipt_2 || ... || receipt_N )
```

where `||` is byte concatenation in the order of dispatch.

## Gates

- **G1 — Hash integrity.** `sha256(file)` must match the actual file content at FUSE time. Drift = re-dispatch.
- **G2 — Exit-zero gate.** If `tests` is present, `exit` must be 0. Non-zero = receipt is a draft.
- **G3 — Const gate.** `l2_proof` must be literally `true`. `false` or missing = invalid.

## Anti-Patterns

- Returning prose instead of JSON.
- Returning JSON without `l2_proof: true`.
- Omitting `sha256` for any file in `files_changed`.
- Returning `exit: 0` without showing the command.

## L2 Evidence

- JSON-Schema validates 100% of staged receipts.
- Hash chain is reproducible from stored receipts.
- Drift detection run on every FUSE.

## Versioning

- Major bump: any field becomes required that was previously optional, or any field is removed.
- Minor bump: new optional field added.
- Patch: wording.

Current version: **1.0.0**
