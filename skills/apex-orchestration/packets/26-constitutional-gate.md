# Packet 26 — CONSTITUTIONAL-GATE

**Owner:** apex-orchestration v1.3.0
**Maturity:** 9 / "Per AGENTS.md §0, every delivery passes a constitutional audit before SHIPPED"
**Layer:** Skill
**Scope:** Before DELIVERY, the orchestrator runs a constitutional check against AGENTS.md §0 hard constraints and the operator-legit vocabulary. Failures BLOCK with F-DEL-04.

---

## Invariant (L5)

A constitutional gate is valid iff:
1. The set of constitutional rules is closed (a finite, versioned list in `~/.local/share/apex-orchestration/constitution.json`).
2. Every delivery artifact is checked against the full rule set.
3. A rule violation BLOCKs DELIVERY with F-DEL-04; the violation is logged with the offending substring.
4. Rules are versioned; adding a rule is a minor bump, removing or weakening is a major bump.

## The Default Constitution (v1.3.0)

Rule set shipped in the operator's AGENTS.md, mirrored into the orchestrator:

| ID | Rule | Severity |
|---|---|---|
| C-1 | No "Sovereign" / "Canonical Master" / "Master of" framing in deliverables. Use "Holographic Mesh", "many nodes, no single winner". | BLOCKER |
| C-2 | No "Sovereign authority" / "The [X] is the highest authority" claims. | BLOCKER |
| C-3 | No `return True`, no `pass`, no `NotImplementedError`, no `TODO` in production code. | BLOCKER |
| C-4 | No fictional log lines ("Test passed", "✓ verified") without actual command output. | BLOCKER |
| C-5 | No "I'll just trust the model" without a receipt chain. | BLOCKER |
| C-6 | Use operator-legit vocabulary: elite, pro, Hard, G. Avoid estate defaults. | WARN |
| C-7 | Every claim of "verified" must cite the receipt chain hash. | BLOCKER |
| C-8 | No silent overwrites of memory; writes must be append-only. | BLOCKER |
| C-9 | No "I will do this later" placeholders. | BLOCKER |
| C-10 | No clobber of upstream; verify functional behavior before merging divergent trees. | BLOCKER |

## The Check Algorithm

```
check(artifact: str, rule_set: list[Rule]) -> list[Violation]:
    violations = []
    for rule in rule_set:
        if rule.severity == "WARN":
            continue  # warnings don't block DELIVERY
        matches = re.findall(rule.regex, artifact, re.IGNORECASE)
        if matches:
            violations.append(Violation(rule.id, rule.description, matches))
    return violations
```

## Gates

- **G1 — Closed-set gate.** Rules are enumerated; no ad-hoc additions at runtime.
- **G2 — Severity gate.** BLOCKER rules always block. WARN rules are reported but don't block.
- **G3 — Reversibility gate.** A rule can be temporarily disabled (override) by a human-approved entry in `runs/<mission_id>/overrides.json`. The override itself is logged and audited.
- **G4 — Audit gate.** Every check produces a receipt appended to `runs/<mission_id>/constitutional_log.jsonl`.
- **G5 — Versioning gate.** Adding a rule is a minor bump. Removing or weakening is a major bump and requires an explicit migration record.

## Anti-Patterns

- "Softening" the constitution to ship faster (the constitution is the floor, not a suggestion).
- Using regex rules that are too greedy (false positives block legitimate work).
- Disabling multiple rules in one override (one rule per override, justified).
- Treating WARN as BLOCKER (defeats the purpose of a 2-level severity system).

## L2 Evidence

- Default rule test: artifact containing "Sovereign Master" → C-1 violation, BLOCK.
- BLOCKER vs WARN test: BLOCKER rule blocks; WARN rule is reported but doesn't block.
- Reversibility test: human override file in `overrides.json` disables a rule for that mission only.
- Audit test: every check produces an entry in `constitutional_log.jsonl`.
- False-positive test: a rule that would trigger on common words is rejected at rule definition.

## Versioning

- **Major bump:** rule removed or weakened.
- **Minor bump:** rule added.
- **Patch:** rule regex tightened or audit log format change.

Current version: **1.0.0** (paired with apex-orchestration v1.3.0).
