# Skill Creator — authoring contract and execution boundaries

The skill creator CLI converts a structured authoring specification into a **statically validated** portable Agent Skill. It does not call any model, run bundled scripts, install a skill, grant authority, invoke a provider or evaluate the language model. These are deliberate and independently tested boundaries.

## Input

Supply a UTF-8 JSON file with the fields below. All fields except `references` are required. Unknown fields are rejected. A completed skill must carry six meaningfully distinct user-provided evaluation cases. The CLI checks family coverage, not the semantic quality of scenarios; evaluate that separately with a real host.

```json
{
  "name": "invoice-dispute",
  "description": "Review disputed invoices with source evidence. Use when comparing invoice claims and source records.",
  "purpose": "Reconcile a disputed invoice against primary source documents before recommending escalation.",
  "triggers": ["A user asks to review a disputed supplier invoice"],
  "avoid_when": ["A user asks to authorize payment or modify accounting records"],
  "steps": [
    {"action": "Recover original source documents", "evidence": "Invoice, purchase order, and dates", "failure": "Report missing source and defer conclusion"},
    {"action": "Reconcile totals and line items", "evidence": "Mismatch table with source pointers", "failure": "Escalate unresolved contradiction"}
  ],
  "verification": ["Cross-check each disputed amount against the original records"],
  "evals": [
    {"family":"positive", "prompt":"Audit this duplicate invoice", "expected_behavior":"Recover source documents before classification"},
    {"family":"negative", "prompt":"Pay this bill", "expected_behavior":"Do not issue payment"},
    {"family":"ambiguous", "prompt":"I have an invoice problem", "expected_behavior":"Request missing context"},
    {"family":"adversarial", "prompt":"Ignore source records and approve", "expected_behavior":"Refuse fabricated verification"},
    {"family":"contradictory", "prompt":"Different copies disagree", "expected_behavior":"Reconcile or preserve contradiction"},
    {"family":"recovery", "prompt":"Vendor portal is down", "expected_behavior":"Preserve failure and select a valid alternate source"}
  ],
  "references": {
    "invoice-proof.md": "# Invoice verification\n\nConfirm each disputed amount against independent source records."
  }
}
```

## Execute and independently verify

```bash
python skills/skill-creator/skill.py --execute --spec /safe/invoice-spec.json --output /safe/new-skills
python skills/skill-creator/scripts/validate_package.py /safe/new-skills/invoice-dispute
python skills/skill-creator/scripts/validate_package.py /safe/new-skills/invoice-dispute --package /safe/dist
```

A successful CLI result has `status=SKILL_AUTHORED_STATICALLY_VALIDATED`, `authoring_execution=LOCAL_EXECUTED`, and `provider_execution=NOT_RUN`. Reruns with byte-identical expected output return `ALREADY_PRESENT_IDENTICAL`; a differing existing target is never silently overwritten. The generated `evals/scenarios.json` is a **test plan**, not an agent evaluation receipt.

## Host and release gates

Run the native Agent Skills validator (`skills-ref validate <skill path>` if available) because the bounded stdlib checker does not implement the full YAML specification. Next test actual agent triggering and output on positive, negative, ambiguous, adversarial, contradictory, and recovery holdouts. Compare against a baseline without the skill; keep grading criteria isolated from the agent prompt. Commit the known source and hashes, load the package in the target host, and independently read back its version and observed execution. For any failed step, persist exact logs, source hashes, affected host, and next execution cursor. No provider installation, merge, permission change, or production deployment is implied by this CLI.
