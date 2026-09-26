---
name: research-source-access
description: "Read-only source access for the APEX Max Research Engine. Implements the three declared firewall actions: search_workspace (local corpus search), read_connected_sources (configured connector reads), and load_public_sources (guarded public HTTP GET). Never writes, never mutates, never sends data outward."
---

# Research Source Access

## Purpose

Concrete implementation of the three source-access actions declared by
`apex-max-research-engine` in its firewall policy. Before this skill those
actions were declared but unimplemented, so any mission that actually invoked
them had no code to run.

This skill is **read-only by construction**: every operation returns data to
the caller and never writes to the workspace, never mutates a remote system, and
never transmits anything outward.

## Actions

| Action | What it does | Network |
|--------|--------------|---------|
| `search_workspace` | Ranked term search across a local corpus of text/JSON/Markdown files | No |
| `read_connected_sources` | Read through a named, pre-configured connector (see `connectors.json`) | Only if that connector declares it |
| `load_public_sources` | Guarded HTTP `GET` of a public URL | Yes — read only |

## Safety contract

`load_public_sources` is the only networked action, and it is deliberately narrow:

- **`GET` only.** Any other HTTP method is rejected.
- **Read-only schemes only.** `https` by default; `http` permitted only when
  `allow_insecure_http` is explicitly set.
- **No credentials, ever.** Authorization headers, cookies, and API keys are
  never attached. A URL containing embedded credentials (`user:pass@host`) is
  rejected outright.
- **No private address space.** Hostnames resolving to loopback, link-local,
  private, or reserved ranges are refused, which blocks SSRF against internal
  infrastructure.
- **Bounded.** Response size, redirect count, and timeout are all capped.
- **No transmission.** Nothing from the workspace is ever included in an
  outbound request. These are pull-only reads.

`read_connected_sources` delegates to connectors that are themselves declared
read-only; a connector that declares a write capability is refused.

## Usage

```bash
python skills/research-source-access/skill.py search-workspace \
    --input corpus.json --output results.json

python skills/research-source-access/skill.py load-public-sources \
    --input urls.json --output sources.json
```

## Evidence

Every operation emits a receipt containing the resolved path or URL, a
SHA-256 digest of the retrieved content, byte counts, and any refusal reason.
Refusals are reported, never silently dropped, so a mission can record that a
source was declined and why.
