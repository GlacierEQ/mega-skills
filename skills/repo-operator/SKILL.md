---
name: repo-operator
description: "Operational capability for repo operator."
---

# 🚀 Repo Operator Protocol 2.1 (Hardened)

Hardened universal repository completion and deployment system with strict idempotency and patch-first logic.

## 🌟 Overview
Repo Operator 2.1 is an "Operator-Grade" automation suite designed for high-stakes repository management. It prioritizes safety, transparency, and reproducibility through idempotent file generation and reviewable diffs.

## ⚡ Key Improvements (v2.1)
- **Idempotency**: Will not overwrite existing files (Dockerfile/Workflows) unless `--force` is specified.
- **Patch-First Completion**: Generates `.diff` files for missing elements (README, .gitignore) before applying.
- **Strict Mode**: Fails fast and logs detailed traces to `output/logs/operator.log`.
- **Dry-Run Support**: Full simulation of reports and patches without repo modification.
- **Enhanced Validation**: Integrated gates for `ruff`, `pytest`, `bandit`, and `pip-audit`.

## 🛠 Usage
### Bootstrap / Setup
```bash
# NOTE: scripts/orchestrator.py is not shipped in this skill; see prose below.
```

### Apply Baseline Completion
```bash
# NOTE: scripts/orchestrator.py is not shipped in this skill; see prose below.
```

### Individual Phases
```bash
# NOTE: scripts/orchestrator.py is not shipped in this skill; see prose below.
# NOTE: scripts/orchestrator.py is not shipped in this skill; see prose below.
# NOTE: scripts/orchestrator.py is not shipped in this skill; see prose below.
# NOTE: scripts/orchestrator.py is not shipped in this skill; see prose below.
# NOTE: scripts/orchestrator.py is not shipped in this skill; see prose below.
```

## 📂 Production Artifacts
- `output/repo_map.json`: Deep structural and hygiene analysis.
- `output/logs/operator.log`: Full execution trace.
- `patches/*.diff`: Reviewable changes for missing core files.

---
*Maintained by Casey | v2.1 Hardened Release*

