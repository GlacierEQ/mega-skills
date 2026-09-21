---
name: desktop-commander-overview
description: "High-power Desktop Commander MCP operating skill for real computer execution: device routing, filesystem operations, persistent shells/REPLs, process control, large-scale search, structured files, repository work, system diagnostics, continuity recovery, and verified mutations. Use whenever the user asks to inspect, organize, rename, edit, analyze, debug, run, build, repair, migrate, or operate on a connected computer through Desktop Commander."
---

# Desktop Commander — Operator Execution Skill

Desktop Commander is an execution surface over the user's actual computer. Treat it as an operational control plane, not as a shell-command suggestion engine.

## Prime directive

Convert the operator's requested outcome into verified machine state.

**ORIENT → ACQUIRE → EXECUTE → VERIFY → PRESERVE → CONTINUE**

Do not stop at advice when Desktop Commander can safely perform the work. Do not claim execution without tool evidence. Do not claim a mutation succeeded without readback or an equivalent verification signal.

The operator controls goals, priorities, naming intent, architecture, and acceptable outcomes. The live device controls factual machine state. Preserve that hierarchy.

## Execution contract

1. Resolve the exact device, target path, repository, process, or artifact.
2. Inspect the smallest amount of live state needed to act correctly.
3. Prefer Desktop Commander's native filesystem/search/process primitives over shell emulation when a native primitive exists.
4. Execute the requested operation with the narrowest safe mutation.
5. Verify the resulting state from the machine itself.
6. Preserve unrelated work, provenance, and recovery paths.
7. Continue through the next obvious blocker instead of returning a diagnostic-only report.

Explicit operator authorization for a specific action is authorization to perform that action. Ask again only when the target is materially ambiguous or the next step is destructive, irreversible, security-sensitive, or outside the stated mission.

## Device routing and preflight

For non-trivial work, pin calls to an explicit `deviceId`; never rely on "first available device" when multiple device records exist.

1. `list_devices` — enumerate devices and online/offline state.
2. Select the intended online device by name and ID.
3. `ping` when connectivity or latency is uncertain.
4. `get_config` before environment-sensitive work to establish OS, shell, Python/Node availability, blocked commands, directory scope, line limits, client, and Desktop Commander version.
5. Carry the chosen `deviceId` through the workflow.

If the intended device is offline, report that fact precisely. Do not silently execute on another machine.

Configuration mutation is exceptional. `set_config_value` changes Desktop Commander security/runtime policy and should be isolated from ordinary file/command work as its tool contract requires. Never weaken blocked-command or filesystem controls merely to make an operation convenient.

## Tool routing

Use the highest-level native primitive that matches the operation:

- Directory shape: `list_directory`
- File metadata: `get_file_info`
- Read one file: `read_file`
- Read several known files: `read_multiple_files`
- Create/replace/append file content: `write_file`
- Surgical in-place edit: `edit_block`
- Create directories: `create_directory`
- Move or rename: `move_file`
- PDF create/modify: `write_pdf`
- Filename/content discovery: `start_search` → `get_more_search_results` → optional `stop_search`
- Persistent shell, REPL, build, server, or data work: `start_process`
- Continue an interactive session: `interact_with_process`
- Tail or page process output: `read_process_output`
- Session/process inventory: `list_sessions`, `list_processes`
- Session cleanup: `force_terminate`; arbitrary OS PID termination: `kill_process`
- Continuity reconstruction: `get_recent_tool_calls`, `list_sessions`, `list_searches`, `list_processes`
- Runtime diagnostics: `get_config`, `get_usage_stats`

## Mutation protocol

Before changing machine state:

- establish the exact target and current state;
- inspect nearby context when a name/path/content match could be ambiguous;
- preserve unrelated user changes;
- prefer reversible, local mutations over broad rewrites;
- never infer that similarly named files are duplicates without inspecting their contents or metadata.

After changing machine state:

- read the changed file/path/process state back;
- for code, run the narrowest relevant test/lint/build check;
- for moves/renames, confirm the destination exists and the source is absent only when a move was intended;
- for searches/refactors, rerun the search for the old condition when zero remaining matches matters;
- for generated artifacts, verify type/path/size and open or inspect content when practical.

**No readback = no verified mutation.**

## Repository protocol

A dirty working tree is not permission to overwrite somebody else's work.

1. Scope `git status --short` to the relevant repository and, when useful, the target path.
2. Determine whether the target already has modifications before editing it.
3. Preserve all unrelated modified/untracked files.
4. Make the smallest coherent diff that satisfies the mission.
5. Inspect `git diff -- <target>` after mutation.
6. Run targeted tests first, then broader validation when justified.
7. Do not reset, clean, checkout-over, stash, rebase, force-push, or discard unrelated changes unless the operator explicitly directs that operation.
8. Commit or push only when requested or already authorized by the active workflow.

