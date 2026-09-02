---
name: attio
description: "Operational capability for attio."
---

# 💼 Attio CRM Integration

## Overview
This module provides a unified interface for managing legal cases, contacts, and relationship intelligence using the Attio API.

## Configuration
- \`ATTIO_API_KEY\`: Your Attio API Bearer token.
- \`ATTIO_WORKSPACE_ID\`: The ID of your Attio workspace.

## Planned Tools
- \`list_cases\`: Retrieve all active legal cases from Attio.
- \`create_record\`: Create a new person or company record.
- \`add_note\`: Add a legal note or exhibit reference to an Attio record.
- \`sync_memory\`: Sync Attio relationship data with the Neo4j Knowledge Graph.

## Usage
Currently under development as a custom MCP server.

## Contract Completion

The original instructions above are preserved verbatim; the sections below complete the skill contract.

## Use When

Use this skill when the requested task matches the capability described above and this is the most specific available skill for the work.

## Operating Method

1. Identify the concrete outcome, inputs, and constraints.
2. Inspect relevant project state or artifacts before making changes.
3. Load only the bundled resources needed for the current task.
4. Execute the narrowest complete workflow that produces the requested outcome.
5. Verify the result with observable output, tests, or source-backed evidence.
6. Report the produced artifact or exact resulting state. Never claim execution that did not occur.

## Progressive Disclosure

Keep the core procedure concise. Load detailed references, scripts, and tests only when they are needed.

### Scripts
- scripts/run.py
- scripts/this_skill.py
- skill.py

### Tests
- tests/test_attio.py

## Verification

Instruction readiness and executable readiness are separate. Scripts and integrations must earn behavioral proof through the repository readiness assay before they are described as executed or behavior-verified.

## Boundaries

- Do not invent missing implementation.
- A package-discovery adapter is not evidence of domain execution.
- Preserve upstream provenance and existing project semantics.
- Report unavailable credentials, services, or destructive dependencies precisely instead of fabricating success.
