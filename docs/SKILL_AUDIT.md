# Skill Manifest Audit

> **Superseded — 2026-09-02 re-audit.** The snapshot below is historical. Re-running the same
> checks against all 709 `skills/*/SKILL.md` files on 2026-09-02 found **0 failures**: no
> unsupported top-level frontmatter keys (`version`, `author`), no description over 1024
> characters, no missing body, and every `name` matches its directory. `scripts/validate_hierarchy.py`
> now also fails when a package exists on disk without a registry entry.

This audit evaluates every `skills/**/SKILL.md` against the baseline Manus skill contract: valid YAML frontmatter, required `name` and `description`, supported metadata keys, name format, description limits, a non-empty body, and name-to-directory alignment.

| Metric | Result |
|---|---:|
| Candidates audited | 146 |
| Passing candidates | 47 |
| Failing candidates | 99 |
| New `skills` meta-skill | PASS (validated separately after this snapshot) |

## Interpretation

A registry entry or a persuasive Markdown body does not by itself make a package loadable. The baseline validator rejects unsupported frontmatter keys. In this repository, the dominant issue is legacy metadata such as `version`, plus a smaller number of overlong or malformed descriptions. The repository hierarchy validator and regression suite are separate checks and do not replace per-package manifest validation.

## Candidate results

