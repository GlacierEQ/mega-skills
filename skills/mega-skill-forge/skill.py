#!/usr/bin/env python3
"""
mega-skill-forge. 
Entry point for mega-skill-forge skill.
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def main():
    """Main entry point - dispatches to appropriate script based on args."""
    if len(sys.argv) < 2:
        print(f"Usage: mega-skill-forge <command> [args...]")
        print("Available commands:")
        for sn in ['repo_inspector.py', 'mission_drafter.py', 'combo_selector.py', 'readiness_gate.py', 'contract_author.py', 'registry_publisher.py', 'hierarchy_validator.py', 'release_coordinator.py']:
            print(f"  {sn.replace('.py', '')}")
        return 1
    
    command = sys.argv[1]
    script_path = Path(__file__).parent / "scripts" / f"{command}.py"
    
    if not script_path.exists():
        script_path = Path(__file__).parent / "scripts" / f"{command.replace('-', '_')}.py"
    
    if not script_path.exists():
        print(f"Unknown command: {command}")
        return 1
    
    exec_globals = {"__name__": "__main__"}
    exec(script_path.read_text(), exec_globals)
    return 0

if __name__ == "__main__":
    sys.exit(main())
