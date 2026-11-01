#!/usr/bin/env python3
"""Skill Creator executable entrypoint; delegates to bounded, local authoring."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'scripts'))
from author_skill import main

if __name__ == '__main__':
    raise SystemExit(main())
