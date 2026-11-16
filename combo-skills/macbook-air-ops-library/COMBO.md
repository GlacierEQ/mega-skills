---
id: macbook-air-ops-library
display_name: MacBook Air Ops Library
ownership: glaciereq
maturity: active
version: 1.0.0
status: active
schema: ../../schemas/combo-skill.schema.json
---

# MacBook Air Ops Library

## Purpose and selection

Authoritative link registry for the `glaciereq-macbook-air-expert` Mega Skill. Owns **link
resolution and citation** for five domains: maintenance, OpenCore/OCLP, AI capability,
machine capability ceilings, and off-prem operations.

Use it whenever a claim or action in those domains needs an external reference. Do **not** use
it as a substitute for the Mega Skill's decision logic — this Combo supplies sources, the Mega
Skill supplies the judgment about which source applies and when.

## Incremental value

Individually, these links are just references. As a Combo they provide: domain-partitioned
resolution, a staleness rule, a first-party-authority rule, and a machine-specific binding so
each link is anchored to the observed device profile rather than to generic advice.

## Member contract

| Order | Member | Receives | Must produce | Local validation |
|---:|---|---|---|---|
| 1 | `link-admission` | Candidate source + domain | Admission record | Authority and relevance stated. |
| 2 | `machine-binding` | Admission record + device profile | Bound reference set | Every link tied to an observed property. |
| 3 | `staleness-assess` | Bound reference set | `LINK_STALENESS.md` | Dates and version pins explicit. |
| 4 | `library-quality-audit` | All prior artifacts | `MACBOOK_AIR_LINK_AUDIT.md` | No unsourced capability claim survives. |

## Handoff contract


## Link registry

All links below are **authoritative entry points**, not claims that their current content was
read. Resolve before citing; record the resolved version in `LINK_STALENESS.md`.

### Domain 1 — Maintenance and hardware health

| Source | Authority | Use for |
|---|---|---|
| https://support.apple.com/mac | Apple first-party | Battery service program eligibility, Air hardware specs by model |
| https://support.apple.com/en-us/101575 | Apple first-party | Checking battery service and cycle-count expectations |
| https://support.apple.com/mac/14 | Apple first-party | macOS Sonoma system requirements and security updates |
| https://support.apple.com/guide/security | Apple first-party | FileVault, SIP, and Gatekeeper reference |
| https://github.com/apple-oss-distributions | Apple OSS | Kernel and system source for `boot-args` interpretation |
| https://dortania.github.io | Dortania community | OpenCore install and post-install guidance (non-authoritative) |
| https://github.com/dortania/OpenCore-Legacy-Patcher | Dortania | OCLP releases, patcher behavior, known-issue tracker |

### Domain 2 — OpenCore and OCLP

| Source | Authority | Use for |
|---|---|---|
| https://dortania.github.io/OpenCore-Install-Guide/ | Dortania community | OpenCore install/config reference |
| https://dortania.github.io/OpenCore-Post-Install/ | Dortania community | Post-install ACPI, kext, and NVRAM guidance |
| https://github.com/acidanthera/OpenCorePkg | Acidanthera | OpenCore release notes and changelog |
| https://github.com/acidanthera/OCLP | Acidanthera | OCLP releases and security advisories |
| https://github.com/dortania/OpenCore-Legacy-Patcher/blob/main/docs/FAQ.md | Dortania | OCLP FAQ, patch-set explanation |
| https://dortania.github.io/Getting-Started-With-ACPI/ | Dortania community | ACPI table and SSDT reference |
| https://github.com/CorpNewt/CorpNewt | CorpNewt | `ProperTree` / `ocvalidate` tooling |


### Domain 4 — Machine capability ceilings

| Source | Authority | Use for |
|---|---|---|
| https://support.apple.com/mac/13 | Apple first-party | Per-model memory and CPU ceilings for comparison |
| https://everymac.com | EveryMac | MacBookAir7,2 launch specs and upgrade history |
| https://en.wikichip.org/wiki/intel/core_i5 | Wikichip | Broadwell i5-5250U ISA and cache detail |
| https://www.intel.com | Intel first-party | ISA feature matrix (confirms no AVX2) |
| https://developer.apple.com/documentation | Apple first-party | Platform requirements per macOS release |

### Domain 5 — Off-prem operations and data safety

| Source | Authority | Use for |
|---|---|---|
| https://support.apple.com/guide/mac-help/back-up-your-mac-mh25222 | Apple first-party | Time Machine destination setup and restore testing |
| https://support.apple.com/guide/mac-help/change-firewall-settings-mchlp1203 | Apple first-party | macOS application firewall configuration |
| https://tailscale.com/kb | Tailscale | Overlay network setup and ACLs |
| https://developers.cloudflare.com/cloudflare-one/ | Cloudflare | WARP and `cloudflared` tunnel configuration |
| https://help.dropbox.com/sync/selective-sync | Dropbox | Selective sync and online-only semantics |
| https://support.apple.com/guide/mac-help/file-providers-mac-mchl5f1a5e2c | Apple first-party | File Provider mounts and why deleting propagates |

## Rules

1. **Cite the resolved source, never memory.** A claim without a link is a claim, not evidence.
2. **First-party outranks community** for Apple platform behavior; community sources
   (Dortania, CorpNewt) are authoritative only for their own tooling.
3. **Bind every link to an observed property.** A generic guide is not evidence about *this*
   host. Record which observed fact the link informs.
4. **Record version and date on resolution.** OCLP and OpenCore move fast; an unpinned link is
   a future contradiction.
5. **Community docs are not a substitute for a restore path.** Any EFI-touching procedure
   requires a verified backup first.
6. **Never read secret material while resolving links.** Redact before reading.

## Compound output

**Artifact:** `MACBOOK_AIR_LINK_AUDIT.md`, containing the domain-partitioned resolved sources
with versions and dates, which observed device property each informs, rejected sources with
reasons, and any capability claim left unsupported.

**Ready for Mega Skill integration when:** every downstream capability claim resolves to an
admitted, bound, non-stale source, and no claim about this host's capability rests on a link
that was never actually resolved.

### Domain 3 — AI capability and local inference

| Source | Authority | Use for |
|---|---|---|
| https://ollama.com/library | Ollama | Model library, tags, and quantized sizes |
| https://github.com/ollama/ollama/blob/main/docs/faq.md | Ollama project | Hardware requirements and VRAM behavior |
| https://huggingface.co/docs/hub | Hugging Face | Model cards, quantization formats, license terms |
| https://github.com/ggml-org/llama.cpp | ggml | Reference CPU inference performance, AVX feature gates |
| https://developer.apple.com/machine-learning | Apple first-party | **Contrast reference** — Apple Silicon baseline, to keep claims honest |

`link-admission` passes admitted sources to `machine-binding`, which binds each to a specific
observed property of the host (model, ISA, RAM, security posture). `staleness-assess` receives
the bound set and records version currency. `library-quality-audit` accepts only when every
capability claim in a downstream artifact resolves to an admitted, bound, non-stale source.
A failed admission returns to `link-admission` with the rejection reason.
