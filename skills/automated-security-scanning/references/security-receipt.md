# Security Scan and Remediation Receipt

Use this template after an authorized scan or remediation batch. Redact secrets and sensitive exploit details before sharing.

| Field | Value |
|---|---|
| Authorization and owner | `<approver, scope, and disclosure boundary>` |
| Repository or artifact | `<repo@commit, image@digest, or approved target>` |
| Scan scope | `<languages, paths, assets, environments, exclusions>` |
| Tools and rulesets | `<scanner versions, ruleset IDs, database timestamps>` |
| Baseline | `<exit codes, findings, coverage, known exceptions>` |
| Findings | `<identifier, class, severity, confidence, reachability, affected asset>` |
| Deduplication | `<correlated findings and retained evidence>` |
| Fixes generated | `<root cause, files, minimal mitigation, compatibility impact>` |
| Verification | `<repeat scan, focused tests, full tests, build, dependency resolution>` |
| Original finding status | `<fixed, mitigated, accepted exception, or unresolved>` |
| Tower route | `<not applicable, or preflight → source-of-truth → exhibits/proof → validate → generate → test → build → integrity → receipt>` |
| Exceptions | `<owner, rationale, compensating control, tracking ID, expiry; write “none” when absent>` |
| Residual risk | `<known limitations and untested surfaces>` |
| Disclosure handling | `<redactions, recipients, notification path>` |
| Rollback | `<revert commit, package rollback, or configuration restoration>` |
| Release decision | `<pass, block, or escalate with reason>` |
| Next action | `<merge, deploy, rotate, monitor, retry, or retire>` |
