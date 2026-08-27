# Combo Skill Integration Schema

## Role in the hierarchy

A Combo Skill is a **reusable ordered capability chain**. It connects two or more atomic Skills or external capability references. Its job is to make the handoff contract repeatable and independently reviewable; it is not a container for duplicated lower-layer methods or entire project state.

The canonical contract is [`schemas/combo-skill.schema.json`](../schemas/combo-skill.schema.json). The human-facing template is [`combo-skills/_template/COMBO.md`](../combo-skills/_template/COMBO.md). Every active Combo must conform to both.

## Required integration fields

| Contract area | Required question | Why it exists |
|---|---|---|
| Selection | When is this Combo right, and when must it not be used? | Stops a reusable chain from becoming a generic default. |
| Members | Which exact IDs participate, what kind are they, and which are mandatory? | Prevents ambiguous or imaginary capability references. |
| Ordered execution | What does each member consume, produce, and locally validate? | Makes compounding observable rather than rhetorical. |
| Handoffs | What must cross each boundary, what output is acceptable, and who resolves failure? | Removes raw-conversation and implicit-knowledge handoffs. |
| Evidence | What sources, artifacts, and tests make the compound output trustworthy? | Preserves traceability. |
| Risk boundaries | Which approval, privacy, external-action, and scope boundaries apply? | Prevents a higher-level chain from bypassing safeguards. |
| Quality gates | What must be true before the next stage can use this output? | Prevents unfinished work from snowballing upward. |
| State updates | What durable state must change at a closed transition? | Makes pause and resumption safe. |
| Compounding | What is inherited, what genuinely new integration value is added, and what artifact results? | Ensures the layer compounds instead of duplicates. |

## Integration invariants

1. A Combo has at least two members and an explicit member order.
2. Every step names canonical inputs, an output artifact, and a local validation rule.
3. A handoff may pass only a named, validated output—not raw hidden context or unexplained conclusions.
4. Each failure has an accountable owner and a defined return path.
5. A Combo adds ordering, integration, or a compound decision that none of its individual members owns alone.
6. A Combo cannot require a Mega Skill and cannot import another Combo implicitly; the Mega layer decides which Combinations to compose.
7. A Mega Skill may consume a Combo only after its compound artifact and next-layer-ready checks pass.

## Initial schema adoption

The initial Combos will be migrated into the schema in the same repository change that introduces the first atomic Skill set. The custom hierarchy validator will enforce the minimum contract fields without relying on an external Python dependency. Schema-aware tooling may additionally validate the full JSON Schema in CI later.
