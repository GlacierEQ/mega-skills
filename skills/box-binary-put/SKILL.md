---
name: "box-binary-put"
description: "Byte-faithful binary file upload to Box with readback verification. Use whenever a file must land in Box bit-identical to the source — evidence, originals, anything hash-bound. Replaces the text-only Box upload_file tool for binaries."
metadata: { "includeInPrompt": true }
---

# box-binary-put

## Purpose
Put one file into a Box folder through the native binary path so the bytes
that land are bit-identical to the source bytes. Fail-closed: integrity
gates refuse bad uploads, and every upload is verified by downloading it
back and comparing size + SHA-256.

Use this instead of the Box MCP `upload_file` tool for any binary file.
`upload_file` is text-only — it rewrites non-text extensions (e.g. `.m4a`
→ `.txt`) and re-encodes bytes, silently corrupting the file.

## Tooling
`bin/box-binary-put` — self-contained Python 3 CLI (no extra deps).

```bash
bin/box-binary-put --source drive:<drive_file_id> --name "a.m4a" --box-folder <id>
bin/box-binary-put --source "dbx:/path/in/dropbox/a.m4a" --name "a.m4a" --box-folder <id>
bin/box-binary-put --source /local/a.m4a --name "a.m4a" --box-folder <id>

# integrity gates (refuse on mismatch, exit 2)
bin/box-binary-put --source drive:<id> --name "a.m4a" --box-folder <id> \
  --expected-size 15926312 --expected-sha256 <hex> \
  --expected-dropbox-hash <hex>

# prove the whole path works right now (round-trips a 1MB scratch file, removes it)
bin/box-binary-put --self-test --box-folder <id>
```

Sources: `drive:<file_id>` (Google Drive), `dbx:</path>` (Dropbox team
namespace via the official connector CLI), or a local path.
Conflict handling: `--on-conflict skip-if-identical` (default) | `refuse` |
`new-version`. Output is a single JSON object; exit 0 = verified/skipped,
1 = failed, 2 = refused.

## Auth
- Box: the `box-cli` connection (direct OAuth). `box-cli status` must show
  connected before use.
- Google Drive source: `hatch_gws_cli` (direct OAuth).
- Dropbox source: `/opt/hatch/bin/dropbox` (official Dropbox connector CLI,
  direct OAuth — no Postman, no token juggling).
- No credentials are read from files or env vars by this skill.

## Operating Rules
1. **Preflight first:** the Box folder is checked before any bytes move.
2. **Fail-closed:** `--expected-*` gates refuse the upload on any mismatch.
   A refusal is never retried.
3. **Transient retries only:** network hiccups retry 3x with backoff. 429s,
   409s, hash mismatches, and refusals are never retried — a 429 is a stop
   signal, not a retry signal.
4. **Double verification:** Box's SHA-1 upload receipt is cross-checked
   against the local file, then the file is downloaded back and size +
   SHA-256 must match exactly.
5. **Never overwrite blindly:** a same-named existing file is downloaded and
   byte-compared — identical skips, different refuses unless
   `--on-conflict new-version`.
6. **Box API response shapes vary:** upload ids arrive as `result.id` or
   `result.entries[0].id` — the tool parses both and requires decimal digits.
7. **Box MCP prerequisite for connector users:** the `get_upload_url` /
   `get_download_url` MCP tools are off by default and need a Box admin
   toggle. Without them (or direct-API OAuth), binary upload through the
   connector is impossible — see `references/RUNBOOK.md`.
