# Legal skills index (vendored)

**Vault:** `GlacierEQ/mega-skills/legal/`  
**Private overlay:** `GlacierEQ/job_app_helix` (merge [PR #1](https://github.com/GlacierEQ/job_app_helix/pull/1) → `895fa867c6ef9ba9c93ea602dcdf1190cab8e6a2`)  
**Public manifest:** `GlacierEQ/job-app-helix` → `OFFICIAL_SKILLS.md`, `docs/legal-hire-official.md`  
**HX-28** · Last updated 2026-11-17

## Catalog pin (lawve)

| Field | Value |
| --- | --- |
| Repository | [lawve-ai/awesome-legal-skills](https://github.com/lawve-ai/awesome-legal-skills) |
| Commit | `f9f28cdccbeb98bbdde010042ea9f525ca427c72` |
| Catalog license | CC BY-NC-ND; **per-skill AGPL-3.0** (vault only) |

## Five official lawve picks

| # | Skill | Vault path | Upstream folder | Upstream SHA | License |
| ---: | --- | --- | --- | --- | --- |
| 1 | IRAC prompt builder | `irac-prompt-builder/` | `irac-prompt-builder-stephane-boghossian` | `f9f28cdccbeb98bbdde010042ea9f525ca427c72` | AGPL-3.0 |
| 2 | Tech contract review | `tech-contract-review/` | `tech-contract-review-parth-desai` | `f9f28cdccbeb98bbdde010042ea9f525ca427c72` | AGPL-3.0 |
| 3 | EU AI Act advisor | `eu-ai-act/` | `eu-ai-act-tanaji-hemant-naik` | `f9f28cdccbeb98bbdde010042ea9f525ca427c72` | See skill LICENSE |
| 4 | Law expertise → skill | `law-expertise-to-skill/` | `law-expertise-to-skill-adrian-lerer` | `f9f28cdccbeb98bbdde010042ea9f525ca427c72` | AGPL-3.0 |
| 5 | Privacy policy (CNIL) | `privacy-policy-generator/` | `privacy-policy-generator-malik-taiar` | `f9f28cdccbeb98bbdde010042ea9f525ca427c72` | AGPL-3.0 |

**Dropped:** `privacy-policy-stephane-boghossian` → use malik-taiar generator instead.

## MIT related (official hire spine)

| Skill | Vault path | Upstream | Upstream SHA |
| --- | --- | --- | --- |
| Contract review | `contract-review/` | [evolsb/claude-legal-skill](https://github.com/evolsb/claude-legal-skill) | `bca0d2e9d5ec81298ddfbfde78fa4f38fb4589b0` |
| Redline render | `legal-redline-tools/` | [evolsb/legal-redline-tools](https://github.com/evolsb/legal-redline-tools) | `1dbc70ddfdf594fc4699c31b9077d15e74be56a0` |

## Helix composites (private overlay pointers)

Composites are **not** AGPL; they live only in `job_app_helix` (UNLICENSED). Vault lists paths for operators syncing mega-skills with overlay.

| Composite | Overlay path | Also |
| --- | --- | --- |
| `helix-legal-ops-apply` | `skills/hire/helix-legal-ops-apply/` | `.agents/skills/helix-legal-ops-apply/` |
| `helix-contract-demo` | `skills/legal/helix-contract-demo/` | `.agents/skills/helix-contract-demo/` |
| `helix-compliance-talk-track` | `skills/legal/helix-compliance-talk-track/` | `.agents/skills/helix-compliance-talk-track/` |

**Career MIT slice:** `job_app_helix/skills/career/` @ [career-ops](https://github.com/career-ops-hq/career-ops) `8831748b952bbe96752b7f0319d46c66069fc544` (see `career/` in overlay, not duplicated in vault `legal/`).

## Mirror status

| Area | Status |
| --- | --- |
| `legal/INDEX.md` | Official HX-28 (this file) |
| lawve + MIT trees | Sync from `job_app_helix/skills/legal/`; binary assets under `privacy-policy-generator/assets/` may lag (CNIL PDFs) |

Operator notes: `/cursor/stores/bc-01a1e4b5-c9cc-74b2-8038-c3140c2d8354/docs/legal-hire-official-status.md`
