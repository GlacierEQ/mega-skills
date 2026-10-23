"""Behavioral tests for SDK manifest reconnaissance; no network."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "inspect_sdk.py"
spec = importlib.util.spec_from_file_location("inspect_sdk", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SdkInspectTests(unittest.TestCase):
    def test_node_dependencies_sorted_and_no_secret_spill(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "package.json").write_text(json.dumps({"dependencies": {"@foo/api-client": "^2.0.0", "@bar/sdk": "git+https://user:secret@evil.example/test", "react": "^19.0.0"}}))
            report = module.inspect(root)
            self.assertEqual([x["package"] for x in report["sdk_candidates"]], ["@bar/sdk", "@foo/api-client"])
            self.assertEqual(report["sdk_candidates"][0]["declared_spec"], "SPEC_REDACTED_OR_UNSUPPORTED")
            self.assertNotIn("secret", json.dumps(report))
            self.assertFalse(report["provider_verified"])

    def test_python_optional_and_regular_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "pyproject.toml").write_text('[project]\ndependencies=["awesome-sdk>=2.0", "httpx>=0.27"]\n[project.optional-dependencies]\ntest=["sample-api-client==1.2"]\n')
            report = module.inspect(root)
            self.assertEqual({x["package"] for x in report["sdk_candidates"]}, {"awesome-sdk", "sample-api-client"})

    def test_recognizes_major_sdk_packages_without_sdk_suffix(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "package.json").write_text(json.dumps({"dependencies": {"@openai/agents": "^0.4.0", "ai": "^6.0.0", "react": "^19.0.0"}}))
            (root / "pyproject.toml").write_text('[project]\ndependencies=["openai>=2.0", "anthropic>=0.6", "boto3>=1.0"]\n')
            found = {x["package"] for x in module.inspect(root)["sdk_candidates"]}
            self.assertEqual(found, {"@openai/agents", "ai", "openai", "anthropic", "boto3"})

    def test_identifies_sdk_package_itself_and_declared_entrypoints(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "package.json").write_text(json.dumps({"name": "supermemory", "version": "3.0.0-alpha.26", "types": "dist/index.d.ts", "exports": {".": {"import": "./dist/index.mjs", "require": "./dist/index.js"}}, "dependencies": {}}))
            report = module.inspect(root)
            self.assertEqual(report["package_identity"]["package"], "supermemory")
            self.assertEqual(report["package_identity"]["declared_version"], "3.0.0-alpha.26")
            self.assertEqual(report["package_identity"]["export_conditions"], ["import", "require"])
            self.assertFalse(report["package_identity"]["exports_verified"])

    def test_invalid_json_warns_instead_of_claiming_success(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "package.json").write_text("not json")
            report = module.inspect(root)
            self.assertIn("PARSE_FAILED:package.json", report["warnings"])
            self.assertEqual(report["sdk_candidates"], [])

    def test_no_manifest_discloses_gap(self):
        with tempfile.TemporaryDirectory() as temp:
            report = module.inspect(temp)
            self.assertIn("NO_SUPPORTED_ROOT_MANIFEST", report["warnings"])

    def test_symlink_manifest_not_followed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "actual.json"
            target.write_text('{"dependencies":{"bad-sdk":"1.0.0"}}')
            (root / "package.json").symlink_to(target)
            report = module.inspect(root)
            self.assertIn("SKIPPED_UNSAFE_MANIFEST:package.json", report["warnings"])
            self.assertEqual(report["sdk_candidates"], [])

    def test_cargo_and_go_sdk_candidates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Cargo.toml").write_text('[dependencies]\nfoo-sdk="1.2.3"\n')
            (root / "go.mod").write_text('module x\nrequire (\n example.com/api-client v1.2.3\n)\n')
            report = module.inspect(root)
            self.assertEqual({x["ecosystem"] for x in report["sdk_candidates"]}, {"cargo", "go"})


if __name__ == "__main__":
    unittest.main()
