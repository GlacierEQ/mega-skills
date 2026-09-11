#!/usr/bin/env python3
"""
Cryogenic LOX/CH4 boil-off thermodynamics
Part of aerospace-trajectory-core skill.
"""

import argparse
import json
import math
import sys
from pathlib import Path

# Latent heat of vaporization in J/kg
LATENT_HEAT = {
    "LOX": 213000.0,
    "LCH4": 510000.0,
}


def calculate_boiloff(propellant: str, mass_kg: float, heat_leak_watts: float, duration_hours: float) -> dict:
    """Calculate cryogenic propellant boil-off given heat flux and time."""
    prop = propellant.upper()
    lv = LATENT_HEAT.get(prop, 300000.0)
    duration_sec = duration_hours * 3600.0
    total_heat_joules = heat_leak_watts * duration_sec
    boiloff_mass = min(mass_kg, total_heat_joules / lv)
    boiloff_rate_kg_per_hr = (heat_leak_watts * 3600.0) / lv
    remaining_mass = max(0.0, mass_kg - boiloff_mass)
    percentage_lost = (boiloff_mass / mass_kg * 100.0) if mass_kg > 0 else 0.0

    return {
        "propellant": prop,
        "initial_mass_kg": round(mass_kg, 2),
        "heat_leak_watts": round(heat_leak_watts, 2),
        "duration_hours": round(duration_hours, 2),
        "boiloff_mass_kg": round(boiloff_mass, 4),
        "boiloff_rate_kg_per_hr": round(boiloff_rate_kg_per_hr, 4),
        "remaining_mass_kg": round(remaining_mass, 2),
        "percentage_lost": round(percentage_lost, 4),
    }


def main():
    parser = argparse.ArgumentParser(description="Cryogenic LOX/CH4 boil-off thermodynamics calculator")
    parser.add_argument("--propellant", default="LOX", choices=("LOX", "LCH4"), help="Propellant type")
    parser.add_argument("--mass", type=float, default=100000.0, help="Initial propellant mass (kg)")
    parser.add_argument("--heat-leak", type=float, default=150.0, help="Heat leak rate (Watts)")
    parser.add_argument("--duration", type=float, default=24.0, help="Duration (hours)")
    args = parser.parse_args()

    result = calculate_boiloff(args.propellant, args.mass, args.heat_leak, args.duration)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

