---
name: agy-customizations
description: "Guide for the Antigravity customization system: skills, rules, plugins, hooks, and MCP. Prefer live official docs when local ./docs files are absent. Use to explain loading priority and guide creation of customizations."
---

# Antigravity Customization System Guide

The Antigravity Customization System lets you tailor agent behavior: skills, rules, plugins, hooks, and MCP servers.

## Honesty gate (hidden-harm)

- Local `./docs/*.md` guides are **optional**. If missing, use live Antigravity docs — do not invent loading rules.
- Live starting points:
  - Skills: `https://antigravity.google/docs/skills`
  - Rules / workflows: `https://antigravity.google/docs/rules-workflows`
  - Hooks: `https://antigravity.google/docs/hooks`
  - Plugins: `https://antigravity.google/docs/plugins`
  - MCP: `https://antigravity.google/docs/mcp`

## Customization Types: Quick Reference

| Type | Config File/Folder | Scope | Best For |
|---|---|---|---|
| **Rules** | `GEMINI.md`, `AGENTS.md` | Contextual / Hierarchical | Coding styles, API restrictions, local guidelines |
| **Skills** | `skills/<name>/SKILL.md` | On-Demand (Progressive) | Multi-step procedures and tool workflows |
| **Plugins** | `plugins/<name>/plugin.json` | Bundle | Packaging skills, rules, MCP configs |
| **Hooks** | `hooks.json` | Lifecycle Event | Scripts at agent lifecycle points |
| **MCP Servers** | `mcp_config.json` | Tool Integration | External services / custom tools |

## Discovery Locations

1. **Workspace Customizations** (Project-Specific): `.agents/` (or `.agent/`, `_agents/`, `_agent/`) at project root; walked from CWD up to repo root.
2. **Directory & Project Rules**: `GEMINI.md`, `AGENTS.md`, `.agents/rules/*.md`
3. **Global Configuration** (Machine-Local): `~/.gemini/config/`

## Loading Priority (highest → lowest)

1. Workspace project (hierarchical from CWD → repo root)
2. Declared configurations (`skills.json` / `plugins.json` in workspace)
3. Global discovery (`~/.gemini/config/`)
4. Built-in customizations (mounted by name)
5. Global declared configurations

If local `./docs/json_configs.md` is absent, treat advanced JSON inheritance as `OFFLINE_GAP` and fetch live docs rather than guessing.