| Path | Name | Status | Lines | Blocking issues |
|---|---|---|---:|---|
| `skills/aerospace-trajectory-core` | `aerospace-trajectory-core` | **PASS** | 30 | — |
| `skills/agent-evaluation` | `agent-evaluation` | **FAIL** | 70 | unexpected keys: version |
| `skills/agent-memory-mcp` | `agent-memory-mcp` | **FAIL** | 83 | unexpected keys: version |
| `skills/agent-memory-systems` | `agent-memory-systems` | **FAIL** | 74 | unexpected keys: version |
| `skills/ai-agents-architect` | `ai-agents-architect` | **FAIL** | 92 | unexpected keys: version |
| `skills/ai-deal-finder` | `ai-deal-finder` | **FAIL** | 33 | unexpected keys: version |
| `skills/apex-integrations` | `apex-integrations` | **FAIL** | 35 | unexpected keys: version |
| `skills/apex-sovereign-runtime` | `apex-sovereign-runtime` | **FAIL** | 377 | unexpected keys: version |
| `skills/api-integration` | `api-integration` | **FAIL** | 467 | description exceeds 1024 chars |
| `skills/apple-ane-kv-quantizer` | `apple-ane-kv-quantizer` | **FAIL** | 28 | unexpected keys: version |
| `skills/architecture` | `architecture` | **FAIL** | 59 | unexpected keys: version |
| `skills/aspen-grove` | `aspen-grove` | **FAIL** | 399 | description exceeds 1024 chars |
| `skills/aspen-grove-connectors` | `aspen-grove-connectors` | **FAIL** | 38 | unexpected keys: version |
| `skills/ast-repair-core` | `ast-repair-core` | **PASS** | 32 | — |
| `skills/audio-forensic-core` | `audio-forensic-core` | **PASS** | 31 | — |
| `skills/aws-trainium-neuron-sentinel` | `aws-trainium-neuron-sentinel` | **FAIL** | 29 | unexpected keys: version |
| `skills/brain` | `brain` | **FAIL** | 609 | description exceeds 1024 chars |
| `skills/capability-admission` | `capability-admission` | **PASS** | 31 | — |
| `skills/cc-skill-security-review` | `cc-skill-security-review` | **FAIL** | 496 | unexpected keys: author, version |
| `skills/claim-calibration` | `claim-calibration` | **PASS** | 31 | — |
| `skills/clean-code` | `clean-code` | **FAIL** | 209 | unexpected keys: version |
| `skills/code-review-checklist` | `code-review-checklist` | **FAIL** | 446 | unexpected keys: version |
| `skills/codemaster` | `codemaster` | **FAIL** | 160 | unexpected keys: version |
| `skills/composio` | `composio` | **FAIL** | 82 | unexpected keys: version |
| `skills/computer-user-core` | `computer-user-core` | **PASS** | 31 | — |
| `skills/connector-bridge` | `connector-bridge` | **PASS** | 31 | — |
| `skills/context-capsule` | `context-capsule` | **PASS** | 31 | — |
| `skills/conversation-memory` | `conversation-memory` | **FAIL** | 74 | unexpected keys: version |
| `skills/cross-app-pipeline` | `cross-app-pipeline` | **PASS** | 67 | — |
| `skills/data-analysis` | `data-analysis` | **PASS** | 313 | — |
| `skills/deepseek-mla-moe-sentinel` | `deepseek-mla-moe-sentinel` | **FAIL** | 28 | unexpected keys: version |
| `skills/docker-devops` | `docker-devops` | **FAIL** | 549 | description exceeds 1024 chars |
| `skills/engineering-innovations` | `engineering-innovations` | **FAIL** | 91 | unexpected keys: version |
| `skills/epicenter` | `epicenter` | **PASS** | 39 | — |
| `skills/epistemic-gate` | `epistemic-gate` | **PASS** | 36 | — |
| `skills/evidence-register` | `evidence-register` | **PASS** | 31 | — |
| `skills/far-away-party` | `far-away-party` | **FAIL** | 59 | unexpected keys: version |
| `skills/flagships` | `flagships` | **FAIL** | 86 | unexpected keys: version |
| `skills/fleet-git-harmonizer-core` | `fleet-git-harmonizer-core` | **PASS** | 32 | — |
| `skills/forensic-evidence-chain-core` | `forensic-evidence-chain-core` | **PASS** | 31 | — |
| `skills/fork-overlay-core` | `fork-overlay-core` | **PASS** | 31 | — |
| `skills/forks` | `forks` | **FAIL** | 71 | unexpected keys: version |
| `skills/genesis-prime` | `genesis-prime` | **FAIL** | 37 | unexpected keys: version |
| `skills/github-power` | `github-power` | **FAIL** | 338 | description exceeds 1024 chars |
| `skills/gmail-orchestrator` | `gmail-orchestrator` | **PASS** | 47 | — |
| `skills/handoff-record` | `handoff-record` | **PASS** | 31 | — |
| `skills/icloud-voice-memos` | `icloud-voice-memos` | **PASS** | 57 | — |
| `skills/job-app-portfolio` | `job-app-portfolio` | **FAIL** | 99 | unexpected keys: version |
| `skills/legacy-estate` | `legacy-estate` | **FAIL** | 82 | unexpected keys: version |
| `skills/legal-motion-template` | `legal-motion-template` | **PASS** | 182 | — |
| `skills/legal-powerhouse` | `legal-powerhouse` | **FAIL** | 90 | unexpected keys: version |
| `skills/local-skill` | `local-skill` | **PASS** | 70 | — |
| `skills/long-horizon-core` | `long-horizon-core` | **FAIL** | 48 | unexpected keys: version; description contains angle brackets |
| `skills/make-it-heavy` | `make-it-heavy` | **FAIL** | 98 | unexpected keys: version |
| `skills/master` | `master` | **FAIL** | 178 | unexpected keys: version |
| `skills/mastermind` | `mastermind` | **FAIL** | 121 | unexpected keys: version |
| `skills/mcp-master-server` | `mcp-master-server` | **FAIL** | 38 | unexpected keys: version |
| `skills/mega-agent-core-operations` | `mega-agent-core-operations` | **PASS** | 778 | — |
| `skills/mega-agent-evaluation` | `mega-agent-evaluation` | **FAIL** | 73 | unexpected keys: domains, token_profile |
| `skills/mega-agent-memory-mcp` | `mega-agent-memory-mcp` | **FAIL** | 88 | unexpected keys: domains, token_profile |
| `skills/mega-agent-memory-systems` | `mega-agent-memory-systems` | **FAIL** | 74 | unexpected keys: domains, token_profile |
| `skills/mega-ai-agents-architect` | `mega-ai-agents-architect` | **FAIL** | 96 | unexpected keys: domains, token_profile |
| `skills/mega-ai-deal-finder` | `mega-ai-deal-finder` | **FAIL** | 38 | unexpected keys: domains, token_profile |
| `skills/mega-apex-integrations` | `mega-apex-integrations` | **FAIL** | 39 | unexpected keys: domains, token_profile |
| `skills/mega-apex-sovereign-mastermind` | `mega-apex-sovereign-mastermind` | **PASS** | 726 | — |
| `skills/mega-apex-sovereign-runtime` | `mega-apex-sovereign-runtime` | **FAIL** | 379 | unexpected keys: domains, token_profile |
| `skills/mega-api-integration` | `mega-api-integration` | **FAIL** | 461 | unexpected keys: domains, token_profile |
| `skills/mega-apple-ane-kv-quantizer` | `mega-apple-ane-kv-quantizer` | **FAIL** | 32 | unexpected keys: domains, token_profile |
| `skills/mega-architecture` | `mega-architecture` | **FAIL** | 63 | unexpected keys: domains, token_profile |
| `skills/mega-aspen-grove` | `mega-aspen-grove` | **FAIL** | 299 | unexpected keys: domains, token_profile |
| `skills/mega-aspen-grove-connectors` | `mega-aspen-grove-connectors` | **FAIL** | 42 | unexpected keys: domains, token_profile |
| `skills/mega-aws-trainium-neuron-sentinel` | `mega-aws-trainium-neuron-sentinel` | **FAIL** | 33 | unexpected keys: domains, token_profile |
| `skills/mega-brain` | `mega-brain` | **FAIL** | 601 | unexpected keys: domains, token_profile |
| `skills/mega-cc-skill-security-review` | `mega-cc-skill-security-review` | **FAIL** | 501 | unexpected keys: domains, token_profile |
| `skills/mega-clean-code` | `mega-clean-code` | **FAIL** | 215 | unexpected keys: domains, token_profile |
| `skills/mega-code-review-checklist` | `mega-code-review-checklist` | **FAIL** | 451 | unexpected keys: domains, token_profile |
| `skills/mega-codemaster` | `mega-codemaster` | **FAIL** | 161 | unexpected keys: domains, token_profile |
| `skills/mega-composio` | `mega-composio` | **FAIL** | 84 | unexpected keys: domains, token_profile |
| `skills/mega-conversation-memory` | `mega-conversation-memory` | **FAIL** | 78 | unexpected keys: domains, token_profile |
| `skills/mega-data-analysis` | `mega-data-analysis` | **FAIL** | 310 | unexpected keys: domains, token_profile |
| `skills/mega-deepseek-mla-moe-sentinel` | `mega-deepseek-mla-moe-sentinel` | **FAIL** | 33 | unexpected keys: domains, token_profile |
| `skills/mega-docker-devops` | `mega-docker-devops` | **FAIL** | 540 | unexpected keys: domains, token_profile |
| `skills/mega-engineering-innovations` | `mega-engineering-innovations` | **FAIL** | 92 | unexpected keys: domains, token_profile |
| `skills/mega-filesystem-omni-engine` | `mega-filesystem-omni-engine` | **PASS** | 329 | — |
| `skills/mega-flagships` | `mega-flagships` | **FAIL** | 88 | unexpected keys: domains, token_profile |
| `skills/mega-forks` | `mega-forks` | **FAIL** | 74 | unexpected keys: domains, token_profile |
| `skills/mega-gcp-data-engineering` | `mega-gcp-data-engineering` | **PASS** | 4299 | — |
| `skills/mega-genesis-prime` | `mega-genesis-prime` | **FAIL** | 41 | unexpected keys: domains, token_profile |
| `skills/mega-github-power` | `mega-github-power` | **FAIL** | 280 | unexpected keys: domains, token_profile |
| `skills/mega-job-app-portfolio` | `mega-job-app-portfolio` | **FAIL** | 101 | unexpected keys: domains, token_profile |
| `skills/mega-legacy-estate` | `mega-legacy-estate` | **FAIL** | 85 | unexpected keys: domains, token_profile |
| `skills/mega-legal-forensic-engine` | `mega-legal-forensic-engine` | **PASS** | 361 | — |
| `skills/mega-legal-powerhouse` | `mega-legal-powerhouse` | **FAIL** | 305 | unexpected keys: domains, token_profile |
| `skills/mega-make-it-heavy` | `mega-make-it-heavy` | **FAIL** | 101 | unexpected keys: domains, token_profile |
| `skills/mega-master` | `mega-master` | **FAIL** | 181 | unexpected keys: domains, token_profile |
| `skills/mega-mastermind` | `mega-mastermind` | **FAIL** | 361 | unexpected keys: domains, token_profile |
| `skills/mega-mcp-master-server` | `mega-mcp-master-server` | **FAIL** | 42 | unexpected keys: domains, token_profile |
| `skills/mega-mermicorn-grove` | `mega-mermicorn-grove` | **FAIL** | 38 | unexpected keys: domains, token_profile |
| `skills/mega-mermicorn-mega-boot` | `mega-mermicorn-mega-boot` | **FAIL** | 40 | unexpected keys: domains, token_profile |
| `skills/mega-meta-llama-collective-sentinel` | `mega-meta-llama-collective-sentinel` | **FAIL** | 32 | unexpected keys: domains, token_profile |
| `skills/mega-model-expansion-engine` | `mega-model-expansion-engine` | **PASS** | 126 | — |
| `skills/mega-monolith` | `mega-monolith` | **FAIL** | 103 | unexpected keys: domains, token_profile |
| `skills/mega-openai-reasoning-kv-sentinel` | `mega-openai-reasoning-kv-sentinel` | **FAIL** | 32 | unexpected keys: domains, token_profile |
| `skills/mega-primordial-mesh` | `mega-primordial-mesh` | **FAIL** | 38 | unexpected keys: domains, token_profile |
| `skills/mega-quantum-nexus` | `mega-quantum-nexus` | **FAIL** | 331 | unexpected keys: domains, token_profile |
| `skills/mega-reasoning-variants` | `mega-reasoning-variants` | **FAIL** | 143 | unexpected keys: domains, token_profile |
| `skills/mega-research-study-act` | `—` | **FAIL** | 39 | invalid YAML: mapping values are not allowed here
  in "<unicode string>", line 2, column 40:
     ... tion: 🥋 Research -> Study -> Act: Elite Engineering Protocol
                                         ^; missing name; missing description |
