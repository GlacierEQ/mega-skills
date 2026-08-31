---
name: github-power
description: "Use when working with GitHub repos, PRs, issues, CI/CD, GitHub Actions, GitHub API, GitHub CLI (gh), repository management, code review, issue triage, branch management, merge strategies, conflict resolution, git operations, clone, push, pull, fetch, rebase, cherry-pick, stash, tags, releases, packages, packages registry, GitHub Pages, GitHub Projects, GitHub Discussions, GitHub Security, Dependabot, code scanning, secret scanning, push protection, branch protection rules, required reviews, status checks, merge queues, code owners, CODEOWNERS file, contributing guidelines, templates, issue templates, PR templates, repository templates, GitHub Sponsors, GitHub Actions marketplace, reusable workflows, composite actions, JavaScript actions, Docker actions, self-hosted runners, GitHub-hosted runners, workflow triggers, workflow secrets, workflow variables, workflow outputs, matrix builds, caching, artifacts, logs, deployment environments, environment secrets, protection rules, OIDC, dep..."
---



# GitHub Power Skill — Maximum GitHub Productivity

## Keywords
`github` `gh cli` `github api` `rest api` `graphql api` `repository` `pull request`
`issue` `code review` `branch` `merge` `rebase` `cherry-pick` `clone` `push` `pull`
`fetch` `git` `ci/cd` `github actions` `workflow` `release` `tag` `package` `pages`
`project` `discussion` `security` `dependabot` `code scanning` `secret scanning`
`branch protection` `merge queue` `code owners` `codespaces` `copilot` `webhook`
`automation` `scripting` `deploy` `deploy key` `ssh key` `pat` `fine-grained token`
`github app` `oauth app` `saml sso` `scim` `organization` `team` `enterprise`
`audit log` `compliance` `governance` `multi-repo` `cross-repo` `batch operation`

## Quick Commands

### PR Management
```bash
gh pr list --state open --json number,title,author,labels
gh pr create --title "feat: ..." --body "Description..." --base main
gh pr checkout <pr-number>
gh pr diff <pr-number>
gh pr review <pr-number> --approve/--request-changes
gh pr merge <pr-number> --squash
gh pr ready <pr-number>
gh pr close <pr-number>
gh pr comment <pr-number> --body "Comment..."
gh pr view <pr-number>
gh pr checks <pr-number>
gh pr ready --undo <pr-number>
```

### Issue Management
```bash
gh issue list --state open --json number,title,labels,assignees
gh issue create --title "bug: ..." --body "Steps to reproduce..."
gh issue close <issue-number>
gh issue edit <issue-number> --add-label "priority:high"
gh issue view <issue-number>
gh issue comment <issue-number> --body "Comment..."
gh issue reopen <issue-number>
gh issue transfer <issue-number> --to owner/repo
```

### Repository Info
```bash
gh repo view --json name,description,defaultBranchRef
gh api repos/{owner}/{repo}/actions/runs --jq '.workflow_runs[:5]'
gh api repos/{owner}/{repo}/vulnerability-alerts
gh repo list --json name,updatedAt --jq '.[] | select(.updatedAt > "2026-01-01")'
gh repo clone owner/repo
gh repo create owner/repo --public/--private
gh repo fork owner/repo
gh repo delete owner/repo
```

### CI/CD
```bash
gh workflow list
gh run list --limit 5
gh run watch <run-id>
gh workflow run "Deploy" --ref main
gh run rerun <run-id>
gh run cancel <run-id>
gh run view <run-id>
gh workflow view "CI"
gh workflow enable "Deploy"
gh workflow disable "Deploy"
```

### Branch Operations
```bash
gh api repos/{owner}/{repo}/git/refs/heads --jq '.[].ref'
gh api repos/{owner}/{repo}/git/refs/heads/branch-name
gh api repos/{owner}/{repo}/git/refs -X POST -f "ref=refs/heads/new-branch" -f "sha=abc123"
gh api repos/{owner}/{repo}/git/refs/heads/branch-name -X PATCH -f "sha=def456" -f "force=true"
gh api repos/{owner}/{repo}/git/refs/heads/branch-name -X DELETE
```

