import unittest
import json
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
REPO_ROOT = SKILL_ROOT.parent.parent  # mega-skills/
sys.path.insert(0, str(SKILL_ROOT))

EXPECTED_PACKETS = [
    "01-mesh-definition.md",
    "02-mission-lifecycle.md",
    "03-receipt-format.md",
    "04-routing-heuristics.md",
    "05-verification-gate.md",
    "06-fuse-policy.md",
    "07-delivery-contract.md",
    "08-memory-persistence.md",
    "09-failure-modes.md",
    "10-security-boundary.md",
    "11-token-economy.md",
    "12-observability.md",
    "07-delivery-contract.md",
    "08-memory-persistence.md",
    "09-failure-modes.md",
    "10-security-boundary.md",
    "11-token-economy.md",
    "12-observability.md",
]

EXPECTED_SCHEMAS = [
    "receipt.schema.json",
    "stage-receipt.schema.json",
    "delivery.schema.json",
]


class TestApexOrchestrationStructure(unittest.TestCase):
    def test_skill_md_manifest(self):
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: apex-orchestration", skill_md)
        # version may be 1.0.0 or later (e.g. 1.1.0 with ML packets)
        import re as _re

        m = _re.search(r"^version:\s*(\d+\.\d+\.\d+)\s*$", skill_md, _re.MULTILINE)
        self.assertIsNotNone(m, "no version line found in SKILL.md")
        parts = tuple(int(x) for x in m.group(1).split("."))
        self.assertGreaterEqual(parts, (1, 0, 0), "version must be >= 1.0.0")
        self.assertIn("status: active", skill_md)

    def test_skill_entry_point_exists_and_executable(self):
        skill_py = SKILL_ROOT / "skill.py"
        self.assertTrue(skill_py.exists())
        self.assertTrue(bool(skill_py.stat().st_mode & 0o111))

    def test_scripts_executable(self):
        for script_name in ("run.py", "this_skill.py"):
            p = SKILL_ROOT / "scripts" / script_name
            self.assertTrue(p.exists())
            self.assertTrue(bool(p.stat().st_mode & 0o111))

    def test_all_twelve_packets_present(self):
        for name in EXPECTED_PACKETS:
            p = SKILL_ROOT / "packets" / name
            self.assertTrue(p.exists(), f"missing packet: {name}")
            txt = p.read_text(encoding="utf-8")
            self.assertIn("Maturity:", txt, f"packet {name} missing Maturity line")
            self.assertIn("Invariant", txt, f"packet {name} missing Invariant")
            self.assertIn("Anti-Patterns", txt, f"packet {name} missing Anti-Patterns")
            self.assertIn("L2 Evidence", txt, f"packet {name} missing L2 Evidence")
        # Bonus: confirm ML/self-improving (13-16) and advanced (17-21) packets
        for name in [
            "13-ml-routing.md",
            "14-receipt-mining.md",
            "15-embedding-memory.md",
            "16-self-improving-loop.md",
            "17-speculative-decoding.md",
            "18-semantic-cache.md",
            "19-dag-scheduler.md",
            "20-property-based-testing.md",
            "21-mutation-testing.md",
        ]:
            p = SKILL_ROOT / "packets" / name
            if p.exists():
                txt = p.read_text(encoding="utf-8")
                self.assertIn("Maturity:", txt)
                self.assertIn("Invariant", txt)

    def test_all_packets_maturity_at_least_9(self):
        for name in EXPECTED_PACKETS:
            p = SKILL_ROOT / "packets" / name
            txt = p.read_text(encoding="utf-8")
            m = next((l for l in txt.splitlines() if l.startswith("**Maturity:**")), "")
            self.assertTrue("9" in m, f"packet {name} maturity below 9: {m}")

    def test_all_packets_have_version(self):
        for name in EXPECTED_PACKETS:
            p = SKILL_ROOT / "packets" / name
            txt = p.read_text(encoding="utf-8")
            self.assertIn(
                "Current version:", txt, f"packet {name} missing version line"
            )
            self.assertIn("1.0.0", txt, f"packet {name} version not 1.0.0")

    def test_all_schemas_present_and_valid_json(self):
        for name in EXPECTED_SCHEMAS:
            p = SKILL_ROOT / "schemas" / name
            self.assertTrue(p.exists(), f"missing schema: {name}")
            try:
                json.loads(p.read_text())
            except json.JSONDecodeError as e:
                self.fail(f"invalid JSON in {name}: {e}")

    def test_skill_cli_packets(self):
        r = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "skill.py"), "packets"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        # Should have at least 12 packets (the v1.0.0 baseline); v1.1+ has 16
        import re as _re

        m = _re.search(r"Total:\s*(\d+)\s+packets", r.stdout)
        self.assertIsNotNone(m, "no packet count line in skill.py packets output")
        n = int(m.group(1))
        self.assertGreaterEqual(n, 12)

    def test_skill_cli_mesh(self):
        r = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "skill.py"), "mesh"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("Total: 12 lanes", r.stdout)

    def test_skill_cli_routes(self):
        r = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "skill.py"), "routes"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        for rule in (
            "R-MEDICAL",
            "R-FINANCE",
            "R-MULTIMODAL",
            "R-LONGCTX",
            "R-PLAN",
            "R-CODE-EDIT",
            "R-CODE-FAST",
            "R-DEFAULT",
        ):
            self.assertIn(rule, r.stdout)

    def test_skill_cli_failures(self):
        r = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "skill.py"), "failures"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        for code in ("F-INT-01", "F-DIS-02", "F-FUSE-02", "F-DEL-02"):
            self.assertIn(code, r.stdout)

    def test_skill_cli_hash_chain(self):
        with self.subTest():
            a = (SKILL_ROOT / "packets" / "01-mesh-definition.md").read_bytes()
            b = (SKILL_ROOT / "packets" / "02-mission-lifecycle.md").read_bytes()
            expected = hashlib.sha256(a + b).hexdigest()
        r = subprocess.run(
            [
                sys.executable,
                str(SKILL_ROOT / "skill.py"),
                "hash-chain",
                str(SKILL_ROOT / "packets" / "01-mesh-definition.md"),
                str(SKILL_ROOT / "packets" / "02-mission-lifecycle.md"),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn(expected, r.stdout)

    def test_packet_files_have_required_sections(self):
        required = [
            "## Invariant",
            "## Gates",
            "## Anti-Patterns",
            "## L2 Evidence",
            "## Versioning",
        ]
        for name in EXPECTED_PACKETS:
            p = SKILL_ROOT / "packets" / name
            txt = p.read_text(encoding="utf-8")
            for sec in required:
                self.assertIn(sec, txt, f"packet {name} missing section: {sec}")


class TestMeshContract(unittest.TestCase):
    """The mesh must be a closed set: 12 lanes, no duplicate models in same role, every model is free-tier."""

    def setUp(self):
        r = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "skill.py"), "mesh"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(r.returncode, 0)
        self.lines = r.stdout.splitlines()

    def test_lane_count_is_12(self):
        lane_lines = [
            l
            for l in self.lines
            if l.startswith(
                (
                    "REASON",
                    "CODE",
                    "VERIFY",
                    "REVIEW",
                    "LONG-CTX",
                    "THINK-DEEP",
                    "NANO-PERCEPTION",
                    "DOMAIN-MED",
                    "DOMAIN-FIN",
                    "ROUTER-FREE",
                )
            )
        ]
        self.assertEqual(len(lane_lines), 12)

    def test_no_duplicate_models(self):
        # Every model appears only once (in mesh table)
        models = [
            l.split()[1]
            for l in self.lines
            if l.startswith(
                (
                    "REASON",
                    "CODE",
                    "VERIFY",
                    "REVIEW",
                    "LONG-CTX",
                    "THINK-DEEP",
                    "NANO-PERCEPTION",
                    "DOMAIN-MED",
                    "DOMAIN-FIN",
                    "ROUTER-FREE",
                )
            )
        ]
        self.assertEqual(len(models), len(set(models)))


class TestReceiptSchema(unittest.TestCase):
    def test_receipt_schema_required_fields(self):
        schema = json.loads(
            (SKILL_ROOT / "schemas" / "receipt.schema.json").read_text()
        )
        self.assertIn("lane", schema["required"])
        self.assertIn("model", schema["required"])
        self.assertIn("task", schema["required"])
        self.assertIn("l2_proof", schema["required"])
        # l2_proof must be const true
        self.assertEqual(schema["properties"]["l2_proof"]["const"], True)

    def test_delivery_schema_status_enum(self):
        schema = json.loads(
            (SKILL_ROOT / "schemas" / "delivery.schema.json").read_text()
        )
        self.assertEqual(
            set(schema["properties"]["status"]["enum"]),
            {"SHIPPED", "BLOCKED", "REFUSED"},
        )

    def test_shipped_delivery_requires_verified_run_quality_and_mission_delta(self):
        schema = json.loads(
            (SKILL_ROOT / "schemas" / "delivery.schema.json").read_text()
        )
        run_quality = schema["properties"]["run_quality"]
        self.assertEqual(
            set(run_quality["required"]),
            {"source_coverage", "mission_delta", "durable_outputs", "verification", "next_frontier"},
        )
        self.assertIs(run_quality["properties"]["mission_delta"]["properties"]["changed"]["const"], True)
        self.assertEqual(run_quality["properties"]["verification"]["properties"]["status"]["const"], "verified")
        conditional = schema["allOf"][0]
        self.assertEqual(conditional["if"]["properties"]["status"]["const"], "SHIPPED")
        self.assertIn("run_quality", conditional["then"]["required"])

    def test_stage_receipt_schema_enum(self):
        schema = json.loads(
            (SKILL_ROOT / "schemas" / "stage-receipt.schema.json").read_text()
        )
        self.assertEqual(
            set(schema["properties"]["stage"]["enum"]),
            {"INTAKE", "DECOMPOSE", "DISPATCH", "VERIFY", "FUSE", "DELIVER"},
        )


if __name__ == "__main__":
    unittest.main()
