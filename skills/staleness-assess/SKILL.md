---
name: staleness-assess
description: "Record version and resolution-date currency for bound external sources so a moving target cannot silently become a contradiction. Use after machine binding and before any bound source is cited in a durable artifact."
---

# Staleness Assessment

## Purpose

Pin the currency of bound sources. Upstream projects move fast; an unpinned link is a future contradiction. This Skill owns version and date tracking only.

## Procedure

1. Read the bound source set.
2. Resolve each source and record the version observed and the date it was resolved.
3. Treat any source lacking a version or a resolution date as unpinned, regardless of how authoritative it appears.
4. Emit `LINK_STALENESS.md` with the current set and the unpinned remainder.

## Operations

- `version_pinner` — return sources with their pinned versions
- `date_checker` — return the ids of unpinned sources
- `staleness_recorder` — emit the full `LINK_STALENESS.md` artifact

## Output contract

Produce `LINK_STALENESS.md` recording each source's id, URL, version, and resolution date, plus every unpinned source.

## Input contract

`sources`: bound source objects carrying optional `version` and `resolved_at` fields.

## Local validation

The Skill passes when every current source has both a version and a resolution date, and no unpinned source is presented as current.

## Non-goals

Admitting sources, binding them to device properties, and rejecting unsupported claims are owned by `link-admission`, `machine-binding`, and `library-quality-audit`.
