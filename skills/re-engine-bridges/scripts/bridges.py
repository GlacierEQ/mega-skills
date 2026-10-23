#!/usr/bin/env python3
"""Engine-bridge readiness and provider selection.

REA drives caller-supplied engines; it installs none of them. This module
encodes the readiness rules verified live against rea-agents 6.7.0:

- Ghidra: `rea doctor` reports the provider healthy when the install dir
  and a Java 21 exist, but open-time diagnostics are stricter - a
  runtime-only JRE is rejected with unsupported_version ("Update
  JAVA_HOME to the root of a 64-bit full JDK 21 or newer"). Doctor-green
  is not session-ready; the open-time check is authoritative.
- Hopper/IDA/JEB/Kuna follow the same shape: present binary + version
  floor + platform match, each named separately.
- No engine present is a normal state, not an error: the static readers
  carry the investigation until pseudocode is genuinely required.
"""
from __future__ import annotations

PROVIDERS = {
    "ghidra": {"kind": "deep_native", "env": "GHIDRA_INSTALL_DIR",
               "needs": ["install_dir", "analyze_headless", "native_decompiler", "full_jdk_21+"]},
    "hopper": {"kind": "deep_native", "env": "REA_HOPPER_COMMAND", "needs": ["hopper_binary"]},
    "ida": {"kind": "deep_native", "env": "REA_IDA_COMMAND", "needs": ["ida_binary"]},
    "jeb": {"kind": "managed_android", "env": "REA_JEB_COMMAND", "needs": ["jeb_install"]},
    "kuna": {"kind": "deep_native", "env": "KUNA_INSTALL_DIR", "needs": ["kuna_binary"]},
    "jadx": {"kind": "android_code", "env": "REA_JADX_MCP_JAR",
             "needs": ["checksum_pinned_jar", "java_21+"]},
}


def assess_ghidra(diagnostics: dict) -> dict:
    """Assess Ghidra open-time readiness from a diagnostics record (the
    shape REA returns in provider_unavailable details)."""
    checks = {c["name"]: c for c in diagnostics.get("checks", [])}
    blockers = []
    java = checks.get("java", {})
    if not java.get("ok"):
        detail = java.get("detail", "")
        if "runtime only" in detail:
            blockers.append("JAVA_HOME points at a runtime-only JRE; a full JDK 21+ is required")
        else:
            blockers.append(f"java check failed: {detail}")
    for name in ("installation", "headless", "native_decompiler", "version"):
        if name in checks and not checks[name].get("ok"):
            blockers.append(f"{name} check failed: {checks[name].get('detail', '')}")
    return {"provider": "ghidra", "ready": not blockers, "blockers": blockers,
            "version": diagnostics.get("provider_version")}


def select_provider(question_kind: str, available: list[str]) -> dict:
    """Route a question to the shallowest provider that can answer it.
    Deep engines are an escalation, never the default."""
    static_first = {"layout", "strings", "exports", "resources", "metadata"}
    if question_kind in static_first:
        return {"provider": "rea_static_readers", "escalation": False,
                "reason": "structure questions are answered by the target-free static readers"}
    if question_kind in ("pseudocode", "xrefs", "call_graph", "function_analysis"):
        for candidate in ("ghidra", "hopper", "ida", "kuna"):
            if candidate in available:
                return {"provider": candidate, "escalation": True,
                        "reason": "decompilation requires a caller-supplied engine"}
        return {"provider": None, "escalation": True,
                "reason": "no deep engine available; record the question as an unknown instead of guessing"}
    if question_kind == "android_code":
        if "jadx" in available:
            return {"provider": "jadx", "escalation": True, "reason": "JADX-backed lane selected"}
        return {"provider": None, "escalation": True, "reason": "jadx-headless-mcp JAR not supplied"}
    return {"provider": None, "escalation": False, "reason": f"unrouted question kind: {question_kind}"}


def main(argv=None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Route a question to the shallowest sufficient provider.")
    parser.add_argument("question_kind")
    parser.add_argument("--available", default="", help="comma-separated ready providers")
    args = parser.parse_args(argv)
    available = [p for p in args.available.split(",") if p]
    result = select_provider(args.question_kind, available)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
