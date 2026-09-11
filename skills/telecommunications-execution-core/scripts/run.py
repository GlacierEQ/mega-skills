#!/usr/bin/env python3
from pathlib import Path
import importlib.util, sys
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("telecom_execution_core", root/"skill.py")
mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod)
raise SystemExit(mod.main(sys.argv[1:]))
