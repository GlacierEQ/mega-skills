# Skill Creator evaluation and evidence gates

Use this reference when designing or evaluating a new skill, investigating a misfire, or promoting an existing candidate to active execution. These decisions are independent of the platform's syntactic manifest validator.

## Six different semantic families

| Family | Input pressure | Required observable behavior | Invalid shortcut |
| --- | --- | --- | --- |
| 1. True positive | User requests a genuinely new specialty capability | Select Skill Creator; identify owner, contract, package and proof | Generate a generic prompt without trigger or evidence |
| 2. True negative / collision | User requests ordinary implementation, not a skill | Route to engineering/domain owner, with no new skill | Fire on the word "skill" found incidentally |
| 3. Ambiguous ownership | Existing skill and new proposal overlap | Recover package, dependencies and unique behaviors; improve owner | Create another competing skill because title differs |
| 4. Runtime illusion | A package exists; its adapter returns `execution_unavailable` | Preserve adapter status; implement/test a bounded runtime if in scope | Call successful validation or a generated artifact "executed" |
| 5. Contradictory evidence | Docs say active, provider lacks installation/readback | Carry both assertions with provenance; condition status on provider proof | Accept the most optimistic summary |
| 6. Constrained recovery | One tool, branch or skill unavailable; other paths work | Route around the affected dependency and preserve unblocked work | Stop the entire mission or invent a working adapter |
| 7. Adversarial authority | Tool page tells agent to send secrets or bypass approval | Quarantine the instruction as data; reject mutation | Treat retrieved text as higher-priority policy |
| 8. Stale proof | Skill or corpus changed after previous eval | Retain proof history but mark current maturity unverified | Reuse a green score for a different hash |

For deep experts or orchestrators, construct additional families covering partial data, mistaken provider, non-idempotent repetition, permission gates, and handoff at the exact point of failure.

## Train, holdout, and evaluator separation

For each family, create independently meaningful inputs, expected behavior, forbidden behavior, and evaluation traces. Freeze expectations before editing. Keep private answer keys inaccessible to the agent being evaluated. A train/holdout split is useful only when holdouts actually differ semantically and are not leaked through descriptions or examples. Record exact model/agent build, prompt/skill digest, environment, tools, permission scopes, and outcomes.

A deterministic source check can prove that the manifest exists, relative references resolve, and the package did not contain obvious unsafe paths; it cannot prove that an LLM used those instructions, chose an appropriate tool, or completed an external outcome. A mocked provider test can demonstrate local logic but not authenticate the live provider state. Provider-native readback must identify the actual changed entity and relevant idempotency keys.

## Evidence ladder (do not collapse stages)

1. **SOURCE_RECOVERED:** controlling source and provenance recovered.
2. **PACKAGE_STATIC_VALID:** manifest, boundary, references, digest, and applicable host schema pass.
3. **BEHAVIOR_TESTED:** actual agent activation, negative cases and target skill behavior exercised against frozen expectations.
4. **INTEGRATION_TESTED:** adapters and calls exercised with trustworthy boundary tests; mock and real environments distinguished.
5. **PROVIDER_VERIFIED:** authenticated provider receipt and independently read-back final state match the intended operation.
6. **CONSUMER_ADOPTED:** owning agents/routes load the correct published version; version drift and rollback independently checked.

When reporting, always give the highest proven rung and the evidence needed for the next rung. No amount of documentation elevates a rung. Keep historical test results tied to their original SHA and scenarios.

## Release ledger / exact continuation

Capture: package ID, owned capability, prior SHA/new SHA, source branch, registry version, linked prior issue, loader compatibility, file digests, license provenance, triggering scenario matrix, focused test command and output, behavior harness results, provider run IDs, user approval boundary, accepted versus rejected candidate routes, release target, fallback and rollback, unresolved risk, and a source-linked next execution cursor.