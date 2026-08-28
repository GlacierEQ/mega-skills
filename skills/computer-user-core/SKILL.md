---
name: computer-user-core
description: Native macOS desktop and runtime orchestration via AppleScript, screencapture, GUI event simulation, window state inspection, and process lifecycle supervision.
---

# Computer User Core

## Purpose

Provide deterministic, non-destructive embodiment within the macOS graphical and runtime environment. Automate window management, screen perception, native process lifecycle, and application control.

## Procedure

1. Inspect target application state and process existence via `pgrep` or AppleScript System Events.
2. Capture visual state using `screencapture -x` and inspect pixel dimensions via `sips`.
3. Formulate precise GUI interaction or keystroke sequences via non-blocking AppleScript commands.
4. Execute requested automation, logging window titles, UI focus changes, and process responses.
5. Verify action outcome through screen state delta, clipboard inspection, or process exit status.
6. Terminate transient subprocesses and clean temporary screenshot artifacts.

## Output contract

Produce `computer-user-action-receipt.json` containing target process PID, action type, window bounds, visual delta confirmation, and execution exit codes.

## Local validation

The procedure passes only when the targeted native application executes the requested operation, visual or process state transition is confirmed, and zero zombie processes are left behind.

## Non-goals

Do not execute destructive UI operations without explicit user parameters. Do not poll GUI elements in unbounded busy-wait loops.
