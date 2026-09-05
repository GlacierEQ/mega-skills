#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from engine import PipelineError, execute_pipeline, topological_layers, validate_pipeline


class PipelineCompositorBehaviorTests(unittest.TestCase):
    def test_cycle_rejected(self):
        spec={
            "schema_version":1,
            "id":"cycle",
            "stages":[
                {"id":"a","needs":["b"],"command":[sys.executable,"-c","print('a')"]},
                {"id":"b","needs":["a"],"command":[sys.executable,"-c","print('b')"]}
            ]
        }
        with self.assertRaises(PipelineError):
            validate_pipeline(spec)

    def test_parallel_layers(self):
        spec={
            "schema_version":1,
            "id":"layers",
            "stages":[
                {"id":"a","command":[sys.executable,"-c","print('a')"]},
                {"id":"b","command":[sys.executable,"-c","print('b')"]},
                {"id":"c","needs":["a","b"],"command":[sys.executable,"-c","print('c')"]}
            ]
        }
        self.assertEqual(topological_layers(spec), [["a","b"],["c"]])

    def test_execution_checkpoint_and_resume(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            script=root/"make.py"
            script.write_text("from pathlib import Path\nPath('out.json').write_text('{\\\"ok\\\":true}')\n", encoding="utf-8")
            spec={
                "schema_version":1,
                "id":"demo",
                "manifest":"manifest.json",
                "stages":[
                    {
                        "id":"make",
                        "command":[sys.executable,"make.py"],
                        "produces":["out.json"],
                        "resume_safe":True
                    }
                ]
            }
            first=execute_pipeline(spec,root,state_dir="state",resume=True)
            self.assertEqual(first["status"],"COMPLETE")
            self.assertEqual(first["summary"]["succeeded"],1)
            second=execute_pipeline(spec,root,state_dir="state",resume=True)
            self.assertEqual(second["summary"]["resumed"],1)
            manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"],"COMPLETE")


if __name__=="__main__":
    unittest.main()
