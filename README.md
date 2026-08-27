# GlacierEQ Mega Skills

**GlacierEQ Mega Skills** is a private, monolithic control-plane repository for a compounding hierarchy of agent capability:

```text
SKILLS  →  COMBO SKILLS  →  MEGA SKILLS
atomic      reusable          end-to-end
method      capability chain  mission system
```

The repository keeps the whole capability graph, governance, tests, and release metadata in one place. It does **not** flatten everything into one giant prompt. Each layer has a distinct job:

| Layer | Unit of reuse | Must own | Must not do |
|---|---|---|---|
| **Skills** | A precise capability or procedure | Inputs, outputs, method, local validation | Orchestrate unrelated work or duplicate another skill’s method |
| **Combo Skills** | A repeated, bounded chain of Skills | Handoff contracts, ordering, compound artifact | Hold the full project state or silently replace members |
| **Mega Skills** | A long-horizon mission system | Route selection, durable state, phase gates, integration | Copy all lower-layer instructions into itself |

> **Snowball rule:** every higher layer consumes verified artifacts from lower layers, adds one new integration capability, and emits a more decision-ready artifact. Nothing gets bigger merely by repeating instructions.

## Exact repository layout

```text
GlacierEQ/mega-skills/
├── README.md                                 # Repository contract and contributor entry point
├── HIERARCHY.md                              # Layer rules, dependency direction, and snowball model
├── OWNERSHIP.md                              # Authorship, provenance, and confidentiality rules
├── COMPATIBILITY.md                          # Versioning and external-reference update policy
├── .gitignore                                # Secrets, local state, and generated artifacts
├── registry/
│   ├── skills.json                           # Canonical registry for atomic Skills
│   ├── combo-skills.json                     # Canonical registry for reusable compositions
│   ├── mega-skills.json                      # Canonical registry for mission systems
│   └── external-skills.json                  # Installed-platform references, never source copies
├── skills/
│   └── far-away-party-core/                  # First GlacierEQ-owned atomic Skill
│       ├── SKILL.md
│       ├── references/
│       └── templates/
├── combo-skills/
│   ├── recon-and-map/COMBO.md
│   ├── skill-forge/COMBO.md
│   └── automation-control/COMBO.md
├── mega-skills/
│   └── far-away-party/MEGA.md
├── governance/
│   ├── CONTRIBUTING.md
│   └── decision-records/README.md
├── scripts/validate_hierarchy.py
├── tests/test_hierarchy.py
└── .github/
    ├── CODEOWNERS
    └── workflows/validate-hierarchy.yml
```

## The snowball model

The unit above a Skill must carry forward a real, reviewable asset from the unit below it.

| Step | Input from below | New contribution at this level | Output to the next level |
|---|---|---|---|
| **Skill** | A narrow task and source constraints | A precise method and local acceptance check | A verified atomic artifact |
| **Combo Skill** | Two or more atomic artifacts or capability contracts | A repeated ordering and explicit handoff | A compound work packet with traceable dependencies |
| **Mega Skill** | One or more Combo outputs | Mission routing, durable context, risk gates, and cross-combo integration | An evidence-backed, end-to-end mission result and resume state |

For example, `recon-and-map` does not repeat Far Away Party Core or repository-onboarding instructions. It locks the ordered handoff, produces a project map, and becomes a selectable stage inside the Far Away Party Mega Skill. The Mega layer owns only the long-horizon work: conditional routing, durable state, approval gates, and final integration.

## First graph

```text
                         ┌─────────────────────────────────┐
                         │  MEGA: far-away-party            │
                         │  mission routing + durable state │
                         └───────────────┬─────────────────┘
                                         │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
  COMBO: recon-and-map       COMBO: skill-forge       COMBO: automation-control
  clarify + topology         design + package         assess + configure + run
             │                          │                          │
             ▼                          ▼                          ▼
  SKILL: far-away-party-core  SKILL: far-away-party-core  SKILL: far-away-party-core
  EXTERNAL: repository...     EXTERNAL: skill-creator     EXTERNAL: automation/config/runtime
```

The initial version has one GlacierEQ-owned atomic Skill—`far-away-party-core`—and external/platform references where a procedure belongs outside this repository. Do not fabricate ownership or create empty internal packages merely to make the graph look full.

## Normal operating progression

Use the same sequence for every non-trivial request: **parse** the outcome and constraints; **inspect** current state and relevant layers; **research** only unresolved facts; **decide** the route and approval boundary; **execute** a bounded, verified chunk; then **assimilate** evidence and the next action. Mega Skills apply the progression across a mission, Combo Skills within a repeated capability chain, and Skills within their narrow procedure.

## Creating the private repository

This package is a foundation draft. It has not created or pushed any repository. After review, initialize it as a private repository and push it:

```bash
gh repo create GlacierEQ/mega-skills --private --source /path/to/GlacierEQ-mega-skills-foundation --remote origin --push
```

Run the hierarchy validation before every merge:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s tests -v
```
