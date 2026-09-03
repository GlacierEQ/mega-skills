# ROADMAP — Anthropic Applied AI Career Control Plane

## Current state

The mission is now a weighted, freshness-aware, correlation-aware career evidence control plane rather than a static LinkedIn draft.

### Target contract — COMPLETE v2

- Anthropic Applied AI role family.
- Primary external target: Applied AI Architect.
- Adjacent target: Forward Deployed Engineer.
- Operating identity: Forward Deployed AI Architect.
- 4 current Anthropic/Greenhouse role sources snapshot-dated 2026-09-02.
- 12 weighted requirements with explicit hard gates and minimum proof strengths.
- target freshness gate prevents silently using an old hiring contract.

### Evidence graph — CURRENT

- **13 typed source systems**
- **24 evidence records**
- **20 VERIFIED records**
- **19 public-safe records**
- source-strength classes and freshness decay
- correlation collapsed by independence group before scores compound
- direct runtime/test receipts retained where available
- private evidence excluded from public projection

Current strict evidence coverage:

- **72.4 / 100**
- **9 / 12 requirements satisfied**
- **3 hard gates open**

The score is evidence coverage only. It is not hiring probability, seniority, or employer fit.

### LinkedIn release system — COMPLETE baseline

- operator-authored source preserved: `LINKEDIN_PROFILE_SOURCE.md`
- machine projection: `linkedin-backbone.json`
- human projection: `LINKEDIN_BACKBONE.md`
- sentence/claim audit: `linkedin-claim-audit.json`
- manual LinkedIn state: `linkedin-activation.json`
- prioritized action queue: `linkedin-action-queue.json`
- deterministic release compiler: `scripts/linkedin_release_compiler.py`
- current publication pack: `linkedin-publication-pack.json`
- career authority map: `career-control-plane.json`

## Open hard gates — ordered

1. **Production LLM and agent application delivery** — MISSING
2. **Customer discovery and workflow problem decomposition** — PARTIAL; narrative only
3. **Customer deployment support, adoption, and lifecycle expansion** — PARTIAL; narrative only

Company/role intelligence is deliberately **not** treated as customer discovery.

## Gap-closing law

For every open gate:

`RETRIEVE EXISTING PROOF → VERIFY → INGEST → RESCORE`

Only if no qualifying evidence exists:

`ACTIVATE BOUNDED PROOF PACKET → EXECUTE → VERIFY → RECEIPT → PUBLIC-SAFE CASE STUDY → INGEST`

Prepared proof packets remain `BLOCKED_ON_RETRIEVAL`:

- `work-packets/production-llm-delivery.json`
- `work-packets/customer-discovery.json`
- `work-packets/deployment-adoption.json`

## Next engineering frontier

1. Exhaust estate retrieval for a genuinely provider-connected/deployed LLM application.
2. Exhaust retrieval for real external stakeholder/workflow discovery evidence.
3. Exhaust retrieval for real external deployment/adoption evidence.
4. Activate only the packets that remain unsupported.
5. Regenerate LinkedIn, résumé, portfolio, and interview projections from the strengthened evidence graph.

## Completion criterion

One retained evidence graph regenerates target-specific outward career surfaces while preserving operator wording authority, private/public boundaries, proof ceilings, freshness, and real-customer evidence requirements.
