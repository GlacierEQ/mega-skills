#!/usr/bin/env python3
"""Behavioral tests for automated-performance-profiling."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


class TestAutomatedPerformanceProfiling(unittest.TestCase):
    def setUp(self):
        self.skill_dir = ROOT

    def test_profile_callable_behavioral(self):
        from profiler_engine import profile_callable
        result = profile_callable(lambda: sum(i for i in range(50)), iterations=200)
        self.assertEqual(result["iterations"], 200)
        self.assertTrue("p50_latency_microseconds" in result)
        self.assertTrue("throughput_ops_per_second" in result)
        self.assertTrue(result["throughput_ops_per_second"] > 0)


if __name__ == "__main__":
    unittest.main()