| `skills/mega-skill-forge` | `mega-skill-forge` | **PASS** | 84 | — |
| `skills/mega-skills-test-runner` | `mega-skills-test-runner` | **PASS** | 57 | — |
| `skills/mega-spacex-mission-control` | `mega-spacex-mission-control` | **FAIL** | 32 | unexpected keys: domains, token_profile |
| `skills/mega-supabase-ecosystem` | `mega-supabase-ecosystem` | **PASS** | 305 | — |
| `skills/mega-token-saver` | `mega-token-saver` | **FAIL** | 61 | unexpected keys: domains, token_profile |
| `skills/mega-tower-of-babel` | `mega-tower-of-babel` | **FAIL** | 156 | unexpected keys: domains, token_profile |
| `skills/mega-vercel-ecosystem` | `mega-vercel-ecosystem` | **PASS** | 5662 | — |
| `skills/mega-xai-colossus-2` | `mega-xai-colossus-2` | **FAIL** | 41 | unexpected keys: domains, token_profile |
| `skills/mermicorn-grove` | `mermicorn-grove` | **FAIL** | 34 | unexpected keys: version |
| `skills/mermicorn-mega-boot` | `mermicorn-mega-boot` | **FAIL** | 36 | unexpected keys: version |
| `skills/meta-llama-collective-sentinel` | `meta-llama-collective-sentinel` | **FAIL** | 28 | unexpected keys: version |
| `skills/mission-contract` | `mission-contract` | **PASS** | 31 | — |
| `skills/monolith` | `monolith` | **FAIL** | 100 | unexpected keys: version |
| `skills/neo4j-intelligence-graph` | `neo4j-intelligence-graph` | **PASS** | 254 | — |
| `skills/notion-sync-automation` | `notion-sync-automation` | **PASS** | 139 | — |
| `skills/omni-memory-core` | `omni-memory-core` | **PASS** | 30 | — |
| `skills/openai-reasoning-kv-sentinel` | `openai-reasoning-kv-sentinel` | **FAIL** | 28 | unexpected keys: version |
| `skills/pantheon-extraction` | `pantheon-extraction` | **PASS** | 53 | — |
| `skills/pipeline-compositor` | `pipeline-compositor` | **PASS** | 32 | — |
| `skills/polyglot-rosetta-core` | `polyglot-rosetta-core` | **PASS** | 30 | — |
| `skills/potato-peeler-maximized` | `—` | **FAIL** | 31 | invalid YAML: mapping values are not allowed here
  in "<unicode string>", line 2, column 229:
     ... d custody cases. Primary trigger: Case 1FDV-23-0001009 Kekoa Bar ... 
                                         ^; missing name; missing description |
