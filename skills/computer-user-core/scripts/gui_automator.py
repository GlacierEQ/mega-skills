#!/usr/bin/env python3
"""
GUI Automator
Formulates precise GUI interaction sequences via non-blocking AppleScript.
"""

import subprocess
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class GUIAction:
    action: str  # click, type, key, scroll, move
    target: Dict  # {type: "coordinate"|"element"|"text", value: ...}
    params: Dict


def click_at(x: int, y: int, clicks: int = 1, button: str = "left", delay: float = 0.1) -> bool:
    """Click at screen coordinates."""
    script = f'''
    tell application "System Events"
        set originalPos to (get mouse location)
        set mouse location to {{{int(x)}, {int(y)}}}
        delay {0.05}
        repeat {int(max(1, int(x)))} times
            click at {{{int(x)}, {int(y)}}} using {{left}}
            delay {0.05}
        end repeat
        set mouse location to originalPos
    end tell
    '''
    # Fix the script
    script = f'''
    tell application "System Events"
        set originalPos to (get mouse location)
        set mouse location to {{{int(x)}, {int(y)}}}
        delay 0.05
        click at {{{int(x)}, {int(y)}}}
        delay {0.1}
        set mouse location to originalPos
    end tell
    '''
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def click_element(bundle_id: str, element_description: str) -> bool:
    """Click UI element by description."""
    script = f'''
    tell application "System Events"
        tell process "{bundle_id}"
            click (first UI element whose description contains "{element_description}")
        end tell
    end tell
    '''
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def type_text(text: str, delay: float = 0.01) -> bool:
    """Type text at current cursor position."""
    # Escape quotes and special chars
    escaped = text.replace('"', '\\"').replace('\\', '\\\\')
    script = f'''
    tell application "System Events"
        keystroke "{escaped}"
    end tell
    '''
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def press_key(key: str, modifiers: List[str] = None) -> bool:
    """Press a key with optional modifiers."""
    mod_map = {
        "cmd": "command down",
        "ctrl": "control down",
        "alt": "option down",
        "shift": "shift down"
    }
    
    mod_str = ""
    if modifiers:
        mod_list = [mod_map.get(m, m) for m in modifiers if m in mod_map]
        if mod_list:
            mod_str = " using {" + ", ".join(mod_list) + "}"
    
    script = f'''
    tell application "System Events"
        keystroke "{key}"{mod_str}
    end tell
    '''
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def hotkey(key: str, *modifiers) -> bool:
    """Press key combination (e.g., hotkey('c', 'cmd') for Cmd+C)."""
    return press_key(key, list(modifiers))


def get_mouse_position() -> Tuple[int, int]:
    """Get current mouse position."""
    script = 'tell application "System Events" to get mouse location'
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # Parse "x, y"
            coords = result.stdout.strip().split(", ")
            return int(coords[0]), int(coords[1])
    except Exception:
        pass
    return 0, 0


def scroll(direction: str = "down", amount: int = 3, x: int = None, y: int = None) -> bool:
    """Scroll at current or specified position."""
    if x is not None and y is not None:
        # Move to position first
        script = f'''
        tell application "System Events"
            set mouse location to {{{int(x)}, {int(y)}}}
            delay 0.05
            scroll {direction} {int(amount)}
        end tell
        '''
    else:
        script = f'''
        tell application "System Events"
            scroll {direction} {int(amount)}
        end tell
        '''
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def activate_app(bundle_id: str) -> bool:
    """Bring application to front."""
    script = f'''
    tell application id "{bundle_id}" to activate
    '''
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def wait_for_app(bundle_id: str, timeout: float = 10.0) -> bool:
    """Wait for application to become active."""
    start = time.time()
    while time.time() - start < timeout:
        script = f'''
        tell application "System Events"
            return (name of first process whose frontmost is true and bundle identifier is "{bundle_id}")
        end tell
        '''
        try:
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: gui_automator.py <command> [args...]")
        print("Commands:")
        print("  click <x> <y>              - Click at coordinates")
        print("  type <text>                - Type text")
        print("  key <key> [modifiers...]   - Press key with modifiers")
        print("  hotkey <key> <mod1> [mod2] - Press key combo (e.g., hotkey c cmd)")
        print("  scroll <up|down> [amount]  - Scroll")
        print("  activate <bundle_id>       - Activate app")
        print("  wait <bundle_id> [timeout] - Wait for app to activate")
        print("  position                   - Get mouse position")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "click":
        if len(sys.argv) < 4:
            print("Usage: gui_automator.py click <x> <y>")
            sys.exit(1)
        success = click_at(int(sys.argv[2]), int(sys.argv[3]))
        print(json.dumps({"success": success}))
    
    elif command == "type":
        if len(sys.argv) < 3:
            print("Usage: gui_automator.py type <text>")
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        success = type_text(text)
        print(json.dumps({"success": success}))
    
    elif command == "key":
        if len(sys.argv) < 3:
            print("Usage: gui_automator.py key <key> [modifiers...]")
            sys.exit(1)
        key = sys.argv[2]
        modifiers = sys.argv[3:] if len(sys.argv) > 3 else []
        success = press_key(key, modifiers)
        print(json.dumps({"success": success}))
    
    elif command == "hotkey":
        if len(sys.argv) < 4:
            print("Usage: gui_automator.py hotkey <key> <mod1> [mod2...]")
            sys.exit(1)
        success = hotkey(sys.argv[2], *sys.argv[3:])
        print(json.dumps({"success": success}))
    
    elif command == "scroll":
        if len(sys.argv) < 3:
            print("Usage: gui_automator.py scroll <up|down> [amount]")
            sys.exit(1)
        direction = sys.argv[2]
        amount = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        success = scroll(direction, amount)
        print(json.dumps({"success": success}))
    
    elif command == "activate":
        if len(sys.argv) < 3:
            print("Usage: gui_automator.py activate <bundle_id>")
            sys.exit(1)
        success = activate_app(sys.argv[2])
        print(json.dumps({"success": success}))
    
    elif command == "wait":
        if len(sys.argv) < 3:
            print("Usage: gui_automator.py wait <bundle_id> [timeout]")
            sys.exit(1)
        bundle_id = sys.argv[2]
        timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
        success = wait_for_app(bundle_id, timeout)
        print(json.dumps({"success": success}))
    
    elif command == "position":
        x, y = get_mouse_position()
        print(json.dumps({"x": x, "y": y}))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
