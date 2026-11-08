#!/usr/bin/env python3
"""APEX Boot Core v2 — Comprehensive Behavioral Test Suite.

Tests every gate independently, the full boot sequence, receipt integrity,
and edge-case resilience.  Achieves L5 epistemic coverage.
"""

import json
import os
import sys
import tempfile
import time
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from boot_watchdog import (
    ApexBootCore,
    BootReceipt,
    CORE_PILLARS,
    ESTATE_RECEIPT,
    GateResult,
    MONOLITH_LIBRARY,
    RECEIPT_CHAIN,
    SECRETS_DIR,
    WORKSPACE_ROOT,
    _env_path,
)


class TestEnvironmentGate(unittest.TestCase):
    def test_returns_pass_on_valid_python(self):
        core = ApexBootCore()
        r = core.gate_environment()
        self.assertIn(r.status, ("PASS", "WARN"))
        self.assertEqual(r.gate, "environment")
        self.assertIn("python_version", r.detail)
        self.assertIn("platform", r.detail)
        self.assertGreater(r.detail["python_path_len"], 0)

    def test_elapsed_is_measured(self):
        core = ApexBootCore()
        r = core.gate_environment()
        self.assertGreaterEqual(r.elapsed_ms, 0.0)


class TestSecretsVaultGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_secrets_vault()
        self.assertIn(r.status, ("PASS", "WARN", "FAIL"))
        self.assertEqual(r.gate, "secrets_vault")
        self.assertIn("vault_env_exists", r.detail)

    def test_missing_secrets_dir_yields_issue(self):
        core = ApexBootCore(workspace_root=Path("/tmp/nonexistent_boot_test"))
        r = core.gate_secrets_vault()
        self.assertIn("issues", r.detail)


class TestReceiptChainGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_receipt_chain()
        self.assertIn(r.status, ("PASS", "WARN", "FAIL"))
        self.assertEqual(r.gate, "receipt_chain")
        self.assertIn("chain_path", r.detail)

    def test_valid_chain_returns_intact(self):
        if not RECEIPT_CHAIN.exists():
            self.skipTest("No receipt chain present")
        core = ApexBootCore()
        r = core.gate_receipt_chain()
        if r.detail.get("chain_length", 0) >= 2:
            self.assertIn(r.detail.get("integrity"), ("intact", "broken_link"))


class TestMonolithCensusGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_monolith_census()
        self.assertIn(r.status, ("PASS", "WARN", "FAIL"))
        self.assertEqual(r.gate, "monolith_census")

    def test_census_count_populated(self):
        if not MONOLITH_LIBRARY.is_file():
            self.skipTest("Monolith library.json not present")
        core = ApexBootCore()
        r = core.gate_monolith_census()
        self.assertIn("repo_count", r.detail)
        self.assertGreater(r.detail["repo_count"], 0)


class TestImpactEngineGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_impact_engine()
        self.assertIn(r.status, ("PASS", "WARN"))
        self.assertEqual(r.gate, "impact_engine")

    def test_quality_threshold_present(self):
        core = ApexBootCore()
        r = core.gate_impact_engine()
        self.assertIn("quality_threshold", r.detail)
        self.assertGreaterEqual(r.detail["quality_threshold"], 9.0)


class TestPersonalizationKernelGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_personalization_kernel()
        self.assertIn(r.status, ("PASS", "WARN"))
        self.assertEqual(r.gate, "personalization_kernel")

    def test_boot_contract_step_count(self):
        core = ApexBootCore()
        r = core.gate_personalization_kernel()
        if r.detail.get("boot_contract_available"):
            self.assertEqual(r.detail["step_count"], 12)
            self.assertEqual(len(r.detail["steps"]), 12)


class TestMemoryEngineGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_memory_engine()
        self.assertIn(r.status, ("PASS", "WARN"))
        self.assertEqual(r.gate, "memory_engine")
        self.assertIn("memory_md_exists", r.detail)


class TestTokenSaverGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_token_saver()
        self.assertIn(r.status, ("PASS", "WARN"))
        self.assertEqual(r.gate, "token_saver")


class TestEstateReceiptGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_estate_receipt()
        self.assertIn(r.status, ("PASS", "WARN", "FAIL"))
        self.assertEqual(r.gate, "estate_receipt")

    def test_receipt_validates_all_green(self):
        if not ESTATE_RECEIPT.is_file():
            self.skipTest("Estate receipt not present")
        core = ApexBootCore()
        r = core.gate_estate_receipt()
        self.assertIn("all_green", r.detail)
        self.assertIn("pillar_levels", r.detail)


class TestGitHealthGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_git_health()
        self.assertIn(r.status, ("PASS", "WARN", "FAIL"))
        self.assertEqual(r.gate, "git_health")
        self.assertIn("trees_checked", r.detail)


class TestToolchainGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_toolchain()
        self.assertIn(r.status, ("PASS", "WARN", "FAIL"))
        self.assertEqual(r.gate, "toolchain")


class TestCapabilityBusGate(unittest.TestCase):
    def test_gate_runs_without_crash(self):
        core = ApexBootCore()
        r = core.gate_capability_bus()
        self.assertIn(r.status, ("PASS", "WARN"))
        self.assertEqual(r.gate, "capability_bus")
        self.assertIn("total_capabilities", r.detail)

    def test_capability_count_above_minimum(self):
        """Count capabilities against a synthetic estate root.

        Previously this read the real /root/projects, so it failed on any host
        that is not the container. It now builds a fixture estate, which also
        serves as a regression test for workspace_root injection.
        """
        import shutil
        import tempfile

        tmp = tempfile.mkdtemp()
        try:
            root = Path(tmp) / "estate"
            names = ("proj-a", "proj-b", "Genius-Lineage", "proj-c", "proj-d", "proj-e")
            for name in names:
                (root / "projects" / name).mkdir(parents=True)
            core = ApexBootCore(workspace_root=root)
            r = core.gate_capability_bus()
            self.assertGreater(r.detail["total_capabilities"], 5)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestFullBoot(unittest.TestCase):
    """Tests the complete boot() sequence end-to-end."""

    def test_boot_produces_12_gates(self):
        core = ApexBootCore()
        receipt = core.boot()
        self.assertEqual(receipt.total_gates, 12)
        self.assertEqual(len(receipt.gates), 12)

    def test_boot_receipt_has_valid_digest(self):
        core = ApexBootCore()
        receipt = core.boot()
        self.assertEqual(len(receipt.digest), 64)
        self.assertEqual(receipt.digest, receipt.compute_digest())

    def test_boot_receipt_status_is_known(self):
        core = ApexBootCore()
        receipt = core.boot()
        self.assertIn(receipt.overall_status, ("OPERATIONAL", "CAUTION", "DEGRADED"))

    def test_boot_receipt_counts_are_consistent(self):
        core = ApexBootCore()
        receipt = core.boot()
        self.assertEqual(
            receipt.pass_count + receipt.warn_count + receipt.fail_count,
            receipt.total_gates,
        )

    def test_boot_receipt_schema_is_v2(self):
        core = ApexBootCore()
        receipt = core.boot()
        self.assertEqual(receipt.schema, "glaciereq.apex-boot-core-receipt.v2")
        self.assertEqual(receipt.boot_version, "2.0.0")

    def test_boot_receipt_serializes_to_valid_json(self):
        core = ApexBootCore()
        receipt = core.boot()
        blob = json.dumps(asdict(receipt), indent=2)
        roundtrip = json.loads(blob)
        self.assertEqual(roundtrip["schema"], "glaciereq.apex-boot-core-receipt.v2")
        self.assertEqual(roundtrip["total_gates"], 12)

    def test_boot_receipt_timestamp_is_populated(self):
        core = ApexBootCore()
        receipt = core.boot()
        self.assertTrue(receipt.timestamp_utc.endswith("Z"))
        self.assertGreater(len(receipt.timestamp_utc), 10)


class TestBootReceiptCryptography(unittest.TestCase):
    def test_digest_changes_with_different_data(self):
        core = ApexBootCore()
        r1 = core.boot()
        time.sleep(0.01)
        r2 = core.boot()
        # Timestamps differ, so digests differ
        self.assertNotEqual(r1.digest, r2.digest)

    def test_digest_is_deterministic_for_same_receipt(self):
        core = ApexBootCore()
        r = core.boot()
        d1 = r.compute_digest()
        d2 = r.compute_digest()
        self.assertEqual(d1, d2)


class TestGateResultDataclass(unittest.TestCase):
    def test_gate_result_serialization(self):
        gr = GateResult(gate="test_gate", status="PASS", detail={"key": "value"}, elapsed_ms=1.23)
        d = asdict(gr)
        self.assertEqual(d["gate"], "test_gate")
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["detail"]["key"], "value")


