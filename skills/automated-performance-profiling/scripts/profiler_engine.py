#!/usr/bin/env python3
"""
APEX High-Resolution Performance Profiler Engine
Measures microsecond latency, p50/p95/p99 tail distributions, throughput, and memory RSS deltas.
"""

import argparse
import json
import os
import resource
import statistics
import time
from typing import Callable, Any, Dict, List

def profile_callable(func: Callable, iterations: int = 1000, *args, **kwargs) -> Dict[str, Any]:
    latencies_us = []
    # Warmup
    for _ in range(min(50, iterations)):
        func(*args, **kwargs)
    
    t0 = time.perf_counter_ns()
    for _ in range(iterations):
        call_t0 = time.perf_counter_ns()
        func(*args, **kwargs)
        call_t1 = time.perf_counter_ns()
        latencies_us.append((call_t1 - call_t0) / 1000.0)
    t1 = time.perf_counter_ns()
    
    total_time_s = (t1 - t0) / 1e9
    latencies_us.sort()
    
    p50 = statistics.median(latencies_us)
    p95 = latencies_us[int(len(latencies_us) * 0.95)]
    p99 = latencies_us[int(len(latencies_us) * 0.99)]
    mean = statistics.mean(latencies_us)
    ops_sec = int(iterations / total_time_s) if total_time_s > 0 else iterations
    
    # Memory footprint
    usage = resource.getrusage(resource.RUSAGE_SELF)
    max_rss_mb = usage.ru_maxrss / (1024 * 1024) if sys.platform == 'darwin' else usage.ru_maxrss / 1024
    
    return {
        "iterations": iterations,
        "total_time_seconds": round(total_time_s, 4),
        "mean_latency_microseconds": round(mean, 2),
        "p50_latency_microseconds": round(p50, 2),
        "p95_latency_microseconds": round(p95, 2),
        "p99_latency_microseconds": round(p99, 2),
        "throughput_ops_per_second": ops_sec,
        "max_resident_set_size_mb": round(max_rss_mb, 2),
    }

def main():
    parser = argparse.ArgumentParser(description="APEX Automated Profiler Engine")
    parser.add_argument("--iterations", type=int, default=5000)
    args = parser.parse_args()
    
    def sample_workload():
        _ = sum(i * i for i in range(100))
        
    res = profile_callable(sample_workload, iterations=args.iterations)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    import sys
    main()
