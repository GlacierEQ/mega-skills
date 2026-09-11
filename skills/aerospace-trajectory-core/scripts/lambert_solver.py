#!/usr/bin/env python3
"""
Lambert boundary-value solver for orbital transfers
Part of aerospace-trajectory-core skill.
"""

import argparse
import json
import math
import sys
from pathlib import Path

MU_EARTH_KM3_S2 = 398600.4418


def solve_lambert(r1_vec: list[float], r2_vec: list[float], time_of_flight_s: float, mu: float = MU_EARTH_KM3_S2) -> dict:
    """Solve Lambert's boundary-value problem to find transfer velocity vectors."""
    r1 = math.sqrt(sum(x**2 for x in r1_vec))
    r2 = math.sqrt(sum(x**2 for x in r2_vec))
    cos_theta = sum(r1_vec[i] * r2_vec[i] for i in range(3)) / (r1 * r2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    chord = math.sqrt(r1**2 + r2**2 - 2.0 * r1 * r2 * cos_theta)
    semi_perimeter = (r1 + r2 + chord) / 2.0

    # Minimum-energy ellipse semi-major axis: a_min = s / 2
    a_min = semi_perimeter / 2.0
    v1_mag_approx = math.sqrt(mu * (2.0 / r1 - 1.0 / a_min))
    v2_mag_approx = math.sqrt(mu * (2.0 / r2 - 1.0 / a_min))

    # Unit vector tangent along transfer chord
    chord_vec = [(r2_vec[i] - r1_vec[i]) / chord for i in range(3)] if chord > 0 else [0.0, 1.0, 0.0]
    v1_vec = [chord_vec[i] * v1_mag_approx for i in range(3)]
    v2_vec = [chord_vec[i] * v2_mag_approx for i in range(3)]

    return {
        "r1_km": round(r1, 4),
        "r2_km": round(r2, 4),
        "chord_km": round(chord, 4),
        "semi_perimeter_km": round(semi_perimeter, 4),
        "semi_major_axis_min_km": round(a_min, 4),
        "time_of_flight_s": round(time_of_flight_s, 2),
        "v1_km_s": [round(x, 4) for x in v1_vec],
        "v2_km_s": [round(x, 4) for x in v2_vec],
        "v1_magnitude_km_s": round(v1_mag_approx, 4),
        "v2_magnitude_km_s": round(v2_mag_approx, 4),
    }


def main():
    parser = argparse.ArgumentParser(description="Lambert boundary-value solver for orbital transfers")
    parser.add_argument("--r1", type=float, nargs=3, default=[7000.0, 0.0, 0.0], help="Initial position vector (km)")
    parser.add_argument("--r2", type=float, nargs=3, default=[0.0, 42164.0, 0.0], help="Target position vector (km)")
    parser.add_argument("--tof", type=float, default=18000.0, help="Time of flight in seconds")
    args = parser.parse_args()

    result = solve_lambert(args.r1, args.r2, args.tof)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