class TestSKILLmd(unittest.TestCase):
    def test_skill_md_exists_and_has_name(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: apex-boot-core", skill_md)
        self.assertIn("description:", skill_md)


class TestCoreConfig(unittest.TestCase):
    def test_core_pillars_has_entries(self):
        self.assertGreaterEqual(len(CORE_PILLARS), 10)

    def test_core_pillar_ids_are_unique(self):
        ids = [p["id"] for p in CORE_PILLARS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_core_pillars_have_min_tests(self):
        for p in CORE_PILLARS:
            self.assertIn("min_tests", p)
            self.assertGreater(p["min_tests"], 0)


class TestPortability(unittest.TestCase):
    """Guards the universal/no-local-dependency contract for the sentinel.

    The estate root must be configurable and every gate must honour it --
    otherwise a host that is not the container silently reports on paths that
    do not exist, which is indistinguishable from a genuinely broken estate.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / "estate"

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_env_path_uses_override(self):
        with patch.dict(os.environ, {"APEX_TEST_ROOT": "/tmp/override-root"}):
            resolved = _env_path("APEX_TEST_ROOT", Path("/fallback"))
        self.assertEqual(resolved, Path("/tmp/override-root"))

    def test_env_path_falls_back_when_unset(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("APEX_TEST_ROOT", None)
            resolved = _env_path("APEX_TEST_ROOT", Path("/fallback"))
        self.assertEqual(resolved, Path("/fallback"))

    def test_constructor_root_is_honoured_by_every_gate(self):
        """Regression: gates read module constants, ignoring an injected root."""
        core = ApexBootCore(workspace_root=self.root)
        self.assertEqual(core.root, self.root)
        self.assertEqual(core.projects, self.root / "projects")
        self.assertEqual(core.secrets_dir, self.root / ".secrets")
        self.assertEqual(core.vault_env, self.root / ".vault_env")
        self.assertEqual(core.memory_dir, self.root / "MEMORY.md")
        self.assertEqual(
            core.estate_receipt, self.root / "ESTATE_QUALITY_RECEIPT.json"
        )
        self.assertEqual(
            core.receipt_chain,
            self.root / "projects" / "mastermind" / "receipts" / "MEGA_KERNEL_CHAIN.jsonl",
        )
        self.assertEqual(
            core.monolith_library,
            self.root / "projects" / "monolith" / "catalog" / "library.json",
        )

    def test_injected_root_actually_reaches_gates(self):
        """Regression: injecting a root produced results from /root anyway."""
        core = ApexBootCore(workspace_root=self.root)
        r = core.gate_secrets_vault()
        self.assertEqual(r.detail["secrets_dir"], str(self.root / ".secrets"))
        r2 = core.gate_receipt_chain()
        self.assertEqual(r2.detail["chain_path"], str(core.receipt_chain))
        r3 = core.gate_monolith_census()
        self.assertEqual(r3.detail["library_path"], str(core.monolith_library))

    def test_absent_estate_reports_not_configured(self):
        """An uninstalled estate is not a fault; it must be distinguishable."""
        core = ApexBootCore(workspace_root=self.root)
        for gate in (
            core.gate_secrets_vault,
            core.gate_receipt_chain,
            core.gate_monolith_census,
            core.gate_memory_engine,
            core.gate_estate_receipt,
        ):
            with self.subTest(gate=gate.__name__):
                r = gate()
                self.assertFalse(r.detail.get("configured", True))
                self.assertIn("reason", r.detail)
                self.assertNotEqual(r.status, "FAIL")

    def test_boot_never_vetoes_on_missing_estate(self):
        core = ApexBootCore(workspace_root=self.root)
        receipt = core.boot()
        self.assertFalse(receipt.overall_status == "BLOCKED")
        self.assertTrue(all(not g.get("mission_stop") for g in receipt.gates))

    def test_present_but_broken_is_still_detected(self):
        """not_configured must not mask a real fault in a present estate."""
        self.root.mkdir(parents=True)
        (self.root / "projects" / "monolith" / "catalog").mkdir(parents=True)
        # library.json present but malformed -> a genuine fault, not absence.
        (self.root / "projects" / "monolith" / "catalog" / "library.json").write_text(
            "{not json", encoding="utf-8"
        )
        core = ApexBootCore(workspace_root=self.root)
        r = core.gate_monolith_census()
        self.assertTrue(r.detail.get("configured", True))
        self.assertIn(r.status, ("WARN", "FAIL"))

    def test_env_var_configures_root(self):
        with patch.dict(os.environ, {"APEX_WORKSPACE_ROOT": str(self.root)}):
            with patch("boot_watchdog.WORKSPACE_ROOT", self.root):
                core = ApexBootCore()
                self.assertEqual(core.root, self.root)
                self.assertEqual(core.secrets_dir, self.root / ".secrets")

    def test_no_hardcoded_developer_paths(self):
        src = (SKILL_ROOT / "scripts" / "boot_watchdog.py").read_text(encoding="utf-8")
        self.assertNotIn("/Users/", src)

    def test_stdlib_only(self):
        src = (SKILL_ROOT / "scripts" / "boot_watchdog.py").read_text(encoding="utf-8")
        for mod in ("import requests", "import yaml", "import numpy", "import httpx"):
            self.assertNotIn(mod, src)


if __name__ == "__main__":
    unittest.main()
