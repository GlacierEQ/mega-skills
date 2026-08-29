---
name: mega-architecture
description: Architecture Decision Framework
domains: [architecture]
token_profile: Lean
---

# MEGA-ARCHITECTURE

_Ingested from the opencode skill source. Bundled into the Monolith mega-skills catalog._


# Architecture Decision Framework

> "Requirements drive architecture. Trade-offs inform decisions. ADRs capture rationale."

## 🎯 Selective Reading Rule

**Read ONLY files relevant to the request!** Check the content map, find what you need.

| File | Description | When to Read |
|------|-------------|--------------|
| `context-discovery.md` | Questions to ask, project classification | Starting architecture design |
| `trade-off-analysis.md` | ADR templates, trade-off framework | Documenting decisions |
| `pattern-selection.md` | Decision trees, anti-patterns | Choosing patterns |
| `examples.md` | MVP, SaaS, Enterprise examples | Reference implementations |
| `patterns-reference.md` | Quick lookup for patterns | Pattern comparison |

---

## 🔗 Related Skills

| Skill | Use For |
|-------|---------|
| `agent-memory-systems` | Choosing memory tiers and retrieval strategy |
| `ai-agents-architect` | Agent topology, tool selection, planning loops |
| `clean-code` | Pragmatic coding standards for implementation |
| `code-review-checklist` | Reviewing the resulting design before merge |
| `security-review` | Threat modeling for any service that handles auth or secrets |

---

## Core Principle

**"Simplicity is the ultimate sophistication."**

- Start simple
- Add complexity ONLY when proven necessary
- You can always add patterns later
- Removing complexity is MUCH harder than adding it

---

## Validation Checklist

Before finalizing architecture:

- [ ] Requirements clearly understood
- [ ] Constraints identified
- [ ] Each decision has trade-off analysis
- [ ] Simpler alternatives considered
- [ ] ADRs written for significant decisions
- [ ] Team expertise matches chosen patterns
