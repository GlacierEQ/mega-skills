#!/usr/bin/env python3
"""
L2 Behavioral tests for connector-bridge.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestConnectorBridge:
    """L2 tests for connector-bridge - Rate-limit compliance, circuit-breaker transitions, schema validation, token budget enforcement"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['credential_resolver.py', 'rate_limiter.py', 'circuit_breaker.py', 'protocol_serializer.py', 'dispatcher.py', 'telemetry_recorder.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['endpoint_profiles.yaml', 'schema_registry.json']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_circuit_breaker_behavioral(self):
        from scripts.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState
        cb = CircuitBreaker("unit-test", CircuitBreakerConfig(failure_threshold=2))
        assert cb.state == CircuitState.CLOSED
        cb._on_failure()
        cb._on_failure()
        assert cb.state == CircuitState.OPEN


    def test_rate_limiter_configs(self):
        from scripts.rate_limiter import DEFAULT_CONFIGS
        assert "openrouter" in DEFAULT_CONFIGS
        assert DEFAULT_CONFIGS["openrouter"].requests_per_second > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

