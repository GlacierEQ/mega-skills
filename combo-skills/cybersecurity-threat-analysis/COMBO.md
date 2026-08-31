---
id: cybersecurity-threat-analysis
display_name: Cybersecurity Threat Analysis
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Cybersecurity Threat Analysis

## Purpose and selection

Red-team penetration testing, privilege escalation modeling, and attack surface defense audit are required.

## Incremental value

This Combo Skill composes red-team-tools, privilege-escalation-methods, security-review into a unified, verified `THREAT_MITIGATION_REPORT.md`.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `red-team-tools` | skill | Yes | Execute non-destructive penetration modeling and scan vectors. | System architecture, Threat boundary | red-team-threat-vector.json | Threat vectors mapped without unhandled exceptions. |
| 2 | `privilege-escalation-methods` | skill | Yes | Model privilege boundaries and audit permission elevation risks. | red-team-threat-vector.json | privilege-boundary-audit.json | Zero unmitigated privilege escalation paths verified. |
| 3 | `security-review` | skill | Yes | Synthesize vulnerability mitigation plan and defense audit receipt. | privilege-boundary-audit.json | THREAT_MITIGATION_REPORT.md | Security review verifies all risk remediations pass. |

## Ordered execution

1. **red-team-tools** consumes System architecture, Threat boundary, produces red-team-threat-vector.json, and verifies Threat vectors mapped without unhandled exceptions..
2. **privilege-escalation-methods** consumes red-team-threat-vector.json, produces privilege-boundary-audit.json, and verifies Zero unmitigated privilege escalation paths verified..
3. **security-review** consumes privilege-boundary-audit.json, produces THREAT_MITIGATION_REPORT.md, and verifies Security review verifies all risk remediations pass..

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `red-team-tools` | `privilege-escalation-methods` | red-team-threat-vector.json | privilege-boundary-audit.json | `red-team-tools` | Verified handoff |
| `privilege-escalation-methods` | `security-review` | privilege-boundary-audit.json | THREAT_MITIGATION_REPORT.md | `privilege-escalation-methods` | Verified handoff |

## Compound output

Produce `THREAT_MITIGATION_REPORT.md` upon completion.
