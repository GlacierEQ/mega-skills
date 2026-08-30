#!/usr/bin/env python3
"""
Screen Capture
Captures visual state using screencapture and inspects pixel dimensions via sips.
"""

import subprocess
import json
import sys
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ScreenCapture:
    path: str
    width: int
    height: int
    format: str
    file_size: int


def capture_screen(output_path: str = None, region: Tuple[int, int, int, int] = None, 
                   display: int = 0, cursor: bool = False) -> ScreenCapture:
    """Capture screen using screencapture."""
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".png", prefix="screencap_")
        os.close(fd)
    
    cmd = ["screencapture", "-x"]  # -x = no sound
    
    if not cursor:
        cmd.append("-C")  # Don't capture cursor
    
    if region:
        x, y, w, h = region
        cmd.extend(["-R", f"{x},{y},{w},{h}"])
    
    if display > 0:
        cmd.extend(["-d", str(display)])
    
    cmd.append(output_path)
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        if result.returncode != 0:
            raise RuntimeError(f"screencapture failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("screencapture timed out")
    
    # Get dimensions using sips
    width, height = get_image_dimensions(output_path)
    
    file_size = os.path.getsize(output_path)
    
    return ScreenCapture(
        path=output_path,
        width=width,
        height=height,
        format="png",
        file_size=os.path.getsize(output_path)
    )


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """Get image dimensions using sips."""
    try:
        result = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", image_path],
            capture_output=True, text=True, timeout=5
        )
        width = height = 0
        for line in result.stdout.split('\n'):
            if "pixelWidth:" in line:
                width = int(line.split(":")[1].strip())
            elif "pixelHeight:" in line:
                height = int(line.split(":")[1].strip())
        return width, height
    except Exception:
        return 0, 0


def capture_window(window_id: int, output_path: str = None) -> str:
    """Capture specific window by ID."""
    if output_path is None:
        import tempfile
        fd, output_path = tempfile.mkstemp(suffix=".png", prefix="windowcap_")
        os.close(fd)
    
    try:
        result = subprocess.run(
            ["screencapture", "-x", "-l", str(window_id), output_path],
            capture_output=True, timeout=10
        )
        if result.returncode != 0:
            raise RuntimeError(f"Window capture failed: {result.stderr}")
        return output_path
    except subprocess.TimeoutExpired:
        raise RuntimeError("Window capture timed out")


def get_displays() -> List[Dict]:
    """Get information about connected displays."""
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType", "-json"],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        displays = []
        for display in data.get("SPDisplaysDataType", []):
            displays.append({
                "name": display.get("_name", "Unknown"),
                "resolution": display.get("spdisplays_resolution", "Unknown"),
                "main": display.get("spdisplays_main", False),
                "builtin": display.get("spdisplays_builtin", False)
            })
        return displays
    except Exception:
        return []


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: screen_capture.py <command> [args...]")
        print("Commands:")
        print("  capture [output.png] [--region x,y,w,h] [--display N] [--cursor]")
        print("  window <window_id> [output.png]")
        print("  displays")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "capture":
        output = None
        region = None
        display = 0
        cursor = False
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--region" and i + 1 < len(sys.argv):
                region = tuple(map(int, sys.argv[i+1].split(",")))
                i += 2
            elif sys.argv[i] == "--display" and i + 1 < len(sys.argv):
                display = int(sys.argv[i+1])
                i += 2
            elif sys.argv[i] == "--cursor":
                cursor = True
                i += 1
            elif not sys.argv[i].startswith("-"):
                output = sys.argv[i]
                i += 1
            else:
                i += 1
        
        cap = capture_screen(output, region=region, display=display, cursor=cursor)
        print(json.dumps({
            "path": cap.path,
            "width": cap.width,
            "height": cap.height,
            "format": cap.format,
            "file_size": cap.file_size
        }, indent=2))
    
    elif command == "window":
        if len(sys.argv) < 3:
            print("Usage: screen_capture.py window <window_id> [output.png]")
            sys.exit(1)
        window_id = int(sys.argv[2])
        output = sys.argv[3] if len(sys.argv) > 3 else None
        path = capture_window(window_id, output)
        print(json.dumps({"path": path}))
    
    elif command == "displays":
        displays = get_displays()
        print(json.dumps(displays, indent=2))
    
    else:
        print(f"Unknown command: {sys.argv[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
