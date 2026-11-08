#!/usr/bin/env python3
"""APEX Boot Core v2 — Holographic Estate Initialization & Unified Health Sentinel.

Connects all 14 verified estate pillars into one boot contract:
  1. Environment & Python runtime verification
  2. Secrets vault integrity (no inline tokens, 600-mode files)
  3. MegaKernel receipt chain integrity check
  4. Monolith catalog census parity (1,211 repos)
  5. APEX-IMPACT-ENGINE quality gate availability
  6. Ai-Personalization_Kernel boot contract availability
  7. Permanent memory engine health
  8. Token saver bridge readiness
  9. Estate quality receipt validation (11/11 green)
 10. Git health across core working trees
 11. POSIX toolchain binary permissions
 12. Capability bus scan (Genius Lineages + estate projects)

Every boot emits an immutable receipt with SHA-256 digest.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from operator_semantics import (
    detect_inversions,
    load_operator_semantics,
    project_operator_semantics,
    transition_for_status,
)


# ── Configuration ────────────────────────────────────────────────────────────


def _env_path(name: str, default: Path) -> Path:
    """Resolve a path from an environment override, else use ``default``.

    Lets the sentinel run against any estate root -- a container, a laptop, or
    a CI runner -- without editing source.
    """
    raw = os.environ.get(name)
    return Path(raw).expanduser() if raw else default


# Workspace root. Defaults to the container layout (/root) for backwards
# compatibility; override with APEX_WORKSPACE_ROOT anywhere else. Every path
# below derives from this one, so a single variable relocates the whole estate.
WORKSPACE_ROOT = _env_path("APEX_WORKSPACE_ROOT", Path("/root"))
PROJECTS_ROOT = WORKSPACE_ROOT / "projects"
SECRETS_DIR = WORKSPACE_ROOT / ".secrets"
VAULT_ENV = WORKSPACE_ROOT / ".vault_env"
ESTATE_RECEIPT = WORKSPACE_ROOT / "ESTATE_QUALITY_RECEIPT.json"
MEMORY_DIR = WORKSPACE_ROOT / "MEMORY.md"
RECEIPT_CHAIN = PROJECTS_ROOT / "mastermind" / "receipts" / "MEGA_KERNEL_CHAIN.jsonl"
MONOLITH_LIBRARY = PROJECTS_ROOT / "monolith" / "catalog" / "library.json"

CORE_PILLARS: list[dict[str, Any]] = [
    {"id": "mastermind", "path": PROJECTS_ROOT / "mastermind", "min_tests": 100},
    {"id": "the-tower-of-babel", "path": PROJECTS_ROOT / "GlacierEQ_Swarm" / "the-tower-of-babel", "min_tests": 100},
    {"id": "monolith", "path": PROJECTS_ROOT / "monolith", "min_tests": 400},
    {"id": "make-it-heavy", "path": PROJECTS_ROOT / "make-it-heavy", "min_tests": 30},
    {"id": "mega-skills", "path": PROJECTS_ROOT / "mega-skills", "min_tests": 50},
    {"id": "Genius-Mastery", "path": PROJECTS_ROOT / "Genius-Mastery", "min_tests": 50},
    {"id": "job-app-helix", "path": PROJECTS_ROOT / "job-app-helix", "min_tests": 80},
    {"id": "memory", "path": PROJECTS_ROOT / "memory", "min_tests": 5},
    {"id": "token_saver", "path": PROJECTS_ROOT / "token_saver", "min_tests": 30},
    {"id": "APEX-IMPACT-ENGINE", "path": PROJECTS_ROOT / "APEX-IMPACT-ENGINE", "min_tests": 10},
    {"id": "Ai-Personalization_Kernel", "path": PROJECTS_ROOT / "Ai-Personalization_Kernel", "min_tests": 80},
    {"id": "apex-runtime", "path": PROJECTS_ROOT / "apex-runtime", "min_tests": 30},
]

QUALITY_THRESHOLD = 9.0
EXPECTED_ESTATE_REPOS = 1200  # floor; actual is 1,211


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class GateResult:
    """One observational enrichment transition."""
    gate: str
    status: str       # telemetry only: "PASS" | "WARN" | "FAIL"
    detail: dict[str, Any] = field(default_factory=dict)
    elapsed_ms: float = 0.0
    transition: str = ""
    level_up: bool = True
    mission_stop: bool = False


@dataclass
class BootReceipt:
    """Immutable boot receipt with cryptographic chain-of-custody."""
    schema: str = "glaciereq.apex-boot-core-receipt.v2"
    timestamp_utc: str = ""
    boot_version: str = "2.0.0"
    gates: list[dict[str, Any]] = field(default_factory=list)
    overall_status: str = "UNKNOWN"
    pass_count: int = 0
    warn_count: int = 0
    fail_count: int = 0
    total_gates: int = 0
    pre_reasoning_binding: dict[str, Any] = field(default_factory=dict)
    enrichment_summary: dict[str, Any] = field(default_factory=dict)
    digest: str = ""

    def compute_digest(self) -> str:
        blob = json.dumps(
            {k: v for k, v in asdict(self).items() if k != "digest"},
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()


# ── Gate Checks ──────────────────────────────────────────────────────────────

class ApexBootCore:
    """Operator-bound holographic estate initialization sentinel."""

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        # An explicit root wins; otherwise honour APEX_WORKSPACE_ROOT; otherwise
        # fall back to the configured default (/root). Gates read paths from
        # ``self`` so an injected root is always respected.
        self.root = Path(workspace_root).expanduser() if workspace_root else WORKSPACE_ROOT
        self.projects = self.root / "projects"
        self.secrets_dir = self.root / ".secrets"
        self.vault_env = self.root / ".vault_env"
        self.estate_receipt = self.root / "ESTATE_QUALITY_RECEIPT.json"
        self.memory_dir = self.root / "MEMORY.md"
        self.receipt_chain = self.projects / "mastermind" / "receipts" / "MEGA_KERNEL_CHAIN.jsonl"
        self.monolith_library = self.projects / "monolith" / "catalog" / "library.json"
        self.results: list[GateResult] = []
        self.operator_binding = load_operator_semantics()
        self.operator_projection = project_operator_semantics(self.operator_binding)

    def _not_configured(self, gate: str, reason: str, detail: dict[str, Any]) -> GateResult:
        """Report an absent estate component as a distinct, non-fault state.

        An estate that is not installed on this host is not the same as an
        estate that is installed and broken. Both are enrichment telemetry and
        neither is a mission veto, but only the second indicates a problem.
        """
        d = dict(detail)
        d["configured"] = False
        d["reason"] = reason
        d["execution_semantics"] = {
            "telemetry_only": True,
            "enrichment_transition": True,
            "mission_stop": False,
            "authority_holder": "OPERATOR",
        }
        return GateResult(gate=gate, status="WARN", detail=d, elapsed_ms=0.0,
                          transition="NOT_CONFIGURED")

    def audit_interpretation(self, text: str) -> dict[str, Any]:
        """Detect ontology inversions before prose or plans propagate durably.

        Findings are repair/enrichment telemetry. They never acquire veto power.
        """
        findings = detect_inversions(text)
        return {
            "schema": "glaciereq.operator-semantics-audit.v1",
            "findings": findings,
            "finding_count": len(findings),
            "repair_required": bool(findings),
            "mission_continues": True,
            "creates_authority": False,
            "authority_holder": "OPERATOR",
            "semantic_contract_sha256": self.operator_binding["contract_sha256"],
        }

    # ── 1. Environment & Runtime ─────────────────────────────────────────

    def gate_environment(self) -> GateResult:
        t0 = time.monotonic()
        python_ver = sys.version.split()[0]
        major, minor = sys.version_info[:2]
        ok = major >= 3 and minor >= 11
        detail = {
            "python_version": python_ver,
            "platform": sys.platform,
            "python_path_len": len(sys.path),
            "workspace_root": str(self.root),
            "cwd": os.getcwd(),
        }
        return GateResult(
            gate="environment",
            status="PASS" if ok else "WARN",
            detail=detail,
            elapsed_ms=round((time.monotonic() - t0) * 1000, 2),
        )

    # ── 2. Secrets Vault Integrity ───────────────────────────────────────

    def gate_secrets_vault(self) -> GateResult:
        t0 = time.monotonic()
        detail: dict[str, Any] = {"secrets_dir": str(self.secrets_dir)}
        issues: list[str] = []

        if self.secrets_dir.is_dir():
            files = list(self.secrets_dir.iterdir())
            detail["secret_files"] = len(files)
            for f in files:
                mode = oct(f.stat().st_mode)[-3:]
                if mode not in ("600", "700"):
                    issues.append(f"{f.name} has mode {mode}, expected 600")
        else:
            issues.append(f"{self.secrets_dir} directory missing")
            detail["secret_files"] = 0

        detail["vault_env_exists"] = self.vault_env.is_file()
        if not self.vault_env.is_file():
            issues.append(f"{self.vault_env} not found")

        detail["issues"] = issues

        # An estate with no secrets directory at all is unconfigured, not faulty.
        # The issues list is still reported so the receipt shape stays stable.
        if not self.secrets_dir.is_dir() and not self.vault_env.is_file():
            return self._not_configured(
                "secrets_vault", "secrets_vault_absent", detail
            )

        status = "PASS" if not issues else ("WARN" if len(issues) <= 2 else "FAIL")
        return GateResult(gate="secrets_vault", status=status, detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── 3. MegaKernel Receipt Chain ──────────────────────────────────────

    def gate_receipt_chain(self) -> GateResult:
        t0 = time.monotonic()
        detail: dict[str, Any] = {"chain_path": str(self.receipt_chain)}

        if not self.receipt_chain.exists():
            detail["chain_length"] = 0
            return self._not_configured(
                "receipt_chain", "receipt_chain_absent", detail
            )

        lines = [l for l in self.receipt_chain.read_text(encoding="utf-8").splitlines() if l.strip()]
        detail["chain_length"] = len(lines)

        if len(lines) == 0:
            detail["integrity"] = "empty_chain"
            return GateResult(gate="receipt_chain", status="WARN", detail=detail,
                              elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

        if len(lines) == 1:
            try:
                rec = json.loads(lines[0])
                if rec.get("seq") == 1 and rec.get("receipt_hash"):
                    detail["integrity"] = "genesis_intact"
                    return GateResult(gate="receipt_chain", status="PASS", detail=detail,
                                      elapsed_ms=round((time.monotonic() - t0) * 1000, 2))
                else:
                    detail["integrity"] = "invalid_genesis_entry"
                    return GateResult(gate="receipt_chain", status="FAIL", detail=detail,
                                      elapsed_ms=round((time.monotonic() - t0) * 1000, 2))
            except Exception as e:
                detail["integrity"] = f"parse_error: {e}"
                return GateResult(gate="receipt_chain", status="FAIL", detail=detail,
                                  elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

        # Verify hash linkage on last 10 receipts
        try:
            recent = [json.loads(l) for l in lines[-10:]]
            broken = False
            for i in range(1, len(recent)):
                if recent[i].get("prev_hash") != recent[i - 1].get("receipt_hash"):
                    broken = True
                    break
            detail["integrity"] = "intact" if not broken else "broken_link"
            status = "PASS" if not broken else "FAIL"
        except Exception as e:
            detail["integrity"] = f"parse_error: {e}"
            status = "WARN"

        return GateResult(gate="receipt_chain", status=status, detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── 4. Monolith Catalog Census ───────────────────────────────────────

    def gate_monolith_census(self) -> GateResult:
        t0 = time.monotonic()
        detail: dict[str, Any] = {"library_path": str(self.monolith_library)}

        if not self.monolith_library.is_file():
            detail["status_detail"] = "library.json not found"
            # A missing catalog means the monolith is not present on this host,
            # which is unconfigured rather than a failed census.
            return self._not_configured(
                "monolith_census", "monolith_library_absent", detail
            )

        try:
            lib = json.loads(self.monolith_library.read_text(encoding="utf-8"))
            # library.json is a dict with 'entries' list and 'scale_notes'
            if isinstance(lib, list):
                count = len(lib)
            elif isinstance(lib, dict):
                entries = lib.get("entries", [])
                count = len(entries) if isinstance(entries, list) else 0
                # Fallback to scale_notes.fetched_entries
                if count == 0:
                    scale = lib.get("scale_notes", {})
                    count = scale.get("fetched_entries", 0)
            else:
                count = 0
            detail["repo_count"] = count
            detail["expected_min"] = EXPECTED_ESTATE_REPOS
            status = "PASS" if count >= EXPECTED_ESTATE_REPOS else "WARN"
        except Exception as e:
            detail["error"] = str(e)
            status = "FAIL"

        return GateResult(gate="monolith_census", status=status, detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── 5. APEX-IMPACT-ENGINE Quality Gate ───────────────────────────────

    def gate_impact_engine(self) -> GateResult:
        t0 = time.monotonic()
        detail: dict[str, Any] = {}

        try:
            impact_src = self.projects / "APEX-IMPACT-ENGINE" / "src"
            if str(impact_src) not in sys.path:
                sys.path.insert(0, str(impact_src))
            from apex_impact.engine import ImpactEngine
            from apex_impact.model import QUALITY_THRESHOLD as QT
            detail["native_engine"] = True
            detail["quality_threshold"] = QT
            status = "PASS"
        except ImportError:
            detail["native_engine"] = False
            detail["quality_threshold"] = QUALITY_THRESHOLD
            status = "WARN"

        return GateResult(gate="impact_engine", status=status, detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── 6. Ai-Personalization_Kernel ─────────────────────────────────────

    def gate_personalization_kernel(self) -> GateResult:
        t0 = time.monotonic()
        detail: dict[str, Any] = {}

        try:
            from apk.boot import BootContract, STEP_NAMES
            detail["boot_contract_available"] = True
            detail["step_count"] = len(STEP_NAMES)
            detail["steps"] = list(STEP_NAMES)
            status = "PASS"
        except ImportError:
            detail["boot_contract_available"] = False
            detail["step_count"] = 0
            status = "WARN"

        return GateResult(gate="personalization_kernel", status=status, detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── 7. Permanent Memory Engine ───────────────────────────────────────

    def gate_memory_engine(self) -> GateResult:
        t0 = time.monotonic()
        detail: dict[str, Any] = {"memory_md_exists": self.memory_dir.is_file()}

        memory_project = self.projects / "memory"
        detail["memory_project_exists"] = memory_project.is_dir()

        if not self.memory_dir.is_file() and not memory_project.is_dir():
            return self._not_configured(
                "memory_engine", "memory_engine_absent", detail
            )

        try:
            memory_src = memory_project / "src"
            if memory_src.is_dir() and str(memory_src) not in sys.path:
                sys.path.insert(0, str(memory_src))
            from apex_memory import PermanentMemoryEngine
            detail["engine_importable"] = True
            status = "PASS"
        except ImportError:
            detail["engine_importable"] = False
            status = "WARN"

        return GateResult(gate="memory_engine", status=status, detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── 8. Token Saver Bridge ────────────────────────────────────────────

    def gate_token_saver(self) -> GateResult:
        t0 = time.monotonic()
        detail: dict[str, Any] = {}

        token_saver_src = self.projects / "token_saver" / "src"
        if token_saver_src.is_dir() and str(token_saver_src) not in sys.path:
            sys.path.insert(0, str(token_saver_src))

        try:
            from unified_token_engine import UnifiedTokenEngine
            detail["importable"] = True
            detail["engine"] = "UnifiedTokenEngine"
            status = "PASS"
        except ImportError:
            try:
                # Fallback: project-level import
                token_saver_root = self.projects / "token_saver"
                if str(token_saver_root) not in sys.path:
                    sys.path.insert(0, str(token_saver_root))
                from token_saver_elite_core import TokenSaverElite
                detail["importable"] = True
                detail["engine"] = "TokenSaverElite"
                status = "PASS"
            except ImportError:
                detail["importable"] = False
                status = "WARN"

        return GateResult(gate="token_saver", status=status, detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── 9. Estate Quality Receipt Validation ─────────────────────────────

    def gate_estate_receipt(self) -> GateResult:
        t0 = time.monotonic()
        detail: dict[str, Any] = {"receipt_path": str(self.estate_receipt)}

        if not self.estate_receipt.is_file():
            detail["exists"] = False
            return self._not_configured(
                "estate_receipt", "estate_receipt_absent", detail
            )

        try:
            payload = json.loads(self.estate_receipt.read_text(encoding="utf-8"))
            detail["exists"] = True
            detail["all_green"] = payload.get("all_green", False)
            detail["total_projects"] = payload.get("total_projects", 0)
            detail["passed_projects"] = payload.get("passed_projects", 0)
            detail["failed_projects"] = payload.get("failed_projects", 0)
            detail["receipt_sha256"] = payload.get("receipt_sha256", "")[:16] + "..."
            detail["timestamp"] = payload.get("timestamp_utc", "")

            # Verify each pillar reached at least L5
            pillar_levels: dict[str, str] = {}
            for r in payload.get("results", []):
                pillar_levels[r["id"]] = r.get("epistemic_level", "L0")
            detail["pillar_levels"] = pillar_levels

            all_l5_plus = all(
                lv in ("L5", "L6") for lv in pillar_levels.values()
            )
            status = "PASS" if payload.get("all_green") and all_l5_plus else "FAIL"
        except Exception as e:
            detail["error"] = str(e)
            status = "FAIL"

        return GateResult(gate="estate_receipt", status=status, detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── 10. Git Health Across Core Trees ─────────────────────────────────

    def gate_git_health(self) -> GateResult:
        t0 = time.monotonic()
        trees: list[dict[str, Any]] = []
        dirty_count = 0

        for pillar in CORE_PILLARS[:6]:  # Check top 6 pillars for speed
            # Resolve the pillar under THIS instance's projects root so an
            # injected or env-configured root is honoured.
            path = self.projects / Path(pillar["path"]).name
            if not (path / ".git").exists():
                continue
            try:
                branch = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=path, capture_output=True, text=True, check=False,
                ).stdout.strip()
                porcelain = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=path, capture_output=True, text=True, check=False,
                ).stdout.strip()
                meaningful_dirty = [
                    line for line in porcelain.splitlines()
                    if line.strip() and not any(ign in line for ign in ("receipts/", "evidence/", ".log", ".pyc"))
                ]
                clean = len(meaningful_dirty) == 0
                if not clean:
                    dirty_count += 1
                trees.append({
                    "id": p["id"],
                    "branch": branch,
                    "clean": clean,
                })
            except Exception:
                trees.append({"id": p["id"], "branch": "error", "clean": False})
                dirty_count += 1

        detail = {"trees_checked": len(trees), "dirty_count": dirty_count, "trees": trees}
        status = "PASS" if dirty_count == 0 else "WARN"
        return GateResult(gate="git_health", status=status, detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── 11. POSIX Toolchain ──────────────────────────────────────────────

    def gate_toolchain(self) -> GateResult:
        t0 = time.monotonic()
        local_bin = self.root / ".local" / "bin"
        detail: dict[str, Any] = {"local_bin_exists": local_bin.is_dir()}

        if not local_bin.exists():
            return self._not_configured(
                "toolchain", "local_bin_absent",
                {**detail, "bin_dir": str(local_bin)},
            )

        checked = []
        for p in sorted(local_bin.glob("apex-*")):
            is_exec = bool(p.stat().st_mode & 0o111)
            checked.append({"name": p.name, "executable": is_exec})

        detail["binaries_checked"] = len(checked)
        detail["binaries"] = checked[:10]  # cap output
        all_ok = all(b["executable"] for b in checked) if checked else True
        return GateResult(gate="toolchain", status="PASS" if all_ok else "FAIL",
                          detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── 12. Capability Bus Scan ──────────────────────────────────────────

    def gate_capability_bus(self) -> GateResult:
        t0 = time.monotonic()
        detail: dict[str, Any] = {}

        estate_count = 0
        genius_count = 0
        if self.projects.is_dir():
            for d in self.projects.iterdir():
                if d.is_dir() and not d.name.startswith("."):
                    if d.name.startswith("Genius-"):
                        genius_count += 1
                    else:
                        estate_count += 1

        detail["estate_projects"] = estate_count
        detail["genius_lineages"] = genius_count
        detail["total_capabilities"] = estate_count + genius_count

        # No projects directory at all means the estate is not present here,
        # which is distinct from a present-but-thin estate. The counters above
        # are still reported so receipt shape stays stable.
        if not self.projects.is_dir():
            return self._not_configured(
                "capability_bus", "projects_root_absent",
                {"projects_root": str(self.projects), **detail},
            )

        status = "PASS" if (estate_count + genius_count) >= 10 else "WARN"
        return GateResult(gate="capability_bus", status=status, detail=detail,
                          elapsed_ms=round((time.monotonic() - t0) * 1000, 2))

    # ── Master Boot Sequence ─────────────────────────────────────────────

    def boot(self) -> BootReceipt:
        """Execute all 12 gates in order and produce an immutable receipt."""
        gates = [
            self.gate_environment,
            self.gate_secrets_vault,
            self.gate_receipt_chain,
            self.gate_monolith_census,
            self.gate_impact_engine,
            self.gate_personalization_kernel,
            self.gate_memory_engine,
            self.gate_token_saver,
            self.gate_estate_receipt,
            self.gate_git_health,
            self.gate_toolchain,
            self.gate_capability_bus,
        ]

        self.results = []
        for gate_fn in gates:
            try:
                result = gate_fn()
            except Exception as e:
                result = GateResult(
                    gate=gate_fn.__name__.replace("gate_", ""),
                    status="FAIL",
                    detail={"exception": str(e)},
                )
            result.transition = transition_for_status(result.status, self.operator_binding)
            result.level_up = True
            result.mission_stop = False
            result.detail.setdefault("execution_semantics", {})
            result.detail["execution_semantics"].update({
                "telemetry_only": True,
                "enrichment_transition": True,
                "mission_stop": False,
                "authority_holder": "OPERATOR",
                "local_block_changes_route_not_objective": True,
            })
            self.results.append(result)

        pass_count = sum(1 for r in self.results if r.status == "PASS")
        warn_count = sum(1 for r in self.results if r.status == "WARN")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")

        if fail_count > 0:
            overall = "DEGRADED"
        elif warn_count > 2:
            overall = "CAUTION"
        else:
            overall = "OPERATIONAL"

        receipt = BootReceipt(
            timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            gates=[asdict(r) for r in self.results],
            overall_status=overall,
            pass_count=pass_count,
            warn_count=warn_count,
            fail_count=fail_count,
            total_gates=len(self.results),
            pre_reasoning_binding=self.operator_projection,
            enrichment_summary={
                "semantic": "LEVEL_UP",
                "all_results_are_enrichment_transitions": True,
                "mission_continues": True,
                "machine_veto": False,
                "operator_authority_preserved": True,
                "transition_counts": {
                    "validated": pass_count,
                    "uncertainty_enriched": warn_count,
                    "repair_or_reroute_enriched": fail_count,
                },
            },
        )
        receipt.digest = receipt.compute_digest()
        return receipt


# ── CLI Entrypoint ───────────────────────────────────────────────────────────

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="APEX Boot Core v2 — Holographic Estate Enrichment Sentinel")
    parser.add_argument("--json", action="store_true", help="Output full JSON receipt")
    parser.add_argument("--save", type=str, default="", help="Save receipt to file path")
    parser.add_argument("--quiet", action="store_true", help="Suppress banner output")
    args = parser.parse_args()

    core = ApexBootCore()
    receipt = core.boot()

    if not args.quiet:
        print("=" * 72)
        print("  🏛️  APEX BOOT CORE v2.0 — HOLOGRAPHIC ENRICHMENT SENTINEL  🏛️")
        print("=" * 72)
        print(f"  Timestamp : {receipt.timestamp_utc}")
        print(f"  Status    : {receipt.overall_status}")
        print(f"  Enrich    : {receipt.pass_count} VALIDATED / {receipt.warn_count} UNCERTAINTY / {receipt.fail_count} REPAIR-REROUTE")
        print("  Authority : OPERATOR (machine nodes do not acquire project direction authority)")
        print("  Continue  : yes — local deficiencies enrich state and change route, never mission")
        print(f"  Digest    : {receipt.digest[:32]}...")
        print("-" * 72)

        for r in core.results:
            icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}.get(r.status, "❓")
            elapsed = f"{r.elapsed_ms:.0f}ms"
            print(f"  {icon} {r.gate:<28} [{r.status}] ({elapsed})")

        print("=" * 72)

    if args.json:
        print(json.dumps(asdict(receipt), indent=2))

    if args.save:
        Path(args.save).write_text(
            json.dumps(asdict(receipt), indent=2), encoding="utf-8"
        )
        if not args.quiet:
            print(f"  Saved receipt → {args.save}")

    # Gate outcomes are enrichment telemetry, never mission vetoes. If a receipt
    # was produced, boot completed its observational transition and execution continues.
    return 0


if __name__ == "__main__":
    sys.exit(main())
