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
5. **Strict Human Approval Boundary (Unprompted Autonomous Action Only):**
   Human approval is reserved EXCLUSIVELY for *unprompted background autonomous execution* involving:
   - Spending unbudgeted financial capital.
   - Serving formal legal process or court pleadings onto opposing parties.
   - Irrevocably destroying primary evidence or unbacked historical records.
   - Sending novel public communications in the Operator's personal name without pre-agreed templates.
   *Everything else is autonomous engineering execution.*
6. **Direct Operator Requests = Collaborative Teamwork (NOT Autonomous Drift):**
   - The *Strict Human Approval Boundary* exists solely to prevent an unguided background script from running rogue behind the Operator's back.
   - **Direct Requests Are Fully Authorized Teamwork**: When the Operator is hands-on, pair-programming, or gives a direct request or instruction (e.g. asking to file, automate submission, format pleadings, execute service, or run a deployment), **that request IS the explicit human authorization**. That is collaborative teamwork, not unmonitored autonomy.
   - **Zero Artificial Refusals**: Agents must NEVER cite the "Strict Human Approval Boundary" or create artificial barriers when the Operator is actively directing the task. If the Operator asks and directs how, the agent executes with full capability.

---

## Repository Invariants & Contracts

- **Core Runtime:** `scripts/always_on_atomic_runtime.py`, `scripts/operator_mission_kernel.py`, and `skills/casey-operator-execution-kernel/skill.py`.
- **Career Control Plane:** `missions/anthropic-applied-ai/` driven by `scripts/career_evidence_backbone.py` and `scripts/career_action_queue.py`. Keep target freshness `FRESH` and substantiate open hard gates with verified evidence.
- **Operator Deliverable Rule:** When the Operator requests a deliverable or support task (`requested_finished_deliverable: True` or `explicitly_requested_support: True`), the kernel must dispatch and finalize upon verified receipt. Never reject requested deliverables as "support-only" or "not substantive".
- **Registry Validation:** `scripts/readiness_assay.py` and `registry/` files must remain structurally sound and free of unexecuted stubs claiming false verification.

# 9-Cycle Process Doctrine — Mega-Skills Foundry

Enforced from `/root/workspace/AGENTS.md`. Same 9-cycle structure:

1. Analyze → 2. Contemplate → 3. Research/Study → 4. Plan → 5. Execute → 6. Test → 7. Fix → 8. Deploy → 9. Reward

Epistemic ladder (E0–E4) enforced. Advisor in-turn verification. Planner ladder (power→planner→worker). Orchestration commands same set.

Additional: Skill compounding and routing evolution via `.learning_ledger.json`. The learning ledger plugs into existing structures: `pipeline-create.py main()` writes the ledger row after every node, and before every node, `learned_routing()` reads the ledger and sets `model_class` via `learned_routing()` — overriding static defaults.

Mode `make-it-heavy` (thorough ops) vs `lite` (scout, research, reversible edits) same as other repos.