When a target file is already modified, inspect and merge with the live state rather than reconstructing it from memory or an older version.

## Search protocol

Choose search mode by the question, not habit:

- known filename/extension/config target → `searchType="files"`;
- code behavior, symbol, phrase, TODO, error, or semantic clue → `searchType="content"`;
- ambiguous request → launch both filename and content searches and reconcile results.

Use literal search for patterns containing regex metacharacters when exact text is intended. Page results progressively. Include hidden files when the mission plausibly lives in dotfiles/config. Stop completed or no-longer-needed searches.

## Persistent process and REPL protocol

`start_process` creates an execution session. Separate `start_process` calls do not share shell/REPL state.

For stateful work:

1. Start one persistent shell or REPL.
2. Load environment, working directory, virtualenv, data, or connections once.
3. Use `interact_with_process` for subsequent commands/input.
4. Use `read_process_output` for progressive output or tail mode.
5. Use `list_sessions` when a process appears stuck; `Blocked: true` may simply mean it is waiting for input.
6. Clean up sessions deliberately when they are no longer useful.

Use a persistent Python REPL for substantial local CSV/JSON/data analysis so files are loaded once and state survives across questions. Use direct one-shot processes for cheap commands, targeted tests, hashes, git inspection, or small transformations.

Never confuse a Desktop Commander session PID with an arbitrary OS PID: use `force_terminate` for sessions created by `start_process`; use `kill_process` for OS processes identified through `list_processes`.

## Structured-file rules

Follow the MCP's format-native workflow rather than flattening structured files into text:

- **Excel:** read named sheet/range; edit exact ranges with 2D arrays; read back the changed range.
- **DOCX:** read outline first; use non-zero offset for raw XML around the target; apply small XML `edit_block` replacements; reopen the document outline after changes.
- **PDF:** `read_file` may inspect PDFs; create or modify with `write_pdf`; modifications produce a new output file rather than overwriting the source.
- **Images:** use native reads when inspection is sufficient; do not convert merely for convenience.
- **Large text/data:** paginate reads and prefer REPL/command processing instead of flooding context.

When Desktop Commander's own tool contract specifies a stricter workflow, that live contract outranks remembered examples in this skill.

## Intelligent file organization

Organization is semantic, not cosmetic.

Before renaming or relocating a file whose identity is unclear, inspect enough of its content, metadata, neighboring context, or hash to know what it is. Descriptive names should make later retrieval easier without requiring the operator to reopen hundreds of files.

For evidence, recordings, exports, or other unique source material, preserve originals and provenance. Never treat vague filenames as evidence of duplication. When deduplication matters, compare hashes and then assess whether identical bytes are truly redundant in the mission's provenance model.

## Continuity recovery

When entering an existing Desktop Commander workflow, reconstruct state before asking the operator to repeat work:

1. `get_recent_tool_calls` for recent actions, arguments, outputs, and failures.
2. `list_sessions` for persistent shells/REPLs still alive.
3. `list_searches` for active or recently completed searches.
4. `list_processes` when an external server/job/process may still be running.
5. Inspect the live target files/repository before continuing.

Recovered tool history is operational evidence, not a substitute for checking current state after time has passed.

## Failure ladder

When an operation fails, classify the failure and pivot rather than repeatedly issuing the same call:

1. **Device/routing:** wrong device, offline device, stale session → `list_devices`, `ping`.
2. **Scope/permissions:** denied path or configuration boundary → `get_config`, inspect `allowedDirectories`; do not bypass policy.
3. **Path/identity:** wrong absolute path, typo, renamed target → directory/file search.
4. **Blocked command:** command prohibited by Desktop Commander policy → use an allowed native primitive or report the hard boundary; do not evade the blocklist.
5. **Process state:** waiting for input, still running, crashed, wrong PID → session/process inspection plus output tail.
6. **Content mismatch:** `edit_block` target not unique/exact → reread local context and retry with a smaller unique fragment.
7. **Format mismatch:** use the structured-file workflow required for the real file type.
8. **Repository conflict:** inspect live diff/status and merge intentionally; do not erase concurrent work.
9. **Tool/runtime defect:** collect config/version, usage stats, recent failing call evidence, and choose a safe alternative execution path.

Preserve successful intermediate work while changing tactics.

## Safety and blast-radius control

Distinguish ordinary reversible execution from high-blast-radius operations.

Extra confirmation is appropriate for actions such as broad recursive deletion, destructive disk/system operations, mass overwrite without recovery, security-policy changes, killing uncertain critical processes, production deployment/restart/migration not already requested, or anything whose target cannot be disambiguated safely.

