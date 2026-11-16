---
name: antigravity-guide
description: "Guide for Google Antigravity (AGY): CLI (agy), IDE, Antigravity 2.0 app, Python SDK, slash commands, keybindings, and customizations. Prefer live official docs; do not invent offline reference files. Activate when the user asks about Antigravity, AGY, the agy CLI, Antigravity IDE, or Antigravity 2.0."
---

# Google Antigravity (AGY) Guide & Sitemap

Google Antigravity is an AI-first development platform.

## Honesty gate (hidden-harm)

- This skill’s `skill.py` is a **compatibility adapter only** (`capability_executed: false`). It does **not** run the Antigravity CLI.
- Offline `references/` subdocs are **optional**. If a linked file is missing, treat that as `OFFLINE_GAP` and fetch the **live** page — never invent CLI behavior from memory alone.
- Operator estate note: some local `antigravity_cli.py` wrappers hardcode Mac absolute paths; those are **not** portable evidence that `agy` is installed on the current machine. Check `command -v agy` / product install before claiming CLI availability.

## 1. Surfaces (live docs are authority)

When the user asks about a surface, fetch the matching live page if offline refs are absent or stale:

| Surface | Live docs | Offline (if present) |
|---|---|---|
| Antigravity CLI (`agy`) | https://antigravity.google/docs | `references/cli.md` |
| Antigravity IDE | https://antigravity.google/docs | `references/ide.md` |
| Antigravity 2.0 app | https://antigravity.google/docs | `references/app.md` |
| Antigravity SDK | https://github.com/google-antigravity/antigravity-sdk-python | `references/sdk.md` |

## 2. Official sitemap (fetch live when needed)

- **Main Documentation Home**: `https://antigravity.google/docs`
- **Skills**: `https://antigravity.google/docs/skills`
- **Rules**: `https://antigravity.google/docs/rules-workflows`
- **Hooks**: `https://antigravity.google/docs/hooks`
- **Plugins**: `https://antigravity.google/docs/plugins`
- **Sidecars**: `https://antigravity.google/docs/sidecars`
- **Model Context Protocol (MCP)**: `https://antigravity.google/docs/mcp`
- **Browser Automation & Testing**: `https://antigravity.google/docs/ide/browser`
- **Agent Permissions & Security**: `https://antigravity.google/docs/permissions`
- **Changelog & Release Notes**: `https://antigravity.google/changelog`
- **Troubleshooting & Support**: `https://antigravity.google/support`

## 3. Related skill

For customization loading priority (rules/skills/plugins/hooks/MCP), also see `agy-customizations` — same honesty rule: missing `./docs/` files ⇒ live docs, not fabricated content.