| `skills/primordial-mesh` | `primordial-mesh` | **FAIL** | 34 | unexpected keys: version |
| `skills/primordial-mesh-titan` | `primordial-mesh-titan` | **PASS** | 30 | — |
| `skills/pro-code-pro-code-double-helix` | `pro-code-pro-code-double-helix` | **PASS** | 27 | — |
| `skills/quality-gate` | `quality-gate` | **PASS** | 31 | — |
| `skills/quantum-nexus` | `quantum-nexus` | **FAIL** | 38 | unexpected keys: version |
| `skills/reasoning-variants` | `reasoning-variants` | **FAIL** | 141 | unexpected keys: version |
| `skills/research-study-act` | `research-study-act` | **FAIL** | 34 | unexpected keys: version; description contains angle brackets |
| `skills/resource-preflight` | `resource-preflight` | **PASS** | 31 | — |
| `skills/roadmap-builder` | `roadmap-builder` | **PASS** | 31 | — |
| `skills/security-review` | `security-review` | **FAIL** | 497 | unexpected keys: version |
| `skills/skills` | `skills` | **PASS** | 40 | — |
| `skills/sovereign-genesis-prime` | `sovereign-genesis-prime` | **PASS** | 30 | — |
| `skills/spacex-mission-control` | `spacex-mission-control` | **FAIL** | 28 | unexpected keys: version |
| `skills/token-saver` | `token-saver` | **FAIL** | 57 | unexpected keys: version |
| `skills/tower-of-babel` | `tower-of-babel` | **FAIL** | 154 | unexpected keys: version |
| `skills/whisperx-audio-processing` | `whisperx-audio-processing` | **PASS** | 109 | — |
| `skills/work-packet` | `work-packet` | **PASS** | 31 | — |
| `skills/xai-colossus-2` | `xai-colossus-2` | **FAIL** | 37 | unexpected keys: version |

## Commands used

```bash
python /home/ubuntu/skills/skill-creator/scripts/quick_validate.py /absolute/path/to/skill
python scripts/validate_hierarchy.py
python -m unittest discover -s tests -v
git diff --check
```

The new `skills` meta-skill at `skills/skills/SKILL.md` defines the audit workflow and points to `skills/skills/references/manifest-contract.md` for the compact contract.
