# Issue schema (ops-only)

## Title

- ≤ 90 characters when possible
- Verb or clear ops outcome first
- Optional prefixes already in the workspace — keep consistent:
  - `[CONNECTOR]`, `[GitHub PR]`, `[Email]`, `CHAIN —`, `P0 —`, mission tags in labels not titles when possible

## Body template

```markdown
## Outcome
One sentence — what done looks like.

## Context
Ops facts only (system, repo, execution id, error class). No sealed strategy.

## Next action
- [ ] Concrete step

## Links
- Tracker / PR / run URL (no secrets in query strings)

## Out of scope
What this ticket is not.
```

## Allowed fields

| Field | Guidance |
|---|---|
| team | Required on create |
| title | Ops outcome |
| description | Template above |
| status | Todo / In Progress / Done / Canceled |
| priority | 0–4 per skill policy |
| labels | Existing workspace labels |
| assignee | User or `me` when asked |
| project | Existing project name/id |
| parentId | For chain steps |
| dueDate | ISO date when real |

## Forbidden content (default deny)

- Minor full name + identifying school/medical detail
- Credentials, bearer tokens, private keys
- Full pleading text or sealed negotiation strategy
- Unredacted third-party personal data not required for the ops step

Public court case numbers already on the public docket may appear when needed
for ops routing (e.g. matter id). Prefer matter issue links over repeating facts.

## GitHub PR mirror body

Keep short — upstream URL, merge state, one next action (`merge`, `close as
duplicate`, `rebase`). Do not paste full PR diffs.
