---
name: glacier-memory-evidence
description: Verify Mem-derived claims and external outcomes against independent provider records before changing case, job, or runtime stages.
---
# Glacier Memory Evidence — forensic authority

1. Build a proposition ledger of actor, action, time, case/matter, external provider, claimant, asserted outcome and native object ID.
2. Assign independent evidence stage per proposition: `ASSERTED`, `DRAFT`, `ACTION_ATTEMPTED`, `PROVIDER_ACCEPTED`, `ACKNOWLEDGED`, `READBACK_VERIFIED`, `CONTESTED`, `SUPERSEDED`.
3. For Gmail use original message ID + Sent/recipient and subsequent provider result; for courts use JEFS/JIMS docket/NEF/service, not a signed PDF; for an application use ATS confirmation and original email, not a success splash; for Box use object/hash/readback; for GitHub use commit/branch/CI.
4. Preserve contradictions side-by-side, timestamp each source snapshot, name applicable actor and recipient, never collapse one event into multiple accomplishments.
5. Allow result promotion only after a native action receipt and independent provider readback matching the original intent. If an outcome is still blocked, preserve exact corrective next action and evidence gap.
6. Update the existing owner note with provenance and cursor using optimistic versioning; never establish new master cases on autopilot.

**Prohibitions:** no invented deadlines or statuses; no destructive dedupe; no unapproved sends, court filings, secret leakage, or sweeping child/medical exports.