### Tags & Releases
```bash
gh release list
gh release view v1.0.0
gh release create v1.0.0 --title "Release 1.0.0" --notes "Changelog..."
gh release delete v1.0.0 --yes
gh api repos/{owner}/{repo}/git/refs/tags
```

## Agent Usage

### PR Review
```
Use the pr-review agent to review PR #123
```

### Issue Triage
```
Use the issue-triage agent to triage open issues
```

### Repo Health
```
Use the repo-health agent to check repository health
```

## Multi-Repo Operations

### Cross-Repo Search
```bash
gh search code "function_name" --repo GlacierEQ/aspen-grove-connectors
gh search issues "bug" --repo GlacierEQ/legal-powerhouse --state open
gh search prs "review" --repo GlacierEQ/quantum-nexus --state open
gh search repos "aspen" --owner GlacierEQ
```

### Batch Operations
```bash
# Close all issues with label "wontfix"
gh issue list --label "wontfix" --json number --jq '.[].number' | xargs -I {} gh issue close {}

# Add label to all open PRs
gh pr list --state open --json number --jq '.[].number' | xargs -I {} gh pr edit {} --add-label "needs-review"

# Comment on all open issues
gh issue list --state open --json number --jq '.[].number' | xargs -I {} gh issue comment {} --body "Automated comment"

# Close all stale PRs
gh pr list --state open --json number,updatedAt --jq '.[] | select(.updatedAt < "2025-01-01") | .number' | xargs -I {} gh pr close {}
```

## Webhooks & Automation

### Create Webhook
```bash
gh api repos/{owner}/{repo}/hooks --method POST \
  -f "config[url]=https://your-webhook.com" \
  -f "config[content_type]=json" \
  -f "events[]=push" \
  -f "events[]=pull_request" \
  -f "events[]=issues" \
  -f "active=true"
```

### GitHub Actions Trigger
```bash
gh api repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches \
  --method POST -f "ref=main"
```

### Create Issue from Template
```bash
gh issue create --template "bug_report" --title "Bug: Description"
gh issue create --template "feature_request" --title "Feature: Description"
```

## GraphQL Queries

### Query Repository
```graphql
query {
  repository(owner: "GlacierEQ", name: "quantum-nexus") {
    name
    description
    defaultBranchRef {
      name
    }
    issues(first: 10, states: OPEN) {
      nodes {
        title
        number
        state
      }
    }
    pullRequests(first: 10, states: OPEN) {
      nodes {
        title
        number
        state
      }
    }
  }
}
```

### Query Organization
```graphql
query {
  organization(login: "GlacierEQ") {
    repositories(first: 20) {
      nodes {
        name
        description
        updatedAt
      }
    }
    teams(first: 10) {
      nodes {
        name
        slug
      }
    }
  }
}
```

## Python Integration

### Using PyGithub
```python
from github import Github

g = Github("YOUR_TOKEN")

# Get repo
repo = g.get_repo("GlacierEQ/quantum-nexus")

# List issues
for issue in repo.get_issues(state="open"):
    print(f"#{issue.number}: {issue.title}")

# Create issue
repo.create_issue(title="New Issue", body="Description...")

# List PRs
for pr in repo.get_pulls(state="open"):
    print(f"PR #{pr.number}: {pr.title}")
```

### Using requests
```python
import requests

headers = {
    "Authorization": "token YOUR_TOKEN",
    "Accept": "application/vnd.github.v3+json"
}

# List repos
response = requests.get("https://api.github.com/user/repos", headers=headers)

# Create issue
issue = {"title": "Bug Report", "body": "Description..."}
response = requests.post(
    "https://api.github.com/repos/GlacierEQ/quantum-nexus/issues",
    json=issue,
    headers=headers
)
```

## Integration Points

### With Quantum Nexus
- Code/evidence storage
- Issue tracking for case
- CI/CD for legal tools

### With Aspen Grove
- GitHub connector for repo sync
- Issue/PR synchronization
- Code review automation

### With Mastermind
- Receipt-backed operations
- Identity for GitHub access
- Lane-based CI/CD

### With Tower of Babel
- Technology selection for projects
- Evidence states for code quality
- Proof classes for verification
