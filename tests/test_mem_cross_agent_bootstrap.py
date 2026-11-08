"""Static contract checks for the existing unified-memory-connect skill's Mem.ai adapter.

These checks validate portability and safety invariants only. They DO NOT
establish MCP handshake, OAuth, provider readback, OMP installation, or
fresh-session behavioral enforcement.
"""
import json
from pathlib import Path
from uuid import UUID
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "skills" / "unified-memory-connect"
PROFILE_PATH = BASE / "references" / "glaciereq-mem-bootstrap.json"
RUNBOOK_PATH = BASE / "references" / "glaciereq-mem-agent-runbook.md"
SKILL_PATH = BASE / "SKILL.md"

class MemCrossAgentBootstrapContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        cls.runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")

    def test_existing_skill_id_is_preserved(self):
        self.assertTrue(self.skill.startswith("---\nname: unified-memory-connect\n"))
        self.assertIn("## Retrieval contract", self.skill)
        self.assertIn("## GlacierEQ Mem.ai cross-agent runtime", self.skill)

    def test_first_party_mem_not_confused_with_mem0(self):
        self.assertEqual(self.profile["providers"]["mem_ai"]["mcp_url"], "https://mcp.mem.ai/mcp")
        self.assertIn("Mem.ai is a distinct provider from Mem0", self.skill)
        self.assertIn("GlacierEQ gateway", self.runbook)

    def test_recovered_gateway_remains_unverified(self):
        gateway = self.profile["providers"]["glaciereq_gateway"]
        self.assertEqual(gateway["status"], "RECOVERED_CONFIGURATION_UNVERIFIED")
        self.assertNotEqual(gateway["mcp_url"], self.profile["providers"]["mem_ai"]["mcp_url"])

    def test_native_cli_commands_are_exact(self):
        clients = self.profile["clients"]
        self.assertEqual(clients["claude_code"]["install"], "claude mcp add --transport http mem https://mcp.mem.ai/mcp")
        self.assertEqual(clients["codex_cli"]["install"], "codex mcp add mem --url https://mcp.mem.ai/mcp")
        self.assertEqual(clients["gemini_cli"]["install"], "gemini mcp add -s user -t http mem https://mcp.mem.ai/mcp")

    def test_omp_does_not_invent_syntax_or_local_dependency(self):
        omp = self.profile["clients"]["omp_glacier"]
        self.assertEqual(omp["status"], "HOST_UNVERIFIED")
        self.assertIn("existing OMP native", omp["install"])
        self.assertIn("Cloud-first", self.runbook)

    def test_note_anchors_are_stable_uuids(self):
        ids = self.profile["mem_note_anchors"]
        self.assertGreaterEqual(len(ids), 5)
        for note_id in ids.values():
            self.assertEqual(str(UUID(note_id)), note_id)

    def test_boot_steps_enforce_owner_and_native_readback(self):
        boot = " | ".join(self.profile["boot_sequence"])
        self.assertIn("exact", boot.lower())
        self.assertIn("source", boot.lower())
        self.assertIn("verify", boot.lower())

    def test_proof_stages_do_not_collapse_into_one(self):
        self.assertEqual(self.profile["certification_stages"], [
            "CONFIGURED", "INITIALIZED", "DISCOVERED", "READ_VERIFIED",
            "WRITE_VERIFIED", "CROSS_SESSION_APPLIED"
        ])
        self.assertIn("Static docs", self.skill)

    def test_no_secrets_and_no_risky_auto_actions(self):
        req = self.profile["requirements"]
        for name in ["no_secrets", "no_auto_replay_on_ambiguous_write",
                     "no_domain_payload_on_global_boot", "no_cross_matter_contamination",
                     "no_unapproved_messages_permissions_merges_deployments"]:
            self.assertIs(req[name], True)
        self.assertNotIn("Bearer sk-", PROFILE_PATH.read_text(encoding="utf-8"))

    def test_doc_links_resolve_relative_to_owning_skill(self):
        self.assertTrue(RUNBOOK_PATH.is_file())
        self.assertTrue(PROFILE_PATH.is_file())
        self.assertIn("(references/glaciereq-mem-agent-runbook.md)", self.skill)
        self.assertIn("(references/glaciereq-mem-bootstrap.json)", self.skill)

if __name__ == "__main__":
    unittest.main()
