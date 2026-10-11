# Skill Lifecycle Playbook

Use this as a lightweight decision record. Keep the record next to the audit or pull request; do not bury it in the skill’s trigger description.

## Intake record

| Field | Record |
|---|---|
| Request | What capability or outcome is needed? |
| Runtime | Which loader, agent, repository, or platform will use it? |
| Scope | What is explicitly in and out? |
| Risk | Read-only, reversible mutation, or irreversible mutation? |
| Evidence | What source, test, example, or user feedback supports the need? |
| Owner | Who owns correctness, security, and maintenance? |

## Discovery and selection record

Record each serious candidate with its source, commit or version, trigger summary, capability boundary, tool requirements, compatibility result, score, and rejection reason if not selected. Prefer reusable, evidenced capabilities and the strongest qualified composition that delivers the whole Operator outcome; precise triggers regulate activation, not mission ambition. A missing candidate changes the route rather than ending the entire mission.

## Creation and upgrade record

Define the complete job-to-be-done and intended outcome, representative examples covering normal and failure paths, all reusable resources necessary to deliver it, an independently observable acceptance test, and the non-goals before editing. For an upgrade, state whether the change is patch, minor, or major and identify any changed trigger, input, output, tool, or safety behavior.

## Release record

Before release, attach the manifest validation result, body/resource review, representative tests, security review, registry update, reviewer, version, commit, and rollback or replacement plan. Release only when the package is reproducible from a clean checkout.

## Observation record

After use, record the task type, selected skill, trigger outcome, tool behavior, output defect, context cost, safety issue, and proposed owning layer. Trace recurring failures through source generators, skill selection, routing, implementation, and consumers. Repair all implicated owning layers, preserve compatible verified capability, and add regression and consumer-path checks.

## Retirement record

Mark the skill deprecated, list dependents, name the replacement or migration path, and define a removal date. Remove it only after dependent combos and mega skills no longer reference it.
