#!/usr/bin/env python3
"""
Process Inspector
Inspects target application state and process existence via pgrep/AppleScript.
"""

import subprocess
import json
import sys
import plistlib
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ProcessInfo:
    pid: int
    name: str
    bundle_id: Optional[str] = None
    path: Optional[str] = None
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    windows: List[Dict] = None


def get_processes_by_name(name: str) -> List[ProcessInfo]:
    """Find processes by name using pgrep and ps."""
    processes = []
    
    # Use pgrep to find PIDs
    try:
        result = subprocess.run(
            ["pgrep", "-f", name],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return processes
        
        pids = [int(p) for p in result.stdout.strip().split() if p.strip().isdigit()]
    except Exception:
        return processes
    
    # Get detailed info for each PID
    for pid in pids:
        try:
            ps_result = subprocess.run(
                ["ps", "-p", str(pid), "-o", "pid,comm,%cpu,%mem,command"],
                capture_output=True, text=True
            )
            lines = ps_result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split(None, 4)
                if len(parts) >= 4:
                    processes.append(ProcessInfo(
                        pid=pid,
                        name=parts[1],
                        cpu_percent=float(parts[2]),
                        memory_mb=float(parts[3]) * 1024  # Convert % to approximate MB
                    ))
        except Exception:
            pass
    
    return processes


def get_processes_by_bundle_id(bundle_id: str) -> List[ProcessInfo]:
    """Find processes by bundle identifier using AppleScript."""
    processes = []
    
    script = f'''
    tell application "System Events"
        set procList to {{}}
        repeat with proc in (every process whose bundle identifier is "{bundle_id}")
            set end of procList to {{pid:unix id of proc, name:name of proc, bundle_id:"{bundle_id}"}}
        end repeat
        return procList
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            # Parse AppleScript record output
            output = result.stdout.strip()
            # Parse format: {pid:123, name:"App", bundle_id:"com.example"}
            import re
            for match in re.finditer(r'pid:(\d+), name:"([^"]+)", bundle_id:"([^"]+)"', output):
                pid, name, bid = match.groups()
                processes.append(ProcessInfo(
                    pid=int(pid),
                    name=name,
                    bundle_id=bid
                ))
    except Exception:
        pass
    
    return processes


def is_process_running(identifier: str, by_bundle_id: bool = False) -> bool:
    """Check if a process is running."""
    if by_bundle_id:
        return len(get_processes_by_bundle_id(identifier)) > 0
    return len(get_processes_by_name(identifier)) > 0


def get_app_windows(bundle_id: str) -> List[Dict]:
    """Get window information for an application."""
    script = f'''
    tell application "System Events"
        set winList to {{}}
        repeat with proc in (every process whose bundle identifier is "{bundle_id}")
            repeat with w in (every window of proc)
                set end of winList to {{title:name of w, bounds:position of w & size of w, pid:unix id of proc}}
            end repeat
        end repeat
        return winList
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            # Parse window list
            output = result.stdout.strip()
            windows = []
            # Parse format: {title:"Title", bounds:{0, 0, 800, 600}, pid:123}
            import re
            for match in re.finditer(r'title:"([^"]+)", bounds:\{([^}]+)\}, pid:(\d+)', output):
                title, bounds_str, pid = match.groups()
                bounds = [int(x.strip()) for x in bounds_str.split(',')]
                windows.append({
                    "title": title,
                    "bounds": bounds,  # [x, y, width, height]
                    "pid": int(pid)
                })
            return windows
    except Exception:
        pass
    
    return []


def main():
    if len(sys.argv) < 2:
        print("Usage: process_inspector.py <command> [args...]")
        print("Commands:")
        print("  list <name>              - List processes by name")
        print("  list-bundle <bundle_id>  - List processes by bundle ID")
        print("  check <name>             - Check if process running")
        print("  check-bundle <bundle_id> - Check by bundle ID")
        print("  windows <bundle_id>      - Get window info for app")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        if len(sys.argv) < 3:
            print("Usage: process_inspector.py list <name>")
            sys.exit(1)
        processes = get_processes_by_name(sys.argv[2])
        print(json.dumps([{
            "pid": p.pid,
            "name": p.name,
            "cpu_percent": p.cpu_percent,
            "memory_mb": round(p.memory_mb, 2)
        } for p in processes], indent=2))
    
    elif command == "list-bundle":
        if len(sys.argv) < 3:
            print("Usage: process_inspector.py list-bundle <bundle_id>")
            sys.exit(1)
        processes = get_processes_by_bundle_id(sys.argv[2])
        print(json.dumps([{
            "pid": p.pid,
            "name": p.name,
            "bundle_id": p.bundle_id
        } for p in processes], indent=2))
    
    elif command == "check":
        if len(sys.argv) < 3:
            print("Usage: process_inspector.py check <name>")
            sys.exit(1)
        running = is_process_running(sys.argv[2])
        print(json.dumps({"running": running}))
    
    elif command == "check-bundle":
        if len(sys.argv) < 3:
            print("Usage: process_inspector.py check-bundle <bundle_id>")
            sys.exit(1)
        running = is_process_running(sys.argv[2], by_bundle_id=True)
        print(json.dumps({"running": running}))
    
    elif command == "windows":
        if len(sys.argv) < 3:
            print("Usage: process_inspector.py windows <bundle_id>")
            sys.exit(1)
        windows = get_app_windows(sys.argv[2])
        print(json.dumps(windows, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