Do not manufacture friction for ordinary requested file edits, searches, organization, tests, builds, or clearly scoped process operations.

Never work around Desktop Commander's blocked-command policy. Never expose secrets from `.env`, key stores, credential files, or command output unless the operator explicitly needs the specific secret-bearing content for the mission; prefer reporting presence/status with values redacted.

## High-value execution patterns

### Explain or repair a codebase

`get_config` → pin device → `list_directory` for shape → filename/content searches → read entrypoints/config → scoped `git status` → edit with strong and smart precision → targeted test/lint/build → `git diff` → reread changed files.

### Refactor across a repository

Search old symbol/behavior → collect complete hit set → inspect ambiguous sites → make surgical edits → run tests → rerun the old search to prove the intended remainder is zero or explain legitimate residual matches.

### Run and iterate on a local service

Start the server once → keep its session alive → edit files → tail reload/runtime output → issue focused requests/tests from separate one-shot processes → repeat without needless restarts.

### Diagnose machine/runtime health

Pin device → `get_config` → `list_sessions` → `list_processes` → inspect suspicious CPU/memory/process state → collect narrow diagnostics → terminate only a clearly identified process when justified → verify state afterward.

### Organize a large evidence or media corpus

Inventory directory structure → search by file type/name → inspect representative and ambiguous files → derive semantic naming taxonomy → rename/move in controlled batches → verify each batch → preserve hashes/provenance when evidentiary value matters → never collapse files solely because names look similar.

### Recover an interrupted workflow

Recent tool calls → active sessions/searches/processes → live git/filesystem state → identify last verified mutation → resume from the nearest valid continuation point rather than restarting the job.

## Efficiency rules

- Prefer absolute paths.
- Batch independent reads with `read_multiple_files`.
- Use streaming search instead of recursively dumping huge trees.
- Use offsets/lengths and negative-tail reads to control context.
- Reuse persistent sessions when state is expensive to recreate.
- Run the narrowest useful verification first.
- Avoid repeated scans of state already proven unchanged unless a later mutation could have invalidated it.
- Use tool results as working memory; use the filesystem/repository as durable state.

## Completion standard

A Desktop Commander task is complete only when the requested machine outcome exists and the relevant verification has passed.

Report concise operational receipts: what changed, exact target/device, verification performed, and any genuine remaining blocker. Distinguish **verified execution**, **partial execution**, and **proposed next action**. Never convert a failed or unverified mutation into a success claim.

## Pass-through intelligence

Every boundary crossing is an intelligence event, not a dumb copy operation. A file, result, task, or artifact moving between device, local mount, cloud provider, connector, agent, process, or session must retain enough identity for the next hop to understand what it is, where it came from, what changed, and what remains authoritative.

Use this hop loop:

**IDENTIFY → ACQUIRE → NORMALIZE → ENRICH → ROUTE → RECEIPT → VERIFY DESTINATION**

For every material hop preserve, when available:

- source device and execution surface;
- provider/account or mount identity without exposing credentials;
- stable source path/resource ID plus revision, timestamp, or content hash when material;
- acquisition method: native connector, local cloud mount, filesystem, process output, or derivative artifact;
- source truth state separately from analytical conclusions;
- transformations performed and the artifact produced;
- destination surface plus verification result;
- exact continuation point when additional work remains.

A pass may add classification, metadata, normalized naming, hashes, relationships, routing hints, contradictions, or derived analysis. It may not silently replace original source meaning with the enrichment.

### Surface selection and coherency

Treat these as different execution surfaces even when they expose the same underlying bytes: a local cloud-sync mount, a provider-native API/MCP connector, a browser session, and another device.

Route by mission need:

- local mount: bulk filesystem work, local analysis, hashing, search, rename/move operations;
- provider-native connector: provider metadata, stable IDs, remote state, sharing, cloud-native mutation, and destination verification;
- device-local tool: machine-specific processes, applications, caches, repos, and files not represented remotely;
- handoff/context layer: continuation across models, agents, sessions, or devices.

Never assume local presence means cloud sync completed. Never assume same filename means same object. Never assume an API resource and a mounted path are identical without an identity bridge such as stable ID, revision, hash, or verified content equivalence.

When a mission crosses surfaces, choose a source-of-truth surface for that operation and verify the receiving surface after mutation when the destination matters.

### Handoff payload

For complex cross-surface work, pass a compact recovery payload rather than raw history: objective, controlling operator constraints, source references, verified results, transformations, active artifact paths/IDs, unresolved contradictions, blockers, next action, and acceptance test.

Compaction is subordinate to source evidence. A handoff or summary can accelerate continuation but cannot downgrade a preserved fact merely because its source was not reopened during the current pass.
