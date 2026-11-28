"""Validation tests for pipeline-execution-manifest.json artifact."""

import json
import unittest
from pathlib import Path

MANIFEST_PATH = Path(__file__).resolve().parents[1] / "missions" / "deep-casebuilding" / "pipeline-execution-manifest.json"


class PipelineExecutionManifestTests(unittest.TestCase):
    """Tests validating the pipeline-execution-manifest.json structure and content."""

    def test_manifest_exists(self):
        """Manifest file exists at expected location."""
        self.assertTrue(MANIFEST_PATH.exists(), f"Manifest not found at {MANIFEST_PATH}")

    def test_manifest_valid_json(self):
        """Manifest is valid JSON."""
        with MANIFEST_PATH.open() as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_manifest_has_required_fields(self):
        """Manifest contains all required fields."""
        with MANIFEST_PATH.open() as f:
            data = json.load(f)
        
        required_fields = [
            "schema_version",
            "pipeline_id",
            "state",
            "stages_completed",
            "last_run_utc",
            "notes",
            "pipeline_definition",
            "owner",
            "created_utc",
            "updated_utc",
            "run_history",
            "current_stage",
            "stage_outputs",
            "verification_receipts",
            "metadata",
        ]
        for field in required_fields:
            self.assertIn(field, data, f"Missing required field: {field}")

    def test_manifest_schema_version(self):
        """Manifest has correct schema version."""
        with MANIFEST_PATH.open() as f:
            data = json.load(f)
        self.assertEqual(data["schema_version"], 1)

    def test_manifest_pipeline_id(self):
        """Manifest has correct pipeline ID."""
        with MANIFEST_PATH.open() as f:
            data = json.load(f)
        self.assertEqual(data["pipeline_id"], "deep-casebuilding")

    def test_manifest_owner(self):
        """Manifest has correct owner."""
        with MANIFEST_PATH.open() as f:
            data = json.load(f)
        self.assertEqual(data["owner"], "projects/labs")

    def test_manifest_metadata_has_leverage(self):
        """Manifest metadata includes leverage score and distill rank."""
        with MANIFEST_PATH.open() as f:
            data = json.load(f)
        metadata = data["metadata"]
        self.assertIn("leverage_score", metadata)
        self.assertIn("distill_rank", metadata)
        self.assertIn("sha256", metadata)
        self.assertEqual(metadata["leverage_score"], 49)
        self.assertEqual(metadata["distill_rank"], 20)
        # This SHA-256 is the original artifact hash from distill.json (provenance)
        self.assertEqual(metadata["sha256"], "04926a9f66ac492f9f41cfb378d4cb29501f4583a4ca786d681f4e653f7a85a0")

    def test_manifest_state_valid(self):
        """Manifest state is a recognized value."""
        with MANIFEST_PATH.open() as f:
            data = json.load(f)
        valid_states = ["initialized", "running", "completed", "failed", "paused"]
        self.assertIn(data["state"], valid_states)

    def test_manifest_stages_completed_is_list(self):
        """Manifest stages_completed is a list."""
        with MANIFEST_PATH.open() as f:
            data = json.load(f)
        self.assertIsInstance(data["stages_completed"], list)

    def test_manifest_last_run_utc_nullable(self):
        """Manifest last_run_utc is either null or ISO timestamp string."""
        with MANIFEST_PATH.open() as f:
            data = json.load(f)
        last_run = data["last_run_utc"]
        self.assertTrue(last_run is None or isinstance(last_run, str))

    def test_manifest_notes_non_empty(self):
        """Manifest notes field has content."""
        with MANIFEST_PATH.open() as f:
            data = json.load(f)
        self.assertIsInstance(data["notes"], str)
        self.assertGreater(len(data["notes"]), 10)

    def test_manifest_serializable_roundtrip(self):
        """Manifest can be serialized and deserialized without loss."""
        with MANIFEST_PATH.open() as f:
            original = json.load(f)
        serialized = json.dumps(original, sort_keys=True)
        deserialized = json.loads(serialized)
        self.assertEqual(original, deserialized)


if __name__ == "__main__":
    unittest.main()