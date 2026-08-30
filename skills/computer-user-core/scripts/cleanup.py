#!/usr/bin/env python3
"""
Cleanup
Terminates transient subprocesses and cleans temporary screenshot artifacts.
"""

import os
import json
import sys
import glob
import subprocess
import time
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class CleanupResult:
    success: bool
    terminated_pids: List[int]
    removed_files: List[str]
    errors: List[str]


def find_transient_processes(patterns: List[str] = None) -> List[int]:
    """Find transient subprocesses matching patterns."""
    pids = []
    default_patterns = ["screencapture", "osascript", "python.*gui_automator", "python.*screen_capture"]
    search_patterns = patterns or default_patterns
    
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True, text=True
        )
        for line in result.stdout.split('\n'):
            for pattern in search_patterns:
                if pattern in line and "grep" not in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            pids.append(int(parts[1]))
                        except ValueError:
                            pass
    except Exception:
        pass
    
    return list(set(pids))  # Deduplicate


def terminate_processes(pids: List[int], force: bool = False) -> List[int]:
    """Terminate processes by PID."""
    terminated = []
    for pid in pids:
        try:
            if force:
                subprocess.run(["kill", "-9", str(pid)], capture_output=True, timeout=2)
            else:
                subprocess.run(["kill", str(pid)], capture_output=True, timeout=2)
            
            # Verify termination
            import time
            time.sleep(0.1)
            try:
                subprocess.run(["kill", "-0", str(pid)], capture_output=True, timeout=1)
            except subprocess.CalledProcessError:
                # Process terminated
                terminated.append(pid)
        except Exception:
            pass
    
    return terminated


def find_temp_files(patterns: List[str] = None, max_age_hours: float = 24.0) -> List[str]:
    """Find temporary files matching patterns."""
    files = []
    default_patterns = [
        "/tmp/screencap_*.png",
        "/tmp/windowcap_*.png",
        "/tmp/screen_*.png",
        "/tmp/cap_*.png",
        "~/Desktop/Screen Shot *.png",
        "~/Desktop/Screenshot *.png"
    ]
    
    search_patterns = patterns or default_patterns
    max_age_seconds = max_age_hours * 3600
    now = time.time()
    
    for pattern in search_patterns:
        expanded = os.path.expanduser(pattern)
        for filepath in glob.glob(expanded):
            try:
                stat = os.stat(filepath)
                if now - stat.st_mtime <= max_age_seconds:
                    files.append(filepath)
            except Exception:
                pass
    
    return files


def remove_files(filepaths: List[str]) -> List[str]:
    """Remove files, return successfully removed."""
    removed = []
    for filepath in filepaths:
        try:
            os.remove(filepath)
            removed.append(filepath)
        except Exception:
            pass
    return removed


def cleanup_all(patterns: List[str] = None, force: bool = False, max_age_hours: float = 24.0) -> dict:
    """Run full cleanup."""
    # Find and terminate transient processes
    transient_pids = find_transient_processes()
    terminated = terminate_processes(transient_pids, force=force)
    
    # Find and remove temp files
    temp_files = find_temp_files(max_age_hours=max_age_hours)
    removed = remove_files(temp_files)
    
    return {
        "terminated_pids": terminated,
        "removed_files": removed,
        "errors": []
    }


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: cleanup.py <command> [args...]")
        print("Commands:")
        print("  all [--force] [--max-age HOURS]  - Full cleanup")
        print("  processes [--force]              - Terminate transient processes only")
        print("  files [--max-age HOURS]          - Remove temp files only")
        print("  list-processes                   - List transient processes")
        print("  list-files [--max-age HOURS]     - List temp files")
        sys.exit(1)
    
    command = sys.argv[1]
    force = "--force" in sys.argv
    max_age = 24.0
    
    if "--max-age" in sys.argv:
        idx = sys.argv.index("--max-age")
        if idx + 1 < len(sys.argv):
            max_age = float(sys.argv[idx + 1])
    
    if command == "all":
        result = cleanup_all(force=force, max_age_hours=max_age)
        print(json.dumps({
            "terminated_pids": result["terminated_pids"],
            "removed_files": result["removed_files"],
            "errors": result["errors"]
        }, indent=2))
    
    elif command == "processes":
        pids = []
        import sys
        patterns = sys.argv[2:] if len(sys.argv) > 2 else None
        from cleanup import find_transient_processes
        pids = find_transient_processes(patterns)
        terminated = terminate_processes(pids, force=force)
        print(json.dumps({"terminated_pids": terminated}, indent=2))
    
    elif command == "files":
        max_age = max_age
        from cleanup import find_temp_files, remove_files
        files = find_temp_files(max_age_hours=max_age)
        removed = remove_files(files)
        print(json.dumps({"removed_files": removed}, indent=2))
    
    elif command == "list-processes":
        pids = find_transient_processes()
        print(json.dumps({"pids": pids}, indent=2))
    
    elif command == "list-files":
        files = find_temp_files(max_age_hours=max_age)
        print(json.dumps({"files": files}, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
