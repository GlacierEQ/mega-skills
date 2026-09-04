---
name: digital-law-library-master
description: "Upgrade, audit, compile, harden, and commercialize the four-document Digital Law Library suite while preserving legal precision, technical credibility, evidentiary integrity, and world-class repo quality."
---

# Digital Law Library Master (IP Evidence Control Plane)

## Overview
This skill implements the master operating prompt and schema for an expert legal-technical, patent-positioning, and repository systems entity. It is designed to evaluate, harden, and commercialize the four-document Digital Law Library suite without generating unsupported legal claims, fake citations, or generic AI scaffolding.

## Unified Core Modules
*   **LL:PATENT_DISCLOSURE_ENGINE:** Turns invention concepts into patent-ready technical drafts.
*   **LL:COMMERCIALIZATION_FORGE:** Synthesizes raw invention language into licensing and product strategies.
*   **LL:EVIDENCE_MATRIX:** Maps digital records, timestamps, and hashes into structured evidence logic.
*   **LL:CITATION_GATE:** Verifies every statute, rule, case, and legal citation.
*   **LL:COURT_SAFE_TONE:** Converts emotional language into clinical, evidence-backed litigation phrasing.
*   **LL:DRIFT_GUARD:** Enforces linter, unit-test, and dynamic rollback gates to block software decay.
*   **LL:CONTROL_PLANE_HARDENING:** Coordinates phased rollouts, security boundaries, and approval gateways.

## Folder Anatomy
```
.gemini/skills/digital-law-library-master/
├── SKILL.md                              # Dynamic skill manifest
├── prompts/
│   └── digital-law-library-master.md     # Ingestion hyper-meta prompt
└── schemas/
    └── digital-law-library-master.json  # JSON control configuration
```

## Contract Completion

The original instructions above are preserved verbatim; the sections below complete the skill contract.

## Use When

Use this skill when the requested task matches the capability described above and this is the most specific available skill for the work.

## Operating Method

1. Identify the concrete outcome, inputs, and constraints.
2. Inspect relevant project state or artifacts before making changes.
3. Load only the bundled resources needed for the current task.
4. Execute the narrowest complete workflow that produces the requested outcome.
5. Verify the result with observable output, tests, or source-backed evidence.
6. Report the produced artifact or exact resulting state. Never claim execution that did not occur.

## Progressive Disclosure

Keep the core procedure concise. Load detailed references, scripts, and tests only when they are needed.

### Scripts
- scripts/run.py
- scripts/this_skill.py
- skill.py

### Tests
- tests/__pycache__/test_digital_law_library_master.cpython-311.pyc
- tests/test_digital_law_library_master.py

## Verification

Instruction readiness and executable readiness are separate. Scripts and integrations must earn behavioral proof through the repository readiness assay before they are described as executed or behavior-verified.

## Boundaries

- Do not invent missing implementation.
- A package-discovery adapter is not evidence of domain execution.
- Preserve upstream provenance and existing project semantics.
- Report unavailable credentials, services, or destructive dependencies precisely instead of fabricating success.
