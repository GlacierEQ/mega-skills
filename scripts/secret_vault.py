#!/usr/bin/env python3
"""Seal secrets on the program side and bind them where they are used.

No plaintext values are printed, committed, or force-pushed.
If a value is provided, it is sealed and bound. Missing values are requested
by name only. Rotation panic is not the interface.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


WRAP_ENV = "GLACIEREQ_SEAL_WRAP"
WRAP_FILE_NAME = ".seal-wrap"
SEALED_NAME = ".sealed-secrets.json"
CATALOG_PATH = Path("secrets/catalog.json")

# Names only. Values never belong in git.
DEFAULT_CATALOG = {
    "schema_version": 1,
    "bindings": {
        "GITHUB_TOKEN": {"use": "gh", "env": "GH_TOKEN"},
        "GH_TOKEN": {"use": "gh", "env": "GH_TOKEN"},
        "BUILDKITE_API_TOKEN": {"use": "buildkite", "env": "BUILDKITE_API_TOKEN"},
        "VERCEL_TOKEN": {"use": "vercel", "env": "VERCEL_TOKEN"},
        "XAI_API_KEY": {"use": "runtime", "env": "XAI_API_KEY"},
        "OPENAI_API_KEY": {"use": "runtime", "env": "OPENAI_API_KEY"},
        "ANTHROPIC_API_KEY": {"use": "runtime", "env": "ANTHROPIC_API_KEY"},
        "AWS_ACCESS_KEY_ID": {"use": "runtime", "env": "AWS_ACCESS_KEY_ID"},
        "AWS_SECRET_ACCESS_KEY": {"use": "runtime", "env": "AWS_SECRET_ACCESS_KEY"},
        "SUPABASE_SERVICE_ROLE_KEY": {"use": "runtime", "env": "SUPABASE_SERVICE_ROLE_KEY"},
    },
}


class VaultError(RuntimeError):
    pass


def _repo_root(start: Path | None = None) -> Path:
    cwd = (start or Path.cwd()).resolve()
    return cwd


def wrap_path(root: Path) -> Path:
    return root / WRAP_FILE_NAME


def sealed_path(root: Path) -> Path:
    return root / SEALED_NAME


def load_catalog(root: Path) -> dict[str, Any]:
    path = root / CATALOG_PATH
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return DEFAULT_CATALOG


def ensure_wrap_key(root: Path) -> bytes:
    if os.environ.get(WRAP_ENV):
        return os.environ[WRAP_ENV].encode("utf-8")
    path = wrap_path(root)
    if path.is_file():
        return path.read_bytes().strip()
    key = base64.urlsafe_b64encode(os.urandom(32))
    path.write_bytes(key + b"\n")
    path.chmod(0o600)
    return key


def _derive(wrap: bytes, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", wrap, salt, 200_000, dklen=32)


def _xor(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def seal_value(wrap: bytes, plaintext: str) -> dict[str, str]:
    salt = os.urandom(16)
    key = _derive(wrap, salt)
    raw = plaintext.encode("utf-8")
    # Stream pad so values of any length stay off the command line.
    pad = hashlib.sha256(key).digest()
    material = pad
    while len(material) < len(raw):
        material += hashlib.sha256(material[-32:] + key).digest()
    cipher = _xor(raw, material[: len(raw)])
    mac = hashlib.sha256(key + salt + cipher).hexdigest()
    return {
        "v": 1,
        "salt": base64.b64encode(salt).decode("ascii"),
        "ct": base64.b64encode(cipher).decode("ascii"),
        "mac": mac,
    }


def unseal_value(wrap: bytes, envelope: dict[str, str]) -> str:
    salt = base64.b64decode(envelope["salt"])
    cipher = base64.b64decode(envelope["ct"])
    key = _derive(wrap, salt)
    expect = hashlib.sha256(key + salt + cipher).hexdigest()
    if not hmac_eq(expect, envelope.get("mac", "")):
        raise VaultError("sealed value failed integrity check")
    pad = hashlib.sha256(key).digest()
    material = pad
    while len(material) < len(cipher):
        material += hashlib.sha256(material[-32:] + key).digest()
    raw = _xor(cipher, material[: len(cipher)])
    return raw.decode("utf-8")


def hmac_eq(left: str, right: str) -> bool:
    if len(left) != len(right):
        return False
    acc = 0
    for a, b in zip(left.encode(), right.encode()):
        acc |= a ^ b
    return acc == 0


def load_store(root: Path) -> dict[str, Any]:
    path = sealed_path(root)
    if not path.is_file():
        return {"schema_version": 1, "values": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def write_store(root: Path, store: dict[str, Any]) -> None:
    path = sealed_path(root)
    path.write_text(json.dumps(store, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)


def bind_from_environ(root: Path) -> list[str]:
    catalog = load_catalog(root)
    wrap = ensure_wrap_key(root)
    store = load_store(root)
    sealed_now = []
    for name, spec in catalog.get("bindings", {}).items():
        env_name = spec.get("env", name)
        value = os.environ.get(env_name) or os.environ.get(name)
        if not value:
            continue
        store.setdefault("values", {})[name] = {
            "use": spec.get("use", "runtime"),
            "env": env_name,
            "envelope": seal_value(wrap, value),
        }
        sealed_now.append(name)
    write_store(root, store)
    return sealed_now


def materialize(root: Path, names: list[str] | None = None) -> dict[str, str]:
    wrap = ensure_wrap_key(root)
    store = load_store(root)
    catalog = load_catalog(root)
    wanted = names or list(catalog.get("bindings", {}))
    out: dict[str, str] = {}
    for name in wanted:
        record = store.get("values", {}).get(name)
        if not record:
            env_name = catalog.get("bindings", {}).get(name, {}).get("env", name)
            live = os.environ.get(env_name) or os.environ.get(name)
            if live:
                out[env_name] = live
            continue
        out[record.get("env", name)] = unseal_value(wrap, record["envelope"])
    return out


def status_report(root: Path) -> dict[str, Any]:
    catalog = load_catalog(root)
    store = load_store(root)
    rows = []
    for name, spec in catalog.get("bindings", {}).items():
        env_name = spec.get("env", name)
        present = name in store.get("values", {}) or bool(os.environ.get(env_name) or os.environ.get(name))
        rows.append(
            {
                "name": name,
                "use": spec.get("use"),
                "bound": present,
                "source": "sealed" if name in store.get("values", {}) else ("env" if present else "missing"),
            }
        )
    return {
        "schema_version": 1,
        "wrap_ready": wrap_path(root).is_file() or bool(os.environ.get(WRAP_ENV)),
        "bindings": rows,
        "missing": [row["name"] for row in rows if not row["bound"]],
        "rule": "values are sealed or read from env; never printed; never force-pushed",
    }


def apply_runtime_env(values: dict[str, str]) -> None:
    runtime = Path(".env.runtime")
    lines = [f"{key}={values[key]}" for key in sorted(values)]
    runtime.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    runtime.chmod(0o600)


def assert_never_force_push(argv: list[str]) -> None:
    joined = " ".join(argv).lower()
    if "push --force" in joined or "push -f" in joined or "git push --force" in joined:
        raise VaultError("force-push is forbidden")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--seal-env", action="store_true", help="seal any catalog secrets already present in the environment")
    parser.add_argument("--seal", nargs=2, metavar=("NAME", "VALUE"), help="seal one named secret")
    parser.add_argument("--apply", action="store_true", help="write gitignored .env.runtime from sealed or env values")
    parser.add_argument("--write-catalog", action="store_true")
    args = parser.parse_args(argv)
    assert_never_force_push(sys.argv)
    root = args.root.resolve()
    if args.write_catalog:
        path = root / CATALOG_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file():
            path.write_text(json.dumps(DEFAULT_CATALOG, indent=2) + "\n", encoding="utf-8")
    if args.seal:
        name, value = args.seal
        wrap = ensure_wrap_key(root)
        store = load_store(root)
        spec = load_catalog(root).get("bindings", {}).get(name, {"use": "runtime", "env": name})
        store.setdefault("values", {})[name] = {
            "use": spec.get("use", "runtime"),
            "env": spec.get("env", name),
            "envelope": seal_value(wrap, value),
        }
        write_store(root, store)
        print(json.dumps({"status": "SEALED", "name": name}))
        return 0
    if args.seal_env:
        sealed = bind_from_environ(root)
        print(json.dumps({"status": "SEALED_ENV", "names": sealed}))
        return 0
    if args.apply:
        values = materialize(root)
        apply_runtime_env(values)
        print(json.dumps({"status": "BOUND", "count": len(values), "target": ".env.runtime"}))
        return 0
    report = status_report(root)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
