# Box Binary Upload Runbook (for ChatGPT / Grok / any assistant)

Goal: move a file into Box **byte-faithful** — the bytes that land must be
bit-identical to the source bytes. Verified end to end 2026-10-03 (six .m4a
originals, Dropbox → Google Drive → Box, SHA-256 verified on readback).

## Why this runbook exists

Box's MCP `upload_file` tool is **text-only**. It accepts a whitelist of text
extensions; anything else gets rewritten (e.g. `.m4a` → `.txt`) and the bytes
get re-encoded. What lands is a corrupted derivative: it may open, but its
hash won't match the original, which kills chain of custody. If you need the
file to survive hashing, you must use the binary path below.

## Prerequisites (pick one)

**Option A — Box MCP with binary tools enabled (recommended for connector users).**
The Box MCP server ships `get_upload_url` / `get_download_url`, but they are
**off by default**. A Box admin must enable them in the MCP server
configuration. Verify: list the advertised tools — if you see only
`upload_file` and no `get_upload_url`, the toggle is off and you cannot do
binary upload through the connector. Stop and use Option B.

**Option B — Direct Box API with OAuth.**
Any OAuth token with write scope works, no MCP needed. Exact command:
```bash
curl -X POST https://upload.box.com/api/2.0/files/content \
  -H "Authorization: Bearer $BOX_TOKEN" \
  -F "attributes={\"name\":\"file.m4a\",\"parent\":{\"id\":\"<folder_id>\"}}" \
  -F "file=@file.m4a"
# response: {"entries":[{"id":"2505299538978", ...}]} — id is nested
```
This is what the reference CLI below uses.

**You also need:** the source file's bytes in your execution environment
(downloaded from Dropbox/Drive/URL into your sandbox — not a link, not a
preview), and an HTTP client that sends raw bytes with no text decoding
(curl, or Python `requests` with the file opened `'rb'`).

## The recipe

1. **Get the bytes.** Download the source file to local disk. Record its size.
2. **Hash before upload.** `sha256sum file` — this is your ground truth.
   If you have an expected hash (manifest, sender), compare now; refuse on mismatch.
3. **Get an upload URL** (Option A: call `get_upload_url`; Option B: use the
   upload endpoint directly with your OAuth token).
4. **PUT the raw bytes.** Do not decode, re-encode, or transcode. Example:
   ```bash
   curl -X PUT --data-binary @file.m4a \
     -H "Content-Type: application/octet-stream" \
     "$UPLOAD_URL"
   ```
   Python equivalent:
   ```python
   import requests
   with open("file.m4a", "rb") as f:
       r = requests.put(upload_url, data=f,
                        headers={"Content-Type": "application/octet-stream"})
   r.raise_for_status()
   file_id = r.json()["entries"][0]["id"]  # note: id is nested, see pitfalls
   ```
5. **Read it back.** Download the file from Box by its id.
6. **Verify.** Size and SHA-256 of the readback must exactly match step 2.
   Only then is the upload complete. Anything else is a failure — say so.

## Failure modes we hit (so you don't)

| Symptom | Cause | Fix |
|---|---|---|
| Uploaded file renamed to `.txt` | Used text-only `upload_file` | Use the binary path (Option A/B) |
| `get_upload_url` not in tool list | Admin toggle off (default) | Enable it, or use Option B |
| Upload "succeeds" but no file id in response | Box nests it: `result.id` on some calls, `result.entries[0].id` on 201-created | Parse both shapes; require decimal digits |
| HTTP 409 `item_name_in_use` | File already exists | Download the existing copy, compare bytes: identical → done; different → refuse or upload a new version, never silently overwrite |
| Dropbox download fails with "could not issue a download URL" | Dropbox MCP server-side breakage (observed 2026-10-03) | Use an alternate source leg (we routed via Google Drive) |
| Repeated 429s from a credential API | You're retrying into a quota wall | **Stop.** A 429 is a stop signal, not a retry signal. Never fetch credentials per file — fetch once per run and cache |

## Reference implementation

`box_binary_put.py` (same directory) implements all of the above as one
hardened command: source from Drive/Dropbox/local, optional expected
size/SHA-256/Dropbox-hash gates, conflict handling (`skip-if-identical` /
`refuse` / `new-version`), readback verification, JSON result, meaningful
exit codes. Tested live 2026-10-03.

```bash
box_binary_put.py --source drive:<drive_id> --name "a.m4a" \
  --box-folder <folder_id> --expected-sha256 <hex>
# {"status": "verified", "box_file_id": "2505291189182", ...}
```
