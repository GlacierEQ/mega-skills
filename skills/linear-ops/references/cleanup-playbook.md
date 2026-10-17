# Cleanup playbook

Use when the user asks to clean, triage, or reduce Linear noise. Prefer **status
and priority edits** over creating new issues (workspaces may hit free issue limits).

## Pass 1 — GitHub PR mirrors

Cluster titles containing `[GitHub PR]`.

| Upstream state | Linear action |
|---|---|
| Merged | Done + one-line note |
| Closed without merge | Canceled or Done with reason |
| Open, duplicate topic (e.g. three hash opts) | Keep one In Progress; mark others duplicate/Canceled |
| Open, still relevant | Low or Medium priority — not High |

Example hash cluster observed historically — treat as one workstream:
`fileboss-whisperx-processor` hash/digest PRs.

## Pass 2 — Completed noise

Issues already `Done` / `statusType=completed` should not appear in the default
execution view. Do not reopen. Suggest view filter `status != Done`.

## Pass 3 — WIP cap

1. Count In Progress.
2. If > 8 per active operator, list candidates to demote to Todo.
3. Demote only with user approval when issues are mission parents
   (labels `Execution Chain`, `Case Binding`, `Mission:*`).
4. Safe auto-suggest demotion without approval — pure PR mirrors and hygiene.

## Pass 4 — Priority deflation

If High+Urgent exceed ~40% of open issues:

- PR mirrors → Low
- Blocked chain steps → Medium
- True external deadline → keep Urgent/High

Report before/after counts.

## Pass 5 — Template and duplicate steps

Groups like `[3/3] GitHub + Notion + Linear` across missions are valid only if
each still has a real next action. Cancel or Todo+block when the parent chain
already absorbed the work.

July-era P0 stacks still Todo while newer mesh issues cover the same matter —
propose **supersede** (link newer issue), do not silent-delete.

## Pass 6 — Mission parents (approval required)

Do **not** bulk-close:

- `Mission: KEKOA`
- `Mission: CHERRY`
- `Mission: JOB`
- 1FDV / Legal Case Management parents

Require explicit operator approval per parent or per labeled batch.

## Reporting format

```text
Cleanup report
- Scanned: N issues
- PR mirrors closed: [ids]
- Demoted to Todo: [ids]
- Priority changes: [id: old → new]
- Skipped (needs approval): [ids + reason]
```
