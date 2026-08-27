# Recon and Map

## Purpose

Convert an uncertain repository or multi-repository request into a truthful context map before any change is proposed. Select this Combo when repository ownership, overlap, or relationship needs inspection.

## Members and order

1. **`far-away-party-core`** defines the mission boundary, risk, acceptance criteria, and evidence record.
2. **`repository-context-onboarding`** identifies candidate repositories, inspects decisive evidence, and produces the relationship map.

## Handoff contract

| Boundary | Required input | Output | Validation |
|---|---|---|---|
| Mission → repository inspection | Mission contract, candidate names/URLs, read-only boundary | Scoped repository inventory | Every plausible candidate is ruled in, ruled out, or marked unresolved. |
| Repository inspection → integration | Metadata, topology, source/manifest evidence, observed tensions | `repository-context-map.md` | Claims separate documented intent, verified behavior, and unknowns. |

## Compound artifact

The context map names repository roles, inspected revisions, tensions, default routing, and the smallest next verification. It becomes Mega-Skill input only after its evidence and next action are explicit.

## Non-goals

Do not execute repository code, mutate a repository, or choose a canonical implementation because a name appears first in search results.
