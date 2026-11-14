---
name: link-admission
description: "Admit candidate external sources for a named domain, recording authority and relevance. Use at the start of any route that depends on external documentation, registries, or vendor guidance before the sources are bound or cited."
---

# Link Admission

## Purpose

Turn a list of candidate URLs into an admitted set with stated authority and relevance. This Skill owns the admission decision; it does not bind, pin, or audit the admitted sources.

## Procedure

1. Read the candidate sources and the domain they must serve.
2. Classify each source's authority. First-party beats community; community sources are authoritative only for their own tooling.
3. Score relevance against the specific decision the source will inform, not against the domain in general.
4. Reject any candidate missing a URL, an authority classification, or a relevance statement. Record the rejection reason.
5. Emit `LINK_ADMISSION.md` with admitted and rejected sets.

## Operations

- `authority_classifier` — return admitted sources with their authority classification
- `relevance_scorer` — return admitted sources with their relevance statement
- `admission_recorder` — emit the full `LINK_ADMISSION.md` artifact

## Output contract

Produce `LINK_ADMISSION.md` containing each admitted source's id, URL, authority, and relevance, plus every rejected source with its reason.

## Input contract

`candidates`: list of `{url, authority, relevance}`. A single candidate may be passed directly as `url`/`authority`/`relevance`.

## Local validation

The Skill passes when every emitted source carries a non-empty URL, authority, and relevance, and every rejected source is named with a reason.

## Non-goals

Binding sources to device properties, version currency, and claim verification are owned by `machine-binding`, `staleness-assess`, and `library-quality-audit` respectively.
