#!/usr/bin/env python3
"""
Merge Engine
Merges or rebases upstream changes onto local branch without mutating overlay contracts.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class MergeResult:
    success: bool
    method: str  # "merge" or "rebase"
    commits_applied: int
    conflicts: List[str]
    error: Optional[str] = None


def run_git(repo_path: Path, args: List[str]) -> Tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path)] + args,
            capture_output=True, text=True, timeout=60
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def get_current_branch(repo_path: Path) -> Optional[str]:
    code, stdout, _ = run_git(repo_path, ["branch", "--show-current"])
    return stdout if code == 0 else None


def get_upstream_branch(repo_path: Path) -> Optional[str]:
    """Find upstream tracking branch."""
    code, stdout, _ = run_git(Path("."), ["branch", "-r", "--list", "upstream/*"])
    branches = [b.strip() for b in stdout.split('\n') if b.strip()] if code == 0 else []
    for b in branches:
        if b.endswith("/main") or b.endswith("/master"):
            return b
    return branches[0] if branches else None


def merge_upstream(repo_path: Path, upstream_branch: str, strategy: str = "recursive") -> MergeResult:
    """Merge upstream branch into current branch."""
    repo_path = Path(repo_path).resolve()
    
    # Check clean
    code, stdout, _ = run_git(repo_path, ["status", "--porcelain"])
    if stdout.strip():
        return MergeResult(False, "merge", 0, [], "Working tree not clean")
    
    # Perform merge
    code, stdout, stderr = run_git(repo_path, ["merge", "--no-ff", f"-s{strategy}", upstream_branch])
    
    if code == 0:
        # Count commits merged
        code, stdout, _ = run_git(Path("."), ["rev-list", "--count", f"HEAD@{1}..HEAD"])
        commits = int(stdout.strip()) if code == 0 and stdout.strip().isdigit() else 1
        return MergeResult(True, "merge", commits, [])
    else:
        # Check for conflicts
        conflicts = []
        if "CONFLICT" in stderr:
            code, stdout, _ = run_git(Path("."), ["diff", "--name-only", "--diff-filter=U"])
            conflicts = [f for f in stdout.split('\n') if f.strip()]
        
        # Abort merge
        run_git(Path("."), ["merge", "--abort"])
        
        return MergeResult(False, "merge", 0, conflicts, stderr)


def rebase_upstream(repo_path: Path, upstream_branch: str) -> MergeResult:
    """Rebase current branch onto upstream."""
    repo_path = Path(repo_path).resolve()
    
    # Check clean
    code, stdout, _ = run_git(repo_path, ["status", "--porcelain"])
    if stdout.strip():
        return MergeResult(False, "rebase", 0, [], "Working tree not clean")
    
    # Perform rebase
    code, stdout, stderr = run_git(repo_path, ["rebase", upstream_branch])
    
    if code == 0:
        code, stdout, _ = run_git(Path("."), ["rev-list", "--count", f"HEAD@{1}..HEAD"])
        commits = int(stdout.strip()) if code == 0 and stdout.strip().isdigit() else 1
        return MergeResult(True, "rebase", int(stdout.strip()) if code == 0 and stdout.strip().isdigit() else 1, [])
    else:
        conflicts = []
        if "CONFLICT" in stderr or "conflict" in stderr.lower():
            code, stdout, _ = run_git(Path("."), ["diff", "--name-only", "--diff-filter=U"])
            conflicts = [f for f in stdout.split('\n') if f.strip()]
        
        # Abort rebase
        run_git(Path("."), ["rebase", "--abort"])
        
        return MergeResult(False, "rebase", 0, conflicts, stderr)


def auto_merge(repo_path: Path, prefer_rebase: bool = False) -> MergeResult:
    """Automatically merge or rebase upstream."""
    upstream = get_upstream_branch(repo_path)
    if not upstream:
        return MergeResult(False, "auto", 0, [], "No upstream branch found")
    
    if prefer_rebase:
        result = rebase_upstream(repo_path, upstream)
        if not result.success:
            # Fallback to merge
            return merge_upstream(repo_path, upstream)
        return result
    else:
        result = merge_upstream(repo_path, upstream)
        if not result.success and "CONFLICT" in (result.error or ""):
            # Try rebase as fallback
            return rebase_upstream(repo_path, upstream)
        return result


def get_conflict_files(repo_path: Path) -> List[str]:
    """Get list of files with merge conflicts."""
    code, stdout, _ = run_git(Path("."), ["diff", "--name-only", "--diff-filter=U"])
    if code == 0:
        return [f for f in stdout.split('\n') if f.strip()]
    return []


def main():
    if len(sys.argv) < 2:
        print("Usage: merge_engine.py <command> [repo_path]")
        print("Commands:")
        print("  merge [repo_path]      - Merge upstream (default: .)")
        print("  rebase [repo_path]     - Rebase onto upstream (default: .)")
        print("  auto [repo_path]       - Auto merge/rebase (default: .)")
        print("  conflicts [repo_path]  - List conflict files (default: .)")
        sys.exit(1)
    
    command = sys.argv[1]
    repo_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    
    if command == "merge":
        upstream = get_upstream_branch(repo_path) or "upstream/main"
        result = merge_upstream(Path(sys.argv[2]) if len(sys.argv) > 2 else Path("."), upstream)
        print(json.dumps({
            "success": result.success,
            "method": result.method,
            "commits_applied": result.commits_applied,
            "conflicts": result.conflicts,
            "error": result.error
        }, indent=2))
        sys.exit(0 if result.success else 1)
    
    elif command == "rebase":
        upstream = get_upstream_branch(repo_path) or "upstream/main"
        result = rebase_upstream(Path(sys.argv[2]) if len(sys.argv) > 2 else Path("."), upstream)
        print(json.dumps({
            "success": result.success,
            "method": result.method,
            "commits_applied": result.commits_applied,
            "conflicts": result.conflicts,
            "error": result.error
        }, indent=2))
        sys.exit(0 if result.success else 1)
    
    elif command == "auto":
        result = auto_merge(Path(sys.argv[2]) if len(sys.argv) > 2 else Path("."), prefer_rebase=False)
        print(json.dumps({
            "success": result.success,
            "method": result.method,
            "commits_applied": result.commits_applied,
            "conflicts": result.conflicts,
            "error": result.error
        }, indent=2))
        sys.exit(0 if result.success else 1)
    
    elif command == "conflicts":
        conflicts = get_conflict_files(Path(sys.argv[2]) if len(sys.argv) > 2 else Path("."))
        print(json.dumps({"conflicts": conflicts}, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
