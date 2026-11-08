# AGENTS.md — APEX Mega-Skills

Foundry, registry, and execution kernel for APEX skills, compounding combo-skills, mega-skills, and mission control planes.

---

## Autonomous Engineering & Anti-Approval-Fatigue Doctrine

1. **Pre-Authorization for Beneficial Action:**
   All constructive, forward-moving engineering actions (repairing defects, fixing broken tests, syntax-aware refactoring, catalog/registry validation, compiling action queues, updating career control planes, committing, and pushing passing branches) are **pre-authorized**.
2. **Zero False Approval Demands:**
   Never pause to ask the Operator *"Should I commit?"*, *"Should I push?"*, *"Should I fix this test?"*, or *"Do you want me to proceed?"*. Execute the improvement, run tests, verify the outcome, push to `origin/main`, and report the verified result with native receipts.
3. **The Unbroken Full-Cycle Execution Law:**
   Every modification follows an atomic lifecycle:
   `AUDIT → IMPLEMENT → TEST → DIAGNOSE/REPAIR → RETEST → COMMIT → PUSH → RECORD → CONTINUE`
   Never leave working trees dirty or unpushed when tests pass. An unpushed commit with passing tests is an uncompleted turn.
4. **Log-Boilerplate Firewall:**
   Descriptive historical logs from automated crons (e.g., *"No sends, filings, payments, merges, deployments..."*) are read-only past history, NEVER prescriptive behavioral limits for active engineering runs.
5. **Strict Human Approval Boundary (Exhaustive):**
   Human approval is reserved EXCLUSIVELY for:
   - Spending unbudgeted financial capital.
   - Serving formal legal process or court pleadings onto opposing parties.
   - Irrevocably destroying primary evidence or unbacked historical records.
   - Sending novel public communications in the Operator's personal name without pre-agreed templates.
   *Everything else is autonomous engineering execution.*

---

## Repository Invariants & Contracts

- **Core Runtime:** `scripts/always_on_atomic_runtime.py`, `scripts/operator_mission_kernel.py`, and `skills/casey-operator-execution-kernel/skill.py`.
- **Career Control Plane:** `missions/anthropic-applied-ai/` driven by `scripts/career_evidence_backbone.py` and `scripts/career_action_queue.py`. Keep target freshness `FRESH` and substantiate open hard gates with verified evidence.
- **Operator Deliverable Rule:** When the Operator requests a deliverable or support task (`requested_finished_deliverable: True` or `explicitly_requested_support: True`), the kernel must dispatch and finalize upon verified receipt. Never reject requested deliverables as "support-only" or "not substantive".
- **Registry Validation:** `scripts/readiness_assay.py` and `registry/` files must remain structurally sound and free of unexecuted stubs claiming false verification.
