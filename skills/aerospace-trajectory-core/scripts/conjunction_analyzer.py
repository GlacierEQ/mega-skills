#!/usr/bin/env python3
"""
Starlink constellation conjunction probability
Part of aerospace-trajectory-core skill.
"""

import argparse
import json
import math
import sys
from pathlib import Path


def analyze_conjunction(
    pos_a_km: list[float],
    vel_a_km_s: list[float],
    pos_b_km: list[float],
    vel_b_km_s: list[float],
    combined_radius_m: float = 10.0,
    position_uncertainty_m: float = 50.0,
) -> dict:
    """Analyze conjunction geometry and collision probability between two satellites."""
    dx = (pos_b_km[0] - pos_a_km[0]) * 1000.0
    dy = (pos_b_km[1] - pos_a_km[1]) * 1000.0
    dz = (pos_b_km[2] - pos_a_km[2]) * 1000.0
    miss_distance_m = math.sqrt(dx * dx + dy * dy + dz * dz)

    dvx = (vel_b_km_s[0] - vel_a_km_s[0]) * 1000.0
    dvy = (vel_b_km_s[1] - vel_a_km_s[1]) * 1000.0
    dvz = (vel_b_km_s[2] - vel_a_km_s[2]) * 1000.0
    rel_velocity_m_s = math.sqrt(dvx * dvx + dvy * dvy + dvz * dvz)

    # 2D encounter plane Gaussian probability (Foster / Akella approximation)
    sigma2 = position_uncertainty_m * position_uncertainty_m
    hard_sphere_area = math.pi * combined_radius_m * combined_radius_m
    norm_factor = hard_sphere_area / (2.0 * math.pi * sigma2)
    exponent = -(miss_distance_m * miss_distance_m) / (2.0 * sigma2)
    prob = norm_factor * math.exp(exponent) if exponent > -700 else 0.0
    prob = min(1.0, max(0.0, prob))

    risk_tier = "GREEN"
    if prob >= 1e-4:
        risk_tier = "RED"
    elif prob >= 1e-6:
        risk_tier = "YELLOW"

    return {
        "miss_distance_m": round(miss_distance_m, 2),
        "relative_velocity_m_s": round(rel_velocity_m_s, 2),
        "collision_probability": prob,
        "combined_hard_body_radius_m": combined_radius_m,
        "position_uncertainty_sigma_m": position_uncertainty_m,
        "risk_tier": risk_tier,
        "maneuver_recommended": prob >= 1e-5,
    }


def main():
    parser = argparse.ArgumentParser(description="Starlink conjunction probability analyzer")
    parser.add_argument("--miss-dist-m", type=float, default=250.0, help="Direct miss distance in meters")
    parser.add_argument("--rel-vel-m-s", type=float, default=14200.0, help="Relative velocity in m/s")
    parser.add_argument("--sigma-m", type=float, default=100.0, help="Position uncertainty 1-sigma in meters")
    args = parser.parse_args()

    pos_a = [7000.0, 0.0, 0.0]
    pos_b = [7000.0 + (args.miss_dist_m / 1000.0), 0.0, 0.0]
    vel_a = [0.0, 7.5, 0.0]
    vel_b = [0.0, -6.7, 0.0]

    result = analyze_conjunction(pos_a, vel_a, pos_b, vel_b, position_uncertainty_m=args.sigma_m)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

