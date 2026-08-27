# Compatibility and Evolution Policy

## Stable identifiers

Registry IDs are API-like contracts. Rename an ID only through a recorded migration that updates dependent Combo and Mega Skills in one reviewed change.

| Unit | Versioning expectation | Required validation |
|---|---|---|
| GlacierEQ-owned Skill | Semantic version | Package shape, local procedure checks, registry validation |
| Combo Skill | Semantic version | Member IDs, ordering, compound output, and handoff remain explicit |
| Mega Skill | Semantic version | Routes resolve, state contract is compatible, and mission-level test passes |
| External reference | Installed-version snapshot | Re-read the relevant procedure when the snapshot changes |

Do not change a lower-layer contract during an active Mega Skill run without a decision record and a check of every dependent Combo and Mega reference.
