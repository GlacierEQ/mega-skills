---
name: machine-binding
description: "Bind each admitted external source to a specific observed property of the target machine so generic guidance becomes evidence about that host. Use after link admission and before any source is cited as support for a device-specific claim."
---

# Machine Binding

## Purpose

Anchor admitted sources to observed device properties. A generic guide is not evidence about a specific host. This Skill owns that anchoring; admission, pinning, and auditing belong to the other link Skills.

## Procedure

1. Read the admitted source set and the observed device profile.
2. For each source, name the exact observed property it informs — model, ISA, RAM, security posture, storage capacity, and so on.
3. Reject any source that cannot be tied to an observed property. Generic advice with no anchor is not evidence about this machine.
4. Emit `MACHINE_BINDING.md` with the bound set and the unbound remainder.

## Operations

- `property_resolver` — return bound sources with their bound property
- `scope_comparator` — return the device profile keys plus bound/unbound counts
- `binding_recorder` — emit the full `MACHINE_BINDING.md` artifact

## Output contract

Produce `MACHINE_BINDING.md` mapping each source id to its bound device property, and listing every unbound source with the reason it carries no observed anchor.

## Input contract

`links`: admitted source objects. `device_profile`: observed property map used to validate the anchor.

## Local validation

The Skill passes when every bound source names a property present in the device profile, and no source is bound to a property that was never observed.

## Non-goals

Admitting sources, assessing version currency, and rejecting unsupported claims are owned by `link-admission`, `staleness-assess`, and `library-quality-audit`.
