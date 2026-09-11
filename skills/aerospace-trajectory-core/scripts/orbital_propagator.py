#!/usr/bin/env python3
"""
High-order numerical orbital propagation (RK4/DP8)
Part of aerospace-trajectory-core skill.
"""

import argparse
import json
import math
import sys
from pathlib import Path

MU_EARTH_KM3_S2 = 398600.4418  # km^3 / s^2


def gravity_acceleration(r: list[float], mu: float = MU_EARTH_KM3_S2) -> list[float]:
    r_mag = math.sqrt(r[0]**2 + r[1]**2 + r[2]**2)
    if r_mag == 0:
        return [0.0, 0.0, 0.0]
    factor = -mu / (r_mag**3)
    return [factor * r[0], factor * r[1], factor * r[2]]


def propagate_rk4(r0: list[float], v0: list[float], dt: float, steps: int, mu: float = MU_EARTH_KM3_S2) -> dict:
    r = list(r0)
    v = list(v0)

    for _ in range(steps):
        # k1
        a1 = gravity_acceleration(r, mu)
        v1 = list(v)

        # k2
        r2 = [r[i] + 0.5 * dt * v1[i] for i in range(3)]
        a2 = gravity_acceleration(r2, mu)
        v2 = [v[i] + 0.5 * dt * a1[i] for i in range(3)]

        # k3
        r3 = [r[i] + 0.5 * dt * v2[i] for i in range(3)]
        a3 = gravity_acceleration(r3, mu)
        v3 = [v[i] + 0.5 * dt * a2[i] for i in range(3)]

        # k4
        r4 = [r[i] + dt * v3[i] for i in range(3)]
        a4 = gravity_acceleration(r4, mu)
        v4 = [v[i] + dt * a3[i] for i in range(3)]

        for i in range(3):
            r[i] += (dt / 6.0) * (v1[i] + 2.0 * v2[i] + 2.0 * v3[i] + v4[i])
            v[i] += (dt / 6.0) * (a1[i] + 2.0 * a2[i] + 2.0 * a3[i] + a4[i])

    r_mag = math.sqrt(r[0]**2 + r[1]**2 + r[2]**2)
    v_mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    specific_energy = (v_mag**2) / 2.0 - (mu / r_mag)
    semi_major_axis_km = -mu / (2.0 * specific_energy) if specific_energy < 0 else None

    return {
        "final_position_km": [round(x, 4) for x in r],
        "final_velocity_km_s": [round(x, 4) for x in v],
        "radius_km": round(r_mag, 4),
        "speed_km_s": round(v_mag, 4),
        "specific_energy_km2_s2": round(specific_energy, 4),
        "semi_major_axis_km": round(semi_major_axis_km, 4) if semi_major_axis_km else None,
        "elapsed_seconds": round(dt * steps, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Numerical orbital propagator (RK4)")
    parser.add_argument("--altitude-km", type=float, default=500.0, help="Initial circular orbit altitude")
    parser.add_argument("--dt", type=float, default=10.0, help="Timestep in seconds")
    parser.add_argument("--steps", type=int, default=100, help="Number of integration steps")
    args = parser.parse_args()

    r0_mag = 6378.137 + args.altitude_km
    v0_mag = math.sqrt(MU_EARTH_KM3_S2 / r0_mag)
    r0 = [r0_mag, 0.0, 0.0]
    v0 = [0.0, v0_mag, 0.0]

    result = propagate_rk4(r0, v0, args.dt, args.steps)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

