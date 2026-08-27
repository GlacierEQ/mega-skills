---
name: roadmap-builder
description: Convert a mission contract into a dependency-aware sequence of verifiable work chunks. Use when work must be planned across phases, artifacts, risks, or specialist handoffs.
---

# Roadmap Builder

## Purpose

Create a roadmap that makes the next action unambiguous while keeping future work recoverable. This Skill owns decomposition and phase order, not the detailed method executed by a specialist.

## Procedure

1. Read the mission contract and list the required final artifacts and acceptance criteria.
2. Place uncertainty reduction, safety checks, architecture decisions, and approvals before production work that depends on them.
3. Group related chunks into phases with a measurable entry and exit gate.
4. Define each chunk with one objective, bounded inputs, an owner, a named deliverable, a dependency list, a failure path, and a verification check.
5. Identify true parallelism only when inputs and side effects are independent; otherwise preserve the dependency order.
6. Record the exact next atomic chunk and review the roadmap whenever an assumption, dependency, risk, or deliverable changes.

## Output contract

Produce `ROADMAP.md` containing ordered phases, gates, risks, dependencies, chunk packets, statuses, and one exact next action.

## Local validation

The roadmap passes when every acceptance criterion maps to one or more chunks, no chunk requires hidden context, each phase has a gate, and a future operator can resume at the recorded next action.

## Non-goals

Do not create a task list with no dependencies, call attempted work complete without its check, or use parallelism to conceal ownership ambiguity.
