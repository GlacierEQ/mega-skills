---
name: ast-repair-core
description: "Closed-loop AST traceback parsing, pinpoint defect localization, and surgical automated code patching to achieve 100% green test assertions."
---


# AST Repair Core

## Purpose

Execute automated closed-loop code repair by executing test harnesses, intercepting failure tracebacks, isolating exact AST nodes with `ApexEpistemicChunker`, synthesizing strong and smart surgical patches, and verifying resolution.

## Procedure

1. Execute declared test command (`pytest`, `npm test`, `cargo test`).
2. If tests pass, exit with success. If tests fail, intercept stderr traceback.
3. Parse failing source file path and line number from the stack trace.
4. Extract the exact AST code chunk enclosing the defect using `ApexEpistemicChunker`.
5. Dispatch chunk and error context to synthesizer model to generate surgical replacement code.
6. Apply replacement directly to source file on disk.
7. Re-execute test suite and loop until 100% green or bounded attempt limit reached.

## Output contract

Produce `ast-repair-execution-record.json` with failing commands, stack traces, AST chunk boundaries, applied diffs, and final verification status.

## Local validation

The procedure passes only when the test suite passes 100% green following the applied patch, with zero introduced syntax or lint errors.

## Non-goals

Do not apply superficial stubs (`return True`, `pass`). Do not modify test assertion files to force green status.
