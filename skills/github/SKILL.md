---
name: "github"
description: "GitHub: repos, pull requests, issues. Authenticated as GlacierEQ via the gh CLI (verified live 2026-10-03)."
---

# Github

## Purpose
Read and manage the user's GitHub repos, pull requests, and issues.

## Tooling
`bin/github-api` — thin wrapper over the GitHub REST API (https://api.github.com).
Auth order: (1) the `gh` CLI's own secure auth store (`gh auth token`) —
logged in as GlacierEQ 2026-10-03; (2) fallback to the `Github` variable and
other stored GitHub vars in the Postman `Muse Keys` environment (those were
401-dead as of 2026-10-03; kept for when keys rotate). The token is never
stored in this skill.

Usage:
  github-api GET /user
  github-api GET /repos/OWNER/REPO/issues --params '{"state":"open"}'
  github-api POST /repos/OWNER/REPO/issues --data '{"title":"Bug"}'

Prints `{"status": <code>, "body": <json>}`.

`gh` itself is also authenticated (same account), and `gh auth setup-git`
wires it as git's credential helper — `git clone/push/pull` to github.com
work with no extra auth.

## Batching doctrine (big calls, not many little calls)
REST is one-call-per-thing. For bulk work use GraphQL: one query returns
dozens of nodes, and `--paginate` walks an entire connection automatically.
Estate census pattern: 14 GraphQL queries covered 1313 repos — REST would
have needed thousands of calls and blown the rate limit.

`bin/github-graphql` — same auth and rate-limit retries as `github-api`:
```bash
# one cheap query (costs 1 point)
github-graphql --query '{ viewer { login } rateLimit { remaining } }'

# auto-paginate a whole connection (query must take $after and select
# pageInfo { hasNextPage endCursor } + nodes/edges)
github-graphql --paginate viewer.repositories --page-size 100 --query '
  query($after: String, $page_size: Int) {
    viewer { repositories(first: $page_size, after: $after,
              orderBy: {field: PUSHED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes { name pushedAt isPrivate }
    } }
  }'
# {"status": 200, "pages": 14, "nodes": [ ... ]}
```
Prefer one paginated GraphQL call over loops of REST calls. Filter
server-side (`orderBy`, `first`) before spending calls.

## Common operations
```bash
# REST API (any endpoint)
github-api GET /user
github-api GET /repos/OWNER/REPO/issues --params '{"state":"open"}'
github-api POST /repos/OWNER/REPO/issues --data '{"title":"Bug"}'

# Repos, PRs, issues via gh
gh repo clone OWNER/REPO
gh repo view OWNER/REPO --json name,updatedAt
gh pr list --repo OWNER/REPO --state open
gh pr create --repo OWNER/REPO --title "T" --body "B"
gh issue list --repo OWNER/REPO
gh issue create --repo OWNER/REPO --title "T" --body "B"

# git over HTTPS (credential helper handles auth)
git clone https://github.com/OWNER/REPO.git
git push origin main
```

## Auth
Primary: `gh` CLI secure store (`~/.config/gh/hosts.yml`, user-owned).
Fallback: Postman `Muse Keys` GitHub vars. Never ask the user to paste a raw
key in chat, set a secret environment variable, pass a secret flag, or write
an auth file — use `gh auth login` / the existing stores.

A 401 or 403 is a question about the request before it is a question about the
key. Only once a request that definitely carried the key is still rejected,
treat the stored credential as suspect. Note: GitHub rate-limits tokens; a
403 mentioning rate limits usually clears within the hour — stop and wait,
do not hammer.

## Operating Rules
1. Use this skill when the user asks for Github or this provider's API.
2. Restrict authenticated requests to: api.github.com.
3. Do not print, log, or persist raw credentials.
