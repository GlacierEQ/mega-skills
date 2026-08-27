# Ownership, Provenance, and Safety

| Class | Definition | Repository treatment |
|---|---|---|
| `glaciereq` | Authored and maintained by GlacierEQ | Source package is stored and versioned here. |
| `external-platform` | Provided by the runtime or platform | Metadata reference only; no source copy by default. |
| `candidate` | Proposed but not accepted | Keep the proposal and acceptance evidence in a decision record. |

Do not copy a useful external skill into `skills/` merely because it fits the hierarchy. Before adoption, record the origin, license, scope of change, maintainer, test plan, and update policy. Then set ownership deliberately.

Never place credentials, tokens, private prompts, raw connector payloads, user records, private evidence, runtime-memory databases, or local execution artifacts in this repository. A `.gitignore` pattern does not remediate content already committed or pushed.
