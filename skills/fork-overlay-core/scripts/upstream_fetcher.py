#!/usr/bin/env python3
"""
Upstream Fetcher
Fetches latest upstream commits and verifies tracking branch integrity.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class UpstreamStatus:
    repo_path: str
    upstream_url: str
    upstream_branch: str
    local_branch: str
    ahead: int
    behind: int
    diverged: bool
    clean: bool
    fetch_success: bool
    error: Optional[str] = None


def run_git(repo_path: Path, args: List[str]) -> Tuple[int, str, str]:
    """Run git command in repo."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path)] + args,
            capture_output=True, text=True, timeout=30
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def get_remote_url(repo_path: Path, remote: str = "upstream") -> Optional[str]:
    """Get remote URL."""
    code, stdout, _ = run_git(repo_path, ["remote", "get-url", remote])
    if code == 0:
        return stdout
    return None


def get_current_branch(repo_path: Path) -> Optional[str]:
    """Get current branch name."""
    code, stdout, _ = run_git(repo_path, ["branch", "--show-current"])
    if code == 0:
        return stdout
    return None


def fetch_upstream(repo_path: Path, remote: str = "upstream") -> bool:
    """Fetch latest upstream commits."""
    code, _, _ = run_git(repo_path, ["fetch", remote])
    return code == 0


def get_branch_status(repo_path: Path, local_branch: str, upstream_branch: str) -> Dict:
    """Get ahead/behind counts."""
    code, stdout, _ = run_git(repo_path, ["rev-list", "--left-right", "--count", f"{local_branch}...{upstream_branch}"])
    if code == 0:
        parts = stdout.strip().split('\t')
        if len(parts) == 2:
            return {"ahead": int(parts[0]), "behind": int(parts[1])}
    return {"ahead": 0, "behind": 0}


def check_working_tree_clean(repo_path: Path) -> bool:
    """Check if working tree is clean."""
    code, stdout, _ = run_git(repo_path, ["status", "--porcelain"])
    return code == 0 and stdout.strip() == ""


def verify_upstream_tracking(repo_path: Path) -> UpstreamStatus:
    """Verify upstream tracking branch integrity."""
    repo_path = Path(repo_path).resolve()
    
    # Get current branch
    local_branch = get_current_branch(repo_path)
    if not local_branch:
        return UpstreamStatus(
            repo_path=str(repo_path),
            upstream_url="",
            upstream_branch="",
            local_branch="",
            ahead=0, behind=0, diverged=True, clean=False, fetch_success=False,
            error="No current branch"
        )
    
    # Get upstream remote
    upstream_url = get_remote_url(repo_path, "upstream")
    if not upstream_url:
        return UpstreamStatus(
            repo_path=str(repo_path),
            upstream_url="",
            upstream_branch="",
            local_branch=local_branch,
            ahead=0, behind=0, diverged=True, clean=False, fetch_success=False,
            error="No upstream remote"
        )
    
    # Fetch upstream
    fetch_ok = fetch_upstream(repo_path)
    if not fetch_ok:
        return UpstreamStatus(
            repo_path=str(repo_path),
            upstream_url=upstream_url,
            upstream_branch="",
            local_branch=local_branch,
            ahead=0, behind=0, diverged=True, clean=False, fetch_success=False,
            error="Fetch failed"
        )
    
    # Determine upstream branch (typically upstream/main or upstream/master)
    code, stdout, _ = run_git(Path("."), ["branch", "-r", "--list", "upstream/*"])
    upstream_branches = [b.strip() for b in stdout.split('\n') if b.strip()] if code == 0 else []
    
    upstream_branch = None
    for b in upstream_branches:
        if b.endswith("/main") or b.endswith("/master"):
            upstream_branch = b
            break
    if not upstream_branch and upstream_branches:
        upstream_branch = upstream_branches[0]
    
    if not upstream_branch:
        return UpstreamStatus(
            repo_path=str(repo_path),
            upstream_url=upstream_url,
            upstream_branch="",
            local_branch=local_branch,
            ahead=0, behind=0, diverged=True, clean=False, fetch_success=True,
            error="No upstream tracking branch found"
        )
    
    # Get ahead/behind
    status = get_branch_status(repo_path, local_branch, upstream_branch)
    
    # Check clean
    clean = check_working_tree_clean(repo_path)
    
    return UpstreamStatus(
        repo_path=str(repo_path),
        upstream_url=upstream_url,
        upstream_branch=upstream_branch,
        local_branch=local_branch,
        ahead=status["ahead"],
        behind=status["behind"],
        diverged=status["ahead"] > 0 and status["behind"] > 0,
        clean=clean,
        fetch_success=True
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: upstream_fetcher.py <command> [repo_path]")
        print("Commands:")
        print("  verify [repo_path]   - Verify upstream tracking (default: .)")
        print("  fetch [repo_path]    - Fetch upstream (default: .)")
        print("  status [repo_path]   - Show branch status (default: .)")
        sys.exit(1)
    
    command = sys.argv[1]
    repo_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    
    if command == "verify":
        status = verify_upstream_tracking(repo_path)
        print(json.dumps({
            "repo_path": status.repo_path,
            "upstream_url": status.upstream_url,
            "upstream_branch": status.upstream_branch,
            "local_branch": status.local_branch,
            "ahead": status.ahead,
            "behind": status.behind,
            "diverged": status.diverged,
            "clean": status.clean,
            "fetch_success": status.fetch_success,
            "error": status.error
        }, indent=2))
        sys.exit(0 if status.fetch_success and not status.error else 1)
    
    elif command == "fetch":
        if fetch_upstream(repo_path):
            print(json.dumps({"success": True}))
        else:
            print(json.dumps({"success": False, "error": "Fetch failed"}))
            sys.exit(1)
    
    elif command == "status":
        st = verify_upstream_tracking(repo_path)
        print(json.dumps({
            "local_branch": st.local_branch,
            "upstream_branch": st.upstream_branch,
            "ahead": st.ahead,
            "behind": st.behind,
            "diverged": st.diverged,
            "clean": st.clean
        }, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
