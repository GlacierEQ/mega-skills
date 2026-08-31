import importlib.util
import unittest
from pathlib import Path

TEST_FILE = Path(__file__).resolve().parents[1] / "skills" / "autonomous-software-engineering" / "tests" / "test_pipeline_simulation.py"

spec = importlib.util.spec_from_file_location("pipeline_simulation_tests", TEST_FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


# Re-export the suite so the repository's normal unittest discovery executes it.
PipelineSimulationTests = module.PipelineSimulationTests


if __name__ == "__main__":
    unittest.main()
