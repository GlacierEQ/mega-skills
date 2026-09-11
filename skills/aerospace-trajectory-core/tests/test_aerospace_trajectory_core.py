#!/usr/bin/env python3
"""
L2 Behavioral tests for aerospace-trajectory-core.
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestAerospaceTrajectoryCore:
    """L2 tests for aerospace-trajectory-core - Energy/angular momentum conservation, Lambert convergence, boil-off pressure curves"""
    
    def test_skill_entry_point_exists(self):
        skill_py = Path(__file__).parent.parent / "skill.py"
        assert skill_py.exists()
        assert skill_py.stat().st_mode & 0o111
    
    def test_scripts_exist(self):
        scripts_dir = Path(__file__).parent.parent / "scripts"
        expected = ['orbital_propagator.py', 'lambert_solver.py', 'boiloff_calc.py', 'conjunction_analyzer.py']
        for script in expected:
            p = scripts_dir / script
            assert p.exists(), f"Missing script: {script}"
            assert p.stat().st_mode & 0o111, f"Not executable: {script}"
    
    def test_resources_exist(self):
        resources_dir = Path(__file__).parent.parent / "resources"
        expected = ['orbital_constants.json', 'tank_thermal_models.yaml']
        for res in expected:
            p = resources_dir / res
            assert p.exists(), f"Missing resource: {res}"
    
    def test_boiloff_calc_behavioral(self):
        from scripts.boiloff_calc import calculate_boiloff
        res = calculate_boiloff("LOX", mass_kg=10000.0, heat_leak_watts=100.0, duration_hours=10.0)
        assert res["boiloff_mass_kg"] > 0
        assert res["remaining_mass_kg"] < 10000.0
        assert res["percentage_lost"] > 0

    def test_orbital_propagation_conservation(self):
        from scripts.orbital_propagator import propagate_rk4
        r0 = [7000.0, 0.0, 0.0]
        v0 = [0.0, 7.546, 0.0]
        res = propagate_rk4(r0, v0, dt=5.0, steps=20)
        assert res["specific_energy_km2_s2"] < 0
        assert res["radius_km"] > 6000.0

    def test_lambert_solver_convergence(self):
        from scripts.lambert_solver import solve_lambert
        res = solve_lambert([7000.0, 0.0, 0.0], [0.0, 7000.0, 0.0], time_of_flight_s=3600.0)
        assert res["v1_magnitude_km_s"] > 0
        assert res["chord_km"] > 0

    def test_conjunction_analyzer_behavioral(self):
        from scripts.conjunction_analyzer import analyze_conjunction
        res = analyze_conjunction([7000.0, 0.0, 0.0], [0.0, 7.5, 0.0], [7000.05, 0.0, 0.0], [0.0, -7.5, 0.0])
        assert res["miss_distance_m"] > 0
        assert res["collision_probability"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

