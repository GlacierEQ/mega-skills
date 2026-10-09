---
name: "monolith-holdings"
description: "Consult local case holdings before any remote fetch. Use on any 1FDV/docket/evidence question: read the holdings index first, work local sources in consult order, reach remote only when local holdings lack it."
metadata: { "includeInPrompt": true }
---

# Monolith Holdings

## Purpose
The Operator's data is dense and it washes through the agent unless deliberately
collected, indexed, and referenced. This skill is the forcing function:
**recover before recreating.** Never web-search, API-pull, or re-clone what
already sits on local disk.

## Workflow
1. Read `~/workspace/casework/1fdv-23-0001009/HOLDINGS_INDEX.md`.
2. Work the consult order it defines:
   1. Local docket repo (`~/workspace/docket-repo/CASE-1FDV-23-0001009/`)
   2. Chronological docket PDF (`~/workspace/your_files/1FDV-23-0001009_CHRONOLOGICAL_2026-10-01.pdf`)
   3. Docket analysis texts (`~/workspace/casework/docket-analysis/`)
   4. DOCKETS clone (`~/workspace/DOCKETS/` — raw JIMS HTML first, manifests last)
   5. Glacier Gmail (`glacier.equilibrium@gmail.com`) for NEFs
   6. Remote (GitHub API, web) ONLY when 1–5 lack it.
3. If the index is stale (new holdings arrived), update it in the same turn.

## Operating Rules
- The estate is HIS (GitHub repos, Box) — durable, versioned, reachable from all
  his devices. This VM is ephemeral; local copies are working copies, never a
  parallel universe. Index and reference his estate; don't fracture it with
  another silo.
- The first tool call on a case question goes to holdings, never to the network.
- "I can't see it" is forbidden while unconsulted local holdings exist.
- When holdings answer the question, say so and cite the holding.
- When holdings don't have it, say exactly which holdings were checked before
  going remote — the Operator audits this.